"""Single-CT lesion screening demo."""

from inference.demo_utils import run_demo
DEFAULT_PROMPT = "Screen the CT and identify any potential abnormalities: kidney lesion, liver lesion, pancreas lesion, or colon lesion."
DEFAULT_GROUNDED_PROMPT = "Screen the CT and segment any potential abnormalities: kidney lesion, liver lesion, pancreas lesion, or colon lesion."

DEFAULT_CT = "demo_ct/lesion_screening.nii.gz"

if __name__ == "__main__":
    run_demo(
        task='lesion_screening', default_ct=DEFAULT_CT, default_prompt=DEFAULT_PROMPT, default_grounded_prompt=DEFAULT_GROUNDED_PROMPT, max_new_tokens=1024,
    )
