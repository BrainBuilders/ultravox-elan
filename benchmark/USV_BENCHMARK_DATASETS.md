# USV Segmentation Benchmark Datasets

This document lists all publicly available USV (Ultrasonic Vocalization) datasets that include
human-annotated ground truth or USVSEG output files, suitable for benchmarking a custom USVSEG
implementation. Datasets are ordered by priority: **rat first** (primary focus), then multi-species
and mouse-only datasets.

---

## Priority 1 — Rat Datasets (Primary Focus)

### 1. USVSEG Official Benchmark — Rat Calls (Pleasant & Distressed)
**Species:** Rat (*Rattus norvegicus*, Wistar)  
**Ground truth:** Human expert onset/offset annotations (included in archive)  
**Format:** WAV audio + text/mat annotation files  
**Calls:** ~100+ syllables per condition (pleasant ~50 kHz; distressed ~22 kHz)  
**Note:** Two separate conditions — treat as independent datasets; the original USVSEG paper
used different parameter sets for each.

| File | Direct Download |
|------|----------------|
| `rat_pleasant.zip` (35.8 MB) | https://zenodo.org/records/3428024/files/rat_pleasant.zip?download=1 |
| `rat_distressed.zip` (145.5 MB) | https://zenodo.org/records/3428024/files/rat_distressed.zip?download=1 |

**DOI / Landing page:** https://doi.org/10.5281/zenodo.3428024  
**License:** CC BY 4.0  
**Reference:** Tachibana et al., *PLOS ONE*, 2020. https://doi.org/10.1371/journal.pone.0228907

---

### 2. TrackUSF — Rat (Shank3 Autism Model) + Multi-species
**Species:** Rat (Shank3-deficient and wild-type), Mouse, Bat  
**Ground truth:** Manual annotations by a trained observer  
**Format:** Available via Mendeley Data (WAV + annotation files)  
**Note:** Validated against DeepSqueak; includes both normal and autism-model rats. Bat data
is a bonus for non-rodent benchmarking.

**Direct download:** https://data.mendeley.com/datasets/8d4yz5fyhy/2  
**DOI:** https://doi.org/10.17632/8d4yz5fyhy.2  
**License:** CC BY 4.0  
**Reference:** Netser et al., *BMC Biology*, 2022. https://doi.org/10.1186/s12915-022-01299-y

---

## Priority 2 — Multi-Species / Cross-Lab Datasets

### 3. USVSEG Official Benchmark — Gerbil
**Species:** Fat-tailed gerbil (*Pachyuromys duprasi*)  
**Ground truth:** Human expert onset/offset annotations  
**Format:** WAV audio + annotation files  
**Calls:** 100+ syllables

| File | Direct Download |
|------|----------------|
| `gerbil.zip` (31.5 MB) | https://zenodo.org/records/3428024/files/gerbil.zip?download=1 |

**DOI / Landing page:** https://doi.org/10.5281/zenodo.3428024  
**License:** CC BY 4.0  
**Reference:** Tachibana et al., *PLOS ONE*, 2020. https://doi.org/10.1371/journal.pone.0228907

---

### 4. AMVOC — Mouse (Multi-method comparison, CSV ground truth)
**Species:** Mouse (C57BL/6J and B6D2F1/J)  
**Ground truth:** Human-annotated CSV files (`gt_1.csv` … `gt_9.csv`) bundled directly in the
GitHub repository alongside the WAV files. Also includes detection output CSV files from 5 other
methods (DeepSqueak, MUPET, VocalMat, MSA v1, MSA v2) for direct comparison.  
**Format:** WAV + CSV onset/offset files  
**Calls:** 245 syllables across 9 recordings (5–10 s each); intentionally includes noisy recordings  
**Note:** The CSV format is directly comparable to typical USVSEG output. Ideal for benchmarking
detection under noisy conditions.

