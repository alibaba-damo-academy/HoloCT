"""Match one predicted finding to reference findings from one CT."""

import argparse
import json
import re
from typing import Any, Dict, Optional, Sequence

from eval._common import clean_text, read_object, load_judge, judge_one, write_result

SPACE_RE = re.compile(r"\s+")


def normalize_space(text: Any) -> str:
    if text is None:
        return ""
    return SPACE_RE.sub(" ", str(text)).strip()


def coerce_binary(value: Any) -> Optional[int]:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, float)) and value in (0, 1):
        return int(value)
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"1", "true", "yes", "match", "matched"}:
            return 1
        if normalized in {"0", "false", "no", "no_match", "unmatched"}:
            return 0
    return None


def coerce_index(value: Any) -> Optional[int]:
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, str):
        value = value.strip()
        if value.lower() in {"null", "none", "na", "n/a", "-"}:
            return None
        match = re.search(r"-?\d+", value)
        if match:
            return int(match.group(0))
    return None


def extract_first_json_object(text: str) -> Optional[Dict[str, Any]]:
    start = text.find("{")
    if start < 0:
        return None

    depth = 0
    in_string = False
    escaped = False
    for pos in range(start, len(text)):
        char = text[pos]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                candidate = text[start : pos + 1]
                try:
                    decoded = json.loads(candidate)
                    return decoded if isinstance(decoded, dict) else None
                except json.JSONDecodeError:
                    return None
    return None


def parse_named_binary_from_text(text: str, names: Sequence[str]) -> Optional[int]:
    alternatives = "|".join(re.escape(name) for name in names)
    match = re.search(
        rf"(?:{alternatives})\s*[:=]\s*(1|0|true|false|yes|no)",
        text,
        flags=re.IGNORECASE,
    )
    return coerce_binary(match.group(1)) if match else None


def parse_match_output(raw_text: str, gt_count: int) -> Dict[str, Any]:
    cleaned_text = raw_text.strip()
    cleaned_text = re.sub(r"^```(?:json)?\s*", "", cleaned_text, flags=re.IGNORECASE)
    cleaned_text = re.sub(r"\s*```$", "", cleaned_text)

    obj = extract_first_json_object(cleaned_text)
    if obj is not None:
        reported_match = coerce_binary(
            obj.get("match", obj.get("matched", obj.get("label", obj.get("decision"))))
        )
        finding_match = coerce_binary(
            obj.get(
                "finding_match",
                obj.get("core_finding_match", obj.get("pathology_match")),
            )
        )
        location_match = coerce_binary(
            obj.get(
                "location_match",
                obj.get("anatomical_location_match", obj.get("anatomy_match")),
            )
        )
        attribute_conflict = coerce_binary(
            obj.get(
                "attribute_conflict",
                obj.get("material_conflict", obj.get("contradiction")),
            )
        )
        index_value = coerce_index(
            obj.get(
                "matched_gt_index",
                obj.get("gt_index", obj.get("index", obj.get("matched_index"))),
            )
        )
        reason = normalize_space(obj.get("reason", obj.get("explanation", "")))
    else:
        reported_match = parse_named_binary_from_text(
            cleaned_text, ["match", "matched", "decision"]
        )
        finding_match = parse_named_binary_from_text(
            cleaned_text, ["finding_match", "core_finding_match", "pathology_match"]
        )
        location_match = parse_named_binary_from_text(
            cleaned_text,
            ["location_match", "anatomical_location_match", "anatomy_match"],
        )
        attribute_conflict = parse_named_binary_from_text(
            cleaned_text, ["attribute_conflict", "material_conflict", "contradiction"]
        )

        index_search = re.search(
            r"(?:matched_gt_index|gt_index|index)\s*[:=]\s*(null|none|-?\d+)",
            cleaned_text,
            flags=re.IGNORECASE,
        )
        index_value = coerce_index(index_search.group(1)) if index_search else None

        reason_search = re.search(
            r"\breason\s*[:=]\s*(.*)$",
            cleaned_text,
            flags=re.IGNORECASE,
        )
        reason = normalize_space(reason_search.group(1)) if reason_search else ""

    required_binary_fields = (
        reported_match,
        finding_match,
        location_match,
        attribute_conflict,
    )
    parse_ok = all(value in (0, 1) for value in required_binary_fields)

    if not parse_ok:
        return {
            "match": None,
            "reported_match": reported_match,
            "finding_match": finding_match,
            "location_match": location_match,
            "attribute_conflict": attribute_conflict,
            "matched_gt_index": None,
            "reason": reason,
            "logic_corrected": False,
            "parse_ok": False,
        }

    rule_based_match = int(
        finding_match == 1 and location_match == 1 and attribute_conflict == 0
    )
    logic_corrected = int(reported_match) != rule_based_match

    if rule_based_match == 1:
        if index_value is None or not (1 <= index_value <= gt_count):
            return {
                "match": None,
                "reported_match": int(reported_match),
                "finding_match": int(finding_match),
                "location_match": int(location_match),
                "attribute_conflict": int(attribute_conflict),
                "matched_gt_index": None,
                "reason": reason,
                "logic_corrected": logic_corrected,
                "parse_ok": False,
            }
    else:
        index_value = None

    return {
        "match": rule_based_match,
        "reported_match": int(reported_match),
        "finding_match": int(finding_match),
        "location_match": int(location_match),
        "attribute_conflict": int(attribute_conflict),
        "matched_gt_index": index_value,
        "reason": reason,
        "logic_corrected": logic_corrected,
        "parse_ok": True,
    }


