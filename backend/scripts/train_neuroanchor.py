"""
NeuroScrape - NeuroAnchor Model Fine-Tuning Script (Section 6.2)
Fine-tunes sentence-transformers/all-MiniLM-L6-v2 on contrastive DOM pairs
using MultipleNegativesRankingLoss.
"""

import os
import json
import logging
from torch.utils.data import DataLoader
from sentence_transformers import SentenceTransformer, InputExample, losses

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("train_neuroanchor")


def train_model(
    dataset_path: str = "data/neuroanchor_pairs.jsonl",
    output_path: str = "models/neuroanchor-v1",
    epochs: int = 3,
    batch_size: int = 32
):
    if not os.path.exists(dataset_path):
        logger.info(f"Dataset not found at {dataset_path}. Building dataset first...")
        from build_dataset import build_dataset
        build_dataset(dataset_path)

    logger.info(f"Loading contrastive dataset from {dataset_path}...")
    train_examples = []
    with open(dataset_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                item = json.loads(line)
                desc = item["field_description"]
                pos = item["positive_node"]
                train_examples.append(InputExample(texts=[desc, pos]))

    logger.info(f"Prepared {len(train_examples)} training pairs.")

    logger.info("Initializing base model: sentence-transformers/all-MiniLM-L6-v2")
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=batch_size)
    train_loss = losses.MultipleNegativesRankingLoss(model)

    os.makedirs(output_path, exist_ok=True)
    logger.info(f"Starting fine-tuning for {epochs} epochs...")
    
    model.fit(
        train_objectives=[(train_dataloader, train_loss)],
        epochs=epochs,
        warmup_steps=int(len(train_dataloader) * 0.1),
        output_path=output_path,
        show_progress_bar=True
    )

    logger.info(f"Fine-tuning complete! Model saved to {output_path}")


if __name__ == "__main__":
    train_model()
