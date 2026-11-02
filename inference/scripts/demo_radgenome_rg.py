"""Single-CT radgenome rg demo."""

from inference.demo_utils import run_demo
from utils.corpus.prompt_templates import Radgenome_templates, RG_templates

REGIONS = 'lung, trachea and bronchie, mediastinum, heart, esophagus, pleura, bone, abdomen'
DEFAULT_PROMPT = RG_templates["Radgenome_all"][0].format(tag="", region_list=REGIONS)
DEFAULT_GROUNDED_PROMPT = Radgenome_templates["Region_report_questions"][0].format(region_order=REGIONS)

DEFAULT_CT = "demo_ct/radgenome_rg.nii.gz"

if __name__ == "__main__":
    run_demo(
        task='radgenome_rg', default_ct=DEFAULT_CT, default_prompt=DEFAULT_PROMPT, default_grounded_prompt=DEFAULT_GROUNDED_PROMPT, sample=True, max_new_tokens=1024,
    )
