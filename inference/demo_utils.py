"""Shared single-case inference and mask export for the six demos."""

import argparse
import json
from contextlib import nullcontext
from pathlib import Path

import nibabel as nib
import numpy as np
import torch
from monai.transforms import ScaleIntensityRanged


def force_cpu_inverse(
    mask_channels_prob,
    video_meta_tensor,
    transform,
    target_key="video_seg",
    threshold=0.5,
):
    if mask_channels_prob is None:
        return None, None
    probability_cpu = mask_channels_prob.detach().cpu().to(torch.float32)
    meta_cpu = video_meta_tensor.detach().cpu()
    pred_meta = meta_cpu.clone()
    pred_meta.data = probability_cpu
    data_inv = {target_key: pred_meta}
    for current_transform in reversed(transform.transforms):
        if isinstance(current_transform, ScaleIntensityRanged):
            continue
        if not hasattr(current_transform, "inverse"):
            continue
        transform_keys = getattr(
            current_transform,
            "keys",
            None,
        )
        if transform_keys is not None and target_key not in transform_keys:
            continue
        original_keys = transform_keys
        original_allow_missing = getattr(
            current_transform,
            "allow_missing_keys",
            None,
        )
        try:
            if original_keys is not None:
                current_transform.keys = (target_key,)
            if hasattr(current_transform, "allow_missing_keys"):
                current_transform.allow_missing_keys = True
            cpu_input = {
                key: (value.cpu() if torch.is_tensor(value) else value)
                for key, value in data_inv.items()
            }
            data_inv = current_transform.inverse(cpu_input)
        finally:
            if original_keys is not None:
                current_transform.keys = original_keys
            if original_allow_missing is not None and hasattr(
                current_transform,
                "allow_missing_keys",
            ):
                current_transform.allow_missing_keys = original_allow_missing
    recovered_meta = data_inv[target_key]
    recovered_probability = recovered_meta.detach().cpu().numpy()
    recovered_binary = (recovered_probability > float(threshold)).astype(np.int16)
    affine = None
    if hasattr(recovered_meta, "affine"):
        affine = recovered_meta.affine
        if torch.is_tensor(affine):
            affine = affine.detach().cpu().numpy()
        affine = np.asarray(affine, dtype=np.float64)
    if affine is None and hasattr(recovered_meta, "meta"):
        affine = recovered_meta.meta.get(
            "original_affine",
            recovered_meta.meta.get("affine", None),
        )
        if affine is not None:
            if torch.is_tensor(affine):
                affine = affine.detach().cpu().numpy()
            affine = np.asarray(affine, dtype=np.float64)
    if affine is None:
        affine = np.eye(4, dtype=np.float64)
    return recovered_binary, affine


def load_model_and_processor(checkpoint, device, dtype, attention):
    from models import (
        HoloCTForConditionalGeneration,
        HoloCTProcessor,
        HoloCTVideoProcessor,
    )
    from transformers import AutoImageProcessor, Qwen2TokenizerFast

    tokenizer = Qwen2TokenizerFast.from_pretrained(str(checkpoint))
    image_processor = AutoImageProcessor.from_pretrained(str(checkpoint))
    # Construct the CT processor directly; AutoVideoProcessor cannot
    # resolve a locally defined HoloCTVideoProcessor saved in a checkpoint.
    processor = HoloCTProcessor(
        image_processor=image_processor,
        tokenizer=tokenizer,
        video_processor=HoloCTVideoProcessor(**image_processor.to_dict()),
        chat_template=tokenizer.chat_template,
    )
    token_ids = []
    for token in ("<SEG>", "<s>", "</s>"):
        ids = processor.tokenizer(token, add_special_tokens=False).input_ids
        if len(ids) != 1 or ids[0] == processor.tokenizer.unk_token_id:
            raise ValueError(
                f"The checkpoint must encode {token} as one dedicated token."
            )
        token_ids.append(ids[0])
    if len(set(token_ids)) != 3:
        raise ValueError("Grounding tokens must have distinct IDs.")
    model = HoloCTForConditionalGeneration.from_pretrained(
        str(checkpoint),
        torch_dtype=dtype,
        device_map={"": str(device)},
        seg_token_idx=token_ids[0],
        seg_start_idx=token_ids[1],
        seg_end_idx=token_ids[2],
        use_video_checkpoint=False,
        attn_implementation=attention,
    ).eval()
    model.model.cache_for_seg_infer = True
    return model, processor


