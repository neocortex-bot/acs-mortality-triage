# Claim Verification Report

Manuscript checked: `manuscript/acs_mortality_triage_manuscript.docx`.

PDF corpus: `/home/linuxmint/academic/thesis-paperqa/pdf/`.

Vector storage: `/home/linuxmint/academic/thesis-paperqa/vector_storage/`.

## Embedding Check

Before the incremental check, `pdf_hashes.pkl` contained 97 hashes. The current corpus contained 101 PDF files. Four files were missing from the saved hash table: `Prokhorenkova et al.-2018.pdf`, `Van Calster et al.-2019.pdf`, `DeLong et al.-1988.pdf`, and `Byrne et al.-2023.pdf`.

The incremental storage path was invoked. It began appending the four missing files, but the run could not complete in this session: preprocessing could not write filtered PDFs in the external corpus directory because it is read-only here, and the embedding request then stalled under restricted network access. The process was stopped after no progress. Hash count after the stopped run remained 97. Direct PDF text verification below used the actual corpus PDFs.

## Claim-Level Verification

| ID | Manuscript claim | Citation | Status | Source file | Exact supporting quote with page | Assessment |
|---|---|---:|---|---|---|---|
| C1 | Current ESC guidelines emphasize initial risk stratification using clinical history, vital signs, physical findings, ECG, biomarkers, and clinical instability. | [1,2] | FOUND | `Collet-2021.pdf`; `Byrne et al.-2023.pdf` | Collet PDF p. 8: "clinical presentation of acute coronary syndromes (ACS) is broad." Byrne PDF p. 19: "initial short-term risk stratification of ACS" uses clinical history, vital signs, physical findings, ECG, and hs-cTn. | Original wording was narrowed. Both guideline PDFs support guideline-based initial risk assessment and instability framing. |
| C2 | GRACE remains a major reference score with broad validation. | [3,4] | FOUND | `Fox-2006.pdf`; `Granger-2003.pdf` | Fox PDF p. 3: "Prospective and external validation of the GRACE risk score." Granger PDF p. 1: "confirmation GRACE data set" and "GUSTO-IIb database." | Both PDFs support GRACE validation across GRACE and external/confirmation datasets. |
| C3 | Killip class captures heart failure severity after myocardial infarction and remains clinically meaningful decades after its first description. | [5] | FOUND | `Killip and Kimball-1967.pdf` | PDF p. 2: patients were classified into groups after clinical-record review; PDF p. 1: course emphasized "heart failure and cardiac arrest." | The source supports the original Killip clinical severity classification. The current manuscript uses this as historical grounding. |
| C4 | The model used a random forest, an ensemble of tree predictors. | [6] | FOUND | `Breiman-2001.pdf` | PDF p. 1: "Random forests are a combination of tree predictors." | Original wording over-attached Breiman to the local 12-variable model. It was narrowed to the random-forest method. |
| C5 | Reporting follows TRIPOD+AI guidance for prediction models that use regression or machine learning methods. | [7] | FOUND | `Collins et al.-2024.pdf` | PDF p. 1: "updated guidance for reporting clinical prediction models that use regression or machine learning methods." | Supported exactly. Citation was renumbered for Vancouver order. |
| C6 | EPV was retained as a descriptive check because sample-size adequacy extends beyond a simple EPV rule. | [8] | FOUND | `Van Smeden et al.-2019.pdf` | PDF p. 1: title states "Beyond events per variable criteria"; abstract names "Events Per Variable criterion." | Added this citation so the sample-size reference is cited and the claim matches the paper. |
| C7 | GRACE 2.0 in-hospital scores were computed on the same cohort and used as the comparator. | [3,4] | FOUND | `Fox-2006.pdf`; `Granger-2003.pdf` | Fox PDF p. 3: "GRACE risk score"; Granger PDF p. 1: "Predictors of Hospital Mortality in the Global Registry of Acute Coronary Events." | The sources support GRACE as the ACS comparator score; same-cohort computation is local study design, not a literature claim. |
| C8 | Calibration assessment followed prediction-model performance guidance; logistic calibration slope and calibration-in-the-large were reported. | [9,10] | FOUND | `Steyerberg et al.-2018.pdf`; `Van Calster et al.-2019.pdf` | Steyerberg PDF p. 4: "calibration slope" indicates reliability of risk predictions. Van Calster PDF p. 4: "calibration-in-the-large" compares average predicted risk with event rate. | Original wording assigned O:E ratio and ECE to the references. It was split so citations support slope/CITL and general calibration assessment only. |
| C9 | AUCs were compared with the DeLong method for correlated ROC curves. | [11] | FOUND | `DeLong et al.-1988.pdf` | PDF p. 1 title: "Comparing the Areas under Two or More Correlated Receiver Operating Characteristic Curves." | Supported exactly. Citation was renumbered for Vancouver order. |
| C10 | Decision curve analysis followed standard net benefit methods. | [12] | FOUND | `Vickers and Elkin-2006.pdf` | PDF p. 1: "derive the net benefit of the model across different threshold probabilities." | Supported exactly. |
| C11 | GRACE has broad external evidence and remains a reference score in ACS risk assessment. | [3,4] | FOUND | `Fox-2006.pdf`; `Granger-2003.pdf` | Fox PDF p. 1: model was "prospectively validated"; Granger PDF p. 8: model "validated well in 2 independent patient cohorts." | Supported. The local AUC comparison remains framed as complementary decision support, not replacement. |

