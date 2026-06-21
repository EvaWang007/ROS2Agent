"""Create one bootstrap dataset sample in LangSmith."""

from langsmith import Client


def main() -> None:
    client = Client()
    dataset_name = "rosa-agent-single-sample-v1"

    dataset = None
    for ds in client.list_datasets(dataset_name=dataset_name):
        dataset = ds
        break

    if dataset is None:
        dataset = client.create_dataset(
            dataset_name=dataset_name,
            description="Single-sample bootstrap eval for ROSA agent",
        )

    example = {
        "inputs": {
            "query": "机器人规划成功但不动，请检查 /cmd_vel 和 controller_server。",
        },
        "outputs": {
            "expected_answer": "应优先检查 /cmd_vel publisher 与 controller_server lifecycle 状态。",
            "must_include": ["/cmd_vel", "controller_server"],
            "forbidden_claims": ["I cannot check tools"],
        },
        "metadata": {
            "domain": "navigation",
            "scene_id": "nav_ws_house",
            "robot_id": "turtlebot3",
            "case_type": "mixed",
        },
    }

    client.create_examples(dataset_id=dataset.id, examples=[example])
    print("dataset_name:", dataset_name)
    print("dataset_id:", dataset.id)
    print("created_examples: 1")


if __name__ == "__main__":
    main()
