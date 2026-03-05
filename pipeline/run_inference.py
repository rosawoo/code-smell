#!/usr/bin/env python3
"""
Inference Pipeline - Run all coding models on the code smell dataset.

Usage:
    # Run all models
    python -m pipeline.run_inference

    # Run a specific model
    python -m pipeline.run_inference --model qwen2.5-coder-7b

    # Run with quantization for limited VRAM
    python -m pipeline.run_inference --quantize 4bit

    # Resume from where you left off
    python -m pipeline.run_inference --model qwen2.5-coder-7b --resume
"""

import argparse
import json
import os
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from pipeline.model_registry import MODELS, INFERENCE_CONFIG, SYSTEM_PROMPT, get_model_by_id

OUTPUT_DIR = PROJECT_ROOT / "outputs"
DATASET_PATH = PROJECT_ROOT / "dataset" / "prompts_core.json"


def load_dataset() -> list:
    with open(DATASET_PATH) as f:
        return json.load(f)


def get_output_path(model_id: str) -> Path:
    model_dir = OUTPUT_DIR / model_id
    model_dir.mkdir(parents=True, exist_ok=True)
    return model_dir


def load_completed_ids(model_id: str) -> set:
    """Load IDs of already-completed prompts for resume support."""
    results_file = get_output_path(model_id) / "results.jsonl"
    completed = set()
    if results_file.exists():
        with open(results_file) as f:
            for line in f:
                try:
                    record = json.loads(line)
                    completed.add(record["prompt_id"])
                except (json.JSONDecodeError, KeyError):
                    continue
    return completed


def load_model(model_config: dict, quantize: str = None):
    """Load a model and tokenizer from HuggingFace."""
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    model_id = model_config["hf_model_id"]
    print(f"Loading model: {model_id}")

    tokenizer = AutoTokenizer.from_pretrained(
        model_id,
        trust_remote_code=True,
        padding_side="left"
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    load_kwargs = {
        "trust_remote_code": True,
        "device_map": "auto",
    }

    if quantize == "4bit":
        from transformers import BitsAndBytesConfig
        load_kwargs["quantization_config"] = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
        )
    elif quantize == "8bit":
        from transformers import BitsAndBytesConfig
        load_kwargs["quantization_config"] = BitsAndBytesConfig(load_in_8bit=True)
    else:
        load_kwargs["torch_dtype"] = torch.bfloat16

    model = AutoModelForCausalLM.from_pretrained(model_id, **load_kwargs)
    model.eval()

    print(f"Model loaded: {model_id} on {model.device}")
    return model, tokenizer


def build_messages(prompt_text: str) -> list:
    """Build chat messages in standard format."""
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt_text},
    ]


def generate_response(model, tokenizer, prompt_text: str, model_config: dict) -> dict:
    """Generate a single response from the model."""
    import torch
    messages = build_messages(prompt_text)

    # Use the tokenizer's chat template if available
    if hasattr(tokenizer, "apply_chat_template"):
        input_text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
    else:
        input_text = f"### System:\n{SYSTEM_PROMPT}\n\n### User:\n{prompt_text}\n\n### Assistant:\n"

    inputs = tokenizer(input_text, return_tensors="pt").to(model.device)
    input_length = inputs["input_ids"].shape[1]

    start_time = time.time()

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=INFERENCE_CONFIG["max_new_tokens"],
            temperature=INFERENCE_CONFIG["temperature"],
            top_p=INFERENCE_CONFIG["top_p"],
            repetition_penalty=INFERENCE_CONFIG["repetition_penalty"],
            do_sample=INFERENCE_CONFIG["do_sample"],
            pad_token_id=tokenizer.pad_token_id,
        )

    elapsed = time.time() - start_time
    new_tokens = outputs[0][input_length:]
    output_length = len(new_tokens)
    response_text = tokenizer.decode(new_tokens, skip_special_tokens=True)

    return {
        "response": response_text,
        "input_tokens": input_length,
        "output_tokens": output_length,
        "generation_time_s": round(elapsed, 2),
        "tokens_per_second": round(output_length / elapsed, 2) if elapsed > 0 else 0,
    }


def extract_python_code(response: str) -> str:
    """Extract Python code from a model response, handling markdown fences."""
    # Try to extract from ```python ... ``` blocks
    import re
    pattern = r'```(?:python)?\s*\n(.*?)```'
    matches = re.findall(pattern, response, re.DOTALL)
    if matches:
        return "\n\n".join(matches)
    # If no fenced blocks, return the full response
    return response


