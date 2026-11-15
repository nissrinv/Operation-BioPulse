import pandas as pd
import numpy as np
import os

excel_path = "Operation_Bio_Pulse_Clinical_Query_Log.xlsx"

### QUERY TRACKING DataFrame to log any data issues found during the analysis.
    #Error Code: A unique identifier for the type of error or issue found.
    #Source Table: The name of the dataset where the issue was found (e.g., demographics, adverse_events, vitals).
    #Site: The site associated with the subject (if applicable).
    #Subject ID: The unique identifier for the subject associated with the issue.
    #Visit: The visit associated with the issue (if applicable).
    #Variable: The specific variable or column where the issue was found.
    #Error Type: The type of error or issue (e.g., missing value, duplicate entry, invalid value).
    #Description: A brief description of the issue found.
    #Action: The action taken or recommended to resolve the issue (e.g., imputed missing value, removed duplicate, corrected value).
    #Status: The current status of the issue (e.g., resolved, unresolved, in progress).
    #Timestamp: The date and time when the issue was logged or last updated.
 ###   

# 1. Check if a master query log already exists from a previous run
if os.path.exists(excel_path):
    print("Loading existing query log to preserve human updates and statuses...")
    old_query_log = pd.read_excel(excel_path)
else:
    old_query_log = pd.DataFrame()

# 2. Run your validation checks to generate newly found errors (let's call this new_findings_df)
# new_findings_df contains the fresh errors found in today's dataset run.

# 3. Smart Merge / Reconciliation logic:
if not old_query_log.empty and not new_findings_df.empty:
    # Identify errors that already exist (e.g., matching by subject_id and variable)
    # We want to keep the old query_id, old status, and old date_created!
    
    # Merge or filter out duplicates so you don't duplicate queries that are already "Open"
    pass
elif old_query_log.empty:
    # If it's the very first time running, use the new findings as the base
    master_query_log = new_findings_df
    master_query_log['created_at'] = pd.Timestamp.today().strftime('%Y-%m-%d %H:%M:%S')
    master_query_log['status'] = 'Open'
    
# 4. Save back to Excel without losing manual site work
# master_query_log.to_excel(excel_path, index=False)
master_query_log = pd.DataFrame(columns=[
    "error_code",
    "source_table",
    "site",
    "subject_id",
    "visit",
    "variable",
    "error_type",
    "description",
    "action",
    "status",
    "created_at",
    "updated_at"
])

def check_missing_values(df, dataset_name):
    print(f"\n{dataset_name} dataset:")
    print(df.info())
    print(f"Missing values in {dataset_name} dataset:")
    missing_values = df.isnull().sum()
    print(missing_values)

def check_duplicates(df, dataset_name):
    print(f"Analysing duplicate entries in {dataset_name} dataset...")
    duplicate_entries = df[df.duplicated(keep=False)]
    if not duplicate_entries.empty:
        print(duplicate_entries)
    else:
        print(f"No duplicate entries found in {dataset_name} dataset.")

def check_categorical_values(df, column_name, categories ,dataset_name):
    print(f"\nAnalysing categorical values in '{column_name}' column of {dataset_name} dataset are correct...")
    if not df[column_name].isin(categories).all():
        print(f"Invalid values found in '{column_name}' column of {dataset_name} dataset:")
        print(df[~df[column_name].isin(categories)])
    else:
        print(f"All values in '{column_name}' column of {dataset_name} dataset are valid.")

# ======================================
# PHASE 1: DATA INGESTION & INSPECTION
# ======================================
# Loading datasets
demographics = pd.read_csv('data/demographics.csv')
adverse_events = pd.read_csv('data/adverse_events.csv')
vitals = pd.read_csv('data/vitals.csv')

# Checking for missing values in datasets
check_missing_values(demographics, "Demographics")
check_missing_values(adverse_events, "Adverse Events")
check_missing_values(vitals, "Vitals")

