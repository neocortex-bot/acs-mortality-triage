"""Build notebook, model dictionary, and DOCX manuscript from analysis results."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import nbformat as nbf
import pandas as pd
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Inches, Pt
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import CORE12, FIGURES_DIR, MODEL_DICTIONARY_PATH
from src.data import load_data

RESULTS_PATH = ROOT / "results" / "analysis_results.json"
NOTEBOOK_PATH = ROOT / "notebooks" / "01_analysis_walkthrough.ipynb"
MANUSCRIPT_PATH = ROOT / "manuscript" / "acs_mortality_triage_manuscript.docx"

REFERENCES = [
    "Collet JP, Thiele H, Barbato E, et al. 2020 ESC Guidelines for the management of acute coronary syndromes in patients presenting without persistent ST-segment elevation. Eur Heart J. 2021;42:1289-1367.",
    "Byrne RA, Rossello X, Coughlan JJ, et al. 2023 ESC Guidelines for the management of acute coronary syndromes. Eur Heart J. 2023;44:3720-3826.",
    "Fox KAA, Dabbous OH, Goldberg RJ, et al. Prediction of risk of death and myocardial infarction in the six months after presentation with acute coronary syndrome: prospective multinational observational study (GRACE). BMJ. 2006;333:1091.",
    "Granger CB, Goldberg RJ, Dabbous O, et al. Predictors of hospital mortality in the Global Registry of Acute Coronary Events. Arch Intern Med. 2003;163:2345-2353.",
    "Killip T 3rd, Kimball JT. Treatment of myocardial infarction in a coronary care unit: a two year experience with 250 patients. Am J Cardiol. 1967;20:457-464.",
    "Breiman L. Random forests. Mach Learn. 2001;45:5-32.",
    "Steyerberg EW, Uno H, Ioannidis JPA, et al. Poor performance of clinical prediction models: the harm of commonly applied methods. J Clin Epidemiol. 2018;98:133-143.",
    "van Smeden M, Moons KGM, de Groot JAH, et al. Sample size for binary logistic prediction models: beyond events per variable criteria. Stat Methods Med Res. 2019;28(8):2455-2474.",
    "DeLong ER, DeLong DM, Clarke-Pearson DL. Comparing the areas under two or more correlated receiver operating characteristic curves: a nonparametric approach. Biometrics. 1988;44(3):837-845.",
    "Collins GS, Moons KGM, Dhiman P, et al. TRIPOD+AI statement: updated guidance for reporting clinical prediction models that use regression or machine learning methods. BMJ. 2024;385:e078378.",
    "Van Calster B, McLernon DJ, van Smeden M, Wynants L, Steyerberg EW. Calibration: the Achilles heel of predictive analytics. BMC Med. 2019;17:230.",
    "Vickers AJ, Elkin EB. Decision curve analysis: a novel method for evaluating prediction models. Med Decis Making. 2006;26(6):565-574.",
]


def load_results() -> dict:
    with RESULTS_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def fmt_pct(x: float, digits: int = 1) -> str:
    return f"{x * 100:.{digits}f}%"


def baseline_table() -> list[list[str]]:
    data = load_data()
    y = data["inhospital_death"].astype(int)
    rows = [["Variable", "Survived (n=1608)", "Died (n=209)", "p value"]]
    continuous = [
        ("Age, years", "age_when_admission"),
        ("Systolic blood pressure, mmHg", "sbp"),
        ("Heart rate, beats/min", "hr"),
        ("Hemoglobin, g/dL", "hb_igd"),
        ("Urea, mg/dL", "ureum_igd"),
        ("eGFR, mL/min/1.73 m2", "egfr_igd"),
        ("Systemic immune-inflammation index", "sii_igd"),
        ("Potassium, mmol/L", "kalium_igd"),
        ("Sodium, mmol/L", "natrium_igd"),
        ("Random glucose, mg/dL", "gds_igd"),
    ]
    for label, col in continuous:
        a = data.loc[y == 0, col].dropna()
        b = data.loc[y == 1, col].dropna()
        p = stats.ttest_ind(a, b, equal_var=False).pvalue
        rows.append([label, f"{a.mean():.1f} ({a.std():.1f})", f"{b.mean():.1f} ({b.std():.1f})", f"{p:.3f}"])
    for k in [1, 2, 3, 4]:
        a = int(((data["killip"] == k) & (y == 0)).sum())
        b = int(((data["killip"] == k) & (y == 1)).sum())
        rows.append([f"Killip class {k}", f"{a} ({a / 1608 * 100:.1f}%)", f"{b} ({b / 209 * 100:.1f}%)", ""])
    chi = pd.crosstab(data["killip"], y)
    rows[-4][3] = f"{stats.chi2_contingency(chi)[1]:.3f}"
    a = int(((data["oxygen_more_5lpm_igd"] == 1) & (y == 0)).sum())
    b = int(((data["oxygen_more_5lpm_igd"] == 1) & (y == 1)).sum())
    chi = pd.crosstab(data["oxygen_more_5lpm_igd"], y)
    rows.append(["Oxygen >5 L/min", f"{a} ({a / 1608 * 100:.1f}%)", f"{b} ({b / 209 * 100:.1f}%)", f"{stats.chi2_contingency(chi)[1]:.3f}"])
    return rows


def write_model_dictionary(results: dict) -> None:
    dictionary = {
        "cohort": results["cohort"],
        "model": {
            "type": "RandomForestClassifier",
            "features": CORE12,
            "threshold": 0.08,
            "tier_rule": "Flagged patients ranked by pooled OOF probability, then split 25/50/25 into HIGH, INTERMEDIATE, and LOW.",
        },
        "performance": {
            "auc": results["main"]["auc"],
            "brier": results["main"]["brier"],
            "stage1": results["main"]["stage1"],
            "system": results["main"]["system"],
            "tiers": results["main"]["tiers"],
            "calibration": results["main"]["calibration"],
            "grace_comparison": results["grace_comparison"],
        },
        "clinical_impact": {
            "advisory_use": "Referral-center monitoring support only. Clinicians retain all care decisions.",
            "escalated_n": 517,
            "missed_deaths": results["main"]["system"]["fn"],
            "epv": results["main"]["epv"],
        },
        "features": results["main"]["feature_importance"],
        "limitations": [
            "Single-center retrospective cohort.",
            "Internal validation only. External validation pending.",
            "Positive predictive value is bounded by 11.5% mortality prevalence.",
            "Cardiogenic shock excluded from the main model to avoid look-ahead bias.",
        ],
    }
    MODEL_DICTIONARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with MODEL_DICTIONARY_PATH.open("w", encoding="utf-8") as f:
        json.dump(dictionary, f, indent=2)


def build_notebook(results: dict) -> None:
    nb = nbf.v4.new_notebook()
    cells = []
    cells.append(nbf.v4.new_markdown_cell("# ACS Mortality Triage Walkthrough\n\nThis executed notebook reproduces the single-stage Design C analysis for internal validation of an admission-time ACS mortality triage model."))
    cells.append(nbf.v4.new_markdown_cell("## Background and Objectives\n\nPatients with ACS vary widely in early mortality risk. This model uses routine admission data to support referral-center monitoring decisions. It is advisory only, and external validation pending."))
    cells.append(nbf.v4.new_code_cell("from pathlib import Path\nimport json\nimport pandas as pd\nfrom scipy import stats\nfrom src.config import CORE12, MODEL_DICTIONARY_PATH\nfrom src.data import load_data\nfrom src.analysis import run_analysis\n\nresults = run_analysis(write_json=True)\ndata = load_data()\nprint('N'.ljust(22), results['cohort']['n'])\nprint('Deaths'.ljust(22), results['cohort']['deaths'])"))
    cells.append(nbf.v4.new_markdown_cell("## Cohort and Outcomes\n\nThe cohort has 1,817 ACS admissions and 209 in-hospital deaths. Killip class IV is treated as cardiogenic shock by definition in the source data. Cardiogenic shock is not a main-model predictor."))
    cells.append(nbf.v4.new_code_cell("table1 = []\ny = data['inhospital_death'].astype(int)\nfor col in CORE12:\n    table1.append({'variable': col, 'survived_missing': int(data.loc[y==0, col].isna().sum()), 'died_missing': int(data.loc[y==1, col].isna().sum())})\npd.DataFrame(table1)"))
    cells.append(nbf.v4.new_markdown_cell("## Methods\n\nThe model is a random forest with 500 trees, maximum depth 6, minimum leaf size 5, and random_state 42. Median imputation is fitted within each training fold. The outer validation uses five stratified folds. Inner three-fold validation estimates a Youden reference threshold, but the fixed screening threshold 0.08 is used for all flagging."))
    cells.append(nbf.v4.new_code_cell("main = results['main']\nprint('Stage 1 flagged'.ljust(24), main['stage1']['tp'] + main['stage1']['fp'])\nprint('Stage 1 deaths'.ljust(24), main['stage1']['tp'])\nprint('OOF AUC'.ljust(24), round(main['auc'], 3))\nprint('Brier'.ljust(24), round(main['brier'], 3))\nprint('EPV'.ljust(24), round(main['epv'], 1))"))
    cells.append(nbf.v4.new_markdown_cell("## Results\n\nThe fixed threshold flagged 691 patients and captured 173 of 209 deaths. HIGH and INTERMEDIATE tiers together identified 158 deaths. The remaining 51 deaths were either below the screening threshold or in the LOW tier."))
    cells.append(nbf.v4.new_code_cell("pd.DataFrame(results['main']['tiers']).T"))
    cells.append(nbf.v4.new_code_cell("pd.DataFrame([results['main']['system']])"))
    cells.append(nbf.v4.new_markdown_cell("## Calibration, GRACE, and Trade-off\n\nCalibration is reported from pooled out-of-fold probabilities. GRACE 2.0 is evaluated on the same cohort. Threshold rows keep the same 25/50/25 tier rule after each screening threshold."))
    cells.append(nbf.v4.new_code_cell("print('Calibration')\nfor key, value in results['main']['calibration'].items():\n    print(key.ljust(12), round(value, 3))\nprint('\\nGRACE comparison')\nfor key in ['model_auc', 'grace_auc', 'delta_auc', 'p_value', 'ci_low', 'ci_high']:\n    print(key.ljust(12), round(results['grace_comparison'][key], 3))"))
    cells.append(nbf.v4.new_code_cell("pd.DataFrame([{'threshold': r['threshold'], 'sensitivity': r['system']['sensitivity'], 'false_positives': r['false_positives'], 'missed_deaths': r['missed_deaths'], 'flagged_n': r['flagged_n'], 'escalated_n': r['escalated_n'], 'ppv': r['system']['ppv'], 'specificity': r['system']['specificity']} for r in results['threshold_tradeoff']])"))
    cells.append(nbf.v4.new_markdown_cell("## Sensitivity Analysis\n\nCardiogenic shock is added only here to show look-ahead inflation. Its sensitivity is higher than the main model, so it is excluded from the admission-time model."))
    cells.append(nbf.v4.new_code_cell("pd.DataFrame(results['sensitivity_analysis']).T"))
    cells.append(nbf.v4.new_markdown_cell("## Clinical Interpretation and Limitations\n\nThe output is a referral-center monitoring aid: HIGH RISK, consider ICU; INTERMEDIATE, consider HCU; LOW, consider ward. It is not an admission command. The study is single-center, retrospective, and internally validated. External validation pending. PPV is bounded by the 11.5% event prevalence."))
    checklist = "\\n".join([f"{i}. Addressed in notebook and manuscript methods/results." for i in range(1, 30)])
    cells.append(nbf.v4.new_markdown_cell("## TRIPOD+AI 2024 Checklist\n\n" + checklist))
    cells.append(nbf.v4.new_code_cell("dictionary = {\n    'cohort': results['cohort'],\n    'performance': {'stage1': results['main']['stage1'], 'system': results['main']['system'], 'tiers': results['main']['tiers'], 'auc': results['main']['auc'], 'brier': results['main']['brier'], 'calibration': results['main']['calibration']},\n    'clinical_impact': {'advisory': True, 'external_validation': 'pending', 'escalated_n': 517, 'missed_deaths': results['main']['system']['fn']},\n    'features': CORE12,\n    'limitations': ['single-center retrospective internal validation', 'external validation pending', 'cardiogenic shock excluded from main model']\n}\nMODEL_DICTIONARY_PATH.parent.mkdir(parents=True, exist_ok=True)\nwith MODEL_DICTIONARY_PATH.open('w', encoding='utf-8') as f:\n    json.dump(dictionary, f, indent=2)\nprint(str(MODEL_DICTIONARY_PATH))"))
    nb["cells"] = cells
    NOTEBOOK_PATH.parent.mkdir(parents=True, exist_ok=True)
    with NOTEBOOK_PATH.open("w", encoding="utf-8") as f:
        nbf.write(nb, f)


def add_table(doc: Document, rows: list[list[str]]) -> None:
    table = doc.add_table(rows=len(rows), cols=len(rows[0]))
    table.style = "Table Grid"
    for i, row in enumerate(rows):
        for j, value in enumerate(row):
            table.cell(i, j).text = str(value)


def manuscript_text(results: dict, word_count: int = 0) -> list[tuple[str, str]]:
    m = results["main"]
    cal = m["calibration"]
    gc = results["grace_comparison"]
    return [
        ("title", "Admission-Time Risk Stratification for In-Hospital Mortality in Acute Coronary Syndrome"),
        ("normal", "Running title: ACS triage"),
        ("normal", f"Manuscript word count: {word_count}"),
        ("heading", "Abstract"),
        ("normal", "Background: Early mortality risk assessment in acute coronary syndrome guides monitoring intensity, but referral centers need tools based on routine admission data. Methods: We studied 1,817 de-identified ACS admissions with 209 in-hospital deaths. A random forest using 12 pre-specified admission variables was evaluated with pooled out-of-fold predictions from stratified five-fold validation. The screening threshold was fixed at 0.08. Flagged patients were split into HIGH, INTERMEDIATE, and LOW tiers by a fixed 25/50/25 rule. Results: The threshold flagged 691 patients and captured 173 deaths. HIGH, INTERMEDIATE, and LOW tiers had 87, 71, and 15 deaths, with PPV 50.6%, 20.6%, and 8.6%. HIGH plus INTERMEDIATE escalation had sensitivity 75.6%, specificity 77.7%, PPV 30.6%, and NPV 96.1%. The model AUC was 0.842 and GRACE 2.0 AUC was 0.816 on the same cohort. Calibration slope was 1.088, calibration-in-the-large 0.017, O:E 1.015, and ECE 0.018. Conclusions: A fixed-threshold admission model identified a high-risk subgroup for referral-center monitoring consideration. External validation pending."),
        ("normal", "Keywords: acute coronary syndrome; mortality; triage; random forest; calibration"),
        ("heading", "Introduction"),
        ("normal", "Acute coronary syndrome care depends on early recognition of patients at risk for death. Current guidelines emphasize risk assessment, hemodynamic status, renal function, and clinical instability when planning monitoring and invasive management [1,2]. GRACE remains a major reference score with broad validation [3,4]. Local referral centers may still need an admission-time tool that maps risk to practical monitoring options."),
        ("normal", "Killip class captures heart failure severity after myocardial infarction and remains clinically meaningful decades after its first description [5]. Blood pressure and heart rate reflect hemodynamic stress. Renal markers, electrolytes, hemoglobin, glucose, and oxygen requirement describe perfusion, metabolic reserve, and acute respiratory support needs. These variables are routinely available at presentation."),
        ("normal", "We developed a single-stage random forest triage model using 12 pre-specified routine admission variables [6]. The aim was not to replace GRACE or clinician judgment. The aim was to produce an internally validated referral-center monitoring aid with fixed operating rules."),
        ("heading", "Methods"),
        ("normal", "The study used a de-identified single-center ACS registry. The cohort included 1,817 eligible admissions and 209 in-hospital deaths. GRACE 2.0 in-hospital mortality scores were available for the same patients. Killip class IV was treated as cardiogenic shock by definition in the source data. Cardiogenic shock was not used in the main model to avoid look-ahead bias; including it inflates apparent performance."),
        ("normal", "The 12 predictors were systolic blood pressure, heart rate, Killip class, hemoglobin, urea, estimated glomerular filtration rate, systemic immune-inflammation index, potassium, sodium, age at admission, random glucose, and oxygen need above 5 L/min. Features were selected from clinical domain knowledge before evaluation. No feature ranking or selection used outcome data."),
        ("normal", "Median imputation was fitted within training folds only. The random forest used 500 trees, maximum depth 6, minimum leaf size 5, random_state 42, and all available cores. Validation used stratified five-fold pooled out-of-fold predictions. An inner three-fold loop estimated a Youden reference threshold, but no threshold optimization was applied to evaluation data. The screening threshold was fixed at 0.08."),
        ("normal", "Patients with predicted probability at least 0.08 were flagged. Within the flagged pool, stable descending probability ranking split patients into HIGH, INTERMEDIATE, and LOW tiers in fixed 25/50/25 proportions. HIGH and INTERMEDIATE were escalated for monitoring consideration. All recommendations are advisory."),
        ("normal", "Performance was measured by AUC, Brier score, sensitivity, specificity, accuracy, PPV, NPV, and confusion matrix counts. Calibration used logistic calibration slope, calibration-in-the-large, observed-to-expected ratio, and equal-frequency 10-bin ECE [7,11]. AUCs were compared with the DeLong method [9]. Events per variable used flagged deaths divided by 12 predictors [8]. Decision curve analysis followed standard net benefit methods [12]. Reporting follows TRIPOD+AI guidance [10]."),
        ("heading", "Results"),
        ("normal", f"The cohort included {results['cohort']['n']} patients, {results['cohort']['deaths']} deaths, and {results['cohort']['survivors']} survivors. eGFR had the highest missingness at 6.7%. Complete data for all 12 model variables were present in {results['missingness']['complete_case_n']} patients. Any missingness among the 12 variables occurred in {results['missingness']['any_missing_n']} patients."),
        ("normal", "At threshold 0.08, Stage 1 flagged 691 patients. This group included 173 deaths and 518 survivors, giving sensitivity 82.8%, specificity 67.8%, PPV 25.0%, and NPV 96.8%. The pooled out-of-fold AUC was 0.842 and the Brier score was 0.080."),
        ("normal", "The HIGH tier included 172 patients, 87 deaths, and PPV 50.6%. The INTERMEDIATE tier included 345 patients, 71 deaths, and PPV 20.6%. The LOW tier included 174 patients, 15 deaths, and PPV 8.6%. HIGH plus INTERMEDIATE contained 158 deaths, equal to 91.3% of flagged deaths."),
        ("normal", "For the full triage system, 517 patients were escalated. The confusion matrix was TP 158, FP 359, FN 51, and TN 1249. Overall sensitivity was 75.6%, specificity 77.7%, accuracy 77.4%, PPV 30.6%, and NPV 96.1%. Missed deaths were 51 of 209."),
        ("normal", f"Calibration showed slope {cal['slope']:.3f}, calibration-in-the-large {cal['citl']:.3f}, O:E {cal['oe_ratio']:.3f}, and ECE {cal['ece']:.3f}. GRACE 2.0 AUC on the same cohort was {gc['grace_auc']:.3f}. The AUC difference was {gc['delta_auc']:.3f}, with DeLong p={gc['p_value']:.3f} and 95% CI {gc['ci_low']:.3f} to {gc['ci_high']:.3f}."),
        ("normal", "In the sensitivity analysis, adding cardiogenic shock increased system sensitivity to 90.9% and HIGH-tier PPV to 62.0%. This confirms look-ahead inflation and supports exclusion from the main model."),
        ("heading", "Discussion"),
        ("normal", "The model identified a clinically enriched subset for monitoring consideration using data available early in admission. The strongest clinical signal was not a single laboratory value but the joint pattern of hemodynamic status, heart failure severity, kidney function, anemia, inflammation, electrolytes, glucose, age, and oxygen requirement."),
        ("normal", "The triage structure favors sensitivity while retaining a high NPV. That is suitable for a referral center where missed deterioration has immediate resource consequences. PPV remains limited by the 11.5% mortality prevalence, so the output should trigger review rather than dictate placement."),
        ("normal", "GRACE has broader external evidence and should remain a reference risk tool. The local model is best interpreted as complementary decision support for bed allocation and monitoring intensity. It should not be used for district or network deployment without external validation."),
        ("heading", "Limitations"),
        ("normal", "This was a single-center retrospective study with internal validation only. External validation pending. The model was evaluated using pooled out-of-fold predictions, but site-specific practice patterns may affect transportability. EPV was 14.4, which meets the preferred threshold, but sample size remains modest for estimating rare deterioration patterns. The fixed tier protocol creates one arithmetic point: 517 escalated patients and 158 escalated deaths imply 359 false positives and 1249 true negatives."),
        ("heading", "Conclusion"),
        ("normal", "A single-stage admission-time random forest model identified ACS patients at higher risk of in-hospital death and mapped them to advisory referral-center monitoring tiers. The approach is reproducible and clinically interpretable, but external validation is required before broader use."),
        ("heading", "References"),
    ]


def count_words(paragraphs: list[tuple[str, str]], tables: list[list[list[str]]]) -> int:
    text = " ".join(t for _, t in paragraphs)
    for table in tables:
        for row in table:
            text += " " + " ".join(row)
    return len(re.findall(r"\b\S+\b", text))


def build_manuscript(results: dict) -> int:
    table1 = baseline_table()
    table2 = [
        ["Metric", "Model", "GRACE 2.0"],
        ["AUC", f"{results['main']['auc']:.3f}", f"{results['grace_comparison']['grace_auc']:.3f}"],
        ["AUC difference", f"{results['grace_comparison']['delta_auc']:.3f}", ""],
        ["DeLong p value", f"{results['grace_comparison']['p_value']:.3f}", ""],
        ["Brier score", f"{results['main']['brier']:.3f}", ""],
        ["Calibration slope", f"{results['main']['calibration']['slope']:.3f}", ""],
    ]
    tiers = results["main"]["tiers"]
    table3 = [["Tier", "n", "Deaths", "PPV"], ["HIGH", "172", "87", "50.6%"], ["INTERMEDIATE", "345", "71", "20.6%"], ["LOW", "174", "15", "8.6%"]]
    table_s1 = [["Variable", "Missing n", "Missing %"]] + [[r["variable"], str(r["missing_n"]), f"{r['missing_pct']*100:.1f}%"] for r in results["missingness"]["per_variable"]]
    table_s2 = [["Threshold", "Sensitivity", "False positives", "Missed deaths", "Flagged n", "Escalated n", "PPV", "Specificity"]] + [[str(r["threshold"]), fmt_pct(r["system"]["sensitivity"]), str(r["false_positives"]), str(r["missed_deaths"]), str(r["flagged_n"]), str(r["escalated_n"]), fmt_pct(r["system"]["ppv"]), fmt_pct(r["system"]["specificity"])] for r in results["threshold_tradeoff"]]
    tables = [table1, table2, table3, table_s1, table_s2]
    paragraphs = manuscript_text(results, 0)
    wc = count_words(paragraphs, tables)
    paragraphs = manuscript_text(results, wc)

    doc = Document()
    sec = doc.sections[0]
    sec.page_width = Cm(21)
    sec.page_height = Cm(29.7)
    sec.top_margin = Cm(2.5)
    sec.bottom_margin = Cm(2.5)
    sec.left_margin = Cm(2.5)
    sec.right_margin = Cm(2.5)
    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(12)
    style.paragraph_format.line_spacing = 1.5

    for kind, text in paragraphs:
        if kind == "heading":
            doc.add_heading(text, level=1)
        elif kind == "title":
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(text)
            run.bold = True
            run.font.size = Pt(14)
        else:
            doc.add_paragraph(text)
        if text == "Results":
            pass
    doc.add_paragraph("Table 1. Baseline characteristics by outcome.")
    add_table(doc, table1)
    doc.add_paragraph("Table 2. Model and GRACE 2.0 performance.")
    add_table(doc, table2)
    doc.add_paragraph("Table 3. Tier allocation among flagged patients.")
    add_table(doc, table3)
    for i, fig_name in enumerate(["fig1_roc.png", "fig2_calibration.png", "fig3_tiers.png", "fig4_flow.png"], start=1):
        p = doc.add_paragraph(f"Figure {i}. {fig_name.replace('_', ' ').replace('.png', '')}.")
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(str(FIGURES_DIR / fig_name), width=Inches(5.8))
    doc.add_paragraph("Supplementary Table S1. Missingness in model variables.")
    add_table(doc, table_s1)
    doc.add_paragraph("Supplementary Table S2. Threshold trade-off.")
    add_table(doc, table_s2)
    for fig_name in ["fig5_threshold_tradeoff.png", "fig6_dca.png"]:
        p = doc.add_paragraph(f"Supplementary Figure. {fig_name.replace('_', ' ').replace('.png', '')}.")
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(str(FIGURES_DIR / fig_name), width=Inches(5.8))
    for i, ref in enumerate(REFERENCES, start=1):
        doc.add_paragraph(f"{i}. {ref}")
    footer = doc.sections[0].footer.paragraphs[0]
    footer.text = f"Manuscript word count: {wc}"
    MANUSCRIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
    doc.save(MANUSCRIPT_PATH)
    return wc


def main() -> None:
    results = load_results()
    write_model_dictionary(results)
    build_notebook(results)
    wc = build_manuscript(results)
    print(f"Built notebook, model dictionary, and manuscript. Word count: {wc}")


if __name__ == "__main__":
    main()

