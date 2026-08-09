# PPSN 2026 IVF-Hosts Reviewer Revision Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Apply the complete reviewer punchlist (C1–C2, M1–M7, Mo1–Mo10, minor items, five figure caption rewrites, twenty sentence-level rewrites, three cross-section transitions, Fig. 2 split, Zenodo DOI mint) to `paper/ppsn2026-ivf-hosts/main.tex` without touching scientific claims.

**Architecture:** Seven sequential tasks matching the seven design phases. Each task ends with a verification step and a scoped commit. Text edits use LaTeX `Edit`/`Write` with exact `old_string`/`new_string` pairs. One Python plotting script (`plot_hosts_figures_v2.py::fig2_heatmap`) is modified to produce a two-panel figure. Zenodo deposit is prepared via GitHub Release webhook.

**Tech Stack:** LaTeX (llncs), BibTeX, Python 3 (matplotlib, pandas, seaborn) via `.venv`, `latexmk`/`pdflatex`, `pdftotext`, GitHub Releases + Zenodo.

---

## File Structure

**Modified:**
- `paper/ppsn2026-ivf-hosts/main.tex` — body edits, captions, transitions, placeholders filled.
- `paper/ppsn2026-ivf-hosts/references.bib` — DOI added to `zambrano2026ivfspea2`, optionally to MaF/DTLZ refs.
- `src/python/analysis/plot_hosts_figures_v2.py` — `fig2_heatmap()` rewritten to a two-panel layout.

**Regenerated:**
- `paper/ppsn2026-ivf-hosts/figures/hosts_v2_fig2_heatmap.pdf` — two-panel (M=2 top, M=3 bottom).

**Created:**
- `artifact/ppsn2026-ivf-hosts-rev1/` — staging directory for Zenodo zip.
- `artifact/ppsn2026-ivf-hosts-rev1/README.md` — reproducibility README.
- `artifact/ppsn2026-ivf-hosts-rev1.zip` — deposit bundle.
- `artifact/zenodo-metadata.json` — Zenodo deposit metadata draft.
- `artifact/github-release-notes.md` — GitHub Release body text.

**Reference only (not modified):**
- `docs/superpowers/specs/2026-04-17-ppsn2026-ivf-hosts-reviewer-revision-design.md`.

---

## Task 0: Preflight & Information Gathering

**Files:** none modified. Read-only diagnostics.

- [ ] **Step 0.1: Detect MATLAB release**

Run: `matlab -batch "disp(version)" 2>/dev/null | head -5`
Expected: a line like `25.2.0.123456 (R2025b)`. Record the parenthesized form for the paper.

- [ ] **Step 0.2: Detect PlatEMO version**

Run: `grep -r -m1 -i "version" /home/pedro/code/research/ivfspea2/src/matlab/lib/PlatEMO/ --include="*.md" --include="VERSION" --include="*.m" 2>/dev/null | head -10`
If no explicit version tag found, run: `git -C /home/pedro/code/research/ivfspea2 log --oneline -1 -- src/matlab/lib/PlatEMO/ 2>/dev/null | head -1` and record `commit <hash>` as the version surrogate.

- [ ] **Step 0.3: Detect hardware**

Run:
```bash
echo "CPU: $(lscpu | grep 'Model name' | sed 's/Model name:\s*//')"
echo "RAM: $(free -h | awk '/^Mem:/ {print $2}')"
echo "OS: $(lsb_release -ds 2>/dev/null || uname -a)"
```
Record the three values.

- [ ] **Step 0.4: Compile current PDF**

Run:
```bash
cd /home/pedro/code/research/ivfspea2/paper/ppsn2026-ivf-hosts && make
```
Expected: `build/main.pdf` produced; no LaTeX errors. If the `assets` target fails because of a missing `.venv`, run `make -C /home/pedro/code/research/ivfspea2 setup` first then retry.

- [ ] **Step 0.5: Ligature check on compiled PDF**

Run:
```bash
pdftotext -layout /home/pedro/code/research/ivfspea2/paper/ppsn2026-ivf-hosts/build/main.pdf - \
  | grep -nE 'dierent|intensication|eect|conrmatory|dicult|simpli |sucient|specic' \
  || echo "LIGATURES OK"
```
If `LIGATURES OK` prints → reviewer's PDF-extraction was the culprit; no LaTeX change needed; log "ligatures classified as reviewer-side artifact" in the checkpoint report.
If matches print → add `\usepackage{cmap}` after `\usepackage[T1]{fontenc}` in `main.tex` and recompile. If that fails, replace with `\usepackage{lmodern}`. Recheck until `LIGATURES OK`.

- [ ] **Step 0.6: Checkpoint A — report findings to user**

Format:
```
Checkpoint A
  MATLAB release     : <value>
  PlatEMO version    : <value>
  CPU                : <value>
  RAM                : <value>
  OS                 : <value>
  Ligatures          : OK | fixed-with-cmap | fixed-with-lmodern
```
Wait for user confirmation before proceeding to Task 1.

- [ ] **Step 0.7: Commit preflight (only if PDF was fixed)**

