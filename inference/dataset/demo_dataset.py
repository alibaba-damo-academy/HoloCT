"""One CT and a user prompt for HoloCT inference."""

from pathlib import Path

import nibabel as nib
import numpy as np
import torch
from torch.utils.data import Dataset

from utils.preprocess import messages_for_apply_template, pad_to_shape
from utils.preprocess.transform import build_video_deterministic_transform


class DatasetArgs:
    space_x = space_y = space_z = 1.5
    a_min, a_max = -1000.0, 1000.0
    b_min, b_max = 0.0, 1.0


class DemoDataset(Dataset):
    """Preprocess once and reuse the same CT tensors for both prompts."""

    def __init__(self, ct_path, *, fix_segment_spacing=False):
        self.ct_path = Path(ct_path).expanduser().resolve()
        if not self.ct_path.is_file():
            raise FileNotFoundError(f"CT file not found: {self.ct_path}")
        if not self.ct_path.name.lower().endswith((".nii", ".nii.gz")):
            raise ValueError(
                "Provide one 3D NIfTI CT (.nii or .nii.gz) in Hounsfield units."
            )
        image = nib.load(str(self.ct_path))
        if len(image.shape) != 3:
            raise ValueError(f"Expected a 3D CT; got shape {image.shape}.")
        if (
            not np.isfinite(image.affine).all()
            or abs(np.linalg.det(image.affine[:3, :3])) < 1e-12
        ):
            raise ValueError("The CT affine must be finite and nonsingular.")
        self.original_shape = tuple(image.shape)
        self.original_affine = image.affine.copy()
        self.transforms = build_video_deterministic_transform(
            DatasetArgs(), fix_segment_spacing=fix_segment_spacing
        )
        self.volume = self.transforms(
            {"video_seg": str(self.ct_path), "video_txt": str(self.ct_path)}
        )
        if any(
            not torch.isfinite(self.volume[key]).all()
            for key in ("video_seg", "video_txt")
        ):
            raise ValueError("The preprocessed CT contains NaN or infinity.")

    def __len__(self):
        return 1

    def __getitem__(self, index):
        if index != 0:
            raise IndexError("DemoDataset contains exactly one CT.")
        return self.volume

    def sample(self, prompt):
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("The prompt must be a nonempty string.")
        return {
            "video_seg": self.volume["video_seg"],
            "video_txt": self.volume["video_txt"],
            "video_path": str(self.ct_path),
            "transform": self.transforms,
            "conv": [
                {
                    "role": "system",
                    "content": "You are an AI medical assistant specialized in radiology.",
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "video", "video": str(self.ct_path)},
                        {"type": "text", "text": prompt},
                    ],
                },
            ],
        }


def collate_fn_infer(examples, processor):

    video_meta_list = [ex["video_seg"] for ex in examples]
    video_inputs_txt = [ex["video_txt"] for ex in examples]
    video_paths = [ex["video_path"] for ex in examples]

    video_inputs = [torch.as_tensor(v, dtype=torch.float32) for v in video_meta_list]

    convs = [ex["conv"] for ex in examples]

    transforms = [ex.get("transform", None) for ex in examples]

    original_shapes = [(v.shape[1], v.shape[2], v.shape[3]) for v in video_inputs]
    patch_size = 16
    video_grid_thw = [
        (d // (patch_size * 2), h // patch_size, w // patch_size)
        for (d, h, w) in original_shapes
    ]

    max_D = max(d for d, _, _ in original_shapes)
    max_H = max(h for _, h, _ in original_shapes)
    max_W = max(w for _, _, w in original_shapes)

    video_inputs_padded = torch.stack(
        [pad_to_shape(v, (max_D, max_H, max_W), pad_value=0) for v in video_inputs]
    )

    messages_for_apply_chat_template, answers = messages_for_apply_template(convs)
    text = processor.apply_chat_template(
        messages_for_apply_chat_template, tokenize=False, add_generation_prompt=True
    )

    shapes_txt = [tuple(v.shape) for v in video_inputs_txt]
    if len(set(shapes_txt)) != 1:
        raise ValueError(f"video_txt shapes are not the same: {shapes_txt}")

    video_txt = torch.stack(video_inputs_txt)

    inputs = processor(
        text=text,
        videos_seg=video_inputs_padded,
        videos_txt=video_txt,
        videos_kwargs={
            "video_grid_override": torch.tensor(video_grid_thw, dtype=torch.long)
        },
        padding=True,
        return_tensors="pt",
    )
    if "second_per_grid_ts" in inputs:
        inputs.pop("second_per_grid_ts")

    batch = dict(inputs)
    batch["video_original_shape"] = torch.tensor(original_shapes, dtype=torch.long)
    batch["video_metas_tensor"] = video_meta_list

    batch["transforms"] = transforms
    batch["video_paths"] = video_paths
    batch["conv"] = convs

    batch["segment_paths"] = [
        ex["segment_path"] if "segment_path" in ex else None for ex in examples
    ]
    batch["answer_gts"] = [
        ex["answer_gt"] if "answer_gt" in ex else None for ex in examples
    ]
    batch["VQA_types"] = [
        ex["VQA_type"] if "VQA_type" in ex else None for ex in examples
    ]
    batch["seg_class"] = [
        ex["seg_class"] if "seg_class" in ex else None for ex in examples
    ]
    batch["questions"] = [
        next(
            item["text"] for item in ex["conv"][1]["content"] if item["type"] == "text"
        )
        for ex in examples
    ]
    return batch
