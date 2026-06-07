# PPSN 2026 — Final-Decision Reviews (verbatim)

**Paper:** Operator-Host Compatibility in Multi-Objective Intensification: IVF Across SPEA2, NSGA-II, and NSGA-III
**Decision:** **ACCEPTED** for the Conference Proceedings (camera-ready).
**Decision e-mail:** 2026-05-27, PPSN Organizing Committee (`ppsn2026@unitn.it`).
**Source:** `~/Downloads/[PPSN 2026] Final decision ...IVF Across SPEA2, NSGA-II, and NSGA-III.eml`

## Hard constraints from the acceptance letter

- **Camera-ready deadline: 2026-06-12, End-of-Day AoE — mandatory.**
- **Page limit: 14 pages**, excluding acknowledgments and references. *Hard constraint — overlength papers are excluded.* Appendices/extra material must be external links.
- Must comply with the **LNCS template**.
- Upload **all source files (LaTeX), PDF, and figures**; delete irrelevant/outdated files.
- Check author names, affiliations, and order (paper + Meteor).
- A **mandatory regular registration** is required (early-bird 2026-07-12, late 2026-07-31).

> The committee asks only to *"do your best to address the reviewers' comments"* in the camera-ready. **There is no re-review and no formal rebuttal channel** — addressing comments is best-effort. A point-by-point "response to reviewers" is therefore optional (useful as an internal changelog / optional cover note), not a required deliverable.

---

## Review 1 (Revision)

This paper compares three existing IVF-based schemes in MOEAs, i.e., IVF/SPEA2, IVF/NSGA-II, and IVF/NSGA-III, and argues that these three couplings behave differently. The topic is interesting. Below are my comments:

1. The authors claim that SPEA2, NSGA-II, and NSGA-III provide different types of selection mechanisms. However, for NSGA-II and NSGA-III, the main difference lies in the selection of solutions from the last front. This means that their behavioral difference becomes more evident only when many non-dominated solutions appear. If the number of non-dominated solutions is limited, their search behavior may be close. I suggest replacing NSGA-III with algorithms that have more clearly different selection structures, such as RVEA or MOEA/D.

2. The three compared algorithms differ not only in the host algorithms and IVF strategies, but also in the offspring-generation mechanisms. In particular, IVF/NSGA-III uses a DE operator, while the other variants use SBX. Therefore, I think the current comparison is not fully fair or directly comparable. It is difficult to determine whether the observed differences are caused by the selection mechanism of the host algorithm or by the different variation operators. If the operator itself provides stronger local or global search ability, then it is unsurprising that the IVF strategy may not bring an obvious additional improvement.

3. I strongly suggest that the authors expand the experimental scale and design more controlled experiments. Drawing conclusions only from existing published IVF pipelines may be misleading, because too many factors differ simultaneously. The authors should control variables as much as possible to reduce the influence of factors other than the host's selection mechanism.

4. The authors should not only consider the relative improvement after injecting IVF, but also consider the absolute performance of the host algorithm itself. A weak baseline algorithm can naturally obtain a larger improvement after adding an extra operator, and may even show improvements across most test cases.

Overall, this work is interesting, and the question of operator-host compatibility is worth studying. However, I think the current experiments are insufficient to fully support the conclusions. Even at the empirical level, the observed results may have several alternative explanations. More controlled experiments are needed to show whether the differences truly come from host compatibility rather than from implementation-level differences among the IVF variants.

---

## Review 2 (Revision)

PPSN2026

Review of paper: Operator-Host Compatibility in Multi-Objective Intensification: IVF Across SPEA2, NSGA-II, and NSGA-III

**Recommendation: maybe accept, reviewer low confidence**

This paper is about local search (LS) methods, which can be added to well-known multi-objective optimisation (MOO) methods. As I understand it, the LS methods are not new to this paper, but the paper is about a detailed comparison of the LS methods in the context of the specific MOO methods they are paired with. We do not get a comparison of all MOO methods hybridised with all LS methods. We do get a comparison of each MOO method on its own versus with its specific LS method.

There is some interesting discussion of the properties of MOO methods and LS methods and how/why they match or do not match. This is a strength of the paper.

The descriptions of the LS methods Sections 3.1-3.3 are not accessible to a typical reader, even one who works with multi-objective algorithms. They are very good in that they supply technical details and settings, referring to previous work. But the paper is not self-contained in this respect. It might be better to just use Table 1 to convey the details, remove the textual description of the same details, and devote the space to a more readable description of the concepts and motivations.

The experimental section is pretty dense! Same for results. I'm not familiar with everything here. Probably a reader who works in this very specific field will find this good. Everything looks pretty good to me. The plots and stat tests seem good.

Sorry that my review is a bit low-confidence due to lack of familiarity with the niche.

---

## Review 3 (submitted by email)

**Recommendation: 3 (strong accept). Reviewer's confidence: 5 (expert).**

