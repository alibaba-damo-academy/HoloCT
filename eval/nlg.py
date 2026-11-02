"""BLEU-4, ROUGE-L and METEOR for one answer or report pair."""

import argparse

from eval._common import (
    add_text_arguments,
    clean_text,
    read_text_arguments,
    write_result,
)


def evaluate_sample(prediction, reference):
    prediction, reference = clean_text(prediction), clean_text(reference)
    if not reference:
        raise ValueError("The reference must not be empty.")
    if not prediction:
        return {"bleu4": 0.0, "rougeL": 0.0, "meteor": 0.0}
    import evaluate

    bleu = evaluate.load("bleu").compute(
        predictions=[prediction],
        references=[[reference]],
        max_order=4,
        smooth=True,
    )["bleu"]
    rouge = evaluate.load("rouge").compute(
        predictions=[prediction],
        references=[reference],
        rouge_types=["rougeL"],
        use_stemmer=True,
        use_aggregator=False,
    )["rougeL"][0]
    meteor = evaluate.load("meteor").compute(
        predictions=[prediction],
        references=[reference],
    )["meteor"]
    return {"bleu4": float(bleu), "rougeL": float(rouge), "meteor": float(meteor)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    add_text_arguments(parser)
    parser.add_argument("--output")
    args = parser.parse_args()
    write_result(evaluate_sample(*read_text_arguments(args)), args.output)


if __name__ == "__main__":
    main()
