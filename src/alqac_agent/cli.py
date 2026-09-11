from __future__ import annotations

import argparse
import json
from dataclasses import replace

from .config import Settings
from .data import load_json, load_law_articles
from .evaluation import evaluate_outcomes
from .experiments import ExperimentInfo, default_experiment_id, run_ljp_experiment
from .ljp_graph import run_ljp_public
from .llm import LegalAgents
from .retrieval import LawRetriever


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ViZeroLJP experiment runner")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="validate benchmark and law files")
    validate.add_argument("--input", default="ALQAC2026_public_test.json")
    validate.add_argument("--laws", default="corpus_law_pub.json")

    inspect = subparsers.add_parser("inspect-law", help="run local BM25 law retrieval")
    inspect.add_argument("query")
    inspect.add_argument("--laws", default="corpus_law_pub.json")
    inspect.add_argument("--top-k", type=int, default=5)

    evaluate = subparsers.add_parser("evaluate", help="evaluate LJP predictions")
    evaluate.add_argument("--gold", default="ALQAC2026_public_test.json")
    evaluate.add_argument("--predictions", default="submission.public.json")

    ljp = subparsers.add_parser(
        "run-ljp",
        help="run zero-shot Legal Judgment Prediction from case_fact",
    )
    ljp.add_argument("--input", default="ALQAC2026_public_test.json")
    ljp.add_argument("--laws", default="corpus_law_pub.json")
    ljp.add_argument("--output", default="runs/submission.ljp.public.json")
    ljp.add_argument(
        "--model",
        default="qwen3.5-9b",
        help="model alias served by the OpenAI-compatible LLM server",
    )
    ljp.add_argument("--llm-base-url", default=None)
    ljp.add_argument("--llm-provider", default=None, choices=("vllm", "ollama", "groq"))
    ljp.add_argument(
        "--structured-method",
        default=None,
        choices=("json_schema", "prompt_json"),
    )
    ljp.add_argument("--limit", type=int)
    ljp.add_argument("--no-resume", action="store_true")
    ljp.add_argument("--no-llm", action="store_true")
    ljp.add_argument("--law-candidates", type=int, default=18)
    ljp.add_argument(
        "--trace-output",
        default=None,
        help="optional trace path with processed input, law query, laws, and reasoning",
    )

    experiment = subparsers.add_parser(
        "run-ljp-experiment",
        help="run an LJP experiment and write all outputs to result/",
    )
    experiment.add_argument("--input", default="ALQAC2026_public_test.json")
    experiment.add_argument("--laws", default="corpus_law_pub.json")
    experiment.add_argument("--result-dir", default="result")
    experiment.add_argument("--experiment-id", default=None)
    experiment.add_argument("--type", default="General Domain")
    experiment.add_argument("--backbone", required=True)
    experiment.add_argument("--params", required=True)
    experiment.add_argument("--domain", default="General")
    experiment.add_argument(
        "--mode",
        required=True,
        choices=(
            "prompt_only",
            "method",
            "no_law_retrieval",
            "no_input_processing",
            "no_law_retrieval_no_input_processing",
        ),
    )
    experiment.add_argument(
        "--model",
        required=True,
        help="model alias served by the OpenAI-compatible LLM server",
    )
    experiment.add_argument("--llm-base-url", default=None)
    experiment.add_argument("--llm-provider", default=None, choices=("vllm", "ollama", "groq"))
    experiment.add_argument(
        "--structured-method",
        default=None,
        choices=("json_schema", "prompt_json"),
    )
    experiment.add_argument("--limit", type=int)
    experiment.add_argument("--no-resume", action="store_true")
    experiment.add_argument("--no-llm", action="store_true")
    experiment.add_argument("--law-candidates", type=int, default=18)
    experiment.add_argument(
        "--runs",
        type=int,
        default=1,
        help="number of independent runs; paper tables use the average when >1",
    )
    return parser


def _settings_from_args(args: argparse.Namespace) -> Settings:
    settings = Settings.from_env()
    overrides = {"llm_structured_method": "prompt_json"}
    if getattr(args, "model", None) is not None:
        overrides["llm_model"] = args.model
    if getattr(args, "llm_base_url", None) is not None:
        overrides["llm_base_url"] = args.llm_base_url
    if getattr(args, "llm_provider", None) is not None:
        overrides["llm_provider"] = args.llm_provider
    if getattr(args, "structured_method", None) is not None:
        overrides["llm_structured_method"] = args.structured_method
    return replace(settings, **overrides)


def main() -> None:
    args = _parser().parse_args()

    if args.command == "validate":
        cases = load_json(args.input)
        articles = load_law_articles(args.laws)
        print(
            json.dumps(
                {
                    "status": "ok",
                    "input_cases": len(cases),
                    "law_articles": len(articles),
                    "network_calls": 0,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    if args.command == "inspect-law":
        retriever = LawRetriever(load_law_articles(args.laws))
        print(json.dumps(retriever.search(args.query, args.top_k), ensure_ascii=False, indent=2))
        return

    if args.command == "evaluate":
        print(
            json.dumps(
                evaluate_outcomes(args.gold, args.predictions),
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    if args.command == "run-ljp":
        settings = _settings_from_args(args)
        settings.validate_for_run(require_api_key=False)
        agents = None if args.no_llm else LegalAgents(settings)
        run_ljp_public(
            input_path=args.input,
            law_path=args.laws,
            output_path=args.output,
            judge=agents,
            limit=args.limit,
            resume=not args.no_resume,
            law_candidates=args.law_candidates,
            trace_output_path=args.trace_output,
        )
        return

    if args.command == "run-ljp-experiment":
        settings = _settings_from_args(args)
        settings.validate_for_run(require_api_key=False)
        experiment_id = args.experiment_id or default_experiment_id(
            args.backbone,
            args.params,
            args.mode,
        )
        summary = run_ljp_experiment(
            input_path=args.input,
            law_path=args.laws,
            result_dir=args.result_dir,
            info=ExperimentInfo(
                experiment_id=experiment_id,
                model_type=args.type,
                backbone=args.backbone,
                params=args.params,
                domain=args.domain,
                mode=args.mode,
            ),
            judge=None if args.no_llm else LegalAgents(settings),
            limit=args.limit,
            resume=not args.no_resume,
            law_candidates=args.law_candidates,
            runs=args.runs,
        )
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return


if __name__ == "__main__":
    main()
