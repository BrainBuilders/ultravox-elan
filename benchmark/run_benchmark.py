#!/usr/bin/env python3
"""
USV Detection Benchmark

Compares three detection methods against human ground truth annotations
from the USVSEG benchmark dataset (Tachibana et al., 2020):

  1. UltraVox Threshold - amplitude-based detection
  2. UltraVox USVSEG   - spectral-saliency detection (UltraVox implementation)
  3. Original USVSEG    - reference USVSEG algorithm (Tachibana et al., 2020)

Ground truth: human expert onset/offset annotations from Zenodo 3428024.

Usage:
    python benchmark/run_benchmark.py [--data-dir PATH] [--detector PATH]
"""

import argparse
import csv
import math
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DATASETS = {
    "rat_pleasant": {
        "description": "Rat 50-kHz pleasant calls (Wistar)",
        "freq_range": (40000, 80000),
        "dur_range": (0.010, 0.500),
        "usvseg_params": {
            "freqmin": 40000,
            "freqmax": 80000,
            "threshval": 4.5,
            "durmin": 0.010,
            "durmax": 0.500,
            "gapmin": 0.030,
            "margin": 0.015,
        },
    },
    "rat_distressed": {
        "description": "Rat 22-kHz distressed calls (Wistar)",
        "freq_range": (18000, 30000),
        "dur_range": (0.050, 4.000),
        "usvseg_params": {
            "freqmin": 18000,
            "freqmax": 30000,
            "threshval": 4.5,
            "durmin": 0.050,
            "durmax": 4.000,
            "gapmin": 0.030,
            "margin": 0.015,
        },
    },
}

DEFAULT_DATA_DIR = "/mnt/bb/datasets/UltraVox/usvseg"


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------

@dataclass
class Interval:
    start: float
    end: float


@dataclass
class MatchResult:
    true_positives: int
    false_positives: int
    false_negatives: int
    gt_count: int
    det_count: int

    @property
    def precision(self) -> float:
        return self.true_positives / self.det_count if self.det_count else 0.0

    @property
    def recall(self) -> float:
        return self.true_positives / self.gt_count if self.gt_count else 0.0

    @property
    def f1(self) -> float:
        p, r = self.precision, self.recall
        return 2 * p * r / (p + r) if (p + r) else 0.0


# ---------------------------------------------------------------------------
# Matching: bipartite assignment with IoU threshold
# ---------------------------------------------------------------------------

def iou(a: Interval, b: Interval) -> float:
    overlap = max(0.0, min(a.end, b.end) - max(a.start, b.start))
    union = (a.end - a.start) + (b.end - b.start) - overlap
    return overlap / union if union > 0 else 0.0


def match_detections(
    ground_truth: list[Interval],
    detections: list[Interval],
    iou_threshold: float = 0.3,
) -> MatchResult:
    """Greedy bipartite matching by descending IoU."""
    gt_matched = set()
    det_matched = set()

    pairs = []
    for gi, g in enumerate(ground_truth):
        for di, d in enumerate(detections):
            score = iou(g, d)
            if score >= iou_threshold:
                pairs.append((score, gi, di))
    pairs.sort(key=lambda x: -x[0])

    for _, gi, di in pairs:
        if gi not in gt_matched and di not in det_matched:
            gt_matched.add(gi)
            det_matched.add(di)

    tp = len(gt_matched)
    return MatchResult(
        true_positives=tp,
        false_positives=len(detections) - tp,
        false_negatives=len(ground_truth) - tp,
        gt_count=len(ground_truth),
        det_count=len(detections),
    )


# ---------------------------------------------------------------------------
# File loaders
# ---------------------------------------------------------------------------

def load_ground_truth(csv_path: Path) -> list[Interval]:
    """Load human annotations: start,end per line (no header)."""
    intervals = []
    with open(csv_path) as f:
        for line in f:
            parts = line.strip().rstrip(",").split(",")
            if len(parts) >= 2:
                try:
                    intervals.append(Interval(float(parts[0]), float(parts[1])))
                except ValueError:
                    continue
    return intervals


def load_ultravox_csv(csv_path: Path) -> list[Interval]:
    """Load UltraVox detector output: semicolon-separated with header."""
    intervals = []
    with open(csv_path) as f:
        reader = csv.reader(f, delimiter=";")
        header = next(reader, None)
        if not header:
            return intervals
        for row in reader:
            if len(row) >= 5:
                try:
                    intervals.append(Interval(float(row[3]), float(row[4])))
                except (ValueError, IndexError):
                    continue
    return intervals


