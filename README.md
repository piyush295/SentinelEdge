# SentinelEdge

**On-Device AI Security Analyst for Snapdragon-Powered HP PCs**

A fully offline, privacy-first AI security assistant that runs entirely on the Snapdragon Hexagon NPU — no cloud, no data leakage, no subscription.

> Submitted for the **Snapdragon® AI Lab Build & Present Challenge** (Qualcomm).

---

## The idea in one line
SentinelEdge turns any Snapdragon HP OmniBook into a private, offline AI security analyst that detects phishing, malicious files, and on-screen scams — and explains each threat in plain language — with **zero data ever leaving the device**.

## Why it needs an NPU (and the cloud can't do it)
- Runs a quantized LLM + detection models on the **45+ TOPS Hexagon NPU**, so reasoning is real-time and battery-friendly (15–30 W envelope).
- Because inference is 100% local, sensitive content (emails, legal/medical docs) **never leaves the laptop** — the core privacy guarantee.
- Works **offline**: on a flight, in low-bandwidth regions, or in air-gapped environments where cloud security fails.

## Model stack (Qualcomm AI Hub / open-source, all on-device)

| Capability | Model | Runtime |
|---|---|---|
| Threat reasoning & explanation | Quantized LLM (Llama 3.x 8B / Phi-3-mini, INT4/INT8 GGUF) | llama.cpp + Qualcomm backend / GenieX |
| Phishing text classification | Lightweight transformer / LLM prompt | Qualcomm AI Engine Direct |
| On-screen text extraction | OCR | LiteRT |
| Visual threat detection | Quantized YOLOv7 (INT8) | Qualcomm AI Engine Direct |
| Voice command (optional) | Whisper | LiteRT |

## Architecture
See [`docs/PROPOSAL.md`](docs/PROPOSAL.md) for the full architecture, data flow, deployment plan, and roadmap.

## Repository structure
```
SentinelEdge/
├── README.md            ← you are here
├── docs/
│   └── PROPOSAL.md       ← full proposal (4 judging criteria)
└── prototype/            ← proof-of-concept phishing classifier (offline)
```

## Status
Proposal stage. A proof-of-concept phishing classifier (offline, CPU/NPU-portable) lives in [`prototype/`](prototype/) to validate the core detection claim with real metrics.

---

*This proposal and repository are the original work and idea of the participant. All referenced models are available via Qualcomm AI Hub or open-source platforms and are intended to run on-device via Qualcomm AI Engine Direct / LiteRT.*