#--- So from this initial inspection, we can see that there are 4 missing values in the 'age' column of the demographics dataset.
#--- while the rest of the columns in each dataset have no missing values. 
#--- This indicates that we will need to handle these missing values in our data cleaning phase.
#--- The link between all three datasets is the 'subject_id' column, which is present in all three datasets. This will allow us to merge the datasets later on for further analysis.

# Checking for duplicate entries in datasets
check_duplicates(demographics, "Demographics")
check_duplicates(adverse_events, "Adverse Events")
check_duplicates(vitals, "Vitals")

# ====================================================================================
# PHASE 2: DATA CLEANING & VALIDATION - DEMOGRAPHICS DATASET
# ====================================================================================
# Handling **missing values** in demographics dataset
# For the 'age' column, we will fill the missing values with the median age of the dataset.
median_age = demographics['age'].median()
demographics['age']=demographics['age'].fillna(median_age)

print("\nThe median age is:")
print(median_age)
missing_demographics_after = demographics.isnull().sum()
print("Missing values in demographics dataset after handling missing values:")
print(missing_demographics_after)

# Now we will check if the values of the columns in the demographics dataset are within the expected ranges.
    # Subject_id must be unique and non-null.
    # Site must match an active, approved investigator sites which are Waterford, Cork & Dublin.
    # Sex must be either M or F. Cannot be missing.
    # Consent must be prior to or equal to any study activities or randomization.
    # Age should be between (18 - 85)
    # Randomisation should be either must be a valid calendar date & must be on or after `consent_date`.
    # Arm must be either A or B

# Checking for duplicates in the demographics dataset based on the 'subject_id' column.
print('\n--- Checking for duplicates in demographics dataset ---')
duplicate_entries_demographics = demographics[demographics.duplicated(keep=False)]
if not duplicate_entries_demographics.empty:
    print("Duplicate entries found in demographics dataset:")
    print(duplicate_entries_demographics)
else:
    print("No duplicate entries found in demographics dataset.")
    
# ==========================================
# DATA VALIDATION & CLEANING - SUBJECT_ID RULES
# ==========================================

print('\n--- Validating subject_id rules ---')
duplicate_subject_ids = demographics[demographics.duplicated(subset='subject_id', keep=False)]
if not duplicate_subject_ids.empty:
    print("Duplicate subject_id found:")
    print(duplicate_subject_ids)    
else:
    print("No duplicate subject_id found.")
# There are 6 rows with 3 duplications in the demographics dataset. We will need to investigate these duplicates further to determine 
# if they are valid or if they need to be removed.

# ==========================================
# DATA VALIDATION & CLEANING - SITE RULES
# ==========================================

check_categorical_values(demographics, 'site', ['Waterford', 'Cork', 'Dublin'], "Demographics")

# Column site is valid as all values are either Waterford, Cork or Dublin. No further action is required.

# ==========================================
# DATA VALIDATION & CLEANING - SEX RULES
# ==========================================
check_categorical_values(demographics, 'sex', ['M', 'F'], "Demographics")
# Column sex has accidental spaces in values, some of the values are uppercase and some are lowercase. And some have full name like female instead of F. 
demographics['sex'] = demographics['sex'].str.strip().str.upper().replace({'FEMALE': 'F', 'MALE': 'M'})

#checking again for invalid sex values after cleaning
check_categorical_values(demographics, 'sex', ['M', 'F'], "Demographics")

# ==========================================
# DATA VALIDATION & CLEANING - CONSENT RULES
# ==========================================
print('\n--- Validating consent rules ---')
# Checking if consent_date is prior to or equal to any study activities or randomization.
demographics['consent_date'] = pd.to_datetime(demographics['consent_date'], errors='coerce')
demographics['randomisation_date'] = pd.to_datetime(demographics['randomisation_date'], errors='coerce')
invalid_consent = demographics[demographics['consent_date'] > demographics['randomisation_date']]
if not invalid_consent.empty:
    print("Invalid consent date(s) found:")
    print(invalid_consent)
else:
    print("All consent dates are valid.")