def load_usvseg_csv(csv_path: Path) -> list[Interval]:
    """Load original USVSEG output: #,start,end,duration,..."""
    intervals = []
    with open(csv_path) as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if not header:
            return intervals
        for row in reader:
            if len(row) >= 3:
                try:
                    intervals.append(Interval(float(row[1]), float(row[2])))
                except (ValueError, IndexError):
                    continue
    return intervals


# ---------------------------------------------------------------------------
# Original USVSEG runner
# ---------------------------------------------------------------------------

def run_original_usvseg(wav_path: Path, params: dict, output_csv: Path):
    """Run the original USVSEG algorithm via the Python port."""
    try:
        import usvseg.func as uf
    except ImportError:
        print("  [SKIP] usvseg package not installed (pip install usvseg)")
        return False

    usvseg_params = {
        "timestep": 0.0005,
        "margin": params["margin"],
        "durmax": params["durmax"],
        "durmin": params["durmin"],
        "gapmin": params["gapmin"],
        "wavfileoutput": 0,
        "imageoutput": 0,
        "traceoutput": 0,
        "readsize": 30,
        "fftsize": 512,
        "freqmin": params["freqmin"],
        "freqmax": params["freqmax"],
        "threshval": params["threshval"],
        "bandwidth": 9,
        "liftercutoff": 3,
        "imagetype": 1,
        "mapL": -3,
        "mapH": 3,
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        uf.proc_wavfile(
            usvseg_params,
            str(wav_path),
            str(output_csv),
            tmpdir,
        )

    return True


# ---------------------------------------------------------------------------
# UltraVox detector runner
# ---------------------------------------------------------------------------

def run_ultravox_detector(
    detector_bin: Path, uvl_path: Path, wav_path: Path, output_csv: Path
):
    """Run the UltraVox file-based detector."""
    result = subprocess.run(
        [str(detector_bin), str(uvl_path), str(wav_path)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"  [ERROR] detector failed: {result.stderr[:200]}")
        return False
    output_csv.write_text(result.stdout)
    return True


# ---------------------------------------------------------------------------
# Main benchmark
# ---------------------------------------------------------------------------

def find_detector(benchmark_dir: Path) -> Path:
    candidate = benchmark_dir.parent / "detector" / "build" / "ultravox-elan-file"
    if candidate.exists():
        return candidate
    raise FileNotFoundError(
        f"detector-file binary not found at {candidate}. Build it first."
    )


def run_benchmark(data_dir: Path, benchmark_dir: Path, detector_bin: Path):
    results_dir = benchmark_dir / "results"
    results_dir.mkdir(exist_ok=True)

    all_results = {}
    iou_threshold = 0.3

    for dataset_name, config in DATASETS.items():
        dataset_dir = data_dir / dataset_name
        if not dataset_dir.exists():
            print(f"[SKIP] {dataset_name}: not found at {dataset_dir}")
            continue

        print(f"\n{'='*70}")
        print(f"Dataset: {dataset_name} - {config['description']}")
        print(f"{'='*70}")

        wav_files = sorted(dataset_dir.glob("*.wav"))
        gt_files = {
            p.stem: p
            for p in dataset_dir.glob("*.csv")
            if "_uv4" not in p.name
        }

        dataset_results = {
            "threshold": MatchResult(0, 0, 0, 0, 0),
            "usvseg_ultravox": MatchResult(0, 0, 0, 0, 0),
            "usvseg_original": MatchResult(0, 0, 0, 0, 0),
        }

        for wav_path in wav_files:
            stem = wav_path.stem
            gt_path = gt_files.get(stem)
            if not gt_path:
                print(f"  [SKIP] {stem}: no ground truth")
                continue

            gt = load_ground_truth(gt_path)
            print(f"\n  File: {stem} ({len(gt)} ground truth calls)")

            # --- UltraVox Threshold ---
            uvl_threshold = benchmark_dir / f"{dataset_name}_threshold.uvl"
            out_threshold = results_dir / f"{stem}_threshold.csv"
            if not out_threshold.exists():
                run_ultravox_detector(detector_bin, uvl_threshold, wav_path, out_threshold)
            det = load_ultravox_csv(out_threshold)
            m = match_detections(gt, det, iou_threshold)
            print(f"    Threshold:        {m.det_count:4d} det | P={m.precision:.3f} R={m.recall:.3f} F1={m.f1:.3f}")
            dataset_results["threshold"] = _merge(dataset_results["threshold"], m)

            # --- UltraVox USVSEG ---
            uvl_usvseg = benchmark_dir / f"{dataset_name}_usvseg.uvl"
            out_usvseg = results_dir / f"{stem}_usvseg.csv"
            if not out_usvseg.exists():
                run_ultravox_detector(detector_bin, uvl_usvseg, wav_path, out_usvseg)
            det = load_ultravox_csv(out_usvseg)
            m = match_detections(gt, det, iou_threshold)
            print(f"    UltraVox USVSEG:  {m.det_count:4d} det | P={m.precision:.3f} R={m.recall:.3f} F1={m.f1:.3f}")
            dataset_results["usvseg_ultravox"] = _merge(dataset_results["usvseg_ultravox"], m)

            # --- Original USVSEG ---
            out_original = results_dir / f"{stem}_usvseg_original.csv"
            if not out_original.exists():
                print(f"    Running original USVSEG (this may take a while)...")
                ok = run_original_usvseg(wav_path, config["usvseg_params"], out_original)
                if not ok:
                    continue
            if out_original.exists() and out_original.stat().st_size > 0:
                det = load_usvseg_csv(out_original)
                m = match_detections(gt, det, iou_threshold)
                print(f"    Original USVSEG:  {m.det_count:4d} det | P={m.precision:.3f} R={m.recall:.3f} F1={m.f1:.3f}")
                dataset_results["usvseg_original"] = _merge(dataset_results["usvseg_original"], m)

        all_results[dataset_name] = dataset_results

        # Print dataset summary
        print(f"\n  --- {dataset_name} Summary ---")
        for method, m in dataset_results.items():
            if m.gt_count > 0:
                print(
                    f"    {method:20s}: GT={m.gt_count} Det={m.det_count} "
                    f"TP={m.true_positives} FP={m.false_positives} FN={m.false_negatives} | "
                    f"P={m.precision:.3f} R={m.recall:.3f} F1={m.f1:.3f}"
                )

    # Grand summary
    print(f"\n{'='*70}")
    print("OVERALL SUMMARY")
    print(f"{'='*70}")
    print(f"{'Method':24s} {'GT':>5s} {'Det':>5s} {'TP':>5s} {'FP':>5s} {'FN':>5s} {'Prec':>6s} {'Rec':>6s} {'F1':>6s}")
    print("-" * 70)
    for dataset_name, methods in all_results.items():
        print(f"  {dataset_name}:")
        for method, m in methods.items():
            if m.gt_count > 0:
                print(
                    f"    {method:22s} {m.gt_count:5d} {m.det_count:5d} "
                    f"{m.true_positives:5d} {m.false_positives:5d} {m.false_negatives:5d} "
                    f"{m.precision:6.3f} {m.recall:6.3f} {m.f1:6.3f}"
                )


def _merge(a: MatchResult, b: MatchResult) -> MatchResult:
    return MatchResult(
        true_positives=a.true_positives + b.true_positives,
        false_positives=a.false_positives + b.false_positives,
        false_negatives=a.false_negatives + b.false_negatives,
        gt_count=a.gt_count + b.gt_count,
        det_count=a.det_count + b.det_count,
    )


def main():
    parser = argparse.ArgumentParser(description="USV Detection Benchmark")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path(DEFAULT_DATA_DIR),
        help="Path to USVSEG dataset directory",
    )
    parser.add_argument(
        "--detector",
        type=Path,
        default=None,
        help="Path to ultravox-elan-file binary",
    )
    args = parser.parse_args()

    benchmark_dir = Path(__file__).parent
    detector = args.detector or find_detector(benchmark_dir)

    if not detector.exists():
        print(f"Error: detector not found at {detector}")
        sys.exit(1)

    print(f"Data directory: {args.data_dir}")
    print(f"Detector:       {detector}")
    print(f"IoU threshold:  0.3")

    run_benchmark(args.data_dir, benchmark_dir, detector)


if __name__ == "__main__":
    main()