## Reference Metadata Check

| Final # | Corpus file | DOI status | Verification status |
|---:|---|---|---|
| 1 | `Collet-2021.pdf` | DOI found in PDF: 10.1093/eurheartj/ehaa575 | FOUND for C1 |
| 2 | `Byrne et al.-2023.pdf` | DOI found in PDF metadata/text: 10.1093/eurheartj/ehad191 | FOUND for C1 |
| 3 | `Fox-2006.pdf` | DOI found in PDF: 10.1136/bmj.38985.646481.55 | FOUND for C2, C7, C11 |
| 4 | `Granger-2003.pdf` | DOI cross-checked by PubMed/JAMA: 10.1001/archinte.163.19.2345 | FOUND for C2, C7, C11 |
| 5 | `Killip and Kimball-1967.pdf` | DOI cross-checked by Crossref-indexed records: 10.1016/0002-9149(67)90023-9 | FOUND for C3 |
| 6 | `Breiman-2001.pdf` | DOI cross-checked by Springer: 10.1023/A:1010933404324 | FOUND for C4 |
| 7 | `Collins et al.-2024.pdf` | DOI found in PDF: 10.1136/bmj-2023-078378 | FOUND for C5 |
| 8 | `Van Smeden et al.-2019.pdf` | DOI found in PDF: 10.1177/0962280218784726 | FOUND for C6 |
| 9 | `Steyerberg et al.-2018.pdf` | DOI found in PDF metadata/text: 10.1016/j.jclinepi.2017.11.013 | FOUND for C8 |
| 10 | `Van Calster et al.-2019.pdf` | DOI found in PDF metadata/text: 10.1186/s12916-019-1466-7 | FOUND for C8 |
| 11 | `DeLong et al.-1988.pdf` | DOI cross-checked by Crossref-indexed records: 10.2307/2531595 | FOUND for C9 |
| 12 | `Vickers and Elkin-2006.pdf` | DOI found in PDF: 10.1177/0272989X06295361 | FOUND for C10 |

## Summary

| Status | Count |
|---|---:|
| FOUND | 11 |
| PARTIALLY FOUND | 0 |
| NOT FOUND | 0 |

Changes made:

- Narrowed the ESC guideline claim to directly supported initial risk-stratification wording.
- Narrowed the Breiman citation to the random-forest method definition.
- Split the calibration methods sentence so cited sources support calibration guidance, slope, and calibration-in-the-large; O:E ratio and ECE remain local analysis metrics.
- Added a citation to van Smeden et al. for EPV as a descriptive sample-size check.
- Reordered references into Vancouver order by first appearance and renumbered affected citations.