# ==========================================
# DATA VALIDATION & CLEANING - AGE RULES
# ==========================================
print('\n--- Validating age rules ---')
# Checking if age is between 18 and 85
invalid_age = demographics[(demographics['age'] < 18) | (demographics['age'] > 85)]
if not invalid_age.empty:
    print("Invalid age(s) found:")
    print(invalid_age)
else:
    print("All age values are valid.")
# We have two subjects with age less than 18 and one subject with age greater than 85. We will need to investigate these subjects further to determine 
# if its an input data error or a protocol violation.

# ==========================================
# DATA VALIDATION & CLEANING - RANDOMISATION RULES
# ==========================================
print('n--- Validating randomisation rules ---')
randomation_invalid = demographics[demographics['randomisation_date'] < demographics['consent_date']]
if not randomation_invalid.empty:
    print("Invalid randomisation date(s) found:")
    print(randomation_invalid)
else:
    print("All randomisation dates are valid.") 

# ==========================================
# DATA VALIDATION & CLEANING - ARM RULES
# ==========================================
check_categorical_values(demographics, 'arm', ['A', 'B'], "Demographics")
# ====================================================================================
# PHASE 2: DATA CLEANING & VALIDATION - ADVERSE EVENT DATASET
# ====================================================================================
# There is no missing values in the adverse events dataset.
# Checking for duplicate entries in the adverse events dataset.
check_duplicates(adverse_events, "Adverse Events")
# ==========================================
# DATA VALIDATION & CLEANING - SUBJECT_ID RULES
# ==========================================
# There could be more than one entry for each subject_id so to find duplicates we will check for all rows that have save values.
print('\n--- Validating subject_id rules ---')
duplicates_subjectid_adverse = adverse_events[adverse_events.duplicated(keep=False)]
if not duplicates_subjectid_adverse.empty:
    print("Duplicate subject_id found in adverse events dataset:")
    print(duplicates_subjectid_adverse)
else:
    print("No duplicate subject_id found in adverse events dataset.")

print('n--- Validating that all subjects in adverse events dataset are present in demographics dataset ---')
demographics_subjects_ids = demographics['subject_id'].unique()
adverse_events_subjects_ids = adverse_events['subject_id'].unique()
if not np.isin(adverse_events_subjects_ids, demographics_subjects_ids).all():
    missing_subjects = adverse_events_subjects_ids[~np.isin(adverse_events_subjects_ids, demographics_subjects_ids)]
    print("Subjects in adverse events dataset not present in demographics dataset:")
    print(missing_subjects)
else:
    print("All subjects in adverse events dataset are present in demographics dataset.")
# ==========================================
# DATA VALIDATION & CLEANING - AE TERM RULES
# ==========================================
# Checking all unique values in the 'ae_term' column to ensure they are valid and consistent.
check_categorical_values(adverse_events, 'ae_term', ['Fatigue', 'Rash', 'Nausea', 'Headache', 'Dizziness', 'Cough'], "Adverse Events")
# All data consistent and valid. No further action is required.

# ==========================================
# DATA VALIDATION & CLEANING - START DATE RULES
# ==========================================
# Start date must be a valid caledar date and must be on or after the subject's randomisation date.
print('\n--- Validating start date rules ---')
adverse_events['start_date'] = pd.to_datetime(adverse_events['start_date'], errors='coerce')
mapping_rand_dates_to_adverse_events = adverse_events.merge(demographics,left_on='subject_id',right_on='subject_id')
invalid_start_date = mapping_rand_dates_to_adverse_events[mapping_rand_dates_to_adverse_events['start_date'] < mapping_rand_dates_to_adverse_events['consent_date']]
if not invalid_start_date.empty:
    print("There is invalid start dates:")
    print(invalid_start_date)
else:
    print("All start dates are valid.")

# ==========================================
# DATA VALIDATION & CLEANING - END DATE RULES
# ==========================================
# End date cant be before the start date and must be a valid calendar date.
print('\n--- Validating end date rules ---')
adverse_events['end_date'] = pd.to_datetime(adverse_events['end_date'], errors='coerce')
invalid_end_date = adverse_events[adverse_events['end_date'] < adverse_events['start_date']]
if not invalid_end_date.empty:
    print("There is invalid end dates:")
    print(invalid_end_date)