SYSTEM_PROMPT = """You are an expert thoracic radiologist and a STRICT semantic matcher for abnormal CT findings.

For each request, you receive:
1. ONE predicted abnormal-finding sentence; and
2. ALL mutually exclusive ground-truth abnormal-finding sentences from the same CT sample.

Your task is to decide whether exactly one GT sentence describes the SAME abnormal finding as the predicted sentence.

MANDATORY DECISION RULE
A positive match is allowed only when ALL three conditions hold:

1. finding_match = 1
   The main pathology or imaging morphology is the same or clinically
   synonymous. Sharing an organ, region, or generic word is not enough.

2. location_match = 1
   The anatomical organ and all stated location information are compatible:
   side/laterality, lobe, segment, pleural versus parenchymal compartment,
   central versus peripheral distribution, and relevant spatial relationships.

3. attribute_conflict = 0
   There is no material contradiction in lesion identity, morphology,
   presence/absence, laterality, focal versus diffuse/bilateral distribution,
   or a specifically stated spatial relationship.

The final rule is:
match = finding_match AND location_match AND NOT attribute_conflict

STRICT FINDING RULES
- Location words are NOT finding identities. Words such as "subpleural",
  "peripheral", "parenchymal", "apical", "basal", and "upper lobe" cannot by
  themselves establish a match.
- Generic words such as "lesion", "opacity", "abnormality", or "density" cannot
  by themselves establish a match.
- Do not match two sentences merely because both describe a lung abnormality.
- Do not replace the specific morphology with a broad topical similarity.

Examples that are NOT equivalent merely because the location overlaps:
- reticular densities / reticulation versus consolidation
- ground-glass opacity versus consolidation
- pulmonary nodule versus pulmonary mass
- pleural effusion versus pleural thickening
- atelectasis versus consolidation
- bronchiectasis versus bronchial-wall thickening
- emphysema versus pulmonary cyst
- calcification versus a non-calcified soft-tissue nodule

Examples of acceptable terminology equivalence when location is also compatible:
- ground-glass opacity versus GGO
- pleural fluid versus pleural effusion
- pulmonary nodule versus nodular pulmonary lesion
- bronchial dilatation versus bronchiectasis, when the described morphology is compatible

STRICT LOCATION RULES
- A broader location may match a more specific location only when it truly
  contains that location and no statement conflicts.
  Example: "right lung" can be compatible with "right upper lobe".
- Left versus right is a mismatch.
- A bilateral/diffuse finding must NOT automatically match a localized
  unilateral finding.
- Different lobes or segments are mismatches when both sentences specify them.
- "Near a consolidation" is a meaningful spatial relation and must not be
  treated as equivalent to unspecified bilateral nodules.
- If one sentence omits location detail, accept only when the stated details in
  the other sentence do not create a contradiction and the finding identity is
  otherwise clear.

DETAIL AND CONTAINMENT
- Differences in severity, degree adverbs, approximate size, stability, or
  nonessential descriptive detail may be ignored when the core finding and
  location remain compatible.
- A predicted sentence may contain the GT description and add
  non-contradictory detail.
- Do not ignore an additional independent unsupported pathology merely because
  part of the predicted sentence overlaps a GT sentence.

SELECTION
- Compare the predicted sentence with every GT sentence.
- Because GT sentences are mutually exclusive, select at most one best match.
- If no GT satisfies all mandatory conditions, return match=0 and
  matched_gt_index=null.
- For a no-match case, the three component fields should describe the closest
  candidate, but matched_gt_index must still be null.

OUTPUT
Return exactly one compact JSON object and nothing else, using all fields:

{"match": 1, "matched_gt_index": 2, "finding_match": 1, "location_match": 1, "attribute_conflict": 0, "reason": "Same pulmonary nodule finding with compatible right-upper-lobe location."}

For no match:
{"match": 0, "matched_gt_index": null, "finding_match": 0, "location_match": 1, "attribute_conflict": 1, "reason": "Reticulation is not consolidation despite overlapping subpleural right-upper-lobe location."}

matched_gt_index is 1-based. Keep the reason brief but explicitly mention the decisive finding and/or location issue.
"""