The submission draws heavily on the authors' prior work. They use this as reasonable argument for not justifying their choice of parameters. However their interest is in justifying their "IVF" technique in three popular multi-objective approaches but their results suggest performance gain is not uniform and depends heavily on:

- which EMO is used
- their parameter pipeline and
- the benchmark they used in their comparison.

Details of the benchmark are not given. Thus they do not answer their reader's question: I have a problem, perhaps it is similar to benchmark xyz; which of your 6 techniques did well on xyz? Although they do attempt to quantify if differences are real or just random and is the difference big enough for the reader to care.

They do not make clear if their technique is powerful enough to compensate for differences between the three EMO algorithms they choose and if so when.

"IVF" is not a widely used name. There seems to be considerable overlap with Tackett's soft brood selection: WCCI 1994 10.1109/ICEC.1994.350023

The paper draws heavily on your prior work, nonetheless there appears to be sufficient novelty to warrant publication.

Not clear if results could be simply due to changes in selection pressure or diversity preservation techniques.

Heavy use of jargon eg: intensification operators, Host, pipeline, gates, budget gate, continuation criterion, DE, IGD, HV, BH, ECDF, power loss, \DeltaAUC

There are some scrappy notes below. They are intended to be constructive _suggestions_. Please do not be offended by their brevity.

**p1**

- *title* — The title is confusing. The title is heavily laden with jargon.
- *Abstract* — Reduce waffle. Avoid junk like "is a first-order design concern,". Include only words that count.
- *Keywords* — Choose keywords that do not simply repeat what is in the title.

**sect 1**

- Avoid starting with junk, jargon "intensification operators". Nobody at PPSN is going to care unless you take the trouble to put your work in our language.
- Make clear there is no difference between "mother" and "father". Their representation is the same? Their role in crossover and mutation is the same? That is, sex is _not_(?) chosen at birth and fixed for life of individual.
- Is the population size fixed? Is it generational or steady state? Are offspring both mutated and created by crossover or are these alternatives.
- Make text clear.

**page 2**

- top para: unclear — perhaps remove or explain "hybrid and memetic".
- Avoid poor line breaks, eg M-PAES.
- The whole use of "host" terminology is wrong.
- para "Hypothesis H." — make easy to read.
- para "Scope of inference" — Yuk awful section title. Avoid junk expressions like "in this paper". Make easy to read. Perhaps try "We compare".

**p3**

- sec 2.2 — Perhaps a picture.
- sec 3 — Make easy to read.
- sec 3.1 IVF/SPEA2 — "published" is wrong here. cite [20] is just some web page you have created. You have submitted to PPSN to have your work reviewed and formally published, calling [20] published undermines PPSN. Para is hard to follow and jargon laden. "high objective-space dissimilarity" unclear, give all details. "cycles continue only while the average population fitness improves collectively" unclear, give all details.
- sec 3.2 IVF/NSGA-II — do you mean "fathers are sampled" _uniformly_ at random from the whole population? Make clear.

**p4**

- Table 1, Row "Mother selection" — Why is SPEA2 selection described as "fitness" when NSGA2/3 it is "rank".
- "DE" needs to be defined and citation given. DE itself uses a population, how (if at all) does your use of DE relate to the NSGA-3's population.
- Perhaps para starting "Table 1" should be section 3.4.
- sec 4 — "Budget accounting" find better section heading. Similarly section headings on page 5 and sec 5.1 and sec 5.2 and 5.4.

**p5**

- excess of abbreviations. Especially BH — use in full Benjamini-Hochberg or Bonferroni-Holm.

**p6**

- sec "Dynamic block." — make easier to read.
- sec "5 Results" — "The ordering is immediate" rewrite in simple words. Make easier to read.
- Fig 1 etc — Avoid use of red v. green (red/green is most common form of color blindness).
- Fig 1 — Y-axis avoid abbreviations. Key not clear. Why 4 things? (rather than 3 SPEA2, NSGA2, NSGA3). Caption too long — say what you have plotted. Do you need both Fig 1 and Fig 3, i.e. could they be combined?
- Fig 2 — Font too small.

**p9** — sec 5.3 — Sentence "At M" is poor. Rephrase.

**p10** — too much jargon.

**p11** — Fig 4 — Font too small, caption too long.

**p12** — Fig 5 — Font too small.

**sec 6** — rephrase 1st sentence.

**p13** — Avoid bad line breaks eg: "IVF/NSGA-II's", "k-nearest-neighbour". Explain _why_.

**p14** — Sec 7 — avoid junk expressions like "This paper". Make easy to read.

**References**

- [20] Do not repeat URL with same DOI.
- Do not blindly copy page numbers from web pages. It is not physically possible for all the papers in a proceedings to have page numbers which start at 1. Better to omit details than copy someone else's error.
- With (esp. smaller) conferences and workshops give date and address where they were held. If published (and not obvious) include publisher.