def segmentation_features(model, outputs, prompt_length, attention_mask):
    """Select generated SEG states with a one-step causal offset."""
    sequence = outputs.sequences[0]
    positions = (
        torch.nonzero(sequence[prompt_length:] == model.seg_token_idx).flatten()
        + prompt_length
    )
    if not positions.numel():
        return None, positions
    if int(positions[-1]) == len(sequence) - 1:
        # generate() returns the last selected token before consuming it. Consume
        # that token once to obtain its state, without generating another token.
        if outputs.past_key_values is None:
            raise RuntimeError("A terminal SEG token requires the generation KV cache.")
        extension = attention_mask.new_ones((1, len(sequence) - prompt_length))
        tail = model(
            input_ids=sequence[None, -1:],
            attention_mask=torch.cat([attention_mask, extension], dim=1),
            past_key_values=outputs.past_key_values,
            cache_position=torch.tensor([len(sequence) - 1], device=sequence.device),
            use_cache=True,
            output_hidden_states=True,
            return_dict=True,
        )
        outputs.hidden_states = tuple(outputs.hidden_states) + (tail.hidden_states,)
    features = [
        outputs.hidden_states[int(p) - prompt_length + 1][-1][0, 0, :]
        for p in positions
    ]
    return torch.stack(features).unsqueeze(0), positions


def mask_labels(tokenizer, generated_ids, seg_id, start_id, end_id):
    """Match each mask to the nearest complete label before its SEG token."""
    ids = generated_ids.tolist()
    rows = []
    previous = -1
    for position, token in enumerate(ids):
        if token != seg_id:
            continue
        prefix = ids[previous + 1 : position]
        starts = [i for i, value in enumerate(prefix) if value == start_id]
        label = None
        if starts:
            start = starts[-1]
            ends = [
                i for i, value in enumerate(prefix) if value == end_id and i > start
            ]
            if ends:
                label = (
                    tokenizer.decode(
                        prefix[start + 1 : ends[0]], skip_special_tokens=False
                    ).strip()
                    or None
                )
        rows.append(
            {"index": len(rows), "label": label, "generated_token_index": position}
        )
        previous = position
    return rows


def generate_case(
    model, processor, dataset, prompt, generation, seed, threshold, device, dtype
):
    from inference.dataset.demo_dataset import collate_fn_infer

    batch = collate_fn_infer([dataset.sample(prompt)], processor)
    keys = {
        "input_ids",
        "attention_mask",
        "video_original_shape",
        "pixel_values_videos_seg",
        "pixel_values_videos_txt",
        "video_grid_thw",
    }
    model_inputs = {
        k: v.to(device) if torch.is_tensor(v) else v
        for k, v in batch.items()
        if k in keys
    }
    prompt_length = model_inputs["input_ids"].shape[1]
    torch.manual_seed(seed)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(seed)
    model.model.cached_encode_feats = None
    context = (
        torch.autocast("cuda", dtype=dtype)
        if device.type == "cuda" and dtype != torch.float32
        else nullcontext()
    )
    with torch.inference_mode(), context:
        outputs = model.generate(
            **model_inputs,
            **generation,
            num_beams=1,
            use_cache=True,
            output_hidden_states=True,
            return_dict_in_generate=True,
        )
        generated = outputs.sequences[0, prompt_length:]
        raw_text = processor.tokenizer.decode(
            generated, skip_special_tokens=False, clean_up_tokenization_spaces=False
        ).strip()
        text = processor.tokenizer.decode(
            generated, skip_special_tokens=True, clean_up_tokenization_spaces=False
        ).strip()
        features, positions = segmentation_features(
            model, outputs, prompt_length, model_inputs["attention_mask"]
        )
        masks, affine = None, None
        if features is not None:
            if model.model.cached_encode_feats is None:
                raise RuntimeError(
                    "The model did not cache its CT features for mask decoding."
                )
            decoded = model.decode_features(model.model.cached_encode_feats[0])
            logits = model.mask_from_features(decoded, features)
            if not torch.is_tensor(logits):
                raise RuntimeError(
                    "Expected a single-scale mask decoder output."
                )
            if not torch.isfinite(logits).all():
                raise RuntimeError(
                    "The mask decoder produced NaN or infinity; no mask was saved."
                )
            logits = logits.squeeze(0)
            if logits.shape[0] != len(positions):
                raise RuntimeError(
                    "Mask channels do not match the generated SEG tokens."
                )
            probabilities = torch.sigmoid(logits).detach().cpu().to(torch.float32)
            masks, affine = force_cpu_inverse(
                probabilities,
                batch["video_metas_tensor"][0],
                dataset.transforms,
                threshold=threshold,
            )
            if tuple(masks.shape[1:]) != dataset.original_shape:
                raise RuntimeError(
                    f"Restored mask shape {masks.shape[1:]} differs from CT shape {dataset.original_shape}."
                )
    labels = mask_labels(
        processor.tokenizer,
        generated,
        model.seg_token_idx,
        model.seg_start_idx,
        model.seg_end_idx,
    )
    return {
        "prompt": prompt,
        "text": text,
        "raw_text": raw_text,
        "generated_tokens": int(generated.numel()),
        "token_limit_reached": int(generated.numel()) >= generation["max_new_tokens"],
        "seg_token_count": len(labels),
        "masks": labels,
        "mask_data": masks,
        "affine": affine,
    }