Only run if a ligature fix was applied:
```bash
cd /home/pedro/code/research/ivfspea2
git add paper/ppsn2026-ivf-hosts/main.tex
git commit -m "$(cat <<'EOF'
revision: [passo 11-preflight] font/ligature fix

Adds cmap (or lmodern) to ensure PDF text-extraction produces correct
words without ff/fi/ffi ligature extraction artifacts, flagged by
reviewer.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

---

## Task 1: Critical + Major Text Edits

**Files:**
- Modify: `paper/ppsn2026-ivf-hosts/main.tex`

Apply the edits below in order. After each sub-step, `grep` the file to verify the old text is gone and the new text is present.

- [ ] **Step 1.1: Fill MATLAB release and PlatEMO version in §4**

Edit:
```
OLD: All experiments were conducted in MATLAB~\texttt{[release]} using PlatEMO version~\texttt{[PlatEMO version]}~\cite{tian2017platemo}.
NEW: All experiments were conducted in MATLAB~\texttt{<MATLAB_VALUE>} using PlatEMO version~\texttt{<PLATEMO_VALUE>}~\cite{tian2017platemo}.
```
Substitute `<MATLAB_VALUE>` and `<PLATEMO_VALUE>` with the Checkpoint A values.

- [ ] **Step 1.2: Fill CPU / RAM / OS in §4 "Metrics and references"**

Edit:
```
OLD: The runs were executed on \texttt{[CPU / RAM / OS]}, and the processed CSV files, raw metric traces, and analysis scripts used to generate the reported tables and figures are archived at \texttt{[artifact URL or DOI]}.
NEW: The runs were executed on <HARDWARE_VALUE>, and the processed CSV files, raw metric traces, and analysis scripts used to generate the reported tables and figures are archived at \texttt{[ARTIFACT_DOI_PENDING]}.
```
Substitute `<HARDWARE_VALUE>` with "an AMD/Intel …, N GB RAM, <OS>" style prose (no `\texttt` since it is not a single token). Leave `[ARTIFACT_DOI_PENDING]` — Task 6 fills it.

- [ ] **Step 1.3: Abstract — M1 notation + remove "only"**

Edit:
```
OLD: IVF/SPEA2 records +33/=15/-3 IGD outcomes, IVF/NSGA-III records +22/=29/-0, and IVF/NSGA-II records only +1/=48/-2;
NEW: IVF/SPEA2 achieves 33 wins, 15 ties, and 3 losses in IGD; IVF/NSGA-III achieves 22 wins, 29 ties, and 0 losses; and IVF/NSGA-II achieves 1 win, 48 ties, and 2 losses;
```

- [ ] **Step 1.4: Abstract — M2 caveat compression**

Find the final sentence of the abstract starting "Taken together, these results support a pipeline-level compatibility interpretation: ..." and replace:
```
OLD: Taken together, these results support a pipeline-level compatibility interpretation: among the host-specific IVF realizations studied here, IVF/SPEA2 couples most effectively to its host, IVF/NSGA-III is conditionally beneficial, and IVF/NSGA-II is largely neutral.
NEW: Because the three pipelines differ in more than just the host, the evidence supports a pipeline-level compatibility claim: among the published IVF realizations studied here, IVF/SPEA2 couples most effectively with its host's selection mechanism, IVF/NSGA-III is conditionally beneficial, and IVF/NSGA-II is largely neutral.
```

- [ ] **Step 1.5: §1 — M6 actionable → directional**

Edit:
```
OLD: A useful intensification step must receive actionable feedback from the host about where additional search effort should be spent.
NEW: A useful intensification step requires directional feedback from the host: information about where additional search effort is most likely to pay off.
```

- [ ] **Step 1.6: §3 last sentence — M2 compress**

Edit:
```
OLD: Table~\ref{tab:adaptations} summarizes these host-specific choices, so compatibility claims throughout this paper refer to the pipeline level (host + realization), not to a single identical IVF module transplanted unchanged across hosts.
NEW: Table~\ref{tab:adaptations} summarizes these host-specific choices. Because the realizations differ in several components, compatibility claims in this paper refer to the pipeline level (host + realization) rather than to a single IVF module held identical across hosts.
```

- [ ] **Step 1.7: §3.1 — M5 "canonical" disambiguation**

Edit:
```
OLD: IVF/SPEA2 v2 is the canonical implementation in this study~\cite{zambrano2026ivfspea2}.
NEW: IVF/SPEA2 v2 is the published reference implementation used in this study~\cite{zambrano2026ivfspea2}.
```

- [ ] **Step 1.8: §4 Budget accounting — M4 split**

Edit:
```
OLD: In all three host-specific IVF realizations, evaluations spent inside IVF are debited against the host descendants of the same generation: the IVF phase is capped at at most $N$ internal evaluations in an activated generation, and the remaining host variation budget is reduced to $N-\mathrm{FE}_{\mathrm{IVF,gen}}$.
NEW: In all three host-specific IVF realizations, evaluations spent inside IVF are debited from the host's generation budget. The IVF phase consumes at most $N$ internal evaluations per activated generation, and the remaining host variation budget is reduced to \(N - \mathrm{FE}_{\mathrm{IVF,gen}}\).
```

- [ ] **Step 1.9: §4 — M4 move trajectory-interpolation sentence to §5.4**

Remove from §4:
```
OLD: For trajectory plots, small checkpoint drifts are handled by interpolation on a common FE grid when exact checkpoint alignment is unavailable.
NEW: (deleted)
```
Leave this sentence out of §4 — it reappears via the Fig. 5 caption update in Task 4.

- [ ] **Step 1.10: §5 opener — M3 rewrite 6 (shifted furthest) + rewrite 7 (matter of magnitude)**

Edit:
```
OLD: The ordering is immediate: IVF/SPEA2 is shifted furthest into IVF-favoring effect sizes, IVF/NSGA-III is positive but weaker, and IVF/NSGA-II remains concentrated around neutrality. The median oriented effect size is about 0.75 for IVF/SPEA2, 0.60 for IVF/NSGA-III, and 0.51 for IVF/NSGA-II, which already suggests that host compatibility is a matter of magnitude as well as win counts.
NEW: The ordering is immediate: IVF/SPEA2's effect-size distribution is shifted most into the IVF-favoring region, IVF/NSGA-III's is positive but weaker, and IVF/NSGA-II's remains concentrated around neutrality. The median oriented effect size is about 0.75 for IVF/SPEA2, 0.60 for IVF/NSGA-III, and 0.51 for IVF/NSGA-II, which indicates that host compatibility manifests in effect-size magnitude, not only in win counts.
```

- [ ] **Step 1.11: §5.1 — M3 rewrite 8 (Fig. 2 moves) + rewrite 9 (never finds)**

Edit:
```
OLD: Figure~\ref{fig:heatmap} moves from aggregate magnitude to the instance level. The same compatibility ranking remains visible, but the figure also reveals where it comes from.
NEW: Figure~\ref{fig:heatmap} disaggregates the aggregate picture to the instance level. The same ranking remains visible, and the figure additionally shows which benchmark families drive it.
```

Edit:
```
OLD: IVF/NSGA-II never finds a family where IVF becomes consistently useful.
NEW: No benchmark family yields a consistent IVF benefit for IVF/NSGA-II.
```

- [ ] **Step 1.12: §5.2 — M3 rewrite 10 (Geometry sharpens where)**

Edit:
```
OLD: Geometry stratification sharpens where the endpoint gains come from.
NEW: Stratifying by Pareto-front geometry clarifies the source of the endpoint gains.
```

- [ ] **Step 1.13: §5.3 — M3 rewrite 11 (sharp asymmetry belongs)**

Edit:
```
OLD: The sharp asymmetry belongs to IVF/NSGA-III: +18/=11/-0 at $M=2$ collapses to +4/=19/-0 at $M=3$.
NEW: The asymmetry is specific to IVF/NSGA-III: 18/11/0 at $M=2$ collapses to 4/19/0 at $M=3$.
```

- [ ] **Step 1.14: §5.4 — M4 rewrite 14 (all-suite aggregate split)**

Edit:
```
OLD: For the all-suite aggregate, each host pair and run is converted into a normalized progress gap between the pair-specific starting state and the best final value reached by either algorithm on that instance.
NEW: For the all-suite aggregate, every run is transformed into a normalized IGD progress gap. The gap is zero at the pair-specific initial state and one at the best final value attained by either algorithm on that instance.
```

- [ ] **Step 1.15: §5.4 Fig. 4 callout — M7 add "early separation" sentence**

Before the paragraph starting "The corresponding $\Delta$AUC summaries…", edit the sentence ending the Figure 4 paragraph to add a pointer:
```
OLD: This removes the instance-selection issue of the six-case block and still preserves the same ordering at the trajectory level: IVF/SPEA2 separates early and stays above its base curve, IVF/NSGA-III is mixed and often overlaps the base, and IVF/NSGA-II shows only mild late gains.
NEW: This removes the instance-selection issue of the six-case block and still preserves the same ordering at the trajectory level: in Figure~\ref{fig:dynamic_aggregate} the IVF/SPEA2 solid curve rises above its dashed SPEA2 baseline within the first 20\% of the evaluation budget and maintains separation to the end, IVF/NSGA-III's curves overlap or cross the base for much of the budget, and IVF/NSGA-II's curves nearly coincide with a small late-stage separation.
```

- [ ] **Step 1.16: §6 opener — M2 compress + rewrite 16**

Edit:
```
OLD: Figures~\ref{fig:a12_strip}, \ref{fig:heatmap}, \ref{fig:m2_vs_m3}, and~\ref{fig:dynamic_aggregate}, together with Table~\ref{tab:hosts_geometry_summary}, support Hypothesis~H at the pipeline level studied here, but they do not by themselves demonstrate that directional feedback is the sole causal mechanism.
NEW: The endpoint, dimensional, and dynamic analyses (Figs.~\ref{fig:a12_strip}--\ref{fig:dynamic_aggregate}; Table~\ref{tab:hosts_geometry_summary}) support Hypothesis~H at the pipeline level. They do not, however, establish directional feedback as the sole causal mechanism.
```

- [ ] **Step 1.17: Verify all Step 1 edits**

Run:
```bash
cd /home/pedro/code/research/ivfspea2
grep -nE 'shifted furthest|matter of magnitude|moves from aggregate|never finds a family|sharpens where|belongs to IVF/NSGA-III|at at most|actionable feedback|canonical implementation in this study|records \+33/=15/-3|\[release\]|\[PlatEMO version\]|\[CPU / RAM / OS\]' paper/ppsn2026-ivf-hosts/main.tex \
  && echo "FAIL: old phrases still present" || echo "PASS"
grep -nE 'directional feedback|published reference implementation|disaggregates the aggregate|clarifies the source|asymmetry is specific|normalized IGD progress gap|achieves 33 wins|\[ARTIFACT_DOI_PENDING\]' paper/ppsn2026-ivf-hosts/main.tex \
  | head -30
