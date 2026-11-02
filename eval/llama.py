"""Clinical accuracy judgement for one answer or report pair."""

import argparse
import re
from typing import Dict, List, Optional

from eval._common import (
    add_text_arguments,
    read_text_arguments,
    load_judge,
    judge_one,
    write_result,
)


def parse_score(text: str) -> Optional[float]:
    text = text.strip()
    match = re.fullmatch(r"(10|[0-9])(?:/10)?\.?", text)
    if match:
        return float(match.group(1))
    return None


def make_messages(
    question: str, real_answer: str, output: str, type_print: str
) -> List[Dict[str, str]]:
    question = (
        question.replace("<image>\n", "")
        .replace("<report_generation>", "")
        .replace("<short_answer>", "")
        .replace("<long_answer>", "")
        .replace("<multiple_choice>", "")
    )
    output = output.replace("<s>", "").replace("</s>", "")
    system_prompt = "Role: You are an expert medical evaluator specializing in the assessment of clinical accuracy for AI-generated reports and answers derived from 3D chest CT volumes. Your task is to compare the AI-generated answers with the provided ground truth answers and assign a clinical accuracy score based on specific evaluation criteria. Your assessment should focus on precision, relevance, and clinical soundness.\n\nScoring:\n• 10/10: The generated response is fully aligned with the ground truth—completely accurate, relevant, comprehensive, clear, and clinically sound.\n• 7-9/10: The generated response is mostly accurate, with minor discrepancies or omissions that do not significantly affect clinical interpretation.\n• 4-6/10: The generated response contains noticeable errors or omissions that could impact clinical understanding, though some correct information is present.\n• 1-3/10: The generated response has significant inaccuracies, irrelevant content, or lacks essential information, potentially leading to clinical misunderstanding.\n• 0/10: The generated response is completely incorrect or irrelevant, offering no clinical value.\n\nQuestion Types:\nFor each evaluation, you will be provided with the question type, question, ground truth answer, and generated answer.\n• Report Generation: Requires a detailed narrative report summarizing findings from the 3D chest CT volume. Consider the formatting of the output for this question in addition to clinical accuracy. Non-existent pathologies are not necessarily required to be mentioned in the generated report. Do not deduct points if this is the case. Deduct points if the model hallucinates pathologies that are not in the ground truth.\n• Long Answer Questions: Require comprehensive, detailed responses that thoroughly address the question, including necessary explanations or justifications.\n• Short Answer Questions: Require brief, direct answers addressing the question with essential information, such as identifying pathology or confirming a diagnosis.\n• Multiple Choice Questions: Require the selection of the most clinically accurate option from predefined choices, matching the ground truth answer. There should be only one correct answer for this question type. If more than one answer is provided, assign a very low score. If the answer is incorrect, assign a very low score as well.\n\nInstructions:\nPlease review the question type, question, ground truth answer, and generated answer. Assign a score out of 10 based on the evaluation criteria above. Provide only the score without additional commentary or explanation."
    user_prompt = f"Question type: {type_print}\nQuestion: {question}\nGround truth answer: {real_answer}\nGenerated answer: {output}"
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def evaluate_sample(
    prediction, reference, question, question_type, model, tensor_parallel_size=2
):
    llm, tokenizer, sampling = load_judge(model, tensor_parallel_size, 16)
    messages = make_messages(question, reference, prediction, question_type)
    raw = judge_one(llm, tokenizer, sampling, messages)
    score = parse_score(raw)
    if score is None:
        raise ValueError("The judge did not return a score from 0 to 10.")
    return {"llama_score": score, "raw_output": raw}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    add_text_arguments(parser)
    parser.add_argument("--question", required=True)
    parser.add_argument(
        "--question-type",
        required=True,
        choices=["Report generation", "Long answer", "Short answer", "Multiple choice"],
    )
    parser.add_argument("--model", default="weights/Llama-3.1-70B-Instruct")
    parser.add_argument("--tensor-parallel-size", type=int, default=2)
    parser.add_argument("--output")
    args = parser.parse_args()
    pred, ref = read_text_arguments(args)
    write_result(
        evaluate_sample(
            pred,
            ref,
            args.question,
            args.question_type,
            args.model,
            args.tensor_parallel_size,
        ),
        args.output,
    )


if __name__ == "__main__":
    main()
