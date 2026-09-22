# SentinelEdge — On-Device AI Security Analyst for Snapdragon-Powered HP PCs

**Snapdragon® AI Lab Build & Present Challenge — Solution Proposal**

*A fully offline, privacy-first AI security assistant that runs entirely on the Snapdragon Hexagon NPU — no cloud, no data leakage, no subscription.*

---

## Executive Summary

SentinelEdge is an on-device AI security analyst built for Snapdragon-powered HP OmniBook PCs. It continuously watches for phishing, malicious files, suspicious scripts, and risky system behaviour, and explains each threat to the user in plain language — all **100% locally** on the device's Hexagon NPU.

Traditional endpoint security either (a) ships user data to the cloud for analysis, creating a privacy and compliance risk, or (b) runs shallow signature checks that miss novel threats. SentinelEdge takes a third path: it runs real AI models (an LLM reasoning engine plus specialized detection models) **directly on the NPU**, so the intelligence of a cloud SOC analyst lives on the laptop itself — private, instant, and always available, even offline on a flight or in an air-gapped environment.

This proposal is my own original work and idea.

---

## 1. Application Use Case & Innovation

### The problem
- Over 90% of cyberattacks begin with phishing or social engineering, and the victim is almost always an individual on a personal or work laptop.
- Cloud-based security tools require uploading emails, documents, browsing data, and files to third-party servers. For lawyers, doctors, journalists, financial professionals, and enterprises under DPDP Act / GDPR, this is often unacceptable.
- Existing local antivirus relies on signature databases and cannot reason about *why* something is suspicious or explain it to a non-technical user.

### The SentinelEdge solution
SentinelEdge is a background security companion with four capabilities, each mapped to an on-device AI model:

1. **Phishing & scam analysis** — When the user receives an email, message, or opens a link, an on-device LLM reads the text and classifies intent (phishing, scam, safe), highlighting the manipulation tactics used.
2. **Document & file threat triage** — Suspicious files (macros, scripts, PDFs) are summarized and risk-scored by the LLM, which explains the danger in plain English.
3. **Screen-based threat awareness** — An optional OCR + vision model reads on-screen content (e.g., a fake tech-support popup or a spoofed login page) and warns the user in real time.
4. **Natural-language security assistant** — The user can ask "Is this safe to install?" or "What does this script do?" and get an instant, private answer.

### Why this is innovative
- **Privacy is the product, not an afterthought.** Because everything runs on the NPU, sensitive content (emails, legal docs, medical records) *never leaves the device*. This is only practical because of Snapdragon's dedicated AI silicon.
- **Reasoning, not just detection.** Unlike signature antivirus, SentinelEdge uses a generative LLM to *explain* threats, turning every user into an informed defender.
- **Offline-first.** It protects users in air-gapped, travelling, or low-connectivity situations where cloud security simply doesn't work.

---

## 2. Technical Implementation

### Target hardware
- **Device:** HP OmniBook X / OmniBook Ultra (Snapdragon X Elite / X2 Plus).
- **NPU:** Hexagon NPU delivering 45 TOPS (X Elite) and higher on X2 — enough headroom to run a quantized LLM plus lightweight detection models concurrently.
- **Power envelope:** 15–30 W, enabling always-on background protection without draining the ~28-hour battery.

### Model stack (all from Qualcomm AI Hub / open-source, running on NPU)

| Capability | Model | Source | Runtime |
|---|---|---|---|
| Threat reasoning & explanation | Quantized LLM (e.g., Llama 3.x 8B / Phi-3-mini, INT4/INT8 GGUF) | Qualcomm AI Hub GenieX / Hugging Face GGUF | llama.cpp with Qualcomm backend |
| Text classification (phishing) | Fine-tuned lightweight transformer / the LLM via prompt | Qualcomm AI Hub | Qualcomm AI Engine Direct |
| On-screen text extraction | OCR model | Qualcomm AI Hub (OCR category) | LiteRT |
| Visual UI/threat detection | Quantized YOLOv7 (INT8) | Qualcomm AI Hub | Qualcomm AI Engine Direct |
| Voice command (optional) | Whisper (speech-to-text) | Qualcomm AI Hub | LiteRT |

All models are deployed through **Qualcomm AI Engine Direct** or **LiteRT** so that inference is offloaded to the Hexagon NPU rather than the CPU/GPU, keeping the machine responsive and power-efficient.

### Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    SentinelEdge (local app)               │
│                                                            │
│  ┌────────────┐   ┌─────────────┐   ┌──────────────────┐  │
│  │  Collectors │──▶│  Orchestrator│──▶│  AI Inference    │  │
│  │ (email,     │   │  (risk queue,│   │  Layer (NPU)     │  │
│  │  files,     │   │   dedup,     │   │  • LLM reasoning │  │
│  │  clipboard, │   │   routing)   │   │  • OCR / YOLO    │  │
│  │  screen)    │   │              │   │  • classifier    │  │
│  └────────────┘   └─────────────┘   └──────────────────┘  │
│                          │                    │            │
│                          ▼                    ▼            │
│                 ┌──────────────┐     ┌──────────────────┐  │
│                 │ Local SQLite │     │  Explanation UI  │  │
│                 │ event store  │     │  + alert tray    │  │
│                 └──────────────┘     └──────────────────┘  │
│                                                            │
│   NOTHING leaves the device. No network calls for AI.      │
└──────────────────────────────────────────────────────────┘
```

### Data flow (example: phishing email)
1. Collector detects a newly opened email/message (via local accessibility hooks or a browser extension messaging a local service).
2. Orchestrator strips the text, removes duplicates, and queues it.
3. The quantized LLM on the NPU classifies intent and generates a plain-language explanation + risk score (0–100).
4. If risk > threshold, the tray UI shows a non-intrusive warning with the reasoning.
5. The event is logged to a local encrypted SQLite store for the user's own audit — never uploaded.

### Why the NPU is essential
Running an 8B-parameter LLM on the CPU would be slow and would destroy battery life. Offloading to the 45+ TOPS Hexagon NPU makes real-time, always-on reasoning feasible at low wattage — this use case is *only* practical on a Snapdragon AI PC.

---

## 3. Deployment & Accessibility

### Packaging
- Distributed as a native **Windows on ARM64** application (MSIX installer) optimized for Snapdragon.
- Models bundled as pre-compiled Qualcomm AI Engine Direct context binaries + GGUF, so first-run works fully offline with no downloads.

### Accessibility & usability
- **Zero-config**: works out of the box; no cloud account, no API keys, no subscription.
- **Plain-language explanations** make security understandable for non-technical users (elderly users, students, small-business owners).
- **Low resource footprint**: NPU offload keeps CPU/GPU free, so the user notices no slowdown.
- **Optional voice mode** (Whisper) for hands-free/accessibility use.
- **Inclusive**: because it is offline, it serves users in rural / low-bandwidth regions of India equally well.

### Rollout path
1. **Phase 1 (MVP):** Phishing/text analysis + file triage + explanation UI.
2. **Phase 2:** On-screen OCR/vision detection + voice assistant.
3. **Phase 3:** Enterprise dashboard (still on-device; optional local network sync for IT admins), MDM-friendly deployment for HP fleet devices.

### Business / ecosystem fit
- A natural pre-installed differentiator for HP OmniBook Snapdragon devices ("the laptop that protects your privacy *because* it never phones home").
- Showcases Snapdragon's on-device AI leadership in a high-value, easy-to-understand consumer + enterprise story.

---

## 4. Presentation & Documentation

### Summary of the pitch
SentinelEdge turns every Snapdragon HP PC into a private, offline AI security analyst. It is innovative (privacy-by-architecture + reasoning AI), technically grounded (real Qualcomm AI Hub models on the Hexagon NPU), deployable (native ARM64 app, zero-config, offline), and accessible (plain-language, low-footprint, works without internet).

### Roadmap at a glance
| Milestone | Deliverable |
|---|---|
| Month 1 | NPU inference proof-of-concept (LLM classifies phishing text offline) |
| Month 2 | Collectors + orchestrator + local event store |
| Month 3 | Explanation UI + file triage; MVP demo on OmniBook |
| Month 4+ | OCR/vision, voice, enterprise features |

### Success metrics
- Phishing classification accuracy vs. a labelled test set.
- Average inference latency on NPU (target < 1 s for a short email).
- Battery impact (target < 5% additional drain over a work day).
- Zero outbound network requests for AI (verifiable via packet capture) — the core privacy guarantee.

### Closing
SentinelEdge is a use case that is *impossible to do well in the cloud* and *impossible to do at all without a powerful NPU*. That is exactly why it belongs on a Snapdragon-powered HP PC: it converts the platform's biggest strength — private, efficient, on-device AI — into everyday safety that any user can understand and trust.

---

*Submitted for the Snapdragon® AI Lab Build & Present Challenge. This proposal is the original work and idea of the participant. All models referenced are available via Qualcomm AI Hub or open-source platforms and are intended to run on-device via Qualcomm AI Engine Direct / LiteRT.*