def save_case(result, folder, dataset):
    folder.mkdir(parents=True, exist_ok=False)
    data = result.pop("mask_data")
    affine = result.pop("affine")
    for row in result["masks"]:
        name = f"mask_{row['index']:03d}.nii.gz"
        image = nib.Nifti1Image(data[row["index"]].astype(np.uint8), affine)
        image.header.set_xyzt_units("mm")
        nib.save(image, str(folder / name))
        row["file"] = name
        row["foreground_voxels"] = int(np.count_nonzero(data[row["index"]]))
    result["mask_affine"] = affine.tolist() if affine is not None else None
    result["mask_shape"] = list(data.shape[1:]) if data is not None else None
    result["mask_affine_matches_input"] = (
        bool(np.allclose(affine, dataset.original_affine, atol=1e-4))
        if affine is not None
        else None
    )
    (folder / "response.txt").write_text(result["text"] + "\n", encoding="utf-8")
    (folder / "response_raw.txt").write_text(
        result["raw_text"] + "\n", encoding="utf-8"
    )
    (folder / "result.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return result


def run_demo(
    *,
    task,
    default_ct,
    default_prompt,
    default_grounded_prompt=None,
    max_new_tokens=1024,
    sample=False,
):
    """Run the fixed example or a supplied CT/prompt on one GPU."""
    from inference.dataset.demo_dataset import DemoDataset

    paired = default_grounded_prompt is not None
    parser = argparse.ArgumentParser(description=f"HoloCT single-CT demo: {task}")
    parser.add_argument(
        "--ct",
        default=default_ct,
        help="3D NIfTI CT in Hounsfield units; defaults to this task's demo_ct file.",
    )
    parser.add_argument(
        "--model",
        default="weights/HoloCT-4B",
        help="Complete local HoloCT checkpoint directory.",
    )
    parser.add_argument(
        "--prompt",
        default=default_prompt,
        help="Full user prompt (ungrounded prompt for paired demos).",
    )
    if paired:
        parser.add_argument(
            "--grounded-prompt",
            default=default_grounded_prompt,
            help="Full grounded prompt for the same CT.",
        )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("outputs") / task,
        help="Empty output directory.",
    )
    args = parser.parse_args()
    prompts = (
        {"ungrounded": args.prompt, "grounded": args.grounded_prompt}
        if paired
        else {"grounded": args.prompt}
    )
    if any(not p.strip() for p in prompts.values()):
        parser.error("Prompts must not be empty.")
    if not Path(args.ct).is_file():
        parser.error(f"CT not found: {args.ct}. Download this sample or supply --ct.")
    if not Path(args.model).is_dir():
        parser.error(
            "Checkpoint not found. Follow the README download instructions or supply --model."
        )
    if not torch.cuda.is_available():
        parser.error("A CUDA GPU is required for these demos.")
    if not torch.cuda.is_bf16_supported():
        parser.error("These demos require a GPU with bfloat16 support.")
    if args.output.exists() and (
        not args.output.is_dir() or any(args.output.iterdir())
    ):
        parser.error("Output directory is not empty; choose a new --output.")

    device, dtype = torch.device("cuda:0"), torch.bfloat16
    dataset = DemoDataset(args.ct, fix_segment_spacing=(task == "radgenome_rg"))
    model, processor = load_model_and_processor(Path(args.model), device, dtype, "sdpa")
    generation = {"max_new_tokens": max_new_tokens, "do_sample": sample}
    if sample:
        generation.update(temperature=0.15, top_p=0.85, repetition_penalty=1.15)
    results = {}
    for mode, prompt in prompts.items():
        result = generate_case(
            model, processor, dataset, prompt, generation, 42, 0.5, device, dtype
        )
        results[mode] = save_case(result, args.output / mode, dataset)
        print(f"\n[{mode}]\n{result['text']}\nMasks: {result['seg_token_count']}")
        if result["token_limit_reached"]:
            print(
                "The generation token limit was reached; see max_new_tokens in this demo script."
            )

    record = {
        "task": task,
        "ct_filename": dataset.ct_path.name,
        "generation": generation,
        "seed": 42,
        "results": results,
    }
    (args.output / "result.json").write_text(
        json.dumps(record, indent=2) + "\n", encoding="utf-8"
    )
    print(f"\nSaved text and masks to {args.output}")
