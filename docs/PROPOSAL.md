# SentinelEdge — An Offline AI Security Companion for Snapdragon HP PCs

**Snapdragon® AI Lab Build & Present Challenge — Proposal**

---

## Why I'm building this

I've spent a good part of my time in cybersecurity — chasing bugs, studying how attacks actually land on people, and watching the same story repeat: the attack doesn't start at some firewall, it starts on someone's laptop, with a message that looks just real enough. A fake "your account is suspended" email. A document with a macro. A support popup that isn't support.

The tools meant to stop this have a quiet problem. Most of the good ones send your data — your emails, your files, your browsing — off to a server somewhere to be analysed. For a lot of people that's a dealbreaker: lawyers, doctors, journalists, anyone handling something they can't legally or ethically ship to a third party. And the tools that stay local are usually just signature-matching antivirus that can't tell you *why* something is dangerous.

SentinelEdge is my answer to that. It's a security companion that runs its AI entirely on the laptop's NPU. Nothing goes to the cloud. It reads a suspicious email or file, decides how risky it is, and — this is the part I care about — explains it to you in plain language, the way a colleague who knows security would. On a Snapdragon HP PC this is finally practical, because the chip has the AI horsepower to do it locally without killing the battery.

This proposal is my own idea and work.

---

## 1. Application Use Case & Innovation

**The problem, plainly.** Most breaches begin with phishing or social engineering, and the target is almost always a person at a keyboard. Cloud security means uploading private content to analyse it — a non-starter for anyone under DPDP Act or GDPR obligations, or anyone who just doesn't want their inbox living on someone else's server. Local antivirus, meanwhile, matches known signatures and stays silent about anything new, and it can't teach the user anything.

**What SentinelEdge does.** It sits quietly in the background and helps with four things, each backed by a model running on the device:

- **Phishing and scam checks.** When an email or message comes in, or a link gets opened, an on-device language model reads it and calls it: phishing, scam, or safe — and points out the manipulation being used ("this is creating false urgency and asking for your password").
- **File and document triage.** Suspicious files — macros, scripts, odd PDFs — get summarised and risk-scored, with a human-readable explanation of what's actually dangerous about them.
- **On-screen awareness.** Optionally, an OCR and vision model can catch things that live on the screen rather than in a file — a spoofed login page, a fake tech-support window — and warn you in the moment.
- **Just ask it.** "Is this safe to install?" "What does this script do?" You get a private answer, instantly, without googling and landing on another sketchy page.

**Why I think it's genuinely new.** The privacy here isn't a marketing checkbox bolted on afterwards — it's the whole architecture. Because every model runs on the NPU, your sensitive content never leaves the machine. That's only realistic because Snapdragon ships real AI silicon. On top of that, it reasons and explains instead of just flagging, which slowly turns a normal user into someone who can spot the next attack themselves. And it works with the Wi-Fi off — on a flight, in a village with bad signal, on an air-gapped machine — where cloud security is simply dead weight.

---

## 2. Technical Implementation

**What it runs on.** HP OmniBook X / OmniBook Ultra, on Snapdragon X Elite or X2 Plus. The Hexagon NPU gives 45 TOPS on the X Elite and more on X2 — enough to keep a quantized language model resident alongside a couple of smaller detection models. And it does this inside a 15–30 W power budget, which is the only reason "always-on background protection" doesn't mean "dead battery by lunch."

**The models (all from Qualcomm AI Hub or open source, all on-device):**

| What it does | Model | Where it runs |
|---|---|---|
| Reasoning + explaining threats | Quantized LLM (Llama 3.x 8B / Phi-3-mini, INT4/INT8 GGUF) | llama.cpp with the Qualcomm backend / GenieX |
| Fast phishing text scoring | Small transformer / the LLM via prompt | Qualcomm AI Engine Direct |
| Reading text off the screen | OCR | LiteRT |
| Spotting visual threats | Quantized YOLOv7 (INT8) | Qualcomm AI Engine Direct |
| Optional voice control | Whisper | LiteRT |

Everything is pushed onto the Hexagon NPU through Qualcomm AI Engine Direct or LiteRT, so the CPU and GPU stay free and the laptop stays snappy.