```
Expected: first grep prints `PASS`; second grep lists 8+ matches.

- [ ] **Step 1.18: Compile PDF to catch LaTeX breakage**

Run:
```bash
cd /home/pedro/code/research/ivfspea2/paper/ppsn2026-ivf-hosts && latexmk -pdf -pdflatex="pdflatex -interaction=nonstopmode" -outdir=build main.tex
```
Expected: exit 0; `build/main.pdf` regenerated.

- [ ] **Step 1.19: Checkpoint B — user reviews diff**

Show user: `git -C /home/pedro/code/research/ivfspea2 diff paper/ppsn2026-ivf-hosts/main.tex`
Wait for approval.

- [ ] **Step 1.20: Commit Phase 1**

```bash
cd /home/pedro/code/research/ivfspea2
git add paper/ppsn2026-ivf-hosts/main.tex
git commit -m "$(cat <<'EOF'
revision: [passo 11a] critical + major reviewer edits

- C1: fill MATLAB release, PlatEMO version, hardware placeholders; artifact DOI left as sentinel for Phase 6
- M1: abstract switches to wins/ties/losses prose, drops "only"
- M2: compresses pipeline-level caveat in abstract/§3/§6, preserves full statement in §1 and §7
- M3: rewrites six non-native verb/metaphor constructions in §5
- M4: splits overlong sentences in §4 budget-accounting and §5.4 aggregate
- M5: "canonical implementation" → "published reference implementation"
- M6: "actionable" → "directional" throughout
- M7: adds reading pointer to Fig. 4 callout

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

---

## Task 2: Fig. 2 Split by Objective Dimensionality

**Files:**
- Modify: `src/python/analysis/plot_hosts_figures_v2.py` (function `fig2_heatmap`, lines 138–225)
- Regenerate: `paper/ppsn2026-ivf-hosts/figures/hosts_v2_fig2_heatmap.pdf`
- Modify: `paper/ppsn2026-ivf-hosts/main.tex` (Fig. 2 caption)

- [ ] **Step 2.1: Read the full current `fig2_heatmap` implementation**

Run: `Read /home/pedro/code/research/ivfspea2/src/python/analysis/plot_hosts_figures_v2.py` offset 138 limit 90.
Confirm line numbers before editing.

- [ ] **Step 2.2: Replace `fig2_heatmap` with a two-panel version**

Replace the entire `fig2_heatmap` function body with a helper-based two-panel implementation:

```python
def fig2_heatmap(df: pd.DataFrame) -> None:
    family_order = ["DTLZ", "MaF", "WFG", "ZDT"]
    label_order = [label for _, label in TRACKS]

    ordered = df.copy()
    ordered["family_rank"] = ordered["group"].map(
        {fam: idx for idx, fam in enumerate(family_order)}
    )

    m_values = sorted(ordered["M"].unique())  # expected [2, 3]

    fig, axes = plt.subplots(
        nrows=len(m_values),
        ncols=1,
        figsize=(13.8, 3.2 * len(m_values) + 1.0),
        gridspec_kw={"height_ratios": [1.0] * len(m_values)},
    )
    if len(m_values) == 1:
        axes = [axes]

    im = None
    for ax, m_val in zip(axes, m_values):
        sub = ordered[ordered["M"] == m_val]
        instance_order = (
            sub[["problem", "M", "group", "family_rank"]]
            .drop_duplicates()
            .sort_values(["family_rank", "problem"])
        )
        instance_keys = list(zip(instance_order["problem"], instance_order["M"]))
        index = pd.MultiIndex.from_tuples(instance_keys, names=["problem", "M"])

        pivot = sub.pivot_table(
            index=["problem", "M"], columns="label", values="A12_ivf"
        ).reindex(index=index)[label_order]
        sig_pivot = sub.pivot_table(
            index=["problem", "M"], columns="label", values="significant"
        ).reindex(index=index)[label_order]
        group_map = dict(zip(instance_keys, instance_order["group"]))
        col_labels = [problem for problem, _ in instance_keys]
        heat = pivot.values.T
        heat_sig = sig_pivot.values.T

        im = ax.imshow(
            heat,
            aspect="auto",
            cmap=sns.diverging_palette(10, 240, as_cmap=True),
            norm=TwoSlopeNorm(vmin=0.0, vcenter=0.5, vmax=1.0),
            interpolation="nearest",
        )

        for i in range(heat.shape[0]):
            for j in range(heat.shape[1]):
                if bool(heat_sig[i, j]):
                    ax.text(
                        j,
                        i,
                        "*",
                        ha="center",
                        va="center",
                        fontsize=9,
                        fontweight="bold",
                        color="black",
                    )

        prev_group = None
        for j, key in enumerate(instance_keys):
            group = group_map[key]
            if prev_group is not None and group != prev_group:
                ax.axvline(j - 0.5, color="black", linewidth=1.0)
            prev_group = group

        family_spans: dict[str, list[int]] = {}
        for j, key in enumerate(instance_keys):
            group = group_map[key]
            if group not in family_spans:
                family_spans[group] = [j, j]
            family_spans[group][1] = j
        for family, (start, end) in family_spans.items():
            mid = (start + end) / 2
            ax.text(
                mid,
                -0.9,
                family,
                ha="center",
                va="bottom",
                fontsize=9,
                fontweight="bold",
                color=GROUP_COLORS.get(family, "black"),
                clip_on=False,
            )

        ax.set_xticks(range(len(col_labels)))
        ax.set_xticklabels(col_labels, fontsize=7, rotation=90)
        ax.set_yticks(range(len(label_order)))
        ax.set_yticklabels(label_order, fontsize=10)
        ax.set_ylabel(f"$M={m_val}$", fontsize=11, fontweight="bold")

    cbar = fig.colorbar(
        im,
        ax=axes,
        orientation="horizontal",
        fraction=0.04,
        pad=0.12,
        shrink=0.7,
    )
    cbar.set_label(r"$A_{12}^{\mathrm{IVF}}$", fontsize=10)
    cbar.ax.axvline(0.5, color="black", linewidth=0.8)

    save_fig(fig, "hosts_v2_fig2_heatmap.pdf")
    plt.close(fig)
```

Use `Edit` with `old_string` = the entire current function body (lines 138–225) and `new_string` = the block above.

- [ ] **Step 2.3: Regenerate the figure**

Run:
```bash
cd /home/pedro/code/research/ivfspea2 && .venv/bin/python src/python/analysis/plot_hosts_figures_v2.py
```
Expected: console reports `save_fig` writing the PDF; no tracebacks. The file `paper/ppsn2026-ivf-hosts/figures/hosts_v2_fig2_heatmap.pdf` modification time updates.

- [ ] **Step 2.4: Visual validation of the new PDF**

Run: `pdfinfo /home/pedro/code/research/ivfspea2/paper/ppsn2026-ivf-hosts/figures/hosts_v2_fig2_heatmap.pdf | grep -E 'Pages|Page size'`
Expected: 1 page, size consistent with the original figure (within factor of 1.5×). If anomalous (e.g., taller than original), flag to user before continuing.

- [ ] **Step 2.5: Update Fig. 2 caption in `main.tex`**

Edit:
```
OLD: \caption{Instance-level effect sizes across all 51 instances. Each cell shows the oriented $A_{12}^{\mathrm{IVF}}$ for one instance--host pair (blue = IVF benefit, red = IVF harm, white = neutral). Asterisks mark statistically significant cases (Wilcoxon, BH $\alpha=0.05$). Columns are grouped by benchmark family and sorted by $M$.}
NEW: \caption{Per-instance oriented effect size $A_{12}^{\mathrm{IVF}}$ across all 51 instances (rows: three IVF hosts; columns: instances, grouped by family). Top panel: $M=2$ (28 instances); bottom panel: $M=3$ (23 instances). Blue = IVF benefit, red = IVF harm, white = neutrality around $A_{12}^{\mathrm{IVF}}=0.5$. Asterisks mark instances significant under Wilcoxon with BH-FDR correction at $\alpha=0.05$. The IVF/SPEA2 row is dominated by blue cells across all four families; red cells on WFG account for all three IGD losses. IVF/NSGA-III is strongly blue on DTLZ and MaF but near-white on most of WFG. IVF/NSGA-II is near-white across the full suite, with isolated red on ZDT6.}
```

