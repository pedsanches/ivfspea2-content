# WS6 Claim Audit

Date: 2026-03-09
Status: Completed

## Scope

This audit checks whether the manuscript's headline quantitative claims remain
consistent with the frozen canonical artifacts after WS4 and WS5.

## Checked claims

### 1. Abstract synthetic host-comparison counts

Source text:

- `paper/src/sn-article.tex:124`

Canonical evidence:

- `results/tables/claims_summary_audit.csv:5`
- `results/tables/claims_summary_audit.csv:9`
- `results/tables/claims_summary_audit.csv:4`
- `results/tables/claims_summary_audit.csv:8`

Result:

- PASS
- The abstract reports Holm-corrected OOS IGD counts `19/2/3` (`M=2`) and
  `12/0/3` (`M=3`), and full-suite Holm counts `22/3/3` and `15/1/7`.
- These values match the frozen audit CSV exactly.

### 2. Conclusion synthetic host-comparison counts

Source text:

- `paper/src/sn-article.tex:635`

Canonical evidence:

- `results/tables/claims_summary_audit.csv:2`
- `results/tables/claims_summary_audit.csv:3`
- `results/tables/claims_summary_audit.csv:4`
- `results/tables/claims_summary_audit.csv:5`
- `results/tables/claims_summary_audit.csv:6`
- `results/tables/claims_summary_audit.csv:7`
- `results/tables/claims_summary_audit.csv:8`
- `results/tables/claims_summary_audit.csv:9`

Result:

- PASS
- The conclusion's unadjusted and Holm-corrected IGD counts match the audit
  CSV exactly for both `M=2` and `M=3`.

### 3. Engineering transferability summary

Source text:

- `paper/src/sn-article.tex:512`
- `paper/src/sn-article.tex:637`

Canonical evidence:

- `results/engineering_suite/engineering_suite_pairwise_main.csv:2`
- `results/engineering_suite/engineering_suite_pairwise_main.csv:4`
- `results/engineering_suite/engineering_suite_pairwise_main.csv:6`

Result:

- PASS
- The manuscript states `8/0/0` on `RWMOP9` IGD, `3/2/3` on `RWMOP21` IGD, and
  `1/1/5` on `RWMOP8` IGD. These match the canonical engineering pairwise file.

### 4. Phase 3 ablation framing

Source text:

- `paper/src/sn-article.tex:575`

Canonical evidence:

- `results/ablation_v2/phase3/phase3_summary.json:10`
- `results/ablation_v2/phase3/phase3_summary.json:17`

Result:

- PASS
- The manuscript's `v2` vs `v1` near-equivalence framing (`0/50/1` on IGD) and
  the `v2` vs `SPEA2` supportive summary (`25/25/1` on IGD) match the current
  Phase 3 summary JSON.

## Audit conclusion

For the claims checked here, the manuscript is numerically consistent with the
frozen canonical artifacts.

This audit does not certify editorial quality, test status, or final submission
packaging. Those are addressed separately in the WS6 go/no-go memo.
