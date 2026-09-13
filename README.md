# ViZeroLJP: A Retrieval-Augmented Legal Reasoning Framework for Zero-shot Vietnamese Legal Judgment Prediction

## Abstract

Legal Judgment Prediction (LJP) is an important task in legal AI, aiming to predict case outcomes from the facts and legal context of a case. Although LJP has been widely studied in several jurisdictions, Vietnamese LJP remains underexplored, especially in the zero-shot setting where no task-specific training examples are used, in order to address the scarcity of task-specific training data in the Vietnamese legal context. The task is challenging because case facts in Vietnamese judgments are often complex, long, fact-dense, and contain multiple claims, arguments, and outcome cues, while direct prompting can struggle to identify decisive facts and ground predictions in relevant legal provisions. In this paper, we propose **ViZeroLJP**, a zero-shot retrieval-augmented framework for Vietnamese legal judgment prediction. **ViZeroLJP** decomposes the task into three modules: (i) input processing, which extracts structured legal signals from long case facts; (ii) law retrieval, which retrieves relevant statutory provisions from a public law corpus; and (iii) structured outcome reasoning, which predicts the final judgment label from the processed case representation and retrieved legal context. Experiments on the ALQAC 2026 public benchmark show that **ViZeroLJP** improves performance over prompt-only inference across multiple open-source language model backbones.

## Overview

**ViZeroLJP** is a zero-shot framework for Vietnamese Legal Judgment Prediction (LJP). Given a Vietnamese civil case fact (`case_fact`), the system predicts one of four judgment labels:

- `A_WIN`
- `PARTIAL_A_WIN`
- `PARTIAL_B_WIN`
- `B_WIN`

The framework is designed for reproducible experiments on the ALQAC 2026 public benchmark. It does not require task-specific fine-tuning.

The pipeline has three main modules:

1. **Input Processing**: normalize and structure the long Vietnamese `case_fact`.
2. **Law Retrieval**: retrieve relevant legal provisions from `corpus_law_pub.json`.
3. **Judgment Reasoning**: use a zero-shot LLM to predict the final outcome from the processed case and retrieved laws.

## Quantitative Results

Main comparison on the ALQAC 2026 public benchmark. Metrics are percentages. Open-source results are averaged over three runs. `△` denotes the average improvement of **ViZeroLJP** over the corresponding prompt-only baseline.

