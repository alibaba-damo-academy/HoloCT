"""Single-CT rex seg demo."""

from inference.demo_utils import run_demo
from utils.corpus.prompt_templates import Seg_templates

DEFAULT_PROMPT = Seg_templates["ref_questions"][0].format('bilateral pulmonary parenchyma with peripheral subpleural ground-glass opacities')

DEFAULT_CT = "demo_ct/rex_seg.nii.gz"

if __name__ == "__main__":
    run_demo(
        task='rex_seg', default_ct=DEFAULT_CT, default_prompt=DEFAULT_PROMPT, max_new_tokens=1024,
    )
