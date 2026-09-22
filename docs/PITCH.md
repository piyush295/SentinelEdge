# SentinelEdge
### A private, offline AI security companion for Snapdragon HP PCs

Snapdragon AI Lab Build & Present Challenge

---

## The problem

- Attacks start on a person's laptop — a fake email, a bad file, a spoofed popup.
- Cloud security means uploading your private data to analyse it. A dealbreaker for lawyers, doctors, journalists, and anyone under DPDP / GDPR.
- Local antivirus only matches known signatures and never explains anything.

---

## The idea

SentinelEdge runs its AI **entirely on the laptop's NPU**:

- Reads emails, files, and on-screen content
- Scores the risk (0–100)
- **Explains the threat in plain language**
- Nothing ever leaves the device

A security analyst that lives on your laptop — private, instant, offline.

---

## Why it needs Snapdragon

- Quantized LLM + detection models on the **45+ TOPS Hexagon NPU**
- Real-time reasoning inside a **15–30 W** budget — always-on, no battery hit
- 100% local → sensitive content **never leaves the device**
- Works with Wi-Fi off — flights, low-signal areas, air-gapped machines

This use case is impossible in the cloud and impossible without an NPU.

---

## The models (Qualcomm AI Hub / open source)

| Job | Model |
|---|---|
| Reason + explain | Quantized LLM (Llama 3.x / Phi-3-mini, GGUF) |
| Phishing scoring | Small transformer / LLM prompt |
| Read the screen | OCR |
| Visual threats | Quantized YOLOv7 |
| Voice (optional) | Whisper |

Deployed on the NPU via Qualcomm AI Engine Direct / LiteRT.

---

## Already proven

Offline classifier tested on 18,631 real emails (Kaggle):

- **97.10%** accuracy
- **0.9963** ROC-AUC
- **0.22 ms** per email
- Flags an unseen phishing lure at **98.8/100**

Light enough to quantize onto the Hexagon NPU. Code in the repo.

---

## Deployment & reach

- Native Windows-on-ARM64 app, models bundled — works offline on first run
- Zero-config: no account, no API key, no subscription
- Plain-language alerts for non-technical users
- Offline-first = works everywhere, including low-connectivity India

---

## Roadmap

1. **MVP** — phishing/text analysis, file triage, explanation UI
2. **Next** — on-screen OCR/vision, voice assistant
3. **Later** — enterprise view + MDM deployment for HP fleets

---

## SentinelEdge

Takes Snapdragon's biggest strength — private, efficient, on-device AI —
and turns it into everyday safety anyone can understand and trust.

**github.com/piyush295/SentinelEdge**
