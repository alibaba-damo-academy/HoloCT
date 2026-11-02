"""Single-CT seg demo."""

from inference.demo_utils import run_demo
from utils.corpus.prompt_templates import Seg_templates

DEFAULT_PROMPT = Seg_templates["pure_seg_questions"][0].format("liver")

DEFAULT_CT = "demo_ct/seg.nii.gz"

if __name__ == "__main__":
    run_demo(
        task='seg', default_ct=DEFAULT_CT, default_prompt=DEFAULT_PROMPT, max_new_tokens=1024,
    )
