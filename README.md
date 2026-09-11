# ViZeroLJP

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

This repository contains only source code, configuration files, installation files, and benchmark data needed to reproduce experiments. It intentionally excludes generated result files, model weights, virtual environments, and runtime caches.

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
| Gemma-3-4B-it | 4B | `gemma3-4b` | Gemma 3 GGUF release |
| Gemma-3-12B-it | 12B | `gemma3-12b` | `unsloth/gemma-3-12b-it-GGUF` or `ggml-org/gemma-3-12b-it-GGUF` |
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

For text-only Gemma 3 runs, add `--no-mmproj`:

```bash
~/.llama-app/llama serve \
  -hf unsloth/gemma-3-12b-it-GGUF:UD-Q4_K_XL \
  --no-mmproj \
  --host 0.0.0.0 \
  --port 8000 \
  -ngl all \
  -c 8192 \
  -np 1 \
  -a gemma3-12b
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
