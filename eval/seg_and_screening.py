"""Dice, HD95 and an optional grounded screening decision for one CT target."""

import argparse
import math
from typing import Dict, Optional, Tuple

import numpy as np
from surface_distance import metrics as surface_distance

from eval._common import add_mask_arguments, load_mask_pair, write_result


def presence_name(has_gt: bool, has_pred: bool) -> str:
    if has_gt and has_pred:
        return "TP"
    if not has_gt and not has_pred:
        return "TN"
    if not has_gt and has_pred:
        return "FP"
    return "FN"


def fast_binary_dice(gt: np.ndarray, pred: np.ndarray) -> Optional[float]:
    gt = np.asarray(gt, dtype=bool)
    pred = np.asarray(pred, dtype=bool)

    gt_count = int(np.count_nonzero(gt))
    pred_count = int(np.count_nonzero(pred))

    if gt_count == 0 and pred_count == 0:
        return None

    intersection = int(np.count_nonzero(np.logical_and(gt, pred)))
    return float((2.0 * intersection) / max(gt_count + pred_count, 1))


def compute_metrics_deepmind(
    gt: np.ndarray,
    pred: np.ndarray,
    spacing_mm: Tuple[float, float, float],
) -> Dict[str, Optional[float]]:
    gt = np.asarray(gt, dtype=bool)
    pred = np.asarray(pred, dtype=bool)

    has_gt = bool(np.any(gt))
    has_pred = bool(np.any(pred))

    if not has_gt and not has_pred:
        return {"dice": None, "hd95": None}

    if has_gt != has_pred:
        return {"dice": 0.0, "hd95": None}

    dice = fast_binary_dice(gt, pred)

    distances = surface_distance.compute_surface_distances(
        mask_gt=gt,
        mask_pred=pred,
        spacing_mm=spacing_mm,
    )
    hd95 = float(
        surface_distance.compute_robust_hausdorff(
            distances,
            95,
        )
    )

    return {
        "dice": None if dice is None else float(dice),
        "hd95": hd95 if math.isfinite(hd95) else None,
    }


def evaluate_sample(
    prediction, reference, reference_label=None, predicted_positive=None
):
    pred, gt, spacing = load_mask_pair(prediction, reference, reference_label)
    has_gt, has_pred = bool(gt.any()), bool(pred.any())
    result = compute_metrics_deepmind(gt, pred, spacing)
    result.update(
        mask_presence=presence_name(has_gt, has_pred),
        gt_voxels=int(gt.sum()),
        pred_voxels=int(pred.sum()),
        spacing_mm=spacing,
    )
    if predicted_positive is not None:
        if type(predicted_positive) is not bool:
            raise TypeError("predicted_positive must be a boolean.")
        positive = predicted_positive and has_pred
        result["grounded_screening"] = {
            "predicted_positive": positive,
            "reference_positive": has_gt,
            "decision": presence_name(has_gt, positive),
        }
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    add_mask_arguments(parser)
    parser.add_argument(
        "--reference-label",
        type=int,
        help="Foreground label in a multi-label reference.",
    )
    parser.add_argument(
        "--predicted-positive",
        type=int,
        choices=[0, 1],
        help="Explicit text judgement for this target; combined with mask presence.",
    )
    parser.add_argument("--output")
    args = parser.parse_args()
    positive = (
        None if args.predicted_positive is None else bool(args.predicted_positive)
    )
    write_result(
        evaluate_sample(
            args.prediction, args.reference, args.reference_label, positive
        ),
        args.output,
    )


if __name__ == "__main__":
    main()