| Backbone | Params | Method | Acc. | Macro-F1 | A F1 | PA F1 | PB F1 | B F1 | Cov. |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| Llama-3.2-3B-Instruct | 3B | + Prompt-only | 27.33 | 20.85 | 22.54 | 30.04 | 0.00 | **30.82** | 100.00 |
| Llama-3.2-3B-Instruct | 3B | + ViZeroLJP (our) | **47.33** | **31.68** | **45.69** | **66.69** | 0.00 | 14.34 | 100.00 |
| Llama-3.2-3B-Instruct | 3B | △ | +20.00 | +10.83 | +23.15 | +36.65 | +0.00 | -16.48 | +0.00 |
| Llama-3.1-8B-Instruct | 8B | + Prompt-only | 38.00 | 28.78 | **52.76** | 40.92 | 0.00 | 21.44 | 100.00 |
| Llama-3.1-8B-Instruct | 8B | + ViZeroLJP (our) | **47.33** | **32.75** | 48.85 | **59.61** | 0.00 | **22.54** | 100.00 |
| Llama-3.1-8B-Instruct | 8B | △ | +9.33 | +3.97 | -3.91 | +18.69 | +0.00 | +1.10 | +0.00 |
| Phi-4-mini-instruct | 3.8B | + Prompt-only | 36.00 | 14.52 | 0.00 | 58.07 | 0.00 | 0.00 | 100.00 |
| Phi-4-mini-instruct | 3.8B | + ViZeroLJP (our) | **53.33** | **38.91** | **52.17** | **67.10** | 0.00 | **36.36** | 100.00 |
| Phi-4-mini-instruct | 3.8B | △ | +17.33 | +24.39 | +52.17 | +9.03 | +0.00 | +36.36 | +0.00 |
| Phi-4 | 14B | + Prompt-only | 34.67 | 25.34 | 22.22 | 47.62 | **18.18** | 13.33 | 100.00 |
| Phi-4 | 14B | + ViZeroLJP (our) | **46.67** | **35.37** | **52.56** | **59.41** | 0.00 | **29.52** | 100.00 |
| Phi-4 | 14B | △ | +12.00 | +10.03 | +30.34 | +11.79 | -18.18 | +16.19 | +0.00 |
| DeepSeek-R1-Distill-Qwen-7B | 7B | + Prompt-only | 27.33 | 10.79 | 0.00 | 43.15 | 0.00 | 0.00 | 100.00 |
| DeepSeek-R1-Distill-Qwen-7B | 7B | + ViZeroLJP (our) | **52.00** | **38.45** | **50.68** | **67.64** | 0.00 | **35.48** | 100.00 |
| DeepSeek-R1-Distill-Qwen-7B | 7B | △ | +24.67 | +27.66 | +50.68 | +24.49 | +0.00 | +35.48 | +0.00 |
| DeepSeek-R1-Distill-Qwen-14B | 14B | + Prompt-only | 46.67 | 37.69 | **59.04** | 44.93 | 0.00 | **46.77** | 100.00 |
| DeepSeek-R1-Distill-Qwen-14B | 14B | + ViZeroLJP (our) | **48.67** | **38.04** | 52.72 | **58.35** | 0.00 | 41.10 | 100.00 |
| DeepSeek-R1-Distill-Qwen-14B | 14B | △ | +2.00 | +0.35 | -6.32 | +13.42 | +0.00 | -5.67 | +0.00 |
| GPT-5.6 Sol (high-thinking) | - | + Prompt-only | 54.00 | 50.65 | 80.00 | 25.00 | 33.33 | 64.29 | 100.00 |
| Qwen3.5-4B | 4B | + Prompt-only | 34.00 | 27.53 | 38.73 | 43.48 | **4.76** | 23.15 | 100.00 |
| Qwen3.5-4B | 4B | + ViZeroLJP (our) | **52.00** | **37.36** | **55.50** | **64.91** | 0.00 | **29.05** | 100.00 |
| Qwen3.5-4B | 4B | △ | +18.00 | +9.83 | +16.77 | +21.43 | -4.76 | +5.90 | +0.00 |
| Qwen3.5-9B | 9B | + Prompt-only | 44.00 | 34.35 | **55.28** | 46.82 | 0.00 | 35.31 | 100.00 |
| Qwen3.5-9B | 9B | + ViZeroLJP (our) | **53.33** | **43.82** | 47.83 | **64.97** | **25.00** | **37.50** | 100.00 |
| Qwen3.5-9B | 9B | △ | +9.33 | +9.47 | -7.45 | +18.15 | +25.00 | +2.19 | +0.00 |

## Repository Structure

```text
ViZeroLJP/
├── ALQAC2026_public_test.json      # Public benchmark with case_fact and gold verdict labels
├── corpus_law_pub.json             # Public legal corpus for law retrieval
├── assets/                         # Paper/report/slide/poster assets
├── docs/                           # Extra running notes, including Vast.ai + llama.cpp
├── src/alqac_agent/                # ViZeroLJP source code
├── tests/                          # Unit/regression tests
├── pyproject.toml                  # Python package metadata
├── requirements.txt                # Main runtime dependencies
├── requirements-vllm.txt           # Optional vLLM server dependency
└── README.md
```

Generated experiment outputs are written to `result/` and are ignored by Git.

## Benchmark

The default benchmark is:

- `ALQAC2026_public_test.json`: 50 Vietnamese civil cases.
- `corpus_law_pub.json`: legal provisions used by the retrieval module.

Each benchmark item contains the input `case_fact` and the gold `verdict_label`. The framework uses `case_fact` as input and predicts `verdict_label`.

## Labels

| Label | Meaning |
|---|---|
| `A_WIN` | The court fully accepts all of the plaintiff's claims. |
| `PARTIAL_A_WIN` | The court partially accepts the plaintiff's claims, and the accepted portion is greater than 50%. |
| `PARTIAL_B_WIN` | The court partially accepts the plaintiff's claims, but the accepted portion is 50% or less. |
| `B_WIN` | The court fully rejects all of the plaintiff's claims. |

## Environment Setup

Python `3.11+` is recommended. The commands below assume Linux. On Windows, use the equivalent PowerShell commands.

```bash
git clone https://github.com/ThanhHungCS/ViZeroLJP.git
cd ViZeroLJP

python3 -m venv .venv
source .venv/bin/activate

pip install -U pip
pip install -e ".[dev]"
```

Validate the installation:

```bash
alqac-agent --help
pytest
```

## Running With llama.cpp

Most experiments can be run with GGUF models served by `llama.cpp` through an OpenAI-compatible local server.

Install the `llama` command:

```bash
curl -LsSf https://llama.app/install.sh | sh
```

Start a model server in **Terminal 1**. Example for Qwen:

