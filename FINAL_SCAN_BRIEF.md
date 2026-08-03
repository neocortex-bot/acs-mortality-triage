# FINAL SCAN BRIEF — recursive paragraph-by-paragraph review, submission-ready prose

Repo: `/home/linuxmint/acs-mortality-triage` (branch `main`). Read `AGENTS.md`
first. Do NOT commit (your sandbox .git is read-only); leave the tree dirty and
report.

Goal: the manuscript must read as a polished, submission-ready original
article. Scan EVERY paragraph recursively (title page block, abstract,
introduction, methods, results, discussion, conclusion, COI, references,
figure/table captions). Fix in `scripts/build_artifacts.py` (the single
generator), rebuild the docx, re-verify. The manuscript is written as a novel
one-shot study: NO development process may leak into the prose.

## Writing standard (Academic English Prose — the user's writing skill, distilled)

Apply ALL of these to every paragraph:

1. **Zero em dashes.** Also zero en dashes in prose (numbers/CI ranges keep
   hyphen formatting where they already exist). Run `grep` on extracted text.
2. **Sentence rhythm**: vary length within formal bounds — mix short
   declaratives (~10 words) with longer compound sentences (~30 words), and
   start some sentences with introductory clauses ("Although...", "Despite...",
   "Unlike...", "Because..."). Do NOT start every sentence with "The"/a noun.
3. **Decisive claims over hedging**: no "may potentially", "could suggest",
   "it is important to note", "it should be noted", "worth mentioning".
   One hedge per article max. End paragraphs with decisive statements.
4. **Kill AI vocabulary** — Tier 1: delve, landscape (metaphorical), paradigm
   shift, leverage (verb), harness, navigate (metaphorical), realm, myriad,
   plethora, multifaceted, groundbreaking, revolutionize, synergy, ecosystem
   (non-technical), resonate, streamline, robust (as puffery), seamless,
   cutting-edge, innovative (puffery), pivotal, nuanced, transformative,
   bolster, underscore, evolving (puffery), fostering, imperative,
   overarching, unprecedented. Also: "serves as"/"stands as" -> "is";
   "boasts"/"features" -> "has".
5. **No superficial -ing tails** ("highlighting...", "underscoring...",
   "reflecting...", "symbolizing...", "showcasing...", "emphasizing...",
   "contributing to...", "fostering...") — delete or expand into a real
   sentence with a subject.
6. **Transitions**: "Moreover/Furthermore/Additionally/In addition" at most
   once total; prefer starting the next thought directly or using "because",
   "so", "but". No "That said", "Moving forward", "When it comes to".
7. **No significance inflation**: no "pivotal role", "critical importance",
   "underscores the value", "represents a shift". Replace with specific facts.
8. **No rule-of-three forcing**; no "Not only... but..." more than once in
   the whole manuscript (currently appears 2x - reduce to max 1).
9. **No repeated crutch structures**: "This study demonstrates that...",
   "These findings suggest that..." at most once; Discussion must INTERPRET,
   not repeat Results verbatim; Conclusion must SYNTHESIZE, not restate the
   abstract sentence-for-sentence.
10. **Passive/active alternation** — do not let every sentence be passive.
11. **No process traces, EVER**: backfill, derivation, CKD-EPI, creatinine/age
    derivation, Supabase, Codex, reclassif, corrected, fixed, shifted,
    originally, previous, earlier, single-stage, Stage 1, Design C, cohort
    correction. The study is a fresh single analysis of a registry.
12. **Framing rules (keep intact)**: flagged (all >= 0.08) vs escalated
    (HIGH+INTERMEDIATE) distinction stays explicit; advisory-only clinical
    language (ICU/HCU/ward "consideration", never automated); GRACE framed as
    complementary decision support, never inferior/superseded; look-ahead
    cardiogenic-shock sensitivity framed as bias demonstration, not a model
    comparison; single-anchor Killip IV (no "shock on arrival" in prose at all).
13. **Numbers**: every metric must match `results/analysis_results.json`
    (post-eGFR-backfill canonical: flagged 682/172, tiers HIGH 170/88 (51.8%),
    INT 341/70 (20.5%), LOW 171/14 (8.2%), not flagged 1135/37, escalated 511
    (28.1%), CM 158/353/51/1255, sens 75.6%, spec 78.0%, acc 77.8%, PPV 30.9%,
    NPV 96.1%, AUC 0.843, Brier 0.080, GRACE 0.816, delta 0.027, DeLong p
    0.021, cal 1.076/0.015/1.014/0.017, EPV 14.3, missingness urea 1.4%/
    glucose 1.2%/SII 0.9%/eGFR 0.6%, complete 1,745 (96.0%), any 72 (4.0%),
    trade-off 327/439/511/670, with-CS 90.4%/63.2%/0.938, Killip IV 279 (36.9%),
    CS 422 (43.6%), CS without Killip IV 143 (56.6%), captured 158/209, 91.9%
    of 172 flagged deaths, missed 51 (37 not flagged + 14 LOW)). If you find a
    mismatch, the JSON wins - fix the prose.
14. **References**: 12 Vancouver, in-text tags [1]-[12] by first appearance;
    do not change the reference list or the claims' citations.

## Procedure

1. Extract the manuscript text: read `scripts/build_artifacts.py`
   `manuscript_text()` + the tables/captions, AND extract the built docx
   (`python3 -c` with python-docx, paragraphs + tables) so you audit exactly
   what the reader sees.
2. Recursive per-paragraph audit: produce a findings table with columns
   [Paragraph # | Section | Verdict (OK / REWRITE / FIX-NUMBER / FIX-CLAIM /
   FIX-STYLE) | Issue | Action]. Cover: title page block (title, authors,
   affiliations, ORCID, corresponding, running title, word count), abstract,
   every Methods/Results/Discussion/Conclusion paragraph, COI line,
   figure/table captions, reference list.
3. Apply fixes ONLY in `scripts/build_artifacts.py` (keep the data-driven
   f-strings; adjust prose around them; do not hardcode numbers that are
   already f-strings). Do not touch: src/, results/, data/, notebooks/,
   figures/.
4. Rebuild: `python3 -c "import sys; sys.path.insert(0,'scripts'); import
   build_artifacts as b; print('wc:', b.build_manuscript(b.load_results()))"`
   then `python3 scripts/audit_docx.py` (word count must stay 3,400-3,750,
   zero em/en dashes, key numbers OK, 12 refs, 6 figures).
5. Run the AI-pattern detector on the rebuilt docx:
   `python3 ~/.hermes/skills/writing/humanize-writing/scripts/detect-ai-patterns.py
   manuscript/acs_mortality_triage_manuscript.docx` — must stay PASS with the
   "Not only...but" count reduced to <=1.
6. Do NOT commit/push. Leave the tree dirty.

## Report

Report: the full findings table (every paragraph, verdict), what you changed
per section with before->after examples for the 5 most important edits, the
detector output (before/after counts), word count, audit result, and any
paragraphs you deliberately left unchanged and why.
