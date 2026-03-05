#!/usr/bin/env python3
"""
Detection Pipeline - Run the code smell detector on all model outputs.

Usage:
    # Detect smells across all model outputs
    python -m pipeline.run_detection

    # Detect for a specific model
    python -m pipeline.run_detection --model qwen2.5-coder-7b
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from detector.smell_detector import detect_all_smells
from pipeline.model_registry import MODELS

OUTPUT_DIR = PROJECT_ROOT / "outputs"
DATASET_PATH = PROJECT_ROOT / "dataset" / "prompts_core.json"


def load_dataset() -> dict:
    with open(DATASET_PATH) as f:
        prompts = json.load(f)
    return {p["id"]: p for p in prompts}


def run_detection_for_model(model_id: str, prompts: dict):
    """Run code smell detection on all outputs from a single model."""
    model_dir = OUTPUT_DIR / model_id
    code_dir = model_dir / "code"

    if not code_dir.exists():
        print(f"  No code directory found at {code_dir}, skipping.")
        return

    code_files = sorted(code_dir.glob("*.py"))
    if not code_files:
        print(f"  No .py files found in {code_dir}, skipping.")
        return

    print(f"  Analyzing {len(code_files)} code files...")

    all_detections = []
    summary_stats = {
        "model_id": model_id,
        "total_files": len(code_files),
        "files_with_smells": 0,
        "total_smells_detected": 0,
        "smell_type_counts": {},
        "by_complexity": {"basic": 0, "intermediate": 0, "advanced": 0},
        "by_target_smell": {},
        "detection_accuracy": {
            "true_positive": 0,   # Target smell detected
            "total_targets": 0,   # Total target smells across prompts
        },
    }

    for code_file in code_files:
        prompt_id = code_file.stem
        prompt_info = prompts.get(prompt_id, {})
        target_smells = prompt_info.get("code_smells", [])
        complexity = prompt_info.get("complexity", "unknown")

        try:
            code = code_file.read_text(encoding="utf-8")
        except Exception as e:
            print(f"    Error reading {code_file}: {e}")
            continue

        if not code.strip():
            continue

        # Run detection
        detection = detect_all_smells(code)

        record = {
            "prompt_id": prompt_id,
            "model_id": model_id,
            "target_smells": target_smells,
            "complexity": complexity,
            "domain": prompt_info.get("domain", "unknown"),
            "smells_detected": detection["smell_types_detected"],
            "total_smells": detection["total_smells"],
            "smell_details": detection["smells"],
            "code_length_lines": len(code.splitlines()),
        }
        all_detections.append(record)

        # Update summary stats
        if detection["total_smells"] > 0:
            summary_stats["files_with_smells"] += 1
        summary_stats["total_smells_detected"] += detection["total_smells"]

        for smell in detection["smell_types_detected"]:
            summary_stats["smell_type_counts"][smell] = \
                summary_stats["smell_type_counts"].get(smell, 0) + 1

        summary_stats["by_complexity"][complexity] = \
            summary_stats["by_complexity"].get(complexity, 0) + detection["total_smells"]

        # Check detection accuracy (did we detect the target smell?)
        for target in target_smells:
            summary_stats["detection_accuracy"]["total_targets"] += 1
            summary_stats["by_target_smell"].setdefault(target, {"targeted": 0, "detected": 0})
            summary_stats["by_target_smell"][target]["targeted"] += 1

            # Fuzzy match: check if any detected smell name contains the target
            target_lower = target.lower()
            detected_lower = [s.lower() for s in detection["smell_types_detected"]]
            if any(target_lower in d or d in target_lower for d in detected_lower):
                summary_stats["detection_accuracy"]["true_positive"] += 1
                summary_stats["by_target_smell"][target]["detected"] += 1

    # Save detailed detections
    detection_file = model_dir / "detections.jsonl"
    with open(detection_file, "w") as f:
        for record in all_detections:
            f.write(json.dumps(record) + "\n")

    # Save summary
    summary_stats["timestamp"] = datetime.now().isoformat()
    total_targets = summary_stats["detection_accuracy"]["total_targets"]
    true_pos = summary_stats["detection_accuracy"]["true_positive"]
    summary_stats["detection_accuracy"]["accuracy_pct"] = \
        round(true_pos / total_targets * 100, 2) if total_targets > 0 else 0

    with open(model_dir / "detection_summary.json", "w") as f:
        json.dump(summary_stats, f, indent=2)

    print(f"  Files with smells: {summary_stats['files_with_smells']}/{len(code_files)}")
    print(f"  Total smells found: {summary_stats['total_smells_detected']}")
    print(f"  Detection accuracy (target match): {summary_stats['detection_accuracy']['accuracy_pct']}%")
    print(f"  Saved to: {detection_file}")


def generate_comparative_report():
    """Generate a cross-model comparison report."""
    print("\nGenerating comparative report...")

    model_summaries = []
    for model_dir in sorted(OUTPUT_DIR.iterdir()):
        summary_file = model_dir / "detection_summary.json"
        if summary_file.exists():
            with open(summary_file) as f:
                model_summaries.append(json.load(f))

    if not model_summaries:
        print("  No detection summaries found.")
        return

    report = {
        "generated": datetime.now().isoformat(),
        "models_compared": len(model_summaries),
        "comparison": [],
    }

    for s in model_summaries:
        report["comparison"].append({
            "model_id": s["model_id"],
            "files_analyzed": s["total_files"],
            "files_with_smells": s["files_with_smells"],
            "smell_rate_pct": round(s["files_with_smells"] / max(s["total_files"], 1) * 100, 2),
            "total_smells": s["total_smells_detected"],
            "target_accuracy_pct": s["detection_accuracy"]["accuracy_pct"],
            "top_smells": dict(sorted(
                s["smell_type_counts"].items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]),
        })

    # Sort by smell rate (higher = more smells generated = better for our dataset purpose)
    report["comparison"].sort(key=lambda x: x["total_smells"], reverse=True)

    with open(OUTPUT_DIR / "comparative_report.json", "w") as f:
        json.dump(report, f, indent=2)

    # Print table
    print(f"\n{'Model':<30} {'Files':>6} {'Smells':>7} {'Rate%':>7} {'Accuracy%':>10}")
    print("-" * 65)
    for r in report["comparison"]:
        print(f"{r['model_id']:<30} {r['files_analyzed']:>6} {r['total_smells']:>7} "
              f"{r['smell_rate_pct']:>6.1f}% {r['target_accuracy_pct']:>9.1f}%")

    print(f"\nReport saved to: {OUTPUT_DIR / 'comparative_report.json'}")


def main():
    parser = argparse.ArgumentParser(description="Run code smell detection on model outputs")
    parser.add_argument("--model", type=str, help="Analyze a specific model (default: all)")
    args = parser.parse_args()

    prompts = load_dataset()

    if args.model:
        print(f"Running detection for: {args.model}")
        run_detection_for_model(args.model, prompts)
    else:
        for model_dir in sorted(OUTPUT_DIR.iterdir()):
            if model_dir.is_dir() and (model_dir / "code").exists():
                print(f"\nDetection: {model_dir.name}")
                run_detection_for_model(model_dir.name, prompts)

    generate_comparative_report()


if __name__ == "__main__":
    main()
