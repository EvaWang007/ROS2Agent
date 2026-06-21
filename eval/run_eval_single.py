"""Run single-sample eval against LangSmith dataset."""

from langsmith import Client

try:
    # Preferred when running as module: python -m eval.run_eval_single
    from eval.target import target_fn
    from eval.evaluators import (
        must_include_evaluator,
        forbidden_claims_evaluator,
        keyword_correctness_evaluator,
    )
except ModuleNotFoundError:
    # Fallback when running as script: python eval/run_eval_single.py
    from target import target_fn
    from evaluators import (
        must_include_evaluator,
        forbidden_claims_evaluator,
        keyword_correctness_evaluator,
    )


def main() -> None:
    client = Client()
    dataset_name = "rosa-agent-single-sample-v1"

    result = client.evaluate(
        target_fn,
        data=dataset_name,
        evaluators=[
            must_include_evaluator,
            forbidden_claims_evaluator,
            keyword_correctness_evaluator,
        ],
        experiment_prefix="rosa-single-sample",
        max_concurrency=1,
        blocking=True,
    )

    print("Evaluation finished")
    print(result)


if __name__ == "__main__":
    main()
