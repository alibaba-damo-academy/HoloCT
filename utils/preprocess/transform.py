import torch

import numpy as np

from monai.transforms import (
    Compose,
    LoadImaged,
    EnsureChannelFirstd,
    Orientationd,
    Spacingd,
    CropForegroundd,
    ScaleIntensityRanged,
    MapTransform,
    Resized,
    CastToTyped,
)
from monai.data.meta_tensor import MetaTensor


from monai.transforms import DivisiblePadd


from typing import Any, Dict, Hashable, Sequence, Tuple, Union
from monai.data.utils import compute_shape_offset, to_affine_nd, zoom_affine

Number = Union[int, float]


class SafeLoadImaged(LoadImaged):
    """Load the CT branch used by the inference pipeline."""

    def __call__(self, data):
        d = dict(data)
        if tuple(self.keys) != ("video_seg",) or d.get("video_seg") is None:
            raise ValueError("SafeLoadImaged requires one video_seg CT path.")
        loaded = super().__call__({"video_seg": d["video_seg"]})
        d["video_seg"] = loaded["video_seg"]
        return d


class DivisiblePadd32d(DivisiblePadd):
    def __init__(
        self,
        keys,
        multiple=32,
        method="symmetric",
        mode="constant",
        pad_value=0.0,
        allow_missing_keys=False,
        lazy=False,
        debug=False,
    ):
        self.multiple = int(multiple)
        self.pad_method = str(method)
        self.pad_mode = mode
        self.pad_value = float(pad_value)
        self.debug = bool(debug)

        if self.multiple <= 0:
            raise ValueError(f"multiple must be positive; got {self.multiple}")

        if self.pad_method not in {"symmetric", "end"}:
            raise ValueError(
                f"method must be 'symmetric' or 'end'; got {self.pad_method}"
            )

        super().__init__(
            keys=keys,
            k=self.multiple,
            mode=mode,
            method=method,
            allow_missing_keys=allow_missing_keys,
            lazy=lazy,
            value=self.pad_value,
        )

    @staticmethod
    def _spatial_shape(x):
        if not hasattr(x, "shape"):
            raise TypeError(f"Input has no shape attribute; got type {type(x)}")

        if len(x.shape) < 4:
            raise ValueError(
                f"DivisiblePadd32d expects at least four dimensions (C,D,H,W); got shape={tuple(x.shape)}"
            )

        return tuple(int(v) for v in x.shape[-3:])

    def __call__(self, data, lazy=None):
        before_shapes = {}

        for key in self.keys:
            if key in data:
                before_shapes[key] = self._spatial_shape(data[key])

        result = super().__call__(
            data,
            lazy=lazy,
        )

        for key, before_shape in before_shapes.items():
            if key not in result:
                continue

            after_shape = self._spatial_shape(result[key])

            for axis, (before, after) in enumerate(zip(before_shape, after_shape)):
                if after < before:
                    raise RuntimeError(
                        f"{key} on axis={axis} was reduced: {before} -> {after}"
                    )

                if after % self.multiple != 0:
                    raise RuntimeError(
                        f"{key} on axis={axis} was not padded to a multiple of {self.multiple}; after={after}"
                    )

            print(
                f"[DivisiblePadd32d] key={key}, "
                f"before={before_shape}, "
                f"after={after_shape}, "
                f"multiple={self.multiple}, "
                f"method={self.pad_method}, "
                f"value={self.pad_value}"
            )

        return result


"\nAdaptive spacing after foreground cropping. Predict the MONAI output grid and padded volume, select the smallest isotropic scale satisfying the volume bound, then resample once. The same Spacingd instance reverses the operation using its recorded transform trace.\n"


