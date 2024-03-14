import asyncio
import sys
from argparse import ArgumentParser
from logging import getLogger, basicConfig, DEBUG
from typing import Optional

import jsonlines

sys.path.append("..")
from datasets import Dataset
from chatbot.dto.knowledge import KnowledgeResult
from chatbot.service import knowledge as knowledge_service

from ragas import evaluate
from ragas.evaluation import Result

from ragas.metrics import (
    answer_relevancy,
    faithfulness,
    context_precision,
)

from langchain.chat_models import ChatOpenAI
from ragas.llms import LangchainLLM

# ========================================
# Retrieval:
# * MAP@K - Mean Average Precision
# ========================================
# Generation (LLM):
# * Answer Relevancy
# * Faithfullness
# ========================================

basicConfig(format="%(levelname)s:%(message)s", level=DEBUG)
logger = getLogger("evaluate")

# context_precision.llm = LangchainLLM(
#     llm=ChatOpenAI(model="gpt-3.5-turbo-0125", max_retries=100, temperature=0)
# )


async def evaluate_retrieval(dataset: Dataset) -> Result:
    """Evaluate the given dataset for retrieval"""
    logger.debug("evaluate_retrieval, dataset=%s", dataset)
    return evaluate(
        dataset,
        metrics=[
            context_precision,
        ],
    )


async def evaluate_generation(dataset: Dataset) -> Result:
    """Evaluate the given dataset for generation"""
    logger.debug("evaluate_generation, dataset=%s", dataset)
    return evaluate(
        dataset,
        metrics=[
            answer_relevancy,
            faithfulness,
        ],
    )


async def prepare_dataset(
    file_path: str, retrieve: bool, generate: bool, k: int
) -> Dataset:
    """Prepare the dataset for evaluation"""
    logger.debug(
        "prepare_dataset, file_path=%s, retrieve=%s, generate=%s, k=%s",
        file_path,
        retrieve,
        generate,
        k,
    )

    samples: dict = {"question": []}

    if retrieve:
        samples["contexts"] = []

    if generate:
        samples["contexts"] = []
        samples["answer"] = []
        samples["ground_truths"] = []

    with jsonlines.open(file_path) as reader:
        for obj in reader:
            samples["question"].append(obj["question"])

            if generate and "truth" in obj and obj["truth"].strip() != "":
                samples["ground_truths"].append(obj["truth"])

    if retrieve:
        logger.debug("prepare_dataset, retrieve")

        for question in samples["question"]:
            context: list[KnowledgeResult] = await knowledge_service.search(
                question, limit=k
            )
            samples["contexts"].append(list(map(lambda x: x.text, context)))

    if generate:
        logger.debug("prepare_dataset, generate")

    logger.debug("prepare_dataset, samples=%s", samples)

    return Dataset.from_dict(samples)


async def main():
    """Main function"""
    logger.debug("main")

    parser = ArgumentParser()
    parser.add_argument(
        "--dataset-file", type=str, default="datasets/dataset-xml.jsonl"
    )
    parser.add_argument("--retrieve", action="store_true")
    parser.add_argument("--generate", action="store_true")
    parser.add_argument("--details", action="store_true")
    parser.add_argument("-k", type=int, default=3)
    args = parser.parse_args()

    dataset: Dataset = await prepare_dataset(
        args.dataset_file, args.retrieve, args.generate, args.k
    )
    question_list: list[str] = []

    for batch in dataset.select_columns("question").iter(batch_size=10):
        for question in batch["question"]:
            question_list.append(question)

    if args.retrieve:
        retrieval_map_at_k = await evaluate_retrieval(dataset)
        logger.debug(
            "retrieval map@%s=%s", args.k, retrieval_map_at_k["context_precision"]
        )

        if args.details:
            q_idx: int = 0

            for batch in retrieval_map_at_k.scores.iter(batch_size=10):
                for precision in batch["context_precision"]:
                    logger.debug("    %-20s\t%s", question_list[q_idx], precision)
                    q_idx += 1

    if args.generate:
        logger.debug("generation, result=%s", await evaluate_generation(dataset))


if __name__ == "__main__":
    asyncio.run(main())