**Repository:** https://github.com/tyiannak/amvoc  
**Data path in repo:** `data/vocalizations_evaluation/`  
**Clone command:**
```bash
git clone https://github.com/tyiannak/amvoc.git
# Ground truth: amvoc/data/vocalizations_evaluation/{1..9}/gt_{1..9}.csv
# Audio:        amvoc/data/vocalizations_evaluation/{1..9}/rec_{1..9}.wav
```
**License:** Apache 2.0  
**Reference:** Stoumpou et al., *Bioacoustics*, 2023. https://doi.org/10.1080/09524622.2022.2099973

---

## Priority 3 — Mouse Datasets (For Broader Benchmarking)

### 5. USVSEG Official Benchmark — Mouse C57BL/6J Adults (Courtship)
**Species:** Mouse (*Mus musculus*, C57BL/6J, adult males)  
**Ground truth:** Human expert onset/offset annotations  
**Format:** WAV audio + annotation files  
**Calls:** 2,401 USVs across 10 recordings  
**Note:** The largest and most-used benchmark in the USV literature. Validated by USVSEG,
VocalMat, DeepSqueak, MUPET, A-MUD, and others.

| File | Direct Download |
|------|----------------|
| `mouse_C57BL.zip` (427.3 MB) | https://zenodo.org/records/3428024/files/mouse_C57BL.zip?download=1 |

**DOI / Landing page:** https://doi.org/10.5281/zenodo.3428024  
**License:** CC BY 4.0  
**Reference:** Tachibana et al., *PLOS ONE*, 2020. https://doi.org/10.1371/journal.pone.0228907

---

### 6. USVSEG Official Benchmark — Mouse Pups (B6, BALBc, Shank2)
**Species:** Mouse pups (*Mus musculus* — C57BL/6J, BALB/c, Shank2 mutant)  
**Ground truth:** Human expert onset/offset annotations  
**Format:** WAV audio + annotation files  
**Calls:** 409 USVs across 5 recordings (pup isolation calls); Shank2 is an autism model  
**Note:** Useful for showing robustness across strains and developmental stage.

| File | Direct Download |
|------|----------------|
| `mouse_B6pup.zip` (294.5 MB) | https://zenodo.org/records/3428024/files/mouse_B6pup.zip?download=1 |
| `mouse_BALBc.zip` (33.4 MB) | https://zenodo.org/records/3428024/files/mouse_BALBc.zip?download=1 |
| `mouse_Shank2.zip` (81.5 MB) | https://zenodo.org/records/3428024/files/mouse_Shank2.zip?download=1 |

**DOI / Landing page:** https://doi.org/10.5281/zenodo.3428024  
**License:** CC BY 4.0  
**Reference:** Tachibana et al., *PLOS ONE*, 2020. https://doi.org/10.1371/journal.pone.0228907

---

### 7. DeepSqueak Sample Recording — Mouse
**Species:** Mouse (single recording, lab unspecified)  
**Ground truth:** Manually reviewed by VocalMat authors; 762 labeled USVs  
**Format:** WAV (bundled with DeepSqueak GitHub repository)  
**Note:** Widely used as a cross-lab generalizability test. VocalMat and AMVOC both report
results on this exact file, making comparisons easy.

**Repository:** https://github.com/DrCoffey/DeepSqueak  
**Data path in repo:** `Calls/` or `Example Data/`  
**Clone command:**
```bash
git clone https://github.com/DrCoffey/DeepSqueak.git
```
**License:** GPLv3  
**Reference:** Coffey et al., *Neuropsychopharmacology*, 2019. https://doi.org/10.1038/s41386-018-0303-6

---

### 8. SqueakOut / VocalMat Annotated Spectrogram Dataset
**Species:** Mouse (C57BL/6J, NZO, 129S1, NOD, PWK — 5 strains), postnatal day 5–15  
**Ground truth:** Pixel-level spectrogram segmentation masks (binary PNG masks per USV)  
**Format:** 12,954 spectrogram images + segmentation masks  
**Calls:** 10,871 USV spectrograms + 2,083 noise examples  
**Note:** This is a spectrogram-level segmentation dataset rather than a time-domain
onset/offset dataset. Best suited for benchmarking spectral precision of segmentation rather
than temporal detection. Dataset is derived from the VocalMat release.