**How it's wired together:**

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
│   Nothing leaves the device. No network calls for the AI.  │
└──────────────────────────────────────────────────────────┘
```

**Walking through one phishing email:** a collector notices a message got opened (through local accessibility hooks, or a browser extension talking to a local service). The orchestrator pulls out the text, drops duplicates, and queues it. The quantized LLM on the NPU scores the intent and writes a short explanation plus a 0–100 risk number. If it crosses the threshold, a small tray warning pops up with the reasoning behind it. The event gets logged to a local, encrypted SQLite file so you have your own history — and that file never gets uploaded anywhere.

**Why the NPU isn't optional.** Try running an 8B-parameter model on the CPU and you'll feel the machine crawl and watch the battery drain. Offloading it to the 45+ TOPS Hexagon NPU is what makes real-time, always-on reasoning possible at low power. This use case basically doesn't exist without a chip like this.

**I already built and tested the detection core.** Rather than just claim it works, I built the offline classifier and ran it on a real public dataset (Kaggle `subhajournal/phishingemails`, 18,631 emails). The code and steps to reproduce are in the repo under `prototype/`.

| Metric | Result |
|---|---|
| Test accuracy | **97.10%** |
| ROC-AUC | **0.9963** |
| Inference latency | **0.22 ms / email** (CPU only) |
| Model | TF-IDF (1–2 gram) + Logistic Regression |

Thrown a phishing lure it had never seen — an "urgent, your account is suspended, verify your password" message — it scored it **98.8/100**. The point of keeping this model tiny and CPU-only is to show the workload is light enough to quantize onto the Hexagon NPU and run in real time, with the on-device LLM layered on top to do the explaining.

---

## 3. Deployment & Accessibility

**How it ships.** A native Windows-on-ARM64 app (MSIX installer) built for Snapdragon. The models come bundled as pre-compiled Qualcomm AI Engine Direct binaries plus GGUF, so the very first run works offline with nothing to download.

**Who can actually use it.** This part matters to me. It's zero-config — no account, no API key, no subscription. The explanations are in plain language, so it's genuinely useful to people who aren't technical: an elderly parent, a student, someone running a small shop. Because the heavy lifting is on the NPU, the CPU and GPU stay free and nobody notices a slowdown. There's an optional voice mode (Whisper) for hands-free and accessibility use. And since the whole thing is offline, it works exactly as well for someone on a weak rural connection as it does in a city — which, in India especially, is the difference between a tool that helps everyone and one that helps a few.

**Rolling it out:**
1. *MVP:* phishing/text analysis, file triage, and the explanation UI.
2. *Next:* on-screen OCR/vision detection and the voice assistant.
3. *Later:* an enterprise view (still on-device; optional local-network sync for IT admins) and MDM-friendly deployment across HP fleet devices.

**Where it fits.** Honestly, this feels like a natural thing to pre-install on Snapdragon HP OmniBooks — "the laptop that protects your privacy *because* it never phones home." It's a clear, everyday way to show off what on-device AI is actually good for.

---

## 4. Presentation & Documentation

**The pitch in a breath:** SentinelEdge turns a Snapdragon HP PC into a private, offline AI security analyst. It's new in a way that matters (privacy baked into the architecture, plus AI that explains itself), it's grounded in real Qualcomm AI Hub models on the Hexagon NPU, it's deployable as a plain native app that works offline out of the box, and it's built to be understood by ordinary people.

**Rough timeline:**

| When | What's done |
|---|---|
| Month 1 | NPU inference proof — LLM classifies phishing text, fully offline |
| Month 2 | Collectors + orchestrator + local event store |
| Month 3 | Explanation UI + file triage; MVP demo on an OmniBook |
| Month 4+ | OCR/vision, voice, enterprise features |

**How I'll know it's working:**
- Phishing accuracy against a labelled test set (already at 97% in the PoC).
- Inference latency on the NPU — aiming under a second for a short email.
- Battery impact — aiming for under 5% extra drain across a work day.
- Zero outbound network calls for the AI, which you can verify with a packet capture. That last one is the whole promise.

**To close.** The reason I picked this idea is that it's something you genuinely can't do well in the cloud, and can't do at all without a real NPU. That's exactly why it belongs on a Snapdragon HP PC — it takes the platform's biggest strength, private and efficient on-device AI, and turns it into everyday safety that a normal person can actually understand and trust.

---

*Submitted for the Snapdragon® AI Lab Build & Present Challenge. This is my own idea and work. Every model mentioned is available through Qualcomm AI Hub or open-source platforms and is meant to run on-device via Qualcomm AI Engine Direct / LiteRT.*
