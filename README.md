# HoloCT

HoloCT supports CT lesion screening, visual question answering, grounded report generation and segmentation. This repository provides the model implementation, six inference demos and single-sample metric examples.

| Model | Weights |
|---|---|
| HoloCT-4B | [Hugging Face](https://huggingface.co/yolo2025666/HoloCT-4B) |
| HoloCT-8B | [Hugging Face](https://huggingface.co/yolo2025666/HoloCT-8B) |

## Install

Use Ubuntu 22.04, Python 3.10.16 and an NVIDIA GPU supporting bfloat16. Run commands from the repository root.

```bash
conda env create -f environment.yml
conda activate holoct
python -m pip install torch==2.6.0 torchvision==0.21.0 --index-url https://download.pytorch.org/whl/cu124
python -m pip install -r requirements.txt
```

Each demo loads the model on one visible GPU and uses PyTorch SDPA.

## Download weights

Download a complete checkpoint, including its tokenizer and processor files:

```bash
python -c "from huggingface_hub import snapshot_download; snapshot_download('yolo2025666/HoloCT-4B', local_dir='weights/HoloCT-4B')"
python -c "from huggingface_hub import snapshot_download; snapshot_download('yolo2025666/HoloCT-8B', local_dir='weights/HoloCT-8B')"
```

The demos use `weights/HoloCT-4B` by default. Select the 8B model with `--model weights/HoloCT-8B`.

## Demo CTs

Place the six 3D NIfTI volumes in `demo_ct/`. Each demo loads its corresponding file in Hounsfield units and uses the prompt defined in its script.

| Demo | CT file |
|---|---|
| Lesion screening | `demo_ct/lesion_screening.nii.gz` |
| VQA | `demo_ct/vqa.nii.gz` |
| RadGenome reporting | `demo_ct/radgenome_rg.nii.gz` |
| ReXGrounding reporting | `demo_ct/rexgrounding_rg.nii.gz` |
| Segmentation | `demo_ct/seg.nii.gz` |
| ReX referring segmentation | `demo_ct/rex_seg.nii.gz` |

## Run the demos

```bash
CUDA_VISIBLE_DEVICES=0 python -m inference.scripts.demo_lesion_screening
CUDA_VISIBLE_DEVICES=0 python -m inference.scripts.demo_vqa
CUDA_VISIBLE_DEVICES=0 python -m inference.scripts.demo_radgenome_rg
CUDA_VISIBLE_DEVICES=0 python -m inference.scripts.demo_rexgrounding_rg
CUDA_VISIBLE_DEVICES=0 python -m inference.scripts.demo_seg
CUDA_VISIBLE_DEVICES=0 python -m inference.scripts.demo_rex_seg
```

The first four demos run ungrounded and grounded prompts on the same CT. The final two run segmentation prompts.

Specify another CT, prompt or model:

```bash
python -m inference.scripts.demo_seg --ct demo_ct/my_ct.nii.gz --prompt "Segment the liver in this CT scan." --model weights/HoloCT-8B --output outputs/my_seg

python -m inference.scripts.demo_vqa --ct demo_ct/my_ct.nii.gz --prompt "Is there a liver lesion?" --grounded-prompt "Is there a liver lesion? Ground your answer with the mask." --output outputs/my_vqa
```

For paired demos, set both `--prompt` and `--grounded-prompt` when changing the question. Changing `--ct` alone keeps the example prompts. Use a separate output directory for each run.

## Outputs

Results are saved under `outputs/<task>/`. Each `grounded/` or `ungrounded/` directory contains:

- `response.txt`: generated text.
- `response_raw.txt`: generated text with grounding tokens.
- `result.json`: prompt, response and mask-to-label mapping.
- `mask_000.nii.gz`, etc.: one binary mask for each generated `<SEG>` token.

Paired demos also save both responses in the root `result.json`. View masks together with the CT in a NIfTI viewer. Negative screening responses can contain text alone.

## Inference settings

The detailed branch uses foreground cropping, adaptive spacing with a 1.5 mm base, and padding to multiples of 32. The global branch resizes to 128 x 256 x 256. Both branches clip HU to [-1000, 1000] and scale to [0, 1]. Exported masks are thresholded at 0.5 after inverse transformation.

| Demo | Maximum new tokens | Decoding |
|---|---:|---|
| Lesion screening | 1024 | Greedy |
| VQA | 1024 | Greedy |
| RadGenome reporting | 1024 | Sampling |
| ReXGrounding reporting | 1024 | Sampling |
| Segmentation | 1024 | Greedy |
| ReX referring segmentation | 1024 | Greedy |

Reporting uses temperature 0.15, top-p 0.85 and repetition penalty 1.15. Paired runs use seed 42 for each prompt.

## Single-sample evaluation

`eval/` provides examples for Dice, HD95, screening decisions, BLEU-4, ROUGE-L, METEOR, Llama clinical scoring, GREEN, RaTEScore and finding-level grounded-report metrics. Each invocation evaluates one sample. See [evaluation examples](eval/README.md) for inputs and commands.

## Project structure

```text
demo_ct/                Six task-named CT inputs
models/                 HoloCT model, processors and encoder/decoder modules
utils/                  Preprocessing, label dictionaries and prompt templates
inference/dataset/      CT dataset and collator
inference/scripts/      Six inference demos
inference/demo_utils.py Model loading, generation and mask export
eval/                   Single-sample metric examples
```

## License

HoloCT-specific code is licensed under MIT. Third-party attributions are in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) and `LICENSES/`.
