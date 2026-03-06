# USV Detection Benchmark

Compares UltraVox detection methods against human ground truth annotations
from the USVSEG benchmark dataset (Tachibana et al., 2020).

## Methods Under Test

| Method | Description |
|--------|-------------|
| **UltraVox Threshold** | Amplitude-based detection from the UltraVox SDK |
| **UltraVox USVSEG** | Spectral-saliency detection (UltraVox C++ re-implementation of USVSEG) |
| **Original USVSEG** | Reference Python port of the original MATLAB algorithm (Tachibana et al., 2020) |

## Datasets

Data from Zenodo record [3428024](https://doi.org/10.5281/zenodo.3428024), CC BY 4.0.

| Dataset | Species | Call type | Files | Ground truth calls |
|---------|---------|-----------|-------|--------------------|
| rat_pleasant | Wistar rat | ~50 kHz (pleasant) | 3 | 300 |
| rat_distressed | Wistar rat | ~22 kHz (distressed) | 4 | 155 |

## Evaluation Method

- **Matching**: greedy bipartite assignment by descending IoU
- **IoU threshold**: 0.3 (a detection counts as a true positive if it overlaps
  at least 30% with a ground truth interval)
- **Metrics**: Precision, Recall, F1 score

## Results

### rat_pleasant (50-kHz calls, 300 ground truth)

| Method | Detected | TP | FP | FN | Precision | Recall | F1 |
|--------|----------|----|----|----|-----------|--------|------|
| UltraVox Threshold | 113 | 95 | 18 | 205 | 0.841 | 0.317 | 0.460 |
| UltraVox USVSEG | 213 | 204 | 9 | 96 | 0.958 | 0.680 | **0.795** |
| Original USVSEG | 209 | 200 | 9 | 100 | 0.957 | 0.667 | 0.786 |

### rat_distressed (22-kHz calls, 155 ground truth)

| Method | Detected | TP | FP | FN | Precision | Recall | F1 |
|--------|----------|----|----|----|-----------|--------|------|
| UltraVox Threshold | 188 | 153 | 35 | 2 | 0.814 | 0.987 | 0.892 |
| UltraVox USVSEG | 153 | 152 | 1 | 3 | 0.993 | 0.981 | **0.987** |
| Original USVSEG | 153 | 152 | 1 | 3 | 0.993 | 0.981 | **0.987** |

### Key Observations

**rat_distressed (22-kHz)**:
- UltraVox USVSEG matches the original algorithm exactly (F1=0.987).
- The Threshold detector has strong recall (0.987) but lower precision due to
  false positives.

**rat_pleasant (50-kHz)**:
- UltraVox USVSEG surpasses the original (F1=0.795 vs 0.786) with 4 additional
  true positives at the same false positive rate. The improvement comes from
  our symmetric cepstral liftering combined with the USVSEG default threshold
  multiplier (4.0).
- Both USVSEG implementations miss about a third of calls, which is a known
  limitation of the algorithm for short, faint vocalizations.

## Running the Benchmark

Prerequisites:
- Built `ultravox-elan-file` binary (see `detector/`)
- USVSEG dataset at `/mnt/bb/datasets/UltraVox/usvseg/` (or specify `--data-dir`)
- Python `usvseg` package for original USVSEG comparison: `pip install usvseg`

```bash
python benchmark/run_benchmark.py
python benchmark/run_benchmark.py --data-dir /path/to/usvseg
```

## Configuration Files

UVL config files define the detection parameters for each dataset and method:

| File | Method | Frequency band |
|------|--------|---------------|
| `rat_pleasant_threshold.uvl` | threshold | 40-80 kHz |
| `rat_pleasant_usvseg.uvl` | usvseg | 40-80 kHz |
| `rat_distressed_threshold.uvl` | threshold | 18-30 kHz |
| `rat_distressed_usvseg.uvl` | usvseg | 18-30 kHz |

## References

- Tachibana et al. (2020). "An accessible platform for rodent ultrasonic
  vocalization analysis." *PLOS ONE*.
  [doi:10.1371/journal.pone.0228907](https://doi.org/10.1371/journal.pone.0228907)
- Dataset: [Zenodo 3428024](https://doi.org/10.5281/zenodo.3428024)
