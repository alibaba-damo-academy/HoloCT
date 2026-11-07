# Single-sample metrics

Run each example from the repository root. Supply a prediction and its reference from the same CT, question or finding. Results are printed as JSON; `--output metrics/example.json` also saves them.

## Environments

Use Python 3.10.16 on Linux. Each model-based metric has its own Conda environment.

| Metric | Environment file | PyTorch | vLLM | Transformers | NumPy |
|---|---|---|---|---|---|
| Llama clinical score and finding matching | [llama.yml](envs/llama.yml) | 2.9.1 | 0.15.1 | 4.57.0 | 2.2.6 |
| GREEN | [green.yml](envs/green.yml) | 2.13.0 | 0.30.0 | 5.17.0 | 2.2.6 |
| RaTEScore | [ratescore.yml](envs/ratescore.yml) | 2.6.0 | — | 4.57.0 | 1.26.4 |

The corresponding PyTorch CUDA runtimes are 12.8, 13.0 and 12.4. Llama and GREEN require an NVIDIA GPU.

### Mask and text overlap metrics

```bash
conda create -n holoct-eval-basic python=3.10.16 pip -y
conda activate holoct-eval-basic
python -m pip install -r requirements-eval.txt
python -m nltk.downloader punkt_tab wordnet omw-1.4
python -m pip check
```

