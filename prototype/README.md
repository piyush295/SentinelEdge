# SentinelEdge — Proof-of-Concept Phishing Classifier

This is the **offline detection core** referenced in the SentinelEdge proposal. It
validates the central claim of the project: phishing / scam text can be classified
**accurately and instantly by a lightweight model that runs fully on-device** — no
cloud, no network — the kind of model that is quantized and offloaded to the
Snapdragon Hexagon NPU in the full product.

## Verified results (real run on Kaggle data)

| Metric | Value |
|---|---|
| Test accuracy | **97.10%** |
| ROC-AUC | **0.9963** |
| Inference latency | **0.22 ms / email** (CPU) |
| Emails evaluated | 18,631 (20% held-out test) |
| Model | TF-IDF (1–2 gram) + Logistic Regression |
| Dataset | Kaggle `subhajournal/phishingemails` |

Full metrics are saved in [`metrics.json`](metrics.json).

Example ad-hoc classification:
```
$ python phishing_classifier.py "URGENT: Your account has been suspended. Click here
  immediately to verify your password and banking details..."
Verdict : PHISHING
Risk    : 98.8/100
```

## Why this matters for the Snapdragon use case
- The model is tiny and CPU-only here, proving the workload is light enough to run
  **quantized on the Hexagon NPU** in real time at very low power.
- Because it is fully local, **no email content ever leaves the device** — the
  privacy guarantee that makes SentinelEdge viable for sensitive users.
- In the shipped product, this fast classifier acts as a first-pass filter, and a
  quantized on-device **LLM (Qualcomm AI Hub GenieX / llama.cpp)** explains each
  verdict in plain language.

## Run it yourself

```bash
pip install -r requirements.txt

# 1. Get the dataset (Kaggle CLI configured)
kaggle datasets download -d subhajournal/phishingemails -p data --unzip

# 2. Train, evaluate, and save metrics
python phishing_classifier.py

# 3. Classify an ad-hoc message
python phishing_classifier.py "your suspicious text here"
```

## Note
The dataset CSV is **not** committed (see `.gitignore`) because of size and license;
the commands above reproduce it in seconds. The PoC is intentionally simple and
fully reproducible offline.
