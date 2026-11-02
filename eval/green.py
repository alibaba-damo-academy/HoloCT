"""GREEN score and explanation for one report pair."""

import argparse
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple

from eval._common import (
    add_text_arguments,
    read_text_arguments,
    load_judge,
    judge_one,
    write_result,
)

CATEGORIES = [
    "Clinically Significant Errors",
    "Clinically Insignificant Errors",
    "Matched Findings",
]

SUB_CATEGORIES = [
    "(a) False report of a finding in the candidate",
    "(b) Missing a finding present in the reference",
    "(c) Misidentification of a finding's anatomic location/position",
    "(d) Misassessment of the severity of a finding",
    "(e) Mentioning a comparison that isn't in the reference",
    "(f) Omitting a comparison detailing a change from a prior study",
]


def parse_error_counts(text: str, category: str) -> Tuple[int, List[int]]:
    if category not in CATEGORIES:
        return 0, [0] * 6
    pattern = rf"\[{re.escape(category)}\]:\s*(.*?)(?:\n\s*\n|\Z)"
    category_text = re.search(pattern, text, re.DOTALL)
    sub_counts = [0] * 6
    if not category_text:
        return 0, sub_counts
    content = category_text.group(1).strip()
    if content.lower().startswith("no"):
        return 0, sub_counts
    if category == "Matched Findings":
        counts = re.findall(r"^\s*(\d+)\s*\.", content)
        return (int(counts[0]) if counts else 0), sub_counts
    prefixes = [s.split(" ", 1)[0] + " " for s in SUB_CATEGORIES]
    matches = sorted(re.findall(r"\([a-f]\) .*", content))
    if not matches:
        matches = sorted(re.findall(r"\([1-6]\) .*", content))
        prefixes = [f"({i}) " for i in range(1, 7)]
    for position, prefix in enumerate(prefixes):
        for match in matches:
            if match.startswith(prefix):
                count = re.findall(r"(?<=: )\b\d+\b(?=\.)", match)
                if count:
                    sub_counts[position] = int(count[0])
    return sum(sub_counts), sub_counts


def compute_green_score(response: str) -> Tuple[float, Dict[str, Any]]:
    sig_sum, sig_sub = parse_error_counts(response, CATEGORIES[0])
    insig_sum, insig_sub = parse_error_counts(response, CATEGORIES[1])
    matched, _ = parse_error_counts(response, CATEGORIES[2])
    if matched <= 0:
        score = 0.0
    else:
        score = matched / (matched + sig_sum)
    detail = {
        "clinically_significant_errors": sig_sum,
        "clinically_insignificant_errors": insig_sum,
        "matched_findings": matched,
        "significant_error_subcounts": sig_sub,
        "insignificant_error_subcounts": insig_sub,
    }
    return float(score), detail


CHAT_TEMPLATE = "{% for message in messages %}\n{% if message['from'] == 'human' %}\n{{ '<|user|>\n' + message['value'] + eos_token }}\n{% elif message['from'] == 'system' %}\n{{ '<|system|>\n' + message['value'] + eos_token }}\n{% elif message['from'] == 'gpt' %}\n{{ '<|assistant|>\n'  + message['value'] + eos_token }}\n{% endif %}\n{% if loop.last and add_generation_prompt %}\n{{ '<|assistant|>' }}\n{% endif %}\n{% endfor %}"


def load_green_prompt_utils(utils_dir: str):
    import ast

    utils_path = Path(utils_dir) / "utils.py"
    if not utils_path.is_file():
        raise FileNotFoundError(f"utils.py not found: {utils_path}")
    source = utils_path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(utils_path))
    wanted = {"make_prompt", "clean_responses"}
    found = {}
    for node in tree.body:
        if (
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name in wanted
        ):
            found[node.name] = node
    missing = sorted(wanted - set(found))
    if missing:
        raise RuntimeError(
            f"Required GREEN utility function(s) missing from {utils_path}: {missing}"
        )

    future_node = ast.ImportFrom(
        module="__future__",
        names=[ast.alias(name="annotations", asname=None)],
        level=0,
    )
    module = ast.Module(
        body=[future_node, found["make_prompt"], found["clean_responses"]],
        type_ignores=[],
    )
    ast.fix_missing_locations(module)
    namespace = {"__builtins__": __builtins__}
    exec(compile(module, str(utils_path), "exec"), namespace, namespace)
    return namespace["make_prompt"], namespace["clean_responses"]


def evaluate_sample(prediction, reference, model, green_utils):
    make_prompt, clean_responses = load_green_prompt_utils(green_utils)

    llm, tokenizer, sampling = load_judge(model, 1, 2048)
    tokenizer.chat_template = CHAT_TEMPLATE
    raw = judge_one(
        llm,
        tokenizer,
        sampling,
        [{"from": "human", "value": make_prompt(reference, prediction)}],
    )
    response = clean_responses(raw)
    if not all(f"[{category}]:" in response for category in CATEGORIES):
        raise ValueError("The GREEN response is incomplete.")
    score, detail = compute_green_score(response)
    return {"green_score": score, "detail": detail, "explanation": response}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    add_text_arguments(parser)
    parser.add_argument("--model", default="weights/GREEN")
    parser.add_argument(
        "--green-utils",
        default="../GREEN/green_score",
        help="GREEN directory containing utils.py.",
    )
    parser.add_argument("--output")
    args = parser.parse_args()
    write_result(
        evaluate_sample(*read_text_arguments(args), args.model, args.green_utils),
        args.output,
    )


if __name__ == "__main__":
    main()
