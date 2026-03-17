# Springer Figure and Table Compliance (Memetic Computing)

This checklist maps the Springer guidelines (`docs/guidelines_springer.pdf`) to the current manuscript assets.

## 1) Tables

- [x] **Arabic numbering and in-text citation order**
  - Verified in `paper/src/sn-article.tex`: table labels and first references are in consistent order.
- [x] **Caption present for each table**
  - All manuscript tables have `\caption{...}`.
- [x] **Table bodies in LaTeX tabular format**
  - No spreadsheet embeds in manuscript source.
- [x] **Statistical symbols explained**
  - Detailed tables and pairwise tables explain `$+$/$-$/`=` semantics in captions.
- [ ] **Footnote markers (if needed) as superscript lowercase letters**
  - Not currently used; keep this rule if table footnotes are added.

## 2) Figures

- [x] **Arabic numbering and in-text citation order**
  - Verified in `paper/src/sn-article.tex`: `fig:flow`, `fig:boxplots_m2`, `fig:boxplots_m3`, `fig:a12_effect_size`, `fig:sensitivity_combined`.
- [x] **Captions in manuscript, not embedded as caption text in images**
  - Figure captions are in LaTeX source.
- [x] **No color-dependent statement in sensitivity caption**
  - Updated `paper/src/sn-article.tex` to avoid "blue regions" wording.
- [x] **Sensitivity figure panel parts with lowercase letters**
  - Added `(a)`, `(b)`, `(c)` markers in `src/python/analysis/analyze_sensitivity_multiclass.py`.
- [x] **Sans-serif lettering and consistent size for sensitivity figure**
  - Enforced Arial/Helvetica fallback and consistent 8--9 pt text in `src/python/analysis/analyze_sensitivity_multiclass.py`.
- [x] **Accessibility-oriented colormap for sensitivity heatmap**
  - Switched to `cividis` (better grayscale/contrast behavior) in `src/python/analysis/analyze_sensitivity_multiclass.py`.
- [x] **Submission-friendly exports for sensitivity figure**
  - Generated:
    - `paper/figures/sensitivity_multiclass_combined.pdf` (vector)
    - `paper/figures/sensitivity_multiclass_combined.tiff` (600 dpi)

- [x] **A12 heatmap in publication-friendly formats**
  - Generated `paper/figures/heatmap_comparacao.pdf` and `paper/figures/heatmap_comparacao.tiff` (600 dpi)
  - Manuscript now uses the PDF version in `paper/src/sn-article.tex`

## 3) Size and Resolution Audit (current)

- `paper/figures/sensitivity_multiclass_combined.pdf`: **6.85 x 2.75 in** (aligned to Springer double-column width target)
- `paper/figures/sensitivity_multiclass_combined.tiff`: **600 dpi**
- `paper/figures/heatmap_comparacao.pdf`: **7.00 x 5.00 in** (raster-in-PDF)
- `paper/figures/heatmap_comparacao.tiff`: **600 dpi**
- `paper/figures/results_m2.pdf`: **5.64 x 7.94 in**
- `paper/figures/results_m3.pdf`: **5.65 x 7.76 in**
- `paper/figures/flowchart.pdf`: **6.85 x 2.67 in**

## 4) Remaining Recommended Actions Before Submission

1. **Final visual QA at print scale** in compiled PDF:
   - lettering legibility (target ~8--12 pt apparent size),
   - line visibility,
   - grayscale interpretability.
2. **Submission packaging**:
   - include editable source files,
   - include figure source/exports required by submission system,
   - ensure captions remain only in manuscript text.

## 5) Quick Go/No-Go Gate

- GO if: all main figures are legible at final print scale and key files are in accepted formats.
- NO-GO if: any figure requires zoom to read axis labels or relies on color-only distinction.
