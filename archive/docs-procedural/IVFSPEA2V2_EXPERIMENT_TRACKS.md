# IVFSPEA2V2 Experiment Tracks and Phase Semantics

This document prevents phase-name ambiguity across different IVF/SPEA2 workstreams.

---

## Why this exists

The repository contains more than one experimental workflow using the word "phase".
Those phases are **not interchangeable** and must not be mixed in analysis.

---

## Track 1 - v2 Discovery and Consolidation (algorithm factors)

Purpose:
- discover and validate structural IVF improvements (H1-H5) and choose the v2 architecture.

Phase labels:
- **Phase 1**: factor screening (add-one-in)
- **Phase 2**: factorial combinations of promoted factors
- **Phase 3**: full-suite validation

Primary references:
- `docs/IVF_V2_HYPOTHESES_AND_ABLATION_PLAN.md`
- `docs/IVF_V2_CONSOLIDATION.md`

Primary data roots:
- `data/ablation_v2/phase1/`
- `data/ablation_v2/phase2/`
- `data/ablation_v2/phase3/`

---

## Track 2 - v2 Parameter Tuning (post-consolidation)

Purpose:
- tune operational parameters of the already-consolidated `IVFSPEA2V2`
  (activation, collection, cycles, EAR profiles).

Phase labels:
- **Phase A**: AR grid for `R`, `C`, `Cycles`
- **Phase B**: operator comparison (AR/EAR/EARN)
- **Phase C**: local refinement around selected center

Primary reference:
- `docs/IVFSPEA2V2_TUNING_PIPELINE.md`

Primary data roots:
- `data/tuning_ivfspea2v2/phaseA/`
- `data/tuning_ivfspea2v2/phaseB/`
- `data/tuning_ivfspea2v2/phaseC/`

---

## Track 3 - Submission Evidence Rerun (frozen protocol)

Purpose:
- regenerate publication evidence under frozen defaults and isolated run IDs.

Primary reference:
- `docs/submission_rerun_protocol.md`

Key rule:
- submission evidence must not be mixed with discovery/tuning runs.

---

## Naming and citation rules (for paper/reports)

- Use **"Discovery Phase 1/2/3"** only for Track 1.
- Use **"Tuning Phase A/B/C"** only for Track 2.
- When reporting results, always include both:
  - track name, and
  - phase label.
- Always cite data root and manifest file used for each table/figure.

Recommended wording examples:
- "Track 1 (Discovery), Phase 2 factorial results".
- "Track 2 (Tuning), Phase B operator comparison".

---

## Integrity guardrails

- Keep manifests and inventories separated per track.
- Do not merge CSV summaries across tracks before explicit harmonization.
- Keep IGD and HV mandatory in every new track/phase.