- [ ] **Step 2.6: Rewrite the §5.1 callout to match the new figure**

Edit:
```
OLD: Two family-level patterns stand out. ZDT is the sharpest separator: IVF/SPEA2 wins all five cases, IVF/NSGA-III improves only partially, and IVF/NSGA-II remains neutral. WFG concentrates the difficult cases---all three IVF/SPEA2 IGD losses appear here, and IVF/NSGA-III collapses to +3/=15/-0. IVF/NSGA-II never finds a family where IVF becomes consistently useful.
NEW: Reading the $M=2$ panel (top) and the $M=3$ panel (bottom) separately highlights three patterns. First, the IVF/SPEA2 row is dominated by blue across all four families, with its three IGD losses concentrated on WFG. Second, IVF/NSGA-III is strongly blue on DTLZ and MaF at $M=2$ but collapses to near-white on most of WFG and across most $M=3$ instances, with a WFG tally of 3/15/0. Third, the IVF/NSGA-II row is near-white across the full suite, with isolated red on ZDT6. No benchmark family yields a consistent IVF benefit for IVF/NSGA-II. ZDT is the sharpest separator: IVF/SPEA2 wins all five cases, IVF/NSGA-III improves only partially, and IVF/NSGA-II remains neutral.
```

- [ ] **Step 2.7: Compile PDF**

Run:
```bash
cd /home/pedro/code/research/ivfspea2/paper/ppsn2026-ivf-hosts && latexmk -pdf -pdflatex="pdflatex -interaction=nonstopmode" -outdir=build main.tex
```
Expected: exit 0.

- [ ] **Step 2.8: Checkpoint C — user reviews `hosts_v2_fig2_heatmap.pdf`**

Tell user to open `paper/ppsn2026-ivf-hosts/figures/hosts_v2_fig2_heatmap.pdf` and confirm the two panels are legible and asterisks are visible. If the user rejects the layout (e.g., wants horizontal stacking instead of vertical, or different aspect ratio), tune `figsize` / `height_ratios` and re-run 2.3–2.5.

Wait for approval.

- [ ] **Step 2.9: Commit Phase 2**