Text metrics download their metric modules on first use through [Hugging Face Evaluate](https://github.com/huggingface/evaluate).

## Mask and text metrics

### Segmentation and screening

```bash
python -m eval.seg_and_screening --prediction outputs/seg/grounded/mask_000.nii.gz --reference data/reference_mask.nii.gz

python -m eval.seg_and_screening --prediction outputs/lesion_screening/grounded/mask_000.nii.gz --reference data/lesion_mask.nii.gz --predicted-positive 1

python -m eval.rex_seg --prediction outputs/rex_seg/grounded/mask_000.nii.gz --reference data/finding_mask.nii.gz
```

Masks must be 3D volumes with matching shapes and affines. Predictions use threshold `> 0.5`; reference foreground uses `> 0`. For a multi-label segmentation reference, select one target with `--reference-label 1`. Use `--empty-prediction` in place of `--prediction` when generation produced no mask.

- Dice is `2 * intersection / (prediction_voxels + reference_voxels)`.
- HD95 uses the surface-area-weighted robust Hausdorff distance from [surface-distance](https://github.com/google-deepmind/surface-distance), with NIfTI voxel spacing in millimetres.
- General segmentation returns `null` for both-empty Dice and for HD95 when either mask is empty; one-empty Dice is zero.
- Grounded screening combines the explicitly supplied text judgement (`--predicted-positive 0` or `1`) with nonempty mask presence and returns TP, TN, FP or FN for this target. The reference mask defines reference positivity.
- Referring segmentation requires a nonempty reference finding. It returns Dice and HIT indicators defined by `Dice > 0.05` and `Dice > 0.10`.

### Text overlap

```bash
python -m eval.nlg --prediction-file outputs/vqa/grounded/response.txt --reference "There is a lesion in the liver."
```

Use `--prediction` for inline text or `--prediction-file` for a UTF-8 text file; references use the corresponding `--reference` or `--reference-file` options. Grounding tags are removed before text scoring. BLEU-4 uses smoothing, ROUGE-L uses stemming, and METEOR uses the Evaluate defaults. An empty prediction receives zero for these three metrics.

## Model-based text metrics

### Llama clinical score

```bash
conda env create -f eval/envs/llama.yml
conda activate holoct-eval-llama
python -m pip check
```

Download the [Llama-3.1-70B-Instruct](https://huggingface.co/meta-llama/Llama-3.1-70B-Instruct) judge to `weights/Llama-3.1-70B-Instruct` and run:

```bash
CUDA_VISIBLE_DEVICES=0,1 python -m eval.llama --prediction-file outputs/vqa/grounded/response.txt --reference "There is a lesion in the liver." --question "Is there a liver lesion?" --question-type "Short answer"
```

Question types are `Report generation`, `Long answer`, `Short answer` and `Multiple choice`. The output contains the 0-10 score and the judge response. `--tensor-parallel-size` sets the number of GPUs for this one judgement; its default is 2.

### GREEN

```bash
conda env create -f eval/envs/green.yml
conda activate holoct-eval-green
python -m pip check
```

Obtain the [GREEN](https://github.com/Stanford-AIMI/GREEN) prompt utilities and provide its checkpoint at `weights/GREEN`. The script loads `make_prompt` and `clean_responses` from `green_score/utils.py`:

```bash
git clone https://github.com/Stanford-AIMI/GREEN.git ../GREEN
CUDA_VISIBLE_DEVICES=0 python -m eval.green --prediction-file outputs/radgenome_rg/grounded/response.txt --reference-file data/reference_report.txt
```

GREEN returns the explanation, matched findings and error counts. Its score is `matched / (matched + clinically_significant_errors)`, with zero when there are no matched findings. The GREEN prompt uses up to 300 words from each report. Use `--model` for another checkpoint location and `--green-utils` for another directory containing the GREEN `utils.py` file.

### RaTEScore

Create the [RaTEScore](https://github.com/MAGIC-AI4Med/RaTEScore) environment and score a report pair:

```bash
conda env create -f eval/envs/ratescore.yml
conda activate holoct-eval-ratescore
python -m pip check
python -c "from RaTEScore import RaTEScore; print('RaTEScore import OK')"
python -m eval.ratescore --prediction-file outputs/rexgrounding_rg/grounded/response.txt --reference-file data/reference_report.txt --ner-model Angelakeke/RaTE-NER-Deberta --embedding-model FremyCompany/BioLORD-2023-C
```

RaTEScore receives exactly one candidate/reference pair and uses its default long-report affinity matrix. Model arguments also accept local checkpoint directories; `--cpu` selects CPU execution. An empty prediction receives zero.

## Finding matching and grounded-report quality

### Match one finding

Create a local `finding.json` containing one predicted finding and the reference findings from the same CT:

```json
{
  "prediction": "A nodule is present in the right upper lobe.",
  "references": ["A right-upper-lobe pulmonary nodule is present."],
  "question": "Describe the abnormal findings."
}
```

```bash
conda activate holoct-eval-llama
CUDA_VISIBLE_DEVICES=0,1 python -m eval.llama_rex --input finding.json --output metrics/finding_match.json
```

The judge checks finding identity, anatomical location and conflicting attributes. `matched_gt_index` is a 1-based reference index, or `null` for an unmatched prediction. A malformed response is retried once.

### Score one grounded report

Create a local `report_case.json` for the findings in one CT. Enter the semantic match index for each predicted finding using the matching result above. Mask paths are relative to this JSON file:

```json
{
  "reference_masks": ["data/finding_mask.nii.gz"],
  "predictions": [
    {"mask": "outputs/rexgrounding_rg/grounded/mask_000.nii.gz", "matched_gt_index": 1}
  ]
}
```

```bash
conda activate holoct-eval-basic
python -m eval.rex_report --input report_case.json
```

Use `mask: null` for a prediction with no generated mask. A `matched_gt_index` of `null` means the semantic judgement is unmatched. The score uses the findings in this one report:

- TP counts reference findings covered by a semantic match; FP is predicted findings minus TP; FN is reference findings minus TP. Finding F1 is `2TP / (2TP + FP + FN)`, with 1 when both finding sets are empty.
- Each covered reference uses the highest Dice among its semantically matched predictions. Both-empty masks have Dice 1 for this metric.
- Conditional Dice is the mean over covered reference findings. Conditional HIT5% and HIT10% use the same findings with strict `>` thresholds.
- FL-GRQ is finding F1 multiplied by conditional Dice. Conditional metrics and FL-GRQ are `null` when there are no semantic matches.
