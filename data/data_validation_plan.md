# Data Validation Plan & Data Dictionary

This document outlines the clinical data validation rules, data types, and acceptable value ranges for the **Operation BioPulse** clinical dataset. These rules serve as the official specification for Data Quality & Cleaning checks (Phase 2).

---

## 1. Demographics (`demographics.csv`)

Captures baseline participant characteristics, trial site metadata, and study status dates.

* **Primary Key:** `subject_id` (1 record per participant).

| Column Name | Data Type | Valid Range / Allowed Values | Validation Rules & Edit Checks |
| :--- | :--- | :--- | :--- |
| `subject_id` | String / Integer | Unique identifier (e.g., `1` to `7`) | **Primary Key Check:** Must be unique and non-null. |
| `site` | String / Integer | Authorized Site IDs (e.g., `101`, `102`) | Must match an active, approved investigator site ID. Cannot be missing. |
| `sex` | Categorical | `'M'`, `'F'` | Controlled terminology (standardized vocabulary). No null values. |
| `age` | Numeric / Integer | **18 to 85 years** | Inclusion criteria: Adult subjects. Missing values handled via median imputation. |
| `consent_date` | Date (YYYY-MM-DD) | Valid calendar date | **Regulatory Check:** Informed consent date must be prior to or equal to any study activities or randomization. |
| `randomisation_date` | Date (YYYY-MM-DD) | Valid calendar date | Must be on or after `consent_date`. |
| `arm` | Categorical | Treatment arms (e.g., `'Placebo'`, `'Dose A'`, `'Dose B'`) | Must match protocol treatment groups. If randomised, must be assigned to a valid arm. |

---

## 2. Vital Signs (`vitals.csv`)

Tracks physiological parameters across repeated patient visits over time.

* **Foreign Key:** `subject_id` (multiple records per participant allowed).

| Column Name | Data Type | Valid Range / Allowed Values | Validation Rules & Edit Checks |
| :--- | :--- | :--- | :--- |
| `subject_id` | String / Integer | Must exist in `demographics` | **Relational Integrity Check:** Every vital record must belong to a valid registered subject. |
| `visit` | String / Categorical | e.g., `'Screening'`, `'Visit 1'`, `'Visit 2'` | Standardized visit labeling per trial schedule. |
| `visit_date` | Date (YYYY-MM-DD) | Valid calendar date | Must be on or after the subject's `consent_date`. |
| `systolic_bp` | Numeric (mmHg) | **70 to 200 mmHg** | Physiological boundary check. Must be strictly greater than `diastolic_bp`. |
| `diastolic_bp` | Numeric (mmHg) | **40 to 120 mmHg** | Physiological boundary check. Must be strictly less than `systolic_bp`. |
| `heart_rate` | Numeric (bpm) | **40 to 180 bpm** | Resting pulse rate range check. |
| `weight_kg` | Numeric (kg) | **35.0 to 200.0 kg** | Body weight range check. Check for extreme fluctuations across visits. |

---

## 3. Adverse Events (`adverse_events.csv`)

Records any safety complications or side effects reported during the trial.

* **Foreign Key:** `subject_id` (0, 1, or multiple records per participant).

| Column Name | Data Type | Valid Range / Allowed Values | Validation Rules & Edit Checks |
| :--- | :--- | :--- | :--- |
| `subject_id` | String / Integer | Must exist in `demographics` | **Relational Integrity Check:** Event must tie back to a trial participant. |
| `ae_term` | String / Text | Medical term (e.g., `'Headache'`, `'Nausea'`) | Standardized medical term description. Cannot be blank. |
| `start_date` | Date (YYYY-MM-DD) | Valid calendar date | Must be on or after `consent_date`. |
| `end_date` | Date (YYYY-MM-DD) | Valid calendar date (or blank if ongoing) | **Chronological Check:** If present, `end_date` must be after `start_date`. |
| `severity` | Categorical | `'Mild'`, `'Moderate'`, `'Severe'` | Controlled terminology. Mandatory field. |
| `serious` | Categorical | `'Yes'`, `'No'` (or Boolean) | Regulatory flag for Serious Adverse Event (SAE) reporting. |

---

## 4. Cross-Table Logic Checks Summary

1. **Foreign Key Rule:** All `subject_id` entries in `vitals` and `adverse_events` must exist in `demographics`.
2. **Timeline Rule:** `consent_date` $\le$ `randomisation_date` $\le$ `visit_date` / `start_date`.
3. **Blood Pressure Logic:** `diastolic_bp` < `systolic_bp` for all rows in `vitals`.