"""
NeuroScrape - Karma Score Classification Head Trainer (Section 6.4)
Trains a lightweight LogisticRegression model on frozen NeuroAnchor embeddings
to distinguish clean, high-fidelity extractions from placeholder/garbage noise.
Saves to models/karma-head.joblib (< 1 MB).
"""

import os
import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

CLEAN_SAMPLES = [
    "Apple MacBook Pro 16 M3 Max 36GB RAM 1TB SSD Space Black",
    "$1,999.00",
    "In Stock — Ships within 24 hours",
    "Senior Machine Learning Infrastructure Engineer at Bright Data",
    "https://docs.brightdata.com/api-reference/endpoints",
    "Released v2.4.0 with automated DOM self-healing capabilities",
    "4.9 out of 5 stars based on 3,420 customer reviews",
    "San Francisco, CA (Hybrid / Remote Option)",
    "Comprehensive guide to web scraping proxies and browser automation"
]

GARBAGE_SAMPLES = [
    "undefined",
    "null",
    "N/A",
    "[object Object]",
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
    "sample placeholder text",
    "loading...",
    "error 404 not found",
    "",
    "none",
    "nil"
]


def train_karma_head(output_path: str = "models/karma-head.joblib"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    from sentence_transformers import SentenceTransformer
    
    print("Encoding samples with SentenceTransformer...")
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    
    # Generate augmented training data
    X_clean = model.encode(CLEAN_SAMPLES * 10, normalize_embeddings=True)
    y_clean = np.ones(len(X_clean), dtype=int)

    X_garbage = model.encode(GARBAGE_SAMPLES * 10, normalize_embeddings=True)
    y_garbage = np.zeros(len(X_garbage), dtype=int)

    X = np.vstack([X_clean, X_garbage])
    y = np.concatenate([y_clean, y_garbage])

    # Shuffle
    indices = np.arange(len(X))
    np.random.shuffle(indices)
    X, y = X[indices], y[indices]

    clf = LogisticRegression(C=1.0, max_iter=200)
    clf.fit(X, y)

    preds = clf.predict(X)
    acc = accuracy_score(y, preds)
    print(f"Karma classification head trained with accuracy: {acc * 100:.2f}%")

    joblib.dump(clf, output_path)
    print(f"Saved Karma classification head to {output_path} ({os.path.getsize(output_path) / 1024:.2f} KB)")


if __name__ == "__main__":
    train_karma_head()
