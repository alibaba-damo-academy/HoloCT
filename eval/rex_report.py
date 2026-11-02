"""Finding-level grounded-report metrics for one CT with explicit semantic matches."""

import argparse
from pathlib import Path

from eval._common import load_mask_pair, read_object, write_result


def evaluate_sample(sample, base_dir=Path(".")):
    if not isinstance(sample, dict) or set(sample) != {
        "reference_masks",
        "predictions",
    }:
        raise ValueError("Expected one CT object with reference_masks and predictions.")
    references, predictions = sample["reference_masks"], sample["predictions"]
    if not isinstance(references, list) or not isinstance(predictions, list):
        raise ValueError(
            "reference_masks and predictions must describe findings within one CT."
        )
    if not all(isinstance(path, str) and path for path in references):
        raise ValueError("Each reference needs one mask path.")
    candidates = [[] for _ in references]
    for index, prediction in enumerate(predictions):
        if not isinstance(prediction, dict) or set(prediction) != {
            "mask",
            "matched_gt_index",
        }:
            raise ValueError("Each prediction needs mask and matched_gt_index.")
        mask, match = prediction["mask"], prediction["matched_gt_index"]
        if mask is not None and (not isinstance(mask, str) or not mask):
            raise ValueError("mask must be a path or null when no mask was generated.")
        if match is not None:
            if type(match) is not int or not 1 <= match <= len(references):
                raise ValueError(
                    "matched_gt_index must be a 1-based reference index or null."
                )
            candidates[match - 1].append((index, mask))
    rows, matched_dices = [], []
    for index, (reference, matches) in enumerate(zip(references, candidates), start=1):
        reference = Path(base_dir) / reference
        # Validate every reference, including an unmatched finding.
        load_mask_pair(None, reference)
        best = None
        for _, mask in matches:
            prediction = None if mask is None else Path(base_dir) / mask
            pred, gt, _ = load_mask_pair(prediction, reference)
            denominator = int(pred.sum()) + int(gt.sum())
            dice = (
                1.0 if denominator == 0 else 2.0 * int((pred & gt).sum()) / denominator
            )
            best = dice if best is None else max(best, dice)
        if best is not None:
            matched_dices.append(best)
        rows.append(
            {"gt_index": index, "semantic_match": bool(matches), "best_dice": best}
        )
    tp = len(matched_dices)
    fp, fn = len(predictions) - tp, len(references) - tp
    denominator = 2 * tp + fp + fn
    f1 = 2.0 * tp / denominator if denominator else 1.0
    conditional_dice = sum(matched_dices) / tp if tp else None
    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "finding_f1": f1,
        "conditional_dice": conditional_dice,
        "fl_grq": None if conditional_dice is None else f1 * conditional_dice,
        "conditional_hit_5pct": sum(d > 0.05 for d in matched_dices) / tp
        if tp
        else None,
        "conditional_hit_10pct": sum(d > 0.10 for d in matched_dices) / tp
        if tp
        else None,
        "findings": rows,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input", required=True, help="One CT JSON object; see eval/README.md."
    )
    parser.add_argument("--output")
    args = parser.parse_args()
    sample = read_object(args.input, ["reference_masks", "predictions"])
    write_result(evaluate_sample(sample, Path(args.input).parent), args.output)


if __name__ == "__main__":
    main()
