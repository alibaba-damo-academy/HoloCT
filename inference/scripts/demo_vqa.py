"""Single-CT vqa demo."""

from inference.demo_utils import run_demo
from utils.corpus.prompt_templates import VQA_templates, Grounded_VQA_templates

DEFAULT_PROMPT = VQA_templates["reasoning_mcq"][0]["question"].format(
    q='What would be the most likely radiological finding in the liver based on the imaging?',
    opts='A: Multiple low-density lesions\nB: Multiple cystic formations\nC: A single large hepatic mass\nD: Diffuse hepatic steatosis',
)
DEFAULT_GROUNDED_PROMPT = DEFAULT_PROMPT.rstrip() + "\n" + Grounded_VQA_templates["questions"][0]

DEFAULT_CT = "demo_ct/vqa.nii.gz"

if __name__ == "__main__":
    run_demo(
        task='vqa', default_ct=DEFAULT_CT, default_prompt=DEFAULT_PROMPT, default_grounded_prompt=DEFAULT_GROUNDED_PROMPT, max_new_tokens=1024,
    )