```bash
cd /home/pedro/code/research/ivfspea2
git add src/python/analysis/plot_hosts_figures_v2.py \
        paper/ppsn2026-ivf-hosts/figures/hosts_v2_fig2_heatmap.pdf \
        paper/ppsn2026-ivf-hosts/main.tex
git commit -m "$(cat <<'EOF'
revision: [passo 11b] split Fig. 2 heatmap by M

Splits the 51-column heatmap into two stacked panels (M=2 on top, M=3
on bottom) so individual cells and BH asterisks become legible at print
size. Rewrites the caption and §5.1 callout to walk the reader through
each panel. Addresses reviewer's CRITICAL item C2.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: Moderate + Minor Edits + Bibliography DOIs

**Files:**
- Modify: `paper/ppsn2026-ivf-hosts/main.tex`
- Modify: `paper/ppsn2026-ivf-hosts/references.bib`

- [ ] **Step 3.1: Mo1 — split §1 IVF genealogy sentence**

Edit:
```
OLD: IVF was first proposed as a multi-objective hybrid inspired by in vitro fertilization~\cite{camilo-junior2011} and later adapted as an operator for NSGA-II~\cite{sampaio2017ivf}, extended toward many-objective settings~\cite{sampaio2019ivf}, specialized for NSGA-III~\cite{Sampaio2024}, and recently redesigned for SPEA2~\cite{zambrano2026ivfspea2}.
NEW: IVF was first proposed as a multi-objective hybrid inspired by in vitro fertilization~\cite{camilo-junior2011}. It was subsequently adapted as an operator for NSGA-II~\cite{sampaio2017ivf}, extended to many-objective settings~\cite{sampaio2019ivf}, specialized for NSGA-III~\cite{Sampaio2024}, and most recently redesigned for SPEA2~\cite{zambrano2026ivfspea2}.
```

- [ ] **Step 3.2: Mo2 + Mo4 — remove §2.2 and §3 overlap with §1**

Edit §2.2 opening:
```
OLD: The IVF family originates from hybrid evolutionary search inspired by the fertilization process~\cite{camilo-junior2011}. Across variants, the common core is short-cycle intensification: select promising mothers, pair them with fathers, generate intensified offspring, and repeat for a limited number of cycles while a continuation criterion is satisfied~\cite{sampaio2017ivf,sampaio2019ivf,Sampaio2024,zambrano2026ivfspea2}. What changes across hosts is how mothers and fathers are chosen, how continuation is judged, and how the host absorbs the intensified offspring.
NEW: Across IVF variants, the shared core is short-cycle intensification: a subset of promising \emph{mothers} (top-ranked candidates under the host's selection order) is paired with \emph{fathers} (a second sampled parent population), intensified offspring are generated by a crossover operator, and the cycle repeats for a limited number of rounds while a continuation criterion is satisfied~\cite{sampaio2017ivf,sampaio2019ivf,Sampaio2024,zambrano2026ivfspea2}. What changes across hosts is how mothers and fathers are chosen, how continuation is judged, and how the host absorbs the intensified offspring.
```
(This also covers Mo3 — the inline gloss on "mothers/fathers".)

Edit §3 intro paragraph (kept short since Table 1 carries the structure):
```
OLD: The three implementations studied here share the same macro-structure: a top-ranked fraction of the current population is selected as mothers, IVF cycles generate intensified offspring, and the host survival mechanism reinserts those offspring. The relevant differences concern father selection, offspring generation, continuation, and activation budget.
NEW: The three implementations studied here inherit the shared macro-structure summarized in Section~\ref{sec:ivf_family}. They differ in four design axes: father selection, offspring generation, continuation criterion, and activation budget. Table~\ref{tab:adaptations} gives the full breakdown.
```

- [ ] **Step 3.3: Mo5 — Table 1 header clarity + rewording + name consistency**

Edit Table 1 row labels:
```
OLD: Offspring operator & SBX, $\eta_c=20$ & SBX, $\eta_c=15$ & DE/current-to-best \\
NEW: Offspring generation & SBX ($\eta_c=20$) & SBX ($\eta_c=15$) & DE/current-to-best \\
```

Also normalize the column header name to match body-text usage:
```
OLD: \textbf{IVF/SPEA2-v2}
NEW: \textbf{IVF/SPEA2 v2}
```

- [ ] **Step 3.4: Mo6 — §5 opener**

Edit:
```
OLD: Figure~\ref{fig:a12_strip} gives the global picture before the per-host breakdown.
NEW: At the aggregate level, the three pipelines already separate by a large margin (Fig.~\ref{fig:a12_strip}).
```

- [ ] **Step 3.5: Mo7 — §5.4 rewrite 15 reorder**

Edit:
```
OLD: IVF/NSGA-II is no longer completely inert under this aggregate view, but its gains remain modest and concentrated on regular fronts relative to IVF/SPEA2 (for example, IGD $+0.038$ and HV $+0.056$ on regular $M=2$).
NEW: Under the aggregate view, IVF/NSGA-II is no longer completely inert; its gains, however, are small and restricted to regular fronts, in contrast to IVF/SPEA2 (for example, IGD $+0.038$ and HV $+0.056$ on regular $M=2$).
```

- [ ] **Step 3.6: Mo8 — §6 material → relevant**

Edit:
```
OLD: Three threats to validity remain material.
NEW: Three threats to validity remain relevant.
```

- [ ] **Step 3.7: Mo9 — §7 drop "practically useful"**

Edit:
```
OLD: Under that scope, the evidence is consistent and practically useful:
NEW: Under that scope, the evidence is consistent:
```

- [ ] **Step 3.8: Rewrite 12 — §5.3 "indicating that host mechanism"**

Edit:
```
OLD: indicating that the host mechanism governs whether IVF can still identify useful search directions as the objective space expands.
NEW: indicating that the host's selection mechanism determines whether IVF can still produce useful search directions in higher-dimensional objective space.
```

- [ ] **Step 3.9: Rewrite 17 — §6 "hosts offering"**

Edit:
```
OLD: A plausible interpretation is that hosts offering more explicit directional information in objective space make it easier for the IVF core to convert local intensification into offspring that survive environmental selection.
NEW: A plausible interpretation is that hosts providing more explicit directional information in objective space enable the IVF core to convert local intensification into offspring that survive environmental selection.
```

- [ ] **Step 3.10: Rewrite 13 — §5.4 "aggregate view confirmatory"**

Edit:
```
OLD: The aggregate view is the confirmatory dynamic layer, while the six-instance traces remain explanatory case studies.
NEW: The aggregate view serves as the primary dynamic evidence; the six-instance traces serve as diagnostic case studies.
```

- [ ] **Step 3.11: Rewrite 20 — §7 final paragraph split**

Edit:
```
OLD: The full per-instance median/IQR tables for all 51 instances (IGD and HV, by host and $M$), the complete endpoint robustness analyses, the geometry labels and geometry-stratified summaries, the FE-accounting audit, the full paired dynamic-test tables, and the dynamic-selection diagnostics are archived in an auditable artifact at \texttt{[artifact URL or DOI]}. The main text reports only compact summaries; all machine-readable CSV files and figure-generation scripts required to reproduce those summaries are included in the same artifact.
NEW: The archived artifact contains the full per-instance median/IQR tables for all 51 instances (IGD and HV, by host and $M$), the endpoint robustness analyses, the geometry labels and stratified summaries, the FE-accounting audit, the paired dynamic-test tables, and the dynamic-selection diagnostics. All machine-readable CSV files and figure-generation scripts needed to reproduce the summaries reported in the main text are included in the same artifact at \texttt{[ARTIFACT_DOI_PENDING]}.
```

- [ ] **Step 3.12: Mo10 — tense unification in §4**

Find and replace any remaining tense inconsistencies. Current text: "All experiments were conducted", "runs were executed", "are archived" — this is already consistent. Confirm via:
```bash
grep -nE 'were conducted|were executed|are archived|was conducted|was executed' /home/pedro/code/research/ivfspea2/paper/ppsn2026-ivf-hosts/main.tex
```
If `was` forms appear, replace with `were`. If only `were` + `are` forms appear, no edit needed.

- [ ] **Step 3.13: Minor — §3 section title**

Edit:
```
OLD: \section{IVF Adaptations}
NEW: \section{Host-Specific IVF Realizations}
```

- [ ] **Step 3.14: Minor — §5.3 subsection title**

Edit:
```
OLD: \subsection{Dimensional Asymmetry}
NEW: \subsection{Effect of Objective Dimensionality}
```

- [ ] **Step 3.15: Minor — `Cycles=2` spacing**

Run:
```bash
grep -nE 'Cycles=[0-9]' /home/pedro/code/research/ivfspea2/paper/ppsn2026-ivf-hosts/main.tex
```
For each match of the form `\textit{Cycles}=N`, replace with `\textit{Cycles} = N`. Apply via `Edit` with `replace_all=true` on the exact token.

- [ ] **Step 3.16: Rewrite 2 — §1 "common IVF core is stable"**

Edit:
```
OLD: Across these variants, the common IVF core is stable: select a subset of promising individuals, pair them, generate intensified offspring through a short internal reproduction cycle, and transfer those offspring back to the host population.
NEW: Across these variants, the IVF core is shared: select a subset of promising individuals, pair them, generate intensified offspring through a short internal reproduction cycle, and transfer those offspring back to the host population.
```

- [ ] **Step 3.17: `references.bib` — add DOI to ref [20]**

Open `paper/ppsn2026-ivf-hosts/references.bib`, locate the `@…{zambrano2026ivfspea2, …}` entry, and add:
```
doi    = {10.21203/rs.3.rs-9431034/v1},
note   = {Research Square preprint},
```
If the entry currently points to a GitHub URL in `url = {...}`, keep the `url` field but let the `doi` field take precedence in the bibliography style.

- [ ] **Step 3.18: Optional — DOIs for refs [5] and [9]**

Try to find Crossref DOIs:
- Ref [5] Cheng et al. MaF — Complex & Intelligent Systems 2017. Search: `curl -s "https://api.crossref.org/works?query.bibliographic=Benchmark+Many-Objective+Optimization+Problems+MaF&rows=3" | python -c "import json,sys; [print(w.get('DOI'), w.get('title',[''])[0]) for w in json.load(sys.stdin)['message']['items']]"`
- Ref [9] Deb et al. DTLZ — Scalable test problems for evolutionary multi-objective optimization 2005 chapter in Evolutionary Multiobjective Optimization.

If a DOI is found, add a `doi = {...}` field. If not found, skip — these are minor items.

- [ ] **Step 3.19: Verify + compile**

Run:
```bash
cd /home/pedro/code/research/ivfspea2/paper/ppsn2026-ivf-hosts && latexmk -pdf -pdflatex="pdflatex -interaction=nonstopmode" -outdir=build main.tex
```
Run:
```bash
grep -nE '\\section\{IVF Adaptations\}|\\subsection\{Dimensional Asymmetry\}|common IVF core is stable|remain material|practically useful|moves from aggregate|host mechanism governs|hosts offering|confirmatory dynamic layer' /home/pedro/code/research/ivfspea2/paper/ppsn2026-ivf-hosts/main.tex \
  && echo "FAIL: old titles/phrases still present" || echo "PASS"
```
Expected: compilation succeeds; grep prints `PASS`.

- [ ] **Step 3.20: Checkpoint D — user reviews diff**

Show: `git -C /home/pedro/code/research/ivfspea2 diff paper/ppsn2026-ivf-hosts/`
Wait for approval.

- [ ] **Step 3.21: Commit Phase 3**

```bash
cd /home/pedro/code/research/ivfspea2
git add paper/ppsn2026-ivf-hosts/main.tex paper/ppsn2026-ivf-hosts/references.bib
git commit -m "$(cat <<'EOF'
revision: [passo 11c] moderate/minor edits and bibliography DOIs

- Mo1-Mo10: sentence splits, redundancy removal, mothers/fathers gloss, tense unification
- Rewrites 2, 12, 13, 17, 20 from reviewer Part 5.3
- §3 retitled "Host-Specific IVF Realizations"; §5.3 retitled "Effect of Objective Dimensionality"
- Table 1 header tightened; Cycles spacing unified
- references.bib: DOI added to zambrano2026ivfspea2; Crossref DOIs added for MaF/DTLZ where available

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

---

## Task 4: Figure Captions + §5 Callouts

**Files:**
- Modify: `paper/ppsn2026-ivf-hosts/main.tex`

- [ ] **Step 4.1: Fig. 1 caption — add reading guidance**

Edit:
```
OLD: \caption{Oriented effect size $A_{12}^{\mathrm{IVF}}$ for each instance across the three hosts. Values above 0.5 favor the IVF variant. Shaded bands mark small (0.56), medium (0.64), and large (0.71) effect thresholds. Horizontal bars indicate the median per host. Points are colored by benchmark family; circles denote $M=2$, triangles $M=3$.}
NEW: \caption{Oriented Vargha--Delaney effect size $A_{12}^{\mathrm{IVF}}$ per instance for each host (51 instances; 30 runs each). Orientation: $A_{12}^{\mathrm{IVF}}>0.5$ favors the IVF variant, $=0.5$ is neutral, $<0.5$ favors the base host. Green/red shaded bands mark small (0.56), medium (0.64), and large (0.71) thresholds. Horizontal bars are per-host medians. Markers: $\bullet$ $M=2$, $\blacktriangle$ $M=3$; colors encode benchmark family. Reading cue: the vertical centre of mass of each host's cloud is near 0.75 for IVF/SPEA2, 0.60 for IVF/NSGA-III, and 0.51 for IVF/NSGA-II.}
```

- [ ] **Step 4.2: Fig. 3 caption — quantify the collapse**

Edit:
```
OLD: \caption{Effect-size distribution by number of objectives. IVF/NSGA-III collapses from robust benefit at $M=2$ to near-neutrality at $M=3$. IVF/SPEA2 remains strong in both cases. IVF/NSGA-II is neutral regardless of~$M$.}
NEW: \caption{Oriented IGD effect size $A_{12}^{\mathrm{IVF}}$ split by number of objectives. At $M=2$ (left), all three hosts produce distinct distributions; at $M=3$ (right), IVF/NSGA-III collapses toward the IVF/NSGA-II distribution (median drops from $\approx 0.70$ to $\approx 0.54$), while IVF/SPEA2's distribution is largely preserved. IVF/NSGA-II remains near-neutral at both dimensionalities. Markers colored by benchmark family.}
```

- [ ] **Step 4.3: Fig. 4 (dynamic aggregate) caption — add reading cue**

Edit:
```
OLD: \caption{All-suite dynamic aggregate over the 51-instance trace cohort. For each host pair, the curves show the fraction of runs whose cumulative-best IGD reaches a normalized gap of at most $\tau=0.1$ as a function of FE / maxFE. The gap is normalized per instance against the pair-specific initial state and the best final value attained by either algorithm. Shaded bands show 95\% bootstrap confidence intervals.}
NEW: \caption{All-suite dynamic aggregate over the 51-instance trace cohort. Each curve shows the fraction of runs whose cumulative-best IGD has reached a normalized gap of at most $\tau=0.1$ (gap normalized per instance against the pair-specific initial state and the best final value attained by either algorithm) as a function of FE / maxFE. Solid lines: IVF variant; dashed lines: base host. Shaded bands: 95\% bootstrap confidence intervals. Early separation (FE / maxFE $< 0.3$) indicates the IVF variant reaches near-final quality on a larger fraction of runs sooner.}
```

- [ ] **Step 4.4: Fig. 5 (convergence, six panels) caption — tighten**

Edit:
```
OLD: \caption{IGD ratio (base~/~IVF) over normalized function evaluations on six protocol-defined dynamic instances. Values above~1 indicate IVF benefit (green shading); below~1 indicate harm (red shading). FE grids are aligned by linear interpolation when necessary, and shaded bands show 95\% bootstrap confidence intervals over 30 aligned runs.}
NEW: \caption{IGD ratio (base~/~IVF) over normalized function evaluations on the six protocol-defined dynamic instances. Values $>1$ (green shading) indicate IVF benefit; values $<1$ (red shading) indicate harm. Solid lines: host-wise medians across 30 runs per algorithm per instance. Shaded bands: 95\% bootstrap confidence intervals. FE grids aligned by linear interpolation when saved checkpoints are not exactly aligned across runs. Reading cue: each panel shows how early the colored line crosses 1 and how long it stays above --- IVF/SPEA2 shows early, large ratios on DTLZ5 and ZDT4 and a sub-1 excursion on WFG2.}
```

- [ ] **Step 4.5: Verify all caption edits**

Run:
```bash
grep -nE 'vertical centre of mass|collapses toward the IVF/NSGA-II distribution|Early separation \(FE|Reading cue: each panel' /home/pedro/code/research/ivfspea2/paper/ppsn2026-ivf-hosts/main.tex
```
Expected: four matches.

- [ ] **Step 4.6: Compile PDF to catch LaTeX errors in math mode inside captions**

Run:
```bash
cd /home/pedro/code/research/ivfspea2/paper/ppsn2026-ivf-hosts && latexmk -pdf -pdflatex="pdflatex -interaction=nonstopmode" -outdir=build main.tex
```
Expected: exit 0. If errors: `$\blacktriangle$` requires `amssymb` (already included) — if it still fails, replace with `$\vartriangle$`.

- [ ] **Step 4.7: Commit caption phase**

```bash
cd /home/pedro/code/research/ivfspea2
git add paper/ppsn2026-ivf-hosts/main.tex
git commit -m "$(cat <<'EOF'
revision: [passo 11d-captions] rewrite figure captions per reviewer Part 4

Figure 1, 3, 4, 5 captions now self-contained: define orientation of
A12^IVF, quantify the M=3 collapse for IVF/NSGA-III, add reading cues
about early separation in the dynamic aggregate and panel reading in
the convergence ratio plot.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

---

## Task 5: Cross-Section Transitions

**Files:**
- Modify: `paper/ppsn2026-ivf-hosts/main.tex`

- [ ] **Step 5.1: §3 → §4 bridge**

Find the final sentence of §3 ending "...held identical across hosts." (post-Step-1.6 wording). Append the bridge sentence to that paragraph (same line, followed by a real newline that already exists before `\section{Experimental Setup}`):

Use `Edit` with
- `old_string` = `held identical across hosts.`
- `new_string` = `held identical across hosts. With the pipelines specified, we now turn to the experimental protocol under which they are compared.`

- [ ] **Step 5.2: §5.3 → §5.4 bridge**

Find the last sentence of §5.3 ending "...in higher-dimensional objective space." (post-Step-3.8 wording). Append the bridge:

Use `Edit` with
- `old_string` = `in higher-dimensional objective space.`
- `new_string` = `in higher-dimensional objective space. Endpoint analyses alone, however, cannot indicate whether the observed ordering also holds during the search rather than only at its termination.`

- [ ] **Step 5.3: §5 → §6 bridge**

The last sentence of §5 is the cross-host-ranking paragraph followed by `\input{../../results/tables/hosts_a12_summary.tex}`. Insert the bridge between the `\input{...}` and the `\FloatBarrier`/`\section{Discussion}` block. Use `Edit` with

- `old_string` = `\input{../../results/tables/hosts_a12_summary.tex}`
- `new_string` = `\input{../../results/tables/hosts_a12_summary.tex}

We now turn from what the evidence shows to what it licenses as interpretation.`

(Note: the `new_string` contains a real blank line before the sentence. If the Edit tool rejects multi-line new_string with a blank line, split into two edits: delete the `\FloatBarrier` line, re-insert it after the bridge sentence.)

- [ ] **Step 5.4: Verify**

Run:
```bash
grep -nE 'we now turn to the experimental protocol|cannot indicate whether the observed ordering|what it licenses as interpretation' /home/pedro/code/research/ivfspea2/paper/ppsn2026-ivf-hosts/main.tex
```
Expected: three matches.

- [ ] **Step 5.5: Compile + Checkpoint E**

```bash
cd /home/pedro/code/research/ivfspea2/paper/ppsn2026-ivf-hosts && latexmk -pdf -pdflatex="pdflatex -interaction=nonstopmode" -outdir=build main.tex
```
Show user: `git -C /home/pedro/code/research/ivfspea2 diff paper/ppsn2026-ivf-hosts/main.tex` (captures Tasks 4 + 5).
Wait for approval.

- [ ] **Step 5.6: Commit transitions**

```bash
cd /home/pedro/code/research/ivfspea2
git add paper/ppsn2026-ivf-hosts/main.tex
git commit -m "$(cat <<'EOF'
revision: [passo 11d-transitions] cross-section bridges §3→§4, §5.3→§5.4, §5→§6

Each bridge is a single sentence that states why the next section is
necessary given what was just shown.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

---

## Task 6: Zenodo Archive Preparation & DOI Mint

**Files:**
- Create: `artifact/ppsn2026-ivf-hosts-rev1/README.md`
- Create: `artifact/zenodo-metadata.json`
- Create: `artifact/github-release-notes.md`
- Create: `artifact/ppsn2026-ivf-hosts-rev1.zip`
- Modify: `paper/ppsn2026-ivf-hosts/main.tex` (fill DOI sentinel after mint)

- [ ] **Step 6.1: Create staging directory**

```bash
mkdir -p /home/pedro/code/research/ivfspea2/artifact/ppsn2026-ivf-hosts-rev1/{data,tables,figures,scripts}
```

- [ ] **Step 6.2: Copy processed data**

```bash
cd /home/pedro/code/research/ivfspea2
cp data/processed/hosts_paper.csv artifact/ppsn2026-ivf-hosts-rev1/data/
cp data/processed/hosts_convergence.csv artifact/ppsn2026-ivf-hosts-rev1/data/
```

- [ ] **Step 6.3: Copy LaTeX tables and CSV summaries referenced by the paper**

```bash
cd /home/pedro/code/research/ivfspea2
cp results/tables/hosts_*.tex artifact/ppsn2026-ivf-hosts-rev1/tables/
cp results/tables/hosts_*.csv artifact/ppsn2026-ivf-hosts-rev1/tables/
```

- [ ] **Step 6.4: Copy figure PDFs**

```bash
cd /home/pedro/code/research/ivfspea2
cp paper/ppsn2026-ivf-hosts/figures/hosts_v2_fig1_a12_strip.pdf \
   paper/ppsn2026-ivf-hosts/figures/hosts_v2_fig2_heatmap.pdf \
   paper/ppsn2026-ivf-hosts/figures/hosts_v2_fig3_m2_vs_m3.pdf \
   paper/ppsn2026-ivf-hosts/figures/hosts_v2_fig4_convergence.pdf \
   paper/ppsn2026-ivf-hosts/figures/hosts_v2_fig5_dynamic_aggregate.pdf \
   artifact/ppsn2026-ivf-hosts-rev1/figures/
```

- [ ] **Step 6.5: Copy Python analysis scripts**

```bash
cd /home/pedro/code/research/ivfspea2
cp src/python/analysis/build_hosts_paper_csv.py \
   src/python/analysis/build_hosts_convergence_csv.py \
   src/python/analysis/build_hosts_rep_endpoint_table.py \
   src/python/analysis/compute_hosts_tables.py \
   src/python/analysis/compute_hosts_geometry_stratified.py \
   src/python/analysis/compute_hosts_dynamic_aggregate.py \
   src/python/analysis/compute_hosts_pairing_robustness.py \
   src/python/analysis/plot_hosts_figures_v2.py \
   src/python/analysis/plot_hosts_results.py \
   src/python/analysis/plot_hosts_convergence_v2.py \
   artifact/ppsn2026-ivf-hosts-rev1/scripts/
cp requirements.txt artifact/ppsn2026-ivf-hosts-rev1/scripts/
```

- [ ] **Step 6.6: Write reproducibility README**

Create `artifact/ppsn2026-ivf-hosts-rev1/README.md` with:
```markdown
# PPSN 2026 — Operator-Host Compatibility for IVF Intensification
## Reproducibility Artifact (rev1)

This archive accompanies the paper:
> Pedro Sanches Zambrano. *Operator-Host Compatibility in Multi-Objective
> Intensification: IVF Across SPEA2, NSGA-II, and NSGA-III.* PPSN 2026.

## Contents

- `data/hosts_paper.csv` — per-run endpoint metrics (IGD, HV) for the 51 synthetic benchmark instances, three IVF variants, three base hosts, 30 runs each.
- `data/hosts_convergence.csv` — per-checkpoint trajectories for the dynamic block.
- `tables/hosts_*.tex`, `tables/hosts_*.csv` — LaTeX and CSV forms of every table, median/IQR summary, and permutation/BH diagnostic reported or archived by the paper.
- `figures/*.pdf` — final figure PDFs as they appear in the paper (Fig. 1–5).
- `scripts/*.py` — Python analysis and figure-generation scripts. The entry points are `build_hosts_paper_csv.py` (rebuilds the endpoint CSV from raw `.mat` files, not included here due to size) and `plot_hosts_figures_v2.py` (regenerates Fig. 1–3 from `hosts_paper.csv`).

## Reproducing the summaries

With Python 3.11+ and the dependencies in `scripts/requirements.txt`:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r scripts/requirements.txt
python scripts/compute_hosts_tables.py          # regenerates tables/
python scripts/plot_hosts_figures_v2.py          # regenerates figures/
```

All tables and figures in the paper are produced deterministically from `data/hosts_paper.csv` (endpoint) and `data/hosts_convergence.csv` (dynamic).

## Raw MATLAB runs

The raw `.mat` traces (runs 3001–3030 IVF/SPEA2, 4001–4030 NSGA-II/IVF-NSGA-II, 5001–5030 NSGA-III/IVF-NSGA-III) are not included because of file-size constraints. They are available on request from the corresponding author and archived separately at the same Zenodo record (parent DOI).

## Citation

If you use this artifact, please cite the paper and this Zenodo record.

## License

Code: MIT. Data: CC-BY-4.0.
```

- [ ] **Step 6.7: Write Zenodo metadata draft**

Create `artifact/zenodo-metadata.json`:
```json
{
  "metadata": {
    "title": "Operator-Host Compatibility for IVF Intensification — PPSN 2026 reproducibility artifact (rev1)",
    "upload_type": "dataset",
    "description": "Reproducibility artifact for the PPSN 2026 paper 'Operator-Host Compatibility in Multi-Objective Intensification: IVF Across SPEA2, NSGA-II, and NSGA-III'. Contains the processed per-run endpoint metrics, dynamic trajectories, LaTeX tables, figure PDFs, and Python analysis scripts needed to reproduce every summary reported in the paper.",
    "creators": [
      {
        "name": "Zambrano, Pedro Henrique Sanches Pelegrino",
        "affiliation": "Institute of Informatics, Federal University of Goiás",
        "orcid": "<ORCID_IF_AVAILABLE>"
      }
    ],
    "keywords": [
      "multi-objective evolutionary algorithms",
      "intensification",
      "IVF operator",
      "SPEA2",
      "NSGA-II",
      "NSGA-III",
      "reproducibility",
      "PlatEMO"
    ],
    "license": "CC-BY-4.0",
    "related_identifiers": [
      {
        "identifier": "10.21203/rs.3.rs-9431034/v1",
        "relation": "isDerivedFrom",
        "resource_type": "publication-preprint"
      }
    ]
  }
}
```

- [ ] **Step 6.8: Write GitHub Release notes draft**

Create `artifact/github-release-notes.md`:
```markdown
# ppsn2026-ivf-hosts-rev1

Reproducibility artifact snapshot accompanying the revised PPSN 2026 submission *Operator-Host Compatibility in Multi-Objective Intensification: IVF Across SPEA2, NSGA-II, and NSGA-III*.

This release freezes the repository state at the point of manuscript submission for archival via Zenodo.

## Included

- `artifact/ppsn2026-ivf-hosts-rev1.zip` — processed CSVs, LaTeX tables, figure PDFs, and Python analysis scripts sufficient to reproduce all reported summaries.
- `paper/ppsn2026-ivf-hosts/main.tex` — final manuscript source.
- `src/python/analysis/` — full analysis pipeline source.

## Not included

Raw MATLAB `.mat` traces (runs 3001–3030, 4001–4030, 5001–5030) are omitted due to size and are available on request.

## Zenodo

This tag is linked to a Zenodo record; the minted DOI appears on Zenodo and is cited in the manuscript.
```

- [ ] **Step 6.9: Zip the bundle**

```bash
cd /home/pedro/code/research/ivfspea2/artifact
zip -r ppsn2026-ivf-hosts-rev1.zip ppsn2026-ivf-hosts-rev1/
ls -la ppsn2026-ivf-hosts-rev1.zip
```

- [ ] **Step 6.10: `.gitignore` the heavy artifact zip if desired**

```bash
cd /home/pedro/code/research/ivfspea2
grep -q "^artifact/\*\.zip$" .gitignore || echo "artifact/*.zip" >> .gitignore
```

- [ ] **Step 6.11: Commit bundle contents (tracked files only)**

```bash
cd /home/pedro/code/research/ivfspea2
git add artifact/ppsn2026-ivf-hosts-rev1/ artifact/zenodo-metadata.json artifact/github-release-notes.md .gitignore
git commit -m "$(cat <<'EOF'
revision: [passo 11e] stage Zenodo reproducibility artifact

Contents: processed CSVs (hosts_paper, hosts_convergence), all results
tables and CSVs, the five paper figure PDFs, and the Python analysis /
figure scripts needed to regenerate every summary in the paper.

Release notes and Zenodo metadata draft are committed alongside the
bundle. The zip itself is gitignored and prepared at
artifact/ppsn2026-ivf-hosts-rev1.zip for upload.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

- [ ] **Step 6.12: Checkpoint F — user actions (out-of-loop)**

Tell user:

1. Push the commit: `git push origin ppsn2026-population-dynamics`.
2. On GitHub: Releases → Draft a new release → tag `ppsn2026-ivf-hosts-rev1` on branch `ppsn2026-population-dynamics`, paste `artifact/github-release-notes.md` as description, attach `artifact/ppsn2026-ivf-hosts-rev1.zip` as release asset, publish.
3. If Zenodo GitHub integration is already authorized for the repo, the DOI mints automatically within a few minutes at `https://zenodo.org/account/settings/github/`. Otherwise, log in to Zenodo, authorize the repo, then re-create the release (or manually upload the zip via Zenodo's New Upload with the metadata from `artifact/zenodo-metadata.json`).
4. Report the minted DOI back to me (e.g., `10.5281/zenodo.XXXXXXX`).

Wait for the DOI.

- [ ] **Step 6.13: Fill the DOI into `main.tex`**

Once user provides `<ZENODO_DOI>`:
```
OLD: \texttt{[ARTIFACT_DOI_PENDING]}
NEW: \url{https://doi.org/<ZENODO_DOI>}
```
Apply with `replace_all=true` (two occurrences: §4 and §7).

If the llncs style prefers a `\cite`-based reference, instead:
- Add a new `@misc{zenodo_ppsn2026_ivf_hosts, ...}` entry to `references.bib` pointing to the DOI.
- Replace the two `\texttt{[ARTIFACT_DOI_PENDING]}` with `\cite{zenodo_ppsn2026_ivf_hosts}`.

Choose the `\url`-based form by default (simpler, avoids a near-empty bib entry).

- [ ] **Step 6.14: Verify no placeholder remains**

```bash
grep -nE '\[ARTIFACT_DOI_PENDING\]|\[release\]|\[PlatEMO version\]|\[CPU / RAM / OS\]|\[artifact URL or DOI\]' /home/pedro/code/research/ivfspea2/paper/ppsn2026-ivf-hosts/main.tex \
  && echo "FAIL: placeholder remains" || echo "PASS"
```
Expected: `PASS`.

- [ ] **Step 6.15: Compile + commit DOI fill**

```bash
cd /home/pedro/code/research/ivfspea2/paper/ppsn2026-ivf-hosts && latexmk -pdf -pdflatex="pdflatex -interaction=nonstopmode" -outdir=build main.tex
cd /home/pedro/code/research/ivfspea2
git add paper/ppsn2026-ivf-hosts/main.tex paper/ppsn2026-ivf-hosts/references.bib 2>/dev/null
git commit -m "$(cat <<'EOF'
revision: [passo 11f] fill artifact DOI into manuscript

Zenodo record minted from the `ppsn2026-ivf-hosts-rev1` GitHub release
now resolves the reproducibility-artifact pointer in §4 and §7.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

---

## Task 7: Verification & Final Sign-off

**Files:** read-only except for any last patches.

- [ ] **Step 7.1: Final PDF compile**

```bash
cd /home/pedro/code/research/ivfspea2/paper/ppsn2026-ivf-hosts && latexmk -pdf -pdflatex="pdflatex -interaction=nonstopmode" -outdir=build main.tex
```
Expected: exit 0. Record total page count: `pdfinfo build/main.pdf | grep Pages`.

- [ ] **Step 7.2: LaTeX warnings sweep**

```bash
grep -iE 'warning|undefined|overfull|underfull' /home/pedro/code/research/ivfspea2/paper/ppsn2026-ivf-hosts/build/main.log | head -30
```
Classify:
- Undefined references → fix before proceeding.
- Overfull `\hbox` >5pt → manually adjust sentence; overfull ≤5pt → accept.
- Underfull warnings → accept unless visually ugly.

- [ ] **Step 7.3: Placeholder sweep**

```bash
grep -nE '\[.*\]' /home/pedro/code/research/ivfspea2/paper/ppsn2026-ivf-hosts/main.tex | grep -vE '\\\\(cite|ref|bibliographystyle|includegraphics|hypersetup|titlerunning|authorrunning|keywords|paragraph|label|input|usepackage|documentclass|cite\{)'
```
Expected: empty output. Any matches are legitimate bracketed math (e.g., `[tbp]` in `\begin{figure}[tbp]`) — audit manually if uncertain.

- [ ] **Step 7.4: Ligature sweep on final PDF**

```bash
pdftotext -layout /home/pedro/code/research/ivfspea2/paper/ppsn2026-ivf-hosts/build/main.pdf - \
  | grep -nE 'dierent|intensication|eect|conrmatory|dicult|simpli |sucient|specic' \
  || echo "LIGATURES OK"
```
Expected: `LIGATURES OK`.

- [ ] **Step 7.5: Hedge-word preservation check**

Confirm the reviewer's "do not silently strengthen claims" invariant holds by checking that hedge vocabulary density is unchanged or increased:
```bash
grep -cE '\bsuggests?\b|\bsuggestive\b|\bplausible\b|\bconditional\b|\bdirectionally\b|\bmay\b|\bshould be read\b|\bnot yet\b|\bremain material|\bremain relevant|\bremains suggestive\b' /home/pedro/code/research/ivfspea2/paper/ppsn2026-ivf-hosts/main.tex
```
Compare to `git show HEAD~10:paper/ppsn2026-ivf-hosts/main.tex | grep -cE '…'` (same pattern, against the pre-revision tag `a41455b`). Report both counts. New count should be ≥ old count.

- [ ] **Step 7.6: Full diff review**

```bash
git -C /home/pedro/code/research/ivfspea2 diff a41455b -- paper/ppsn2026-ivf-hosts/main.tex | wc -l
git -C /home/pedro/code/research/ivfspea2 diff a41455b -- paper/ppsn2026-ivf-hosts/main.tex | head -400
```
Walk the diff top-to-bottom, confirm each changed line maps to a plan step.

- [ ] **Step 7.7: Float overflow visual inspection**

Open the PDF (user action, `xdg-open build/main.pdf` from the paper directory) and confirm:
- No table/figure exceeds `\textwidth`.
- No figure or table appears orphaned on its own page after its reference.
- Fig. 2 two-panel layout renders correctly at print size.

- [ ] **Step 7.8: Checkpoint G — final sign-off commit**

If Steps 7.1–7.7 all pass, create a final sign-off commit (empty or tagging):
```bash
cd /home/pedro/code/research/ivfspea2
git tag -a ppsn2026-ivf-hosts-reviewer-rev1 -m "Reviewer revision complete; PDF clean; DOI attached."
git log --oneline -10
```

Report to user:
```
Revision complete.
  Pages      : <N>
  Diff lines : <N>
  Ligatures  : OK
  Placeholders: none
  Zenodo DOI : 10.5281/zenodo.<N>
  Tag        : ppsn2026-ivf-hosts-reviewer-rev1
```

---

## Self-Review Checklist (run before handoff)

- [ ] Every reviewer CRITICAL (C1, C2) has a task step.
- [ ] Every reviewer MAJOR (M1–M7) has a task step.
- [ ] Every reviewer MODERATE (Mo1–Mo10) has a task step.
- [ ] Every reviewer Minor item has either a task step or an explicit "skipped because" note.
- [ ] Every reviewer Figure-caption rewrite (Figs. 1–5) has a task step.
- [ ] Every reviewer rewrite 1–20 in Part 5.3 has a task step or is obviated by a larger rewrite.
- [ ] Cross-section transitions §3→§4, §5.3→§5.4, §5→§6 are all scripted.
- [ ] Zenodo DOI appears in both §4 and §7 after Task 6.
- [ ] No step uses a placeholder (TBD, etc.) except the designed `[ARTIFACT_DOI_PENDING]` sentinel, which Task 6 resolves.
- [ ] Each task ends with a commit command.
- [ ] No hedge word is stripped in any task's `new_string`.