**Repository:** https://github.com/ahof1704/SqueakOut  
**License:** MIT  
**Reference:** Lesch et al., *bioRxiv*, 2024. https://doi.org/10.1101/2024.04.19.590368

---

## Summary Table

| # | Dataset | Species | Ground Truth Type | Priority | Size | Direct Download / Source |
|---|---------|---------|------------------|----------|------|--------------------------|
| 1 | USVSEG — Rat pleasant | Rat | Human onset/offset | ⭐⭐⭐ | 35.8 MB | https://zenodo.org/records/3428024/files/rat_pleasant.zip?download=1 |
| 2 | USVSEG — Rat distressed | Rat | Human onset/offset | ⭐⭐⭐ | 145.5 MB | https://zenodo.org/records/3428024/files/rat_distressed.zip?download=1 |
| 3 | TrackUSF | Rat + Mouse + Bat | Human onset/offset | ⭐⭐⭐ | ~varies | https://doi.org/10.17632/8d4yz5fyhy.2 |
| 4 | USVSEG — Gerbil | Gerbil | Human onset/offset | ⭐⭐ | 31.5 MB | https://zenodo.org/records/3428024/files/gerbil.zip?download=1 |
| 5 | AMVOC | Mouse | Human CSV + 5-tool comparison | ⭐⭐⭐ | ~small | https://github.com/tyiannak/amvoc |
| 6 | USVSEG — Mouse C57BL adult | Mouse | Human onset/offset | ⭐⭐⭐ | 427.3 MB | https://zenodo.org/records/3428024/files/mouse_C57BL.zip?download=1 |
| 7 | USVSEG — Mouse pups | Mouse | Human onset/offset | ⭐⭐ | 409 MB | See section 6 above |
| 8 | DeepSqueak sample | Mouse | Manual (762 USVs) | ⭐⭐ | ~small | https://github.com/DrCoffey/DeepSqueak |
| 9 | SqueakOut/VocalMat | Mouse (5 strains) | Pixel mask | ⭐ | ~large | https://github.com/ahof1704/SqueakOut |

---

## Notes on Ground Truth Formats

- **USVSEG Zenodo archives** contain both `.wav` audio and text/mat files with manually annotated
  onset and offset times (seconds). These are the canonical ground truth files used in the original
  USVSEG paper and by all downstream benchmarks.

- **AMVOC** ground truth is already in CSV format (`gt_N.csv`) with onset/offset columns,
  and companion CSVs from DeepSqueak, MUPET, VocalMat, and MSA are included in the same
  directories — making multi-method comparisons trivial.

- **TrackUSF (Mendeley)** annotations follow the format used in the paper; check the README
  in the Mendeley archive for column definitions.

- **SqueakOut** annotations are binary PNG masks aligned to spectrogram images — useful only
  for pixel-level segmentation evaluation, not temporal onset/offset comparison.

---

## Recommended Benchmark Metrics

To keep results comparable with the existing literature:

- **Hit rate (True Positive Rate / Recall)** — fraction of ground truth syllables detected
- **Correct Rejection rate (True Negative Rate)** — fraction of non-vocal frames correctly
  rejected
- **False Discovery Rate (FDR)** — fraction of detections that are not real USVs
- **Accuracy = (Hit + CR) / 2** — balanced performance index used in original USVSEG paper
- **Cohen's κ-index** — inter-rater agreement measure, used in original USVSEG paper
- **F1 score** — used by AMVOC and most deep learning papers
- **Precision / Recall at IoU threshold** — used by DeepSqueak, SqueakOut

---

## Citation Reminder

If using these datasets in a publication, cite the original papers:

- USVSEG dataset: Tachibana et al. (2020) https://doi.org/10.1371/journal.pone.0228907
- AMVOC dataset: Stoumpou et al. (2023) https://doi.org/10.1080/09524622.2022.2099973
- TrackUSF dataset: Netser et al. (2022) https://doi.org/10.1186/s12915-022-01299-y
- DeepSqueak: Coffey et al. (2019) https://doi.org/10.1038/s41386-018-0303-6
- SqueakOut: Lesch et al. (2024) https://doi.org/10.1101/2024.04.19.590368