def build_user_prompt(task: Dict[str, Any], retry: bool = False) -> str:
    gt_lines = "\n".join(
        f"{idx}. {sentence}"
        for idx, sentence in enumerate(task["gt_sentences"], start=1)
    )
    question = normalize_space(task.get("question", ""))
    retry_note = (
        "\nYour previous response could not be parsed. Follow the required JSON format exactly."
        if retry
        else ""
    )
    return (
        f"Task question/context: {question or '[not provided]'}\n\n"
        f"Predicted sentence:\n{task['pred_sentence']}\n\n"
        f"Ground-truth sentences:\n{gt_lines}\n"
        f"{retry_note}"
    )


def evaluate_sample(sample, model, tensor_parallel_size=2):
    if not isinstance(sample, dict) or set(sample) != {
        "prediction",
        "references",
        "question",
    }:
        raise ValueError(
            "Expected one finding object with prediction, references and question."
        )
    prediction = normalize_space(clean_text(sample["prediction"]))
    references = sample["references"]
    if not prediction or not isinstance(references, list) or not references:
        raise ValueError(
            "Supply one predicted finding and nonempty reference findings from the same CT."
        )
    references = [normalize_space(clean_text(text)) for text in references]
    if not all(references):
        raise ValueError("Reference findings must not be empty.")
    task = {
        "pred_sentence": prediction,
        "gt_sentences": references,
        "question": clean_text(sample["question"]),
    }
    llm, tokenizer, sampling = load_judge(model, tensor_parallel_size, 128)
    for attempt in range(2):
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(task, retry=attempt > 0)},
        ]
        raw = judge_one(llm, tokenizer, sampling, messages)
        parsed = parse_match_output(raw, len(references))
        if parsed["parse_ok"]:
            return {**parsed, "raw_output": raw}
    raise ValueError("The judge did not return a valid finding match.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input", required=True, help="One finding JSON object; see eval/README.md."
    )
    parser.add_argument("--model", default="weights/Llama-3.1-70B-Instruct")
    parser.add_argument("--tensor-parallel-size", type=int, default=2)
    parser.add_argument("--output")
    args = parser.parse_args()
    sample = read_object(args.input, ["prediction", "references", "question"])
    write_result(
        evaluate_sample(sample, args.model, args.tensor_parallel_size), args.output
    )


if __name__ == "__main__":
    main()