def run_model(model_id: str, quantize: str = None, resume: bool = False):
    """Run inference for a single model across the full dataset."""
    import torch
    model_config = get_model_by_id(model_id)
    prompts = load_dataset()
    output_path = get_output_path(model_id)

    # Resume support
    completed_ids = load_completed_ids(model_id) if resume else set()
    if completed_ids:
        print(f"Resuming: {len(completed_ids)} prompts already completed")

    remaining = [p for p in prompts if p["id"] not in completed_ids]
    print(f"Model: {model_config['hf_model_id']}")
    print(f"Prompts to process: {len(remaining)} / {len(prompts)}")

    if not remaining:
        print("All prompts already completed!")
        return

    # Skip Mamba models (require special packages)
    if model_config.get("special_requirements"):
        reqs = model_config["special_requirements"]
        for req in reqs:
            try:
                __import__(req.replace("-", "_"))
            except ImportError:
                print(f"WARNING: {model_id} requires '{req}'. Install it first.")
                print(f"  pip install {req}")
                return

    # Load model
    model, tokenizer = load_model(model_config, quantize)

    # Save model metadata
    metadata = {
        "model_id": model_id,
        "hf_model_id": model_config["hf_model_id"],
        "family": model_config["family"],
        "architecture": model_config["architecture"],
        "params": model_config["params"],
        "params_active": model_config["params_active"],
        "dense_or_moe": model_config["dense_or_moe"],
        "code_specific": model_config["code_specific"],
        "inference_config": INFERENCE_CONFIG,
        "quantization": quantize,
        "system_prompt": SYSTEM_PROMPT,
        "torch_dtype": str(model.dtype) if hasattr(model, 'dtype') else INFERENCE_CONFIG["dtype"],
        "device": str(model.device),
        "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu",
        "run_started": datetime.now().isoformat(),
        "total_prompts": len(prompts),
    }
    with open(output_path / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    # Run inference
    results_file = output_path / "results.jsonl"
    errors = []

    for i, prompt in enumerate(remaining):
        prompt_id = prompt["id"]
        print(f"  [{i+1}/{len(remaining)}] {prompt_id} ... ", end="", flush=True)

        try:
            result = generate_response(model, tokenizer, prompt["prompt"], model_config)
            code = extract_python_code(result["response"])

            record = {
                "prompt_id": prompt_id,
                "model_id": model_id,
                "prompt": prompt["prompt"],
                "code_smells_target": prompt["code_smells"],
                "complexity": prompt["complexity"],
                "domain": prompt["domain"],
                "raw_response": result["response"],
                "extracted_code": code,
                "input_tokens": result["input_tokens"],
                "output_tokens": result["output_tokens"],
                "generation_time_s": result["generation_time_s"],
                "tokens_per_second": result["tokens_per_second"],
                "timestamp": datetime.now().isoformat(),
                "error": None,
            }

            # Append to JSONL
            with open(results_file, "a") as f:
                f.write(json.dumps(record) + "\n")

            # Save individual code file for detector
            code_dir = output_path / "code"
            code_dir.mkdir(exist_ok=True)
            with open(code_dir / f"{prompt_id}.py", "w") as f:
                f.write(code)

            print(f"OK ({result['output_tokens']} tokens, {result['generation_time_s']}s)")

        except Exception as e:
            error_msg = f"{type(e).__name__}: {e}"
            print(f"ERROR: {error_msg}")
            errors.append({"prompt_id": prompt_id, "error": error_msg})

            record = {
                "prompt_id": prompt_id,
                "model_id": model_id,
                "prompt": prompt["prompt"],
                "code_smells_target": prompt["code_smells"],
                "complexity": prompt["complexity"],
                "domain": prompt["domain"],
                "raw_response": None,
                "extracted_code": None,
                "input_tokens": 0,
                "output_tokens": 0,
                "generation_time_s": 0,
                "tokens_per_second": 0,
                "timestamp": datetime.now().isoformat(),
                "error": error_msg,
            }
            with open(results_file, "a") as f:
                f.write(json.dumps(record) + "\n")

    # Save run summary
    summary = {
        "model_id": model_id,
        "total_prompts": len(prompts),
        "completed": len(prompts) - len(remaining) + len(remaining) - len(errors),
        "errors": len(errors),
        "error_details": errors,
        "run_finished": datetime.now().isoformat(),
    }
    with open(output_path / "run_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\nDone: {model_id}")
    print(f"  Completed: {summary['completed']}, Errors: {summary['errors']}")
    print(f"  Results saved to: {output_path}")

    # Free GPU memory
    del model, tokenizer
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


def main():
    parser = argparse.ArgumentParser(description="Run code smell inference pipeline")
    parser.add_argument("--model", type=str, help="Run a specific model ID (default: all)")
    parser.add_argument("--quantize", choices=["4bit", "8bit"], help="Quantize models to reduce VRAM")
    parser.add_argument("--resume", action="store_true", help="Resume from completed prompts")
    parser.add_argument("--list-models", action="store_true", help="List all available models")
    args = parser.parse_args()

    if args.list_models:
        print("Available models:")
        for m in MODELS:
            print(f"  {m['id']:30s} {m['params']:>6s} active  {m['hf_model_id']}")
        return

    if args.model:
        run_model(args.model, quantize=args.quantize, resume=args.resume)
    else:
        # Run all models sequentially
        for m in MODELS:
            print(f"\n{'='*60}")
            print(f"Starting: {m['id']}")
            print(f"{'='*60}\n")
            try:
                run_model(m["id"], quantize=args.quantize, resume=args.resume)
            except Exception as e:
                print(f"FAILED: {m['id']} — {e}")
                traceback.print_exc()
                continue


if __name__ == "__main__":
    main()
