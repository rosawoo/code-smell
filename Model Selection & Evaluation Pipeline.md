# Model Selection & Evaluation Pipeline

## Overview

Curated list of open-source, instruction-tuned coding models (1–8B parameters) for code smell detection research. Models were selected for **architectural diversity**, **coding specialization**, and **scalability** across parameter sizes.

All models are instruction-tuned (not base models) and available on Hugging Face.

---

## Selected Models

### 1. Qwen2.5-Coder-Instruct — Alibaba

> Widely regarded as the top open-source code model at 7B. Trained on 5.5T tokens including source code and synthetic data.

| Model | Params | Context | HuggingFace |
| --- | --- | --- | --- |
| Qwen2.5-Coder-1.5B-Instruct | 1.5B | 128K | [Link](https://huggingface.co/Qwen/Qwen2.5-Coder-1.5B-Instruct) |
| Qwen2.5-Coder-3B-Instruct | 3B | 128K | [Link](https://huggingface.co/Qwen/Qwen2.5-Coder-3B-Instruct) |
| Qwen2.5-Coder-7B-Instruct | 7.6B | 128K | [Link](https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct) |

- **Architecture**: Qwen2 Transformer (GQA with 28 Q / 4 KV heads, RoPE, SwiGLU, RMSNorm)
- **Code-Specific**: Yes

---

### 2. DeepSeek-Coder-Instruct — DeepSeek AI

> Two generations: dense v1 models and the V2-Lite MoE with only 2.4B active parameters.

| Model | Params | Active | Context | HuggingFace |
| --- | --- | --- | --- | --- |
| deepseek-coder-1.3b-instruct | 1.3B | 1.3B | 16K | [Link](https://huggingface.co/deepseek-ai/deepseek-coder-1.3b-instruct) |
| deepseek-coder-6.7b-instruct | 6.7B | 6.7B | 16K | [Link](https://huggingface.co/deepseek-ai/deepseek-coder-6.7b-instruct) |
| DeepSeek-Coder-V2-Lite-Instruct | 16B | 2.4B (MoE) | 128K | [Link](https://huggingface.co/deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct) |

- **Architecture**: LLaMA-style (v1) / DeepSeekMoE + Multi-head Latent Attention (V2)
- **Code-Specific**: Yes
- **Note**: V2-Lite is 16B total but only 2.4B active — fits under 8B in effective compute

---

### 3. CodeLlama-Instruct — Meta

> The foundational open-source coding model from Meta, fine-tuned from LLaMA 2.

| Model | Params | Context | HuggingFace |
| --- | --- | --- | --- |
| CodeLlama-7b-Instruct-hf | 7B | 16K | [Link](https://huggingface.co/meta-llama/CodeLlama-7b-Instruct-hf) |

- **Architecture**: LLaMA 2 Transformer
- **Code-Specific**: Yes

---

### 4. Mamba-Codestral — Mistral AI

> The only non-Transformer model in this list. Uses Mamba2 State Space Model architecture.

| Model | Params | Context | HuggingFace |
| --- | --- | --- | --- |
| Mamba-Codestral-7B-v0.1 | 7B | Theoretically unlimited (SSM) | [Link](https://huggingface.co/mistralai/Mamba-Codestral-7B-v0.1) |

- **Architecture**: Mamba2 (State Space Model — fundamentally non-Transformer)
- **Code-Specific**: Yes
- **Benchmarks**: HumanEval 75.0%, MBPP 68.5%

---

### 5. StarCoder2-Instruct — BigCode / Community

> Code-first architecture trained on The Stack v2. Community instruction-tuned variants.

| Model | Params | Context | HuggingFace |
| --- | --- | --- | --- |
| starcoder2-3b-instruct | 3B | 16K | [Link](https://huggingface.co/TechxGenus/starcoder2-3b-instruct) |
| starcoder2-7b-instruct | 7B | 16K | [Link](https://huggingface.co/TechxGenus/starcoder2-7b-instruct) |

- **Architecture**: StarCoder2 Transformer (multi-query attention)
- **Code-Specific**: Yes
- **Benchmarks**: 7B variant achieves HumanEval 73.2% pass@1

---

### 6. Yi-Coder-Chat — 01.AI

> First sub-10B model to pass 20% on LiveCodeBench. Supports 52 programming languages.

| Model | Params | Context | HuggingFace |
| --- | --- | --- | --- |
| Yi-Coder-1.5B-Chat | 1.5B | 128K | [Link](https://huggingface.co/01-ai/Yi-Coder-1.5B-Chat) |
| Yi-Coder-9B-Chat | 9B | 128K | [Link](https://huggingface.co/01-ai/Yi-Coder-9B-Chat) |

- **Architecture**: Yi/LLaMA-style Transformer
- **Code-Specific**: Yes
- **Note**: 9B is slightly above 8B ceiling but is the smallest variant above 1.5B in this family

---

### 7. Phi-4-mini-Instruct — Microsoft

> General-purpose but competitive with 7–9B coding models at just 3.8B parameters.

| Model | Params | Context | HuggingFace |
| --- | --- | --- | --- |
| Phi-4-mini-instruct | 3.8B | 128K | [Link](https://huggingface.co/microsoft/Phi-4-mini-instruct) |

- **Architecture**: Phi Transformer (dense, synthetic-data-heavy training, 200K vocabulary)
- **Code-Specific**: No (general-purpose with strong coding ability)

---

### 8. Granite Code-Instruct — IBM

> Trained exclusively on permissively licensed data. Apache 2.0 license.

| Model | Params | Context | HuggingFace |
| --- | --- | --- | --- |
| granite-3b-code-instruct-128k | 3B | 128K | [Link](https://huggingface.co/ibm-granite/granite-3b-code-instruct-128k) |
| granite-8b-code-instruct-128k | 8B | 128K | [Link](https://huggingface.co/ibm-granite/granite-8b-code-instruct-128k) |

- **Architecture**: LLaMA-based Transformer
- **Code-Specific**: Yes
- **License**: Apache 2.0

---

## Full Comparison Table

| # | Model | Params | Active Params | Architecture | Code-Specific | Context |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Qwen2.5-Coder-1.5B-Instruct | 1.5B | 1.5B (dense) | Qwen2 Transformer | Yes | 128K |
| 2 | Qwen2.5-Coder-3B-Instruct | 3B | 3B (dense) | Qwen2 Transformer | Yes | 128K |
| 3 | Qwen2.5-Coder-7B-Instruct | 7.6B | 7.6B (dense) | Qwen2 Transformer | Yes | 128K |
| 4 | deepseek-coder-1.3b-instruct | 1.3B | 1.3B (dense) | LLaMA-style | Yes | 16K |
| 5 | deepseek-coder-6.7b-instruct | 6.7B | 6.7B (dense) | LLaMA-style | Yes | 16K |
| 6 | DeepSeek-Coder-V2-Lite-Instruct | 16B | 2.4B (MoE) | DeepSeekMoE + MLA | Yes | 128K |
| 7 | CodeLlama-7b-Instruct-hf | 7B | 7B (dense) | LLaMA 2 | Yes | 16K |
| 8 | Mamba-Codestral-7B-v0.1 | 7B | 7B (SSM) | Mamba2 (SSM) | Yes | Unlimited |
| 9 | starcoder2-3b-instruct | 3B | 3B (dense) | StarCoder2 | Yes | 16K |
| 10 | starcoder2-7b-instruct | 7B | 7B (dense) | StarCoder2 | Yes | 16K |
| 11 | Yi-Coder-1.5B-Chat | 1.5B | 1.5B (dense) | Yi Transformer | Yes | 128K |
| 12 | Yi-Coder-9B-Chat | 9B | 9B (dense) | Yi Transformer | Yes | 128K |
| 13 | Phi-4-mini-instruct | 3.8B | 3.8B (dense) | Phi Transformer | No | 128K |
| 14 | granite-3b-code-instruct-128k | 3B | 3B (dense) | LLaMA-based | Yes | 128K |
| 15 | granite-8b-code-instruct-128k | 8B | 8B (dense) | LLaMA-based | Yes | 128K |

---

## Architectural Diversity

**7 distinct architecture families** covered:

1. **Qwen2 Transformer** — Qwen2.5-Coder series
2. **LLaMA / LLaMA 2** — DeepSeek-Coder v1, CodeLlama, Granite Code
3. **DeepSeekMoE + MLA** — DeepSeek-Coder-V2-Lite (Mixture of Experts with Multi-head Latent Attention)
4. **Mamba2 (State Space Model)** — Mamba-Codestral (non-Transformer)
5. **StarCoder2** — Code-first architecture with multi-query attention
6. **Yi** — Yi-Coder series (LLaMA-derived, independently trained)
7. **Phi** — Microsoft dense Transformer with synthetic-data-heavy training

---

## Standardized Inference Settings

To ensure fair comparison across all models:

| Parameter | Value |
| --- | --- |
| Temperature | 0.0 (greedy) for deterministic evaluation |
| Top-p | 1.0 |
| Max new tokens | 2048 |
| Repetition penalty | 1.0 (none) |
| System prompt | Standardized across all models |
| Quantization | None (FP16/BF16) for accuracy; GPTQ/AWQ for resource-constrained runs |
| Batch size | 1 (for consistency) |

---

## Recommendations

| Use Case | Recommended Model |
| --- | --- |
| Best overall quality (7B) | Qwen2.5-Coder-7B-Instruct |
| Best efficiency (low active params) | DeepSeek-Coder-V2-Lite-Instruct (2.4B active) |
| Best tiny model (~1.5B) | Qwen2.5-Coder-1.5B-Instruct |
| Most permissive license | granite-8b-code-instruct-128k (Apache 2.0) |
| Unique architecture (non-Transformer) | Mamba-Codestral-7B-v0.1 |
