# VERIFY REFERENCES BRIEF — Connect real references, Vancouver, zero hallucinated tags

Repo: `/home/linuxmint/acs-mortality-triage` (branch `main`). Read `AGENTS.md`
first. Your job: verify EVERY in-text citation in
`manuscript/acs_mortality_triage_manuscript.docx` against the actual thesis PDF
corpus, fix anything unsupported, ensure Vancouver numbering by first
appearance, and produce a claim-level verification report. No hallucinated
references, no invented metadata.

## Transferred skills (use these; they are the methodology)

### 1. paper-qa pipeline + vector storage (already built for this thesis)

- Pipeline: `/home/linuxmint/academic/thesis-paperqa/`
  - `process_all_questions.py` — HyDE + PaperQA Q&A (needs OPENAI_API_KEY in
    `.env`, already present). Used here mainly for retrieval cross-checks.
  - `pdf_vector_storage.py` — hash-based incremental PDF embedding manager.
    **Existing vector storage is at `/home/linuxmint/academic/thesis-paperqa/vector_storage/`
    (`pdf_embeddings.pkl`, `pdf_hashes.pkl`; 97 hashes). USE it, do not rebuild
    from scratch.** Run it (or a small script importing its functions) to
    confirm all 12 reference PDFs below are embedded; if any are missing, the
    incremental path will add only the new ones.
  - `reference_validator.py` — validates citations in answers against
    retrieved docs.
- PDF corpus: `/home/linuxmint/academic/thesis-paperqa/pdf/` (101 PDFs). The 12
  references below all exist there with real content (verified: not COI-only).
- User preference: PaperQA is a TOOL — never mention it in the manuscript or
  report as if it were a source. Cite the actual papers.

### 2. paper-fetch (DOI -> PDF, only if needed)

- Script: `~/.hermes/skills/research/paper-fetch/scripts/fetch.py`
  - `python3 ~/.hermes/skills/research/paper-fetch/scripts/fetch.py <DOI> --out /home/linuxmint/academic/thesis-paperqa/pdf/`
  - 7-source chain: Unpaywall (needs `UNPAYWALL_EMAIL`) -> Semantic Scholar ->
    arXiv -> PMC -> bioRxiv/medRxiv -> publisher -> Sci-Hub.
- Use ONLY if a cited PDF turns out to be the wrong paper or COI-only. All 12
  are already present and content-verified, so fetching should be unnecessary.

### 3. Source-claim verification (the core methodology)

For each claim, find whether the CITED PDF actually supports it:

1. Extract text: `pdftotext "<pdf>" /tmp/ref.txt` (poppler-utils).
2. Three-tier search: `search_files` grep -> `grep -in "term1\|term2" /tmp/ref.txt` (robust against ligatures/whitespace) -> read surrounding lines for context.
3. Choose claim-specific key terms (e.g., for the GRACE claim: "GRACE",
   "discrimination", "AUC", "validated"; for the Killip claim: "Killip",
   "heart failure", "severity"; for the calibration claim: "calibration
   slope", "calibration-in-the-large").
4. Classify: **FOUND** (exact quote supports the claim), **PARTIALLY FOUND**
   (claim partly supported; caveats), **NOT FOUND** (no supporting text).
5. Report with: claim, status, source PDF, exact quote(s) with page number,
   assessment.

Known pitfalls (from the skills): ESC/OUP guideline PDFs downloaded from the
publisher CDN can be COI-declarations only (the real guideline is the EHJ
article; the corpus copies are already verified as the real articles). PDF
filenames can be misleading. When a claim bundles several elements, verify
each element. Never substitute general knowledge for source text; if no PDF
supports a claim, say NOT FOUND.

## The 12 references and their corpus filenames

| # | Vancouver reference (current) | Corpus file |
|---|---|---|
| 1 | Collet JP, et al. 2020 ESC Guidelines NSTE-ACS. Eur Heart J. 2021;42:1289-1367. | `Collet-2021.pdf` |
| 2 | Byrne RA, et al. 2023 ESC Guidelines ACS. Eur Heart J. 2023;44:3720-3826. | `Byrne et al.-2023.pdf` |
| 3 | Fox KAA, et al. GRACE. BMJ. 2006;333:1091. | `Fox-2006.pdf` |
| 4 | Granger CB, et al. Predictors of hospital mortality in GRACE. Arch Intern Med. 2003;163:2345-2353. | `Granger-2003.pdf` |
| 5 | Killip T 3rd, Kimball JT. Am J Cardiol. 1967;20:457-464. | `Killip and Kimball-1967.pdf` |
| 6 | Breiman L. Random forests. Mach Learn. 2001;45:5-32. | `Breiman-2001.pdf` |
| 7 | Steyerberg EW, et al. Poor performance of clinical prediction models. J Clin Epidemiol. 2018;98:133-143. | `Steyerberg et al.-2018.pdf` |
| 8 | van Smeden M, et al. Sample size for binary logistic prediction models. Stat Methods Med Res. 2019;28(8):2455-2474. | `Van Smeden et al.-2019.pdf` |
| 9 | DeLong ER, et al. Comparing the areas under two or more correlated ROC curves. Biometrics. 1988;44(3):837-845. | `DeLong et al.-1988.pdf` |
| 10 | Collins GS, et al. TRIPOD+AI statement. BMJ. 2024;385:e078378. | `Collins et al.-2024.pdf` |
| 11 | Van Calster B, et al. Calibration: the Achilles heel of predictive analytics. BMC Med. 2019;17:230. | `Van Calster et al.-2019.pdf` |
| 12 | Vickers AJ, Elkin EB. Decision curve analysis. Med Decis Making. 2006;26(6):565-574. | `Vickers and Elkin-2006.pdf` |

## Tasks (in order)

1. **Embedding check**: confirm the 12 PDFs above are in the vector storage
   (`pdf_vector_storage.py`); run the incremental add if any are missing.
   Report hash count before/after.
2. **Extract claims**: read the manuscript docx (paragraphs AND tables), find
   every sentence with an in-text citation `[n]` or `[n,m]`. There are
   currently ~10 such sentences (e.g., guidelines risk assessment [1,2]; GRACE
   validation [3,4]; Killip [5]; random forest [6]; calibration methods [7,11];
   TRIPOD+AI [10]; DeLong [9]; DCA [12]). Also check the reference list block
   for metadata accuracy.
3. **Verify claim-level** per the methodology above: each claim -> its cited
   PDF(s). For grouped citations (e.g. [1,2]), check that EACH cited paper
   supports the claim (or adjust the grouping). Include the Methods claims
   too (DeLong method [9], DCA [12], calibration metrics [7,11], TRIPOD+AI
   [10], random forest [6], sample size/EPV [8] if cited).
4. **Produce `references/claim-verification-report.md`**: per-claim rows with
   claim (verbatim), citation, status (FOUND / PARTIALLY FOUND / NOT FOUND),
   source file, exact quote with page, assessment. End with a summary table.
5. **Fix the manuscript** where needed:
   - NOT FOUND / PARTIALLY FOUND: either re-cite to the correct corpus PDF
     that supports the claim (verify first), or narrow the claim wording to
     exactly what the source supports. Never fabricate a source.
   - Metadata: correct author/journal/year/volume/pages/DOI in the reference
     list from the actual PDFs (extract metadata with PyMuPDF; cross-check
     against CrossRef by title if unsure; DO NOT invent DOIs).
   - Vancouver numbering: order = first appearance in text; renumber if the
     order changed; update all in-text tags accordingly.
   - Keep all numbers, structure, figures, word count rules from AGENTS.md.
     Zero em dashes. Rebuild the docx with `scripts/build_artifacts.py`
     (read it first; it is the generator) and run `scripts/audit_docx.py`
     (word count must stay in 3,400-3,700).
6. **Update `references/verified-references.md`**: final 12 references in
   Vancouver order with verified metadata + DOI + per-reference verification
   status (which claims it supports, FOUND).
7. **Commit** all changes with a clear message. Do not push. Do not touch
   results/, src/, notebooks/, data/, README.md unless a citation in README
   is affected (README has no citations; leave it).

## Report

Report: embedding status before/after, the claim table summary (how many
FOUND / PARTIALLY FOUND / NOT FOUND, which claims changed), any re-cites or
wording changes made, final reference list with DOIs, word count, audit
result, and deviations.
