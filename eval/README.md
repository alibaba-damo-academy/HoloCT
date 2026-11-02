# Single-sample metrics

Run each example from the repository root. Supply a prediction and its reference from the same CT, question or finding. Results are printed as JSON; `--output metrics/example.json` also saves them.

## Mask and text metrics

```bash
python -m pip install -r requirements-eval.txt
python -m nltk.downloader punkt_tab wordnet omw-1.4
```

Text metrics download their metric modules on first use through [Hugging Face Evaluate](https://github.com/huggingface/evaluate).

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

Use a separate environment for each model-based metric and install its inference dependencies. Llama and GREEN entry points use [vLLM](https://docs.vllm.ai/en/latest/getting_started/installation/gpu/):

```bash
conda create -n holoct-judge python=3.10.16 -y
conda activate holoct-judge
python -m pip install vllm==0.7.3 transformers==4.48.2
```

### Llama clinical score

Download the Llama-3.1-70B-Instruct judge to `weights/Llama-3.1-70B-Instruct` and run:

```bash
CUDA_VISIBLE_DEVICES=0,1 python -m eval.llama --prediction-file outputs/vqa/grounded/response.txt --reference "There is a lesion in the liver." --question "Is there a liver lesion?" --question-type "Short answer"
```

Question types are `Report generation`, `Long answer`, `Short answer` and `Multiple choice`. The output contains the 0-10 score and the judge response. `--tensor-parallel-size` sets the number of GPUs for this one judgement; its default is 2.

### GREEN

Obtain the [GREEN](https://github.com/Stanford-AIMI/GREEN) prompt utilities and provide its checkpoint at `weights/GREEN`:

```bash
git clone https://github.com/Stanford-AIMI/GREEN.git ../GREEN
CUDA_VISIBLE_DEVICES=0 python -m eval.green --prediction-file outputs/radgenome_rg/grounded/response.txt --reference-file data/reference_report.txt
```

GREEN returns the explanation, matched findings and error counts. Its score is `matched / (matched + clinically_significant_errors)`, with zero when there are no matched findings. The GREEN prompt uses up to 300 words from each report. Use `--model` for another checkpoint location and `--green-utils` for another directory containing the GREEN `utils.py` file.

### RaTEScore

Install [RaTEScore](https://github.com/MAGIC-AI4Med/RaTEScore) and its model dependencies in its evaluation environment:

```bash
conda create -n holoct-rate python=3.10.16 -y
conda activate holoct-rate
python -m pip install RaTEScore==0.1.0 medspacy transformers torch pandas numpy
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
python -m eval.rex_report --input report_case.json
```

Use `mask: null` for a prediction with no generated mask. A `matched_gt_index` of `null` means the semantic judgement is unmatched. The score uses the findings in this one report:

- TP counts reference findings covered by a semantic match; FP is predicted findings minus TP; FN is reference findings minus TP. Finding F1 is `2TP / (2TP + FP + FN)`, with 1 when both finding sets are empty.
- Each covered reference uses the highest Dice among its semantically matched predictions. Both-empty masks have Dice 1 for this metric.
- Conditional Dice is the mean over covered reference findings. Conditional HIT5% and HIT10% use the same findings with strict `>` thresholds.
- FL-GRQ is finding F1 multiplied by conditional Dice. Conditional metrics and FL-GRQ are `null` when there are no semantic matches.