class AdaptiveSpacingdWithPaddedVolumeLimit(MapTransform):
    def __init__(
        self,
        keys: Sequence[Hashable],
        reference_key: Hashable = "video_seg",
        base_pixdim: Sequence[Number] = (1.5, 1.5, 1.5),
        multiple: int = 32,
        volume_threshold: float = 1800.0,
        norm_factor: Number = 32 * 32 * 16,
        mode: Union[str, Sequence[str]] = ("bilinear", "nearest"),
        padding_mode: Union[str, Sequence[str]] = "border",
        align_corners: Union[bool, Sequence[bool]] = False,
        dtype: Any = np.float64,
        diagonal: bool = False,
        scale_extent: bool = False,
        recompute_affine: bool = False,
        allow_missing_keys: bool = False,
        binary_search_max_iter: int = 20,
        scale_abs_tol: float = 1e-6,
        scale_rel_tol: float = 1e-6,
        safety_scale: float = 1e-7,
        max_scale: float = 64.0,
        growth_factor: float = 1.05,
        print_debug: bool = True,
        meta_prefix: str = "adaptive_spacing",
    ) -> None:
        super().__init__(
            keys=keys,
            allow_missing_keys=allow_missing_keys,
        )

        if reference_key not in self.keys:
            raise ValueError(
                f"reference_key={reference_key!r} must be included in keys={tuple(self.keys)!r}"
            )
        if multiple <= 0:
            raise ValueError(f"multiple must be positive; got {multiple}")
        if volume_threshold <= 0:
            raise ValueError(
                f"volume_threshold must be positive; got {volume_threshold}"
            )
        if norm_factor <= 0:
            raise ValueError(f"norm_factor must be positive; got {norm_factor}")
        if binary_search_max_iter <= 0:
            raise ValueError(
                f"binary_search_max_iter must be positive; got {binary_search_max_iter}"
            )
        if scale_abs_tol <= 0 or scale_rel_tol <= 0:
            raise ValueError("scale_abs_tol and scale_rel_tol must be positive")
        if safety_scale < 0:
            raise ValueError(f"safety_scale must be nonnegative; got {safety_scale}")
        if max_scale <= 1.0:
            raise ValueError(f"max_scale must exceed 1; got {max_scale}")
        if growth_factor <= 1.0:
            raise ValueError(f"growth_factor must exceed 1; got {growth_factor}")

        base = np.asarray(tuple(base_pixdim), dtype=np.float64)
        if base.ndim != 1 or base.size == 0:
            raise ValueError(
                f"base_pixdim must be a nonempty one-dimensional sequence; got shape={base.shape}"
            )
        if not np.all(np.isfinite(base)) or np.any(base <= 0):
            raise ValueError(
                f"base_pixdim must contain finite positive values; got {base}"
            )

        self.reference_key = reference_key
        self.base_pixdim = base
        self.multiple = int(multiple)
        self.volume_threshold = float(volume_threshold)
        self.norm_factor = float(norm_factor)

        self.diagonal = bool(diagonal)
        self.scale_extent = bool(scale_extent)
        self.recompute_affine = bool(recompute_affine)

        self.binary_search_max_iter = int(binary_search_max_iter)
        self.scale_abs_tol = float(scale_abs_tol)
        self.scale_rel_tol = float(scale_rel_tol)
        self.safety_scale = float(safety_scale)
        self.max_scale = float(max_scale)
        self.growth_factor = float(growth_factor)

        self.print_debug = bool(print_debug)
        self.meta_prefix = str(meta_prefix)

        self.spacing_transform = Spacingd(
            keys=self.keys,
            pixdim=tuple(self.base_pixdim.tolist()),
            diagonal=self.diagonal,
            mode=mode,
            padding_mode=padding_mode,
            align_corners=align_corners,
            dtype=dtype,
            scale_extent=self.scale_extent,
            recompute_affine=self.recompute_affine,
            allow_missing_keys=allow_missing_keys,
        )

    @staticmethod
    def _spatial_shape(img: Any) -> Tuple[int, ...]:
        if isinstance(img, MetaTensor) and hasattr(img, "peek_pending_shape"):
            shape = img.peek_pending_shape()
        else:
            shape = img.shape[1:]

        result = tuple(int(x) for x in shape)
        if not result:
            raise ValueError(
                f"Cannot determine the spatial shape; input shape={tuple(img.shape)}"
            )
        return result

    @staticmethod
    def _affine(img: Any, spatial_rank: int) -> np.ndarray:
        value = None

        if isinstance(img, MetaTensor):
            if hasattr(img, "peek_pending_affine"):
                value = img.peek_pending_affine()
            elif hasattr(img, "affine"):
                value = img.affine

        if value is None and hasattr(img, "meta"):
            value = img.meta.get("affine")

        if value is None:
            raise ValueError(
                "AdaptiveSpacingdWithPaddedVolumeLimit requires a MetaTensor with an affine. Preserve metadata through loading, orientation and cropping."
            )

        if torch.is_tensor(value):
            value = value.detach().cpu().numpy()

        return np.asarray(
            to_affine_nd(
                spatial_rank,
                np.asarray(value, dtype=np.float64),
            ),
            dtype=np.float64,
        )

    def _pixdim_for_scale(
        self,
        scale: float,
        spatial_rank: int,
    ) -> np.ndarray:
        base = self.base_pixdim

        if base.size < spatial_rank:
            base = np.concatenate(
                [
                    base,
                    np.repeat(
                        base[-1],
                        spatial_rank - base.size,
                    ),
                ]
            )

        return base[:spatial_rank] * float(scale)

    def _predict_spacing_shape(
        self,
        img: Any,
        scale: float,
    ) -> Tuple[Tuple[int, ...], Tuple[float, ...]]:
        input_shape = self._spatial_shape(img)
        spatial_rank = len(input_shape)
        input_affine = self._affine(
            img,
            spatial_rank=spatial_rank,
        )
        chosen_pixdim = self._pixdim_for_scale(
            scale,
            spatial_rank=spatial_rank,
        )

        output_affine = zoom_affine(
            input_affine,
            chosen_pixdim,
            diagonal=self.diagonal,
        )

        output_shape, _ = compute_shape_offset(
            spatial_shape=input_shape,
            in_affine=input_affine,
            out_affine=output_affine,
            scale_extent=self.scale_extent,
        )

        return (
            tuple(int(x) for x in output_shape),
            tuple(float(x) for x in chosen_pixdim),
        )

    def _future_padded_shape(
        self,
        spacing_shape: Sequence[int],
    ) -> Tuple[int, ...]:
        return tuple(
            max(
                self.multiple,
                ((int(dim) + self.multiple - 1) // self.multiple) * self.multiple,
            )
            for dim in spacing_shape
        )

    def _volume_ratio(
        self,
        padded_shape: Sequence[int],
    ) -> float:
        padded_voxels = int(np.prod(np.asarray(padded_shape, dtype=np.int64)))
        return float(padded_voxels / self.norm_factor)

    def _evaluate(
        self,
        img: Any,
        scale: float,
    ) -> Dict[str, Any]:
        spacing_shape, pixdim = self._predict_spacing_shape(
            img,
            scale=scale,
        )
        padded_shape = self._future_padded_shape(spacing_shape)
        ratio = self._volume_ratio(padded_shape)

        return {
            "scale": float(scale),
            "pixdim": pixdim,
            "spacing_shape": spacing_shape,
            "padded_shape": padded_shape,
            "volume_ratio": ratio,
            "fits": bool(ratio <= self.volume_threshold),
        }

    def _find_scale(
        self,
        img: Any,
    ) -> Tuple[Dict[str, Any], Dict[str, Any], int]:
        base_info = self._evaluate(img, scale=1.0)

        if base_info["fits"]:
            return base_info, base_info, 0

        estimated_scale = max(
            1.0 + self.scale_abs_tol,
            (base_info["volume_ratio"] / self.volume_threshold) ** (1.0 / 3.0),
        )

        low = 1.0
        high = float(estimated_scale)
        high_info = self._evaluate(img, scale=high)

        while not high_info["fits"]:
            low = high
            high *= self.growth_factor

            if high > self.max_scale:
                raise RuntimeError(
                    f"Cannot satisfy the padded volume bound within max_scale: base_info={base_info}, last_scale={high}, max_scale={self.max_scale}, threshold={self.volume_threshold}"
                )

            high_info = self._evaluate(img, scale=high)

        iterations_used = 0

        for _ in range(self.binary_search_max_iter):
            width = high - low
            tolerance = max(
                self.scale_abs_tol,
                self.scale_rel_tol * high,
            )

            if width <= tolerance:
                break

            mid = (low + high) * 0.5
            mid_info = self._evaluate(img, scale=mid)
            iterations_used += 1

            if mid_info["fits"]:
                high = mid
                high_info = mid_info
            else:
                low = mid

        chosen_scale = high * (1.0 + self.safety_scale)
        chosen_info = self._evaluate(
            img,
            scale=chosen_scale,
        )

        if not chosen_info["fits"]:
            chosen_scale = float(
                np.nextafter(
                    np.float64(chosen_scale),
                    np.float64(np.inf),
                )
            )
            chosen_info = self._evaluate(
                img,
                scale=chosen_scale,
            )

        if not chosen_info["fits"]:
            raise RuntimeError(
                f"The selected scale still violates the volume bound: chosen_info={chosen_info}"
            )

        return base_info, chosen_info, iterations_used

    def __call__(
        self,
        data: Dict[Hashable, Any],
    ) -> Dict[Hashable, Any]:
        d = dict(data)

        if self.reference_key not in d or d[self.reference_key] is None:
            if self.allow_missing_keys:
                return d
            raise KeyError(f"Missing reference_key={self.reference_key!r}")

        reference = d[self.reference_key]
        cropped_input_shape = self._spatial_shape(reference)

        base_info, chosen_info, iterations_used = self._find_scale(reference)

        chosen_pixdim = np.asarray(
            chosen_info["pixdim"],
            dtype=np.float64,
        )

        self.spacing_transform.spacing_transform.pixdim = chosen_pixdim.copy()
        out = self.spacing_transform(d)

        actual_spacing_shape = self._spatial_shape(out[self.reference_key])
        actual_padded_shape = self._future_padded_shape(actual_spacing_shape)
        actual_ratio = self._volume_ratio(actual_padded_shape)

        if actual_ratio > self.volume_threshold:
            raise RuntimeError(
                f"The actual padded Spacingd output exceeds the volume bound. The MONAI grid calculation may differ from the predicted grid: cropped_input_shape={cropped_input_shape}, chosen_pixdim={tuple(chosen_pixdim)}, predicted_spacing_shape={chosen_info['spacing_shape']}, actual_spacing_shape={actual_spacing_shape}, actual_padded_shape={actual_padded_shape}, actual_ratio={actual_ratio}, threshold={self.volume_threshold}"
            )

        for key in self.key_iterator(out):
            value = out[key]
            if hasattr(value, "meta"):
                value.meta[f"{self.meta_prefix}_chosen_scale"] = float(
                    chosen_info["scale"]
                )
                value.meta[f"{self.meta_prefix}_chosen_pixdim"] = tuple(
                    float(x) for x in chosen_pixdim
                )
                value.meta[f"{self.meta_prefix}_spacing_shape"] = tuple(
                    int(x) for x in actual_spacing_shape
                )
                value.meta[f"{self.meta_prefix}_future_padded_shape"] = tuple(
                    int(x) for x in actual_padded_shape
                )
                value.meta[f"{self.meta_prefix}_volume_ratio"] = float(actual_ratio)
                value.meta[f"{self.meta_prefix}_search_iterations"] = int(
                    iterations_used
                )

        if self.print_debug:
            changed = not np.allclose(
                chosen_pixdim,
                self._pixdim_for_scale(
                    1.0,
                    len(cropped_input_shape),
                ),
                rtol=0.0,
                atol=1e-12,
            )

            print(
                "[AdaptiveSpacingdWithPaddedVolumeLimit] "
                f"key={self.reference_key}, "
                f"cropped_input_shape={cropped_input_shape}, "
                f"base_pixdim={base_info['pixdim']}, "
                f"base_spacing_shape={base_info['spacing_shape']}, "
                f"base_padded_shape={base_info['padded_shape']}, "
                f"base_ratio={base_info['volume_ratio']:.6f}, "
                f"changed={changed}, "
                f"search_iterations={iterations_used}, "
                f"chosen_scale={chosen_info['scale']:.10f}, "
                f"chosen_pixdim={chosen_info['pixdim']}, "
                f"actual_spacing_shape={actual_spacing_shape}, "
                f"future_padded_shape={actual_padded_shape}, "
                f"final_ratio={actual_ratio:.6f}, "
                f"threshold={self.volume_threshold:.6f}",
                flush=True,
            )

        return out

    def inverse(
        self,
        data: Dict[Hashable, Any],
    ) -> Dict[Hashable, Any]:
        return self.spacing_transform.inverse(data)




# RadGenome preprocessed CTs may encode 1 x 1 x 1 mm instead of 1 x 1 x 3 mm.
# Correct the detailed branch geometry before orientation and resampling.
class FixSegmentSpacingd(MapTransform):
    def __init__(self, keys, allow_missing_keys=False, debug=False):
        super().__init__(keys, allow_missing_keys=allow_missing_keys)
        self.debug = debug

    def __call__(self, data):
        d = dict(data)

        for key in self.keys:
            if key in ["video_txt"] or key not in d or d[key] is None:
                continue

            img = d[key]

            if isinstance(img, MetaTensor):
                curr_affine = img.affine.clone()
                spacing = torch.linalg.norm(curr_affine[:3, :3], dim=0)

                if self.debug:
                    print(f"[FixSegmentSpacingd] key={key}")
                    print(f"  current spacing: {spacing.tolist()}")

                if torch.allclose(
                    spacing,
                    torch.tensor([1.0, 1.0, 1.0], dtype=spacing.dtype),
                    atol=1e-3
                ):
                    if self.debug:
                        print(f"  -> spacing detected as [1,1,1], correcting z to 3.0")

                    curr_affine[:3, 2] *= 3.0
                    img.affine = curr_affine

                    if "affine" in img.meta:
                        img.meta["affine"] = curr_affine.clone()

                    if "original_affine" in img.meta:
                        orig_aff = np.array(img.meta["original_affine"], dtype=np.float64)
                        orig_aff[:3, 2] *= 3.0
                        img.meta["original_affine"] = orig_aff

                    if "pixdim" in img.meta:
                        pixdim = np.array(img.meta["pixdim"])
                        pixdim[3] = 3.0
                        img.meta["pixdim"] = pixdim

                    if "srow_z" in img.meta:
                        srow_z = np.array(img.meta["srow_z"])
                        srow_z[2] = 3.0
                        img.meta["srow_z"] = srow_z

                    if "spacing" in img.meta:
                        img.meta["spacing"] = np.array([1.0, 1.0, 3.0])

                    if self.debug:
                        new_spacing = torch.linalg.norm(img.affine[:3, :3], dim=0)
                        print(f"  corrected spacing: {new_spacing.tolist()}")

            d[key] = img

        return d


class ForegroundAboveThreshold:
    def __init__(self, threshold):
        self.threshold = float(threshold)

    def __call__(self, x):
        return x > self.threshold


def build_video_deterministic_transform(args, fix_segment_spacing=False):
    video_keys = ["video_seg", "video_txt"]

    transforms = [
        SafeLoadImaged(
            keys=["video_seg"],
            allow_missing_keys=True,
        ),
        LoadImaged(keys=["video_txt"]),
    ]

    if fix_segment_spacing:
        transforms.append(FixSegmentSpacingd(keys=["video_seg"]))

    transforms.extend(
        [
            EnsureChannelFirstd(keys=video_keys),
            Orientationd(
                keys=video_keys,
                axcodes="SRA",
            ),
            CropForegroundd(
                keys=["video_seg"],
                source_key="video_seg",
                select_fn=ForegroundAboveThreshold(args.a_min),
            ),
            AdaptiveSpacingdWithPaddedVolumeLimit(
                keys=["video_seg"],
                reference_key="video_seg",
                base_pixdim=(
                    args.space_x,
                    args.space_y,
                    args.space_z,
                ),
                multiple=32,
                volume_threshold=1800,
                norm_factor=32 * 32 * 16,
                mode=("bilinear",),
                padding_mode=("border",),
                align_corners=(False,),
                diagonal=False,
                scale_extent=False,
                recompute_affine=False,
                binary_search_max_iter=20,
                scale_abs_tol=1e-6,
                scale_rel_tol=1e-6,
                safety_scale=1e-7,
                max_scale=64.0,
                growth_factor=1.05,
                print_debug=False,
            ),
            DivisiblePadd32d(
                keys=["video_seg"],
                multiple=32,
                method="symmetric",
                mode="constant",
                pad_value=args.a_min,
                allow_missing_keys=False,
                debug=False,
            ),
            Resized(
                keys=["video_txt"],
                spatial_size=(128, 256, 256),
                mode="bilinear",
            ),
            ScaleIntensityRanged(
                keys=video_keys,
                a_min=args.a_min,
                a_max=args.a_max,
                b_min=args.b_min,
                b_max=args.b_max,
                clip=True,
            ),
            CastToTyped(
                keys=video_keys,
                dtype=torch.float16,
            ),
        ]
    )

    return Compose(transforms)
