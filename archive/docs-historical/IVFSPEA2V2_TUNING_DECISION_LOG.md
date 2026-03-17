# IVFSPEA2V2 Tuning Decision Log

This document records final tuning decisions and the evidence used to promote
configurations after the A/B/C tuning pipeline.

## 2026-02-28 - FULL12 A/B/C + head-to-head promotion check

Scope:
- tuning data root: `data/tuning_ivfspea2v2/`
- phases analyzed: A, B, C
- metrics: IGD and HV
- integrity mode: full metric scan

Integrity status:
- Phase A: 576/576 OK (`results/tuning_ivfspea2v2/integrity_tuning_report_20260228_082721.csv`)
- Phase B: 60/60 OK (`results/tuning_ivfspea2v2/integrity_tuning_report_20260228_082644.csv`)
- Phase C: 432/432 OK (`results/tuning_ivfspea2v2/integrity_tuning_report_20260228_082647.csv`)

Phase recommendations:
- A winner: `A43` (`R=0.20, C=0.16, Cycles=2, M=0, V=0, EARN=0`)
- B winner: `B02` (`EAR light`)
- C winner: `C26` (`R=0.225, C=0.12, Cycles=2, M=0.3, V=0.1, EARN=0`)

Head-to-head command:

```bash
.venv/bin/python src/python/analysis/analyze_ivfspea2v2_tuning_head_to_head.py
```

Head-to-head artifacts:
- `results/tuning_ivfspea2v2/head_to_head_c26_a43_v1_igd.csv`
- `results/tuning_ivfspea2v2/head_to_head_c26_a43_v1_hv.csv`
- `results/tuning_ivfspea2v2/head_to_head_c26_a43_v1_summary.json`
- `results/tuning_ivfspea2v2/head_to_head_c26_a43_v1_report.md`

Key findings (Holm-corrected, per-problem):
- IGD, `C26 vs A43`: `0/12/0` (all ties after correction; raw 5 wins vs 7 losses)
- HV, `C26 vs A43`: `1/11/0`
- IGD, `C26 vs IVFSPEA2v1`: `4/8/0`
- IGD, `A43 vs IVFSPEA2v1`: `4/8/0`

Data note:
- Tuning candidates (`A43`, `C26`) use 30 runs/problem from the tuning pipeline.
- The v1 baseline in this comparison comes from `data/processed/todas_metricas_consolidado.csv`
  with 60 runs/problem (same problem definitions, larger sample size).

Decision:
- **Promoted tuning configuration: `C26`**.

Rationale:
- The tuning protocol is incremental and promotes from Phase C.
- Head-to-head shows no corrected-significance IGD loss of `C26` vs `A43`.
- Both `C26` and `A43` outperform IVF/SPEA2 v1 on key IGD instances, with
  corrected wins and no corrected losses.
