"""RaTEScore for one report pair."""

import argparse
import math

from eval._common import (
    add_text_arguments,
    clean_text,
    read_text_arguments,
    write_result,
)


def evaluate_sample(prediction, reference, ner_model, embedding_model, use_gpu=True):
    prediction, reference = clean_text(prediction), clean_text(reference)
    if not reference:
        raise ValueError("The reference must not be empty.")
    if not prediction:
        return {"ratescore": 0.0}
    from RaTEScore import RaTEScore

    scorer = RaTEScore(
        bert_model=ner_model, eval_model=embedding_model, batch_size=1, use_gpu=use_gpu
    )
    score = float(scorer.compute_score([prediction], [reference])[0])
    if not math.isfinite(score):
        raise ValueError("RaTEScore returned a non-finite score.")
    return {"ratescore": score}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    add_text_arguments(parser)
    parser.add_argument("--ner-model", required=True)
    parser.add_argument("--embedding-model", required=True)
    parser.add_argument("--cpu", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args()
    write_result(
        evaluate_sample(
            *read_text_arguments(args),
            args.ner_model,
            args.embedding_model,
            not args.cpu,
        ),
        args.output,
    )


if __name__ == "__main__":
    main()
