# 📊 LLM Quotas, Rate Limits & Multi-Model Fallback Architecture
## Repository: `guardrails-edge-infra`

This document details the baseline data and FinOps decision framework used to select the primary and fallback LLM models for NVIDIA NeMo Guardrails under strict API rate limits and free tier constraints.

---

## 🎯 1. Engineering Baseline: Gemini Free Tier Model Quotas & Limits

To ensure our AI Banking Agent remains responsive without suffering from HTTP 429 (`Too Many Requests`) or service exhaustion, we benchmarked all available Google Gemini Free Tier models based on **RPM (Requests Per Minute)**, **TPM (Tokens Per Minute)**, and **RPD (Requests Per Day)**:

| Model | Category | RPM (Free/Paid) | TPM (Free/Paid) | RPD (Free) | Google Grounding (Free RPD) | Staff Decision & Priority |
|---|---|---|---|---|---|---|
| **Gemini 2.5 Flash Lite** | Text Output Models | **0 / 10** | **0 / 250K** | **20** | **500** | ⚡ **High Throughput Baseline** |
| **Gemini 3.1 Flash Lite** | Text Output Models | **0 / 15** | **0 / 250K** | **500** | **500** | 🏆 **Primary Guardrail Engine** (500 RPD) |
| **Gemini 2.5 Flash** | Text Output Models | **0 / 5** | **0 / 250K** | **20** | **500** | 🛡️ **Secondary Fallback Engine** |
| **Gemini 3.5 Flash Lite** | Text Output Models | **0 / 15** | **0 / 250K** | **500** | **500** | 🛡️ **Tertiary Fallback Engine** |
| Gemini 3.6 Flash | Text Output Models | 0 / 5 | 0 / 250K | 20 | 0 (Unavailable) | Restricted Daily Quota (20 RPD) |
| Gemini 3.5 Flash | Text Output Models | 0 / 5 | 0 / 250K | 20 | 0 (Unavailable) | Restricted Daily Quota (20 RPD) |
| Gemini 3 Flash | Text Output Models | 0 / 5 | 0 / 250K | 20 | 0 (Unavailable) | Restricted Daily Quota (20 RPD) |
| Gemini 2.5 Flash TTS | Generative Multimodal | 0 / 3 | 0 / 10K | 10 | - | Multimodal Out of Scope |
| Gemini 3.1 Flash TTS | Generative Multimodal | 0 / 3 | 0 / 10K | 10 | 500 | Multimodal Out of Scope |
| Gemini Embedding 1 | Embeddings | 0 / 100 | 0 / 30K | 1K | - | Embedding Utility |
| Gemini Embedding 2 | Embeddings | 0 / 100 | 0 / 30K | 1K | - | Embedding Utility |
| Gemma 4 26B | Open Model | 0 / 30 | 0 / 16K | 14.4K | - | High Latency Open Weight |
| Gemma 4 31B | Open Model | 0 / 30 | 0 / 16K | 14.4K | - | High Latency Open Weight |
| Imagen 4 Generate | Generative Multimodal | - | - | 25 | - | Image Generation Out of Scope |

---

## 🏛️ 2. Architectural Selection Strategy & Multi-Model Resilience

### ❓ Why `Flash Lite` / `Flash` models over Heavy Reasoning Models?

1. **High Daily Request Volume (500 RPD vs 20 RPD)**:
   Models like `Gemini 3.1 Flash Lite` and `Gemini 3.5 Flash Lite` provide **500 Requests Per Day** in the Free Tier, compared to heavy models capped at 20 RPD. This guarantees that Guardrail checks can execute hundreds of times per day without quota exhaustion.

2. **Ultra-Low Latency Inference (<15ms Guardrail Overhead)**:
   Guardrail evaluations (Input Topic Check, PII Masking, Execution Rail Audit) require sub-second responses. `Flash Lite` models return binary decisions in milliseconds.

---

## 🛡️ 3. NVIDIA NeMo Guardrails Multi-Model Fallback Chain

When configured in `config.yml`, NeMo automatically fails over through the defined priority matrix if an upstream API endpoint returns `429 Too Many Requests` or `503 Service Unavailable`:

```yaml
models:
  - type: main
    engine: google
    model: gemini-1.5-flash
    parameters:
      temperature: 0.1
      max_retries: 3

  - type: main_fallback
    engine: google
    model: gemini-2.0-flash
    parameters:
      temperature: 0.1
      max_retries: 3
```
