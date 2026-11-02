"""Dice and HIT indicators for one referring-segmentation finding."""

import argparse

from eval._common import add_mask_arguments, load_mask_pair, write_result


def evaluate_sample(prediction, reference):
    pred, gt, _ = load_mask_pair(prediction, reference)
    gt_count, pred_count = int(gt.sum()), int(pred.sum())
    if gt_count == 0:
        raise ValueError("The reference finding mask must be nonempty.")
    intersection = int((gt & pred).sum())
    dice = 2.0 * intersection / (gt_count + pred_count)
    return {"dice": dice, "hit_5pct": int(dice > 0.05), "hit_10pct": int(dice > 0.10)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    add_mask_arguments(parser)
    parser.add_argument("--output")
    args = parser.parse_args()
    write_result(evaluate_sample(args.prediction, args.reference), args.output)


if __name__ == "__main__":
    main()