else:
    print("All end dates are valid.")

# ==========================================
# DATA VALIDATION & CLEANING - SEVERITY RULES
# ==========================================
# Severity must be either mild, moderate or severe. Cannot be missing.
check_categorical_values(adverse_events, 'severity', ['Mild', 'Severe', 'Moderate'], "Adverse Events")

# ==========================================
# DATA VALIDATION & CLEANING - SERIOUS RULES
# ==========================================
# Serious must be either Y or N. Cannot be missing.
check_categorical_values(adverse_events, 'serious', ['Y', 'N'], "Adverse Events")

# TASK: Need to check that if the severity is severe, then the serious column must be either Y. If the severity is mild or moderate, then the serious column must be N.

# ====================================================================================
# PHASE 2: DATA CLEANING & VALIDATION - VITALS DATASET
# ====================================================================================
# There is no missing values in the vitals dataset. Need to check for duplicate entries in the vitals dataset.
print('\n--- Checking for duplicates in vitals dataset ---')
duplicate_entries_vitals = vitals[vitals.duplicated(keep=False)]
if not duplicate_entries_vitals.empty:
    print("Duplicate entries found in vitals dataset:")
    print(duplicate_entries_vitals)
else:
    print("No duplicate entries found in vitals dataset.")

# ==========================================
# DATA VALIDATION & CLEANING - SUBJECT_ID RULES
# ==========================================
vitals_subjects_id = vitals['subject_id'].unique()
print('\n--- Validating that all subjects in vitals dataset are present in demographics dataset ---')
if not np.isin(vitals_subjects_id, demographics_subjects_ids).all():
    missing_subjects_vitals = vitals_subjects_id[~np.isin(vitals_subjects_id, demographics_subjects_ids)]
    print("Subjects in vitals dataset not present in demographics dataset (orphans):")
    print(missing_subjects_vitals) 
else:
    print("All subjects in vitals dataset are present in demographics dataset.")   
# We have two subjects in the vitals dataset that are not present in the demographics dataset. We will need to investigate these subjects further to determine

# ==========================================
# DATA VALIDATION & CLEANING - VISIT RULES
# ==========================================
check_categorical_values(vitals, 'visit', ['Baseline', 'Week4', 'Week8', 'Week12'], "Vitals")
# All values are valid. No further action is required.

# I need to check that each subject has one visit for each type of visit. 
subject_visit_counts = vitals.groupby('subject_id')['visit'].nunique()
invalid_subject_visits = subject_visit_counts[subject_visit_counts < 4]
print(invalid_subject_visits)


# ==========================================
# DATA VALIDATION & CLEANING - VISIT DATE RULES
# ==========================================
# Visit date must be a valid date calendar and the date needs to be on or after the subject's consent date as well as randomisation date.
print('\n--- Validating visit date rules ---')
vitals['visit_date'] = pd.to_datetime(vitals['visit_date'], errors='coerce')
mapping_rand_dates_to_vitals = vitals.merge(demographics,left_on='subject_id',right_on='subject_id')
print('\n--- Validating visit date agains consent date ---')
invalid_visit_date_consent = mapping_rand_dates_to_vitals[mapping_rand_dates_to_vitals['visit_date'] < mapping_rand_dates_to_vitals['consent_date']]
if not invalid_visit_date_consent.empty:
    print("There is invalid visit dates against consent date:")
    print(invalid_visit_date_consent.sort_values(by=['subject_id', 'visit_date']))
else:
    print("All visit dates are valid against consent date.")
print('\n--- Validating visit date agains randomisation date ---')
invalid_visit_date_randomisation = mapping_rand_dates_to_vitals[mapping_rand_dates_to_vitals['visit_date'] < mapping_rand_dates_to_vitals['randomisation_date']]
if not invalid_visit_date_randomisation.empty:
    print("There is invalid visit dates against randomisation date:")
    print(invalid_visit_date_randomisation.sort_values(by=['subject_id', 'visit_date']))