```bash
~/.llama-app/llama serve \
  -hf unsloth/Qwen3.5-9B-GGUF:UD-Q4_K_XL \
  --host 0.0.0.0 \
  --port 8000 \
  -ngl all \
  -c 8192 \
  -np 1 \
  -a qwen3.5-9b
```

Keep this terminal open. In **Terminal 2**, test the server:

```bash
curl http://127.0.0.1:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer EMPTY" \
  -d '{"model":"qwen3.5-9b","messages":[{"role":"user","content":"Return JSON only: {\"ok\": true}"}],"temperature":0,"max_tokens":512}'
```

If the response contains a `content` field, the server is ready.

## Running One ViZeroLJP Experiment

Set generation limits:

```bash
export LLM_MAX_TOKENS=2048
export LLM_TIMEOUT_SECONDS=900
```

Run the full ViZeroLJP method:

```bash
alqac-agent run-ljp-experiment \
  --input ALQAC2026_public_test.json \
  --laws corpus_law_pub.json \
  --result-dir result \
  --type "General Domain" \
  --backbone "Qwen3.5-9B" \
  --params "9B" \
  --domain "General" \
  --mode method \
  --model qwen3.5-9b \
  --llm-provider vllm \
  --llm-base-url http://127.0.0.1:8000/v1 \
  --structured-method prompt_json \
  --runs 3 \
  --no-resume
```

The command writes:

```text
result/submissions/
result/metrics/
result/confusion_matrices/
result/traces/
result/qualitative/
result/run_manifests/
result/tables/
```

The paper tables are computed from the average of three runs.

## Running Prompt-only Baseline

The prompt-only baseline uses the same LLM but removes ViZeroLJP's input-processing and law-retrieval reasoning structure.

```bash
alqac-agent run-ljp-experiment \
  --input ALQAC2026_public_test.json \
  --laws corpus_law_pub.json \
  --result-dir result \
  --type "General Domain" \
  --backbone "Qwen3.5-9B" \
  --params "9B" \
  --domain "General" \
  --mode prompt_only \
  --model qwen3.5-9b \
  --llm-provider vllm \
  --llm-base-url http://127.0.0.1:8000/v1 \
  --structured-method prompt_json \
  --runs 3 \
  --no-resume
```

## Ablation Study

Use `Qwen3.5-9B` for ablations.

Without input processing:

```bash
alqac-agent run-ljp-experiment \
  --input ALQAC2026_public_test.json \
  --laws corpus_law_pub.json \
  --result-dir result \
  --type "General Domain" \
  --backbone "Qwen3.5-9B" \
  --params "9B" \
  --domain "General" \
  --mode no_input_processing \
  --model qwen3.5-9b \
  --llm-provider vllm \
  --llm-base-url http://127.0.0.1:8000/v1 \
  --structured-method prompt_json \
  --runs 3 \
  --no-resume
```

Without law retrieval:

```bash
alqac-agent run-ljp-experiment \
  --input ALQAC2026_public_test.json \
  --laws corpus_law_pub.json \
  --result-dir result \
  --type "General Domain" \
  --backbone "Qwen3.5-9B" \
  --params "9B" \
  --domain "General" \
  --mode no_law_retrieval \
  --model qwen3.5-9b \
  --llm-provider vllm \
  --llm-base-url http://127.0.0.1:8000/v1 \
  --structured-method prompt_json \
  --runs 3 \
  --no-resume
```

Without both input processing and law retrieval:

```bash
alqac-agent run-ljp-experiment \
  --input ALQAC2026_public_test.json \
  --laws corpus_law_pub.json \
  --result-dir result \
  --type "General Domain" \
  --backbone "Qwen3.5-9B" \
  --params "9B" \
  --domain "General" \
  --mode no_law_retrieval_no_input_processing \
  --model qwen3.5-9b \
  --llm-provider vllm \
  --llm-base-url http://127.0.0.1:8000/v1 \
  --structured-method prompt_json \
  --runs 3 \
  --no-resume
```

## Models Used In The Main Comparison

The following model aliases were used in the experiments. Serve one model at a time on port `8000`, then run both `prompt_only` and `method`.

| Backbone | Params | Suggested server alias | Example GGUF source |
|---|---:|---|---|
| Qwen3.5-4B | 4B | `qwen3.5-4b` | Qwen/Unsloth GGUF release |
| Qwen3.5-9B | 9B | `qwen3.5-9b` | `unsloth/Qwen3.5-9B-GGUF` |
| Llama-3.2-3B-Instruct | 3B | `llama3.2-3b` | llama.cpp-compatible GGUF release |
| Llama-3.1-8B-Instruct | 8B | `llama3.1-8b` | llama.cpp-compatible GGUF release |
| Phi-4-mini-instruct | 3.8B | `phi4-mini` | `jc-builds/Phi-4-mini-instruct-GGUF` |
| Phi-4 | 14B | `phi4-14b` | `microsoft/phi-4-gguf` |
| DeepSeek-R1-Distill-Qwen-7B | 7B | `deepseek-r1-qwen-7b` | `bartowski/DeepSeek-R1-Distill-Qwen-7B-GGUF` |
| DeepSeek-R1-Distill-Qwen-14B | 14B | `deepseek-r1-qwen-14b` | `bartowski/DeepSeek-R1-Distill-Qwen-14B-GGUF` |

Recommended server pattern:

```bash
~/.llama-app/llama serve \
  -hf <HF_GGUF_REPO>:<QUANT_NAME> \
  --host 0.0.0.0 \
  --port 8000 \
  -ngl all \
  -c 8192 \
  -np 1 \
  -a <MODEL_ALIAS>
```

## Running With vLLM

Use vLLM only when a model is not available as GGUF. Keep it in a separate virtual environment to avoid dependency conflicts with the main experiment environment.

Terminal 1:

```bash
python3 -m venv .venv_vllm
source .venv_vllm/bin/activate
pip install -U pip
pip install -r requirements-vllm.txt

vllm serve <HF_MODEL_ID> \
  --host 0.0.0.0 \
  --port 8000 \
  --served-model-name <MODEL_ALIAS> \
  --max-model-len 8192 \
  --gpu-memory-utilization 0.90 \
  --dtype auto
```

Terminal 2:

```bash
source .venv/bin/activate
curl http://127.0.0.1:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer EMPTY" \
  -d '{"model":"<MODEL_ALIAS>","messages":[{"role":"user","content":"Return JSON only: {\"ok\": true}"}],"temperature":0,"max_tokens":512}'
```

Then run `alqac-agent run-ljp-experiment` with `--model <MODEL_ALIAS>` and `--llm-base-url http://127.0.0.1:8000/v1`.

## Evaluating A Prediction File

If you have a prediction file:

```json
[
  {"case_id": "case_4101", "prediction": "PARTIAL_A_WIN"}
]
```

evaluate it with:

```bash
alqac-agent evaluate \
  --gold ALQAC2026_public_test.json \
  --predictions result/submissions/example.json \
  > result/metrics/example.metrics.json
```

Metrics include:

- Accuracy
- Macro-F1
- Precision/Recall/F1 for each label
- Coverage
- Confusion matrix

## Reproducing Paper-ready Tables

Running `run-ljp-experiment` automatically refreshes:

```text
result/tables/main_comparison.md
result/tables/main_comparison.csv
result/tables/ablation_study.md
result/tables/ablation_study.csv
result/tables/all_metrics.json
```

The repository does not include generated tables. Re-run the experiments above to reproduce them.

## Qualitative Analysis Artifacts

Each experiment run writes:

```text
result/qualitative/<experiment_id>.input_processing_outputs.json
result/qualitative/<experiment_id>.retrieval_outputs.json
result/qualitative/<experiment_id>.special_cases.json
```

These files are useful for analyzing:

- what the input-processing module extracted from `case_fact`;
- which law provisions were retrieved;
- which labels and cases are hard for the system.

## Vast.ai Notes

Recommended hardware:

- RTX 3090 / RTX 3090 Ti / RTX 4090 or better.
- At least 24GB VRAM.
- At least 60GB disk, preferably 80GB, if running many models.

If disk is nearly full, remove model caches:

```bash
rm -rf /root/.cache/huggingface/hub/models--*
rm -rf /root/.cache/llama.cpp
df -h /workspace
```

More detailed Vast.ai + llama.cpp notes are in:

```text
docs/vastai_llamacpp_ljp.md
```

## Important Reproducibility Notes

- This repo does not include model weights. The serving command downloads each model automatically from Hugging Face.
- Generated outputs are ignored by Git and should be regenerated by reviewers.
- The default result directory is `result/`.
- Use `--runs 3` for paper-style averaged results.
- Use `--no-resume` when rerunning from scratch.

## Citation

If you use my ViZeroLJP in your work, please use the following BibTeX entries:

```bibtex
@misc{vizero_ljp_2026,
  title        = {ViZeroLJP: A Retrieval-Augmented Legal Reasoning Framework for Zero-shot Vietnamese Legal Judgment Prediction},
  author       = {ThanhHungCS and collaborators},
  year         = {2026},
  howpublished = {\url{https://github.com/ThanhHungCS/ViZeroLJP}},
  note         = {Code and reproducibility materials}
}
```
