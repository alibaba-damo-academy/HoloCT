"""Single-CT rexgrounding rg demo."""

from inference.demo_utils import run_demo
DEFAULT_PROMPT = "Identify all abnormal findings in the lung, pleura, trachea and bronchi."
DEFAULT_GROUNDED_PROMPT = "Identify and segment all abnormal findings in the lung, pleura, trachea and bronchi."

DEFAULT_CT = "demo_ct/rexgrounding_rg.nii.gz"

if __name__ == "__main__":
    run_demo(
        task='rexgrounding_rg', default_ct=DEFAULT_CT, default_prompt=DEFAULT_PROMPT, default_grounded_prompt=DEFAULT_GROUNDED_PROMPT, max_new_tokens=1024, sample=True,
    )
