"""Input and output helpers for one-sample metric examples."""

import json
import re
from pathlib import Path


def clean_text(text):
    if not isinstance(text, str):
        raise TypeError("Expected one text string.")
    return re.sub(r"<\s*/?\s*s\s*>|<\s*SEG\s*>", "", text, flags=re.IGNORECASE).strip()


def add_text_arguments(parser):
    prediction = parser.add_mutually_exclusive_group(required=True)
    prediction.add_argument("--prediction", help="One predicted answer or report.")
    prediction.add_argument("--prediction-file", help="UTF-8 text for one prediction.")
    reference = parser.add_mutually_exclusive_group(required=True)
    reference.add_argument("--reference", help="One reference answer or report.")
    reference.add_argument("--reference-file", help="UTF-8 text for one reference.")


def read_text_arguments(args):
    prediction = (
        Path(args.prediction_file).read_text(encoding="utf-8-sig")
        if args.prediction_file
        else args.prediction
    )
    reference = (
        Path(args.reference_file).read_text(encoding="utf-8-sig")
        if args.reference_file
        else args.reference
    )
    prediction, reference = clean_text(prediction), clean_text(reference)
    if not reference:
        raise ValueError("The reference text must not be empty.")
    return prediction, reference


def write_result(result, output=None):
    text = json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False)
    if output:
        path = Path(output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text + "\n", encoding="utf-8")
    print(text)


def read_object(path, keys):
    value = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict) or set(value) != set(keys):
        raise ValueError("Expected one sample object with keys: " + ", ".join(keys))
    return value


def add_mask_arguments(parser):
    prediction = parser.add_mutually_exclusive_group(required=True)
    prediction.add_argument(
        "--prediction", help="One 3D probability or binary NIfTI mask."
    )
    prediction.add_argument(
        "--empty-prediction", action="store_true", help="No mask was generated."
    )
    parser.add_argument(
        "--reference", required=True, help="One 3D reference NIfTI mask."
    )


def load_mask(path):
    import nibabel as nib
    import numpy as np

    image = nib.load(str(path))
    values = image.get_fdata(dtype=np.float32)
    if values.ndim != 3 or not np.isfinite(values).all():
        raise ValueError("Masks must be finite 3D volumes.")
    if (
        not np.isfinite(image.affine).all()
        or abs(np.linalg.det(image.affine[:3, :3])) < 1e-12
    ):
        raise ValueError("Invalid NIfTI affine.")
    return values, image.affine


def load_mask_pair(prediction, reference, reference_label=None):
    import numpy as np

    gt, affine = load_mask(reference)
    if (gt < 0).any():
        raise ValueError("Reference labels must be nonnegative.")
    if reference_label is not None and reference_label <= 0:
        raise ValueError("The foreground reference label must be positive.")
    gt = gt > 0 if reference_label is None else gt == reference_label
    if prediction is None:
        pred = np.zeros_like(gt)
    else:
        pred, pred_affine = load_mask(prediction)
        if pred.shape != gt.shape or not np.allclose(
            affine, pred_affine, rtol=0, atol=1e-4
        ):
            raise ValueError(
                "Prediction and reference must have the same shape and affine."
            )
        if (pred < 0).any() or (pred > 1).any():
            raise ValueError("Prediction values must lie in [0, 1].")
        pred = pred > 0.5
    spacing = tuple(float(np.linalg.norm(affine[:3, i])) for i in range(3))
    return pred, gt, spacing


def load_judge(model, tensor_parallel_size, max_tokens):
    import os

    os.environ.setdefault("VLLM_WORKER_MULTIPROC_METHOD", "spawn")
    os.environ.setdefault("VLLM_USE_V1", "0")
    from vllm import LLM, SamplingParams

    llm = LLM(
        model=model,
        tensor_parallel_size=tensor_parallel_size,
        trust_remote_code=True,
        gpu_memory_utilization=0.95,
        max_model_len=4096,
        dtype="bfloat16",
        enforce_eager=True,
    )
    return (
        llm,
        llm.get_tokenizer(),
        SamplingParams(temperature=0.0, max_tokens=max_tokens),
    )


def judge_one(llm, tokenizer, sampling, messages):
    prompt = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    output = llm.generate([prompt], sampling, use_tqdm=False)
    return output[0].outputs[0].text.strip()
