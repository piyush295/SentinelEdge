#!/usr/bin/env python3
"""
SentinelEdge — Proof-of-Concept Phishing Classifier
====================================================

This is the offline detection core referenced in the SentinelEdge proposal for the
Snapdragon AI Lab Challenge. It validates the central claim: that phishing / scam
text can be classified accurately by a lightweight model that runs fully on-device
(no cloud, no network) — the kind of model that is quantized and offloaded to the
Snapdragon Hexagon NPU in the full product.

For the PoC we use a compact, fast TF-IDF + Logistic Regression pipeline. It is
deliberately small so it demonstrates the "runs locally, instantly, privately"
property. In the shipped product this classifier is complemented by a quantized
on-device LLM (via Qualcomm AI Hub GenieX / llama.cpp) that *explains* each verdict.

Dataset: Kaggle `subhajournal/phishingemails` (Phishing_Email.csv), labels:
    - "Safe Email"
    - "Phishing Email"

Usage:
    python phishing_classifier.py            # train + evaluate + save metrics
    python phishing_classifier.py "some text" # classify an ad-hoc message
"""

import json
import sys
import time
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

DATA_PATH = Path(__file__).parent / "data" / "Phishing_Email.csv"
METRICS_PATH = Path(__file__).parent / "metrics.json"
RANDOM_STATE = 42


def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    # Normalize columns
    df = df.rename(columns={"Email Text": "text", "Email Type": "label"})
    df = df[["text", "label"]].dropna()
    df = df[df["text"].str.strip().astype(bool)]
    # Binary target: 1 = phishing, 0 = safe
    df["y"] = (df["label"].str.lower().str.contains("phish")).astype(int)
    return df


def build_pipeline() -> Pipeline:
    """A compact pipeline chosen for on-device friendliness (small, fast, no GPU)."""
    return Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    stop_words="english",
                    ngram_range=(1, 2),
                    max_features=50_000,
                    sublinear_tf=True,
                ),
            ),
            (
                "clf",
                LogisticRegression(max_iter=1000, C=4.0, n_jobs=-1),
            ),
        ]
    )


def train_and_evaluate() -> dict:
    print("Loading dataset ...")
    df = load_data()
    print(f"  {len(df):,} usable emails "
          f"({df['y'].mean() * 100:.1f}% phishing)")

    X_train, X_test, y_train, y_test = train_test_split(
        df["text"], df["y"],
        test_size=0.2, stratify=df["y"], random_state=RANDOM_STATE,
    )

    pipe = build_pipeline()

    print("Training ...")
    t0 = time.perf_counter()
    pipe.fit(X_train, y_train)
    train_secs = time.perf_counter() - t0

    print("Evaluating ...")
    t0 = time.perf_counter()
    y_pred = pipe.predict(X_test)
    predict_secs = time.perf_counter() - t0
    y_proba = pipe.predict_proba(X_test)[:, 1]

    acc = accuracy_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_proba)
    per_msg_ms = predict_secs / len(X_test) * 1000

    report = classification_report(
        y_test, y_pred, target_names=["Safe", "Phishing"], digits=4
    )
    cm = confusion_matrix(y_test, y_pred).tolist()

    print("\n" + "=" * 60)
    print("SentinelEdge PoC — Phishing Classifier Results")
    print("=" * 60)
    print(f"Test accuracy      : {acc * 100:.2f}%")
    print(f"ROC-AUC            : {auc:.4f}")
    print(f"Train time         : {train_secs:.1f} s (one-time, offline)")
    print(f"Inference latency  : {per_msg_ms:.3f} ms / email (CPU, single core-ish)")
    print(f"Test set size      : {len(X_test):,} emails")
    print("\nConfusion matrix [rows=true, cols=pred] (Safe, Phishing):")
    print(f"  {cm}")
    print("\nClassification report:")
    print(report)

    metrics = {
        "dataset": "Kaggle subhajournal/phishingemails",
        "model": "TF-IDF (1-2 gram, 50k feats) + Logistic Regression",
        "n_total": int(len(df)),
        "phishing_ratio": round(float(df["y"].mean()), 4),
        "test_accuracy": round(float(acc), 4),
        "roc_auc": round(float(auc), 4),
        "train_seconds": round(train_secs, 2),
        "inference_ms_per_email": round(per_msg_ms, 4),
        "confusion_matrix_safe_phish": cm,
        "note": (
            "PoC runs fully offline on CPU. In the product this compact model is "
            "quantized and offloaded to the Snapdragon Hexagon NPU, and paired with "
            "an on-device LLM (Qualcomm AI Hub GenieX) that explains each verdict."
        ),
    }
    METRICS_PATH.write_text(json.dumps(metrics, indent=2))
    print(f"\nMetrics written to {METRICS_PATH.name}")
    return {"pipe": pipe, "metrics": metrics}


def classify_one(pipe: Pipeline, text: str) -> None:
    proba = pipe.predict_proba([text])[0][1]
    verdict = "PHISHING" if proba >= 0.5 else "SAFE"
    print(f"\nVerdict : {verdict}")
    print(f"Risk    : {proba * 100:.1f}/100")


if __name__ == "__main__":
    result = train_and_evaluate()
    if len(sys.argv) > 1:
        classify_one(result["pipe"], " ".join(sys.argv[1:]))