else:
    print("All visit dates are valid against randomisation date.")

# ==========================================
# DATA VALIDATION & CLEANING - SYSTOLIC RULES
# ==========================================
# **70 to 200 mmHg** | Physiological boundary check. Must be strictly greater than `diastolic_bp`.
print('\n--- Validating systolic rules ---')
invalid_systolic = vitals[(vitals['systolic_bp'] < 70) | (vitals['systolic_bp'] > 200) | (vitals['systolic_bp'] <= vitals['diastolic_bp'])]
if not invalid_systolic.empty:
    print("There is invalid systolic values:")
    print(invalid_systolic)
else:
    print("All systolic values are valid.")

# ==========================================
# DATA VALIDATION & CLEANING - DIASTOLIC RULES
# ==========================================
# **40 to 120 mmHg** | Physiological boundary check. Must be strictly less than `systolic_bp`.
print('\n--- Validating diastolic rules ---')
invalid_diastolic = vitals[(vitals['diastolic_bp'] < 40) | (vitals['diastolic_bp'] > 120) | (vitals['diastolic_bp'] >= vitals['systolic_bp'])]
if not invalid_diastolic.empty:
    print("There is invalid diastolic values:")
    print(invalid_diastolic)
else:
    print("All diastolic values are valid.")

# ==========================================
# DATA VALIDATION & CLEANING - HEART RATE RULES
# ==========================================
# **40 to 180 bpm** | Physiological boundary check.
print('\n--- Validating heart rate rules ---')
invalid_heart_rate = vitals[(vitals['heart_rate'] < 40) | (vitals['heart_rate'] > 180)]
if not invalid_heart_rate.empty:
    print("There is invalid heart rate values:")
    print(invalid_heart_rate)
else:
    print("All heart rate values are valid.")

# ==========================================
# DATA VALIDATION & CLEANING - WEIGHT RULES
# ==========================================
# **30 to 200 kg** | Physiological boundary check. Check for extreme fluctuations across visits.
print('\n--- Validating weight rules ---')
invalid_weight = vitals[(vitals['weight_kg'] < 30) | (vitals['weight_kg'] > 200)]
if not invalid_weight.empty:
    print("There is invalid weight values:")
    print(invalid_weight)
else:
    print("All weight values are valid.")

# I will start by dividing the vitals dataset into the different visits.
# 1. Pivot the table once globally (no loop needed!)
vitals_wide = vitals.pivot_table(
    index='subject_id', 
    columns='visit', 
    values='weight_kg', 
    aggfunc='first'
)

# 2. Calculate raw percentage changes (keeping the sign: negative = loss, positive = gain)
var_w4_baseline = (vitals_wide['Week4'] - vitals_wide['Baseline']) / vitals_wide['Baseline']
var_w8_w4       = (vitals_wide['Week8'] - vitals_wide['Week4']) / vitals_wide['Week4']
vitals_wide['Week12'] - vitals_wide['Week8'] / vitals_wide['Week8'] # (and so on)

# 3. Define smarter clinical thresholds for a weight-loss trial:
# Let's say unexpected rapid weight gain (> 10%) or extreme, impossible weight loss (> 30%)
gain_threshold = 0.10   # 10% sudden gain is suspicious
extreme_loss_threshold = -0.30 # Losing over 30% quickly is a safety/typo flag

# 4. Filter for subjects crossing those specific safety boundaries
extreme_fluctuations = vitals_wide[
    (var_w4_baseline > gain_threshold) | (var_w4_baseline < extreme_loss_threshold) |
    (var_w8_w4 > gain_threshold) | (var_w8_w4 < extreme_loss_threshold)
]

# 5. Output results
if not extreme_fluctuations.empty:
    print("Found subjects with unexpected weight anomalies (possible typos or adverse events):")
    print(extreme_fluctuations)
else:
    print("All weight changes fall within expected clinical parameters.")

# ============================================
# PHASE 3: DERIVATION & FEATURE ENGINEERING
# ============================================