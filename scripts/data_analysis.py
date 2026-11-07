import pandas as pd
import numpy as np
# ======================================
# PHASE 1: DATA INSPECTION & INGESTION 
# ======================================
# Loading datasets
demographics = pd.read_csv('data/demographics.csv')
adverse_events = pd.read_csv('data/adverse_events.csv')
vitals = pd.read_csv('data/vitals.csv')

# Checking for missing values in demographics dataset
print("Demographics dataset:")
print(demographics.info())
print("Missing values in demographics dataset:")
missing_demographics = demographics.isnull().sum()
print(missing_demographics)

# Checking for missing values in adverse events dataset
print("\nAdverse Events dataset:")
print(adverse_events.info())
print("Missing values in adverse events dataset:")
missing_adverse_events = adverse_events.isnull().sum()
print(missing_adverse_events)

# Checking for missing values in vitals dataset
print("\nVitals dataset:")
print(vitals.info())
print("Missing values in vitals dataset:")
missing_vitals = vitals.isnull().sum()
print(missing_vitals)

# So from this initial inspection, we can see that there are 4 missing values in the 'age' column of the demographics dataset.
# while the rest of the columns in each dataset have no missing values. 
# This indicates that we will need to handle these missing values in our data cleaning phase.
# The link between all three datasets is the 'subject_id' column, which is present in all three datasets. This will allow us to merge the datasets later on for further analysis.

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
print('\n--- Validating site rules ---')
if not demographics['site'].isin(['Waterford', 'Cork', 'Dublin']).all():
    invalid_sites = demographics[~demographics['site'].isin(['Waterford', 'Cork', 'Dublin'])]
    print("Invalid site(s) found:")
    print(invalid_sites)
else:
    print("All sites are valid.")

# Column site is valid as all values are either Waterford, Cork or Dublin. No further action is required.

# ==========================================
# DATA VALIDATION & CLEANING - SEX RULES
# ==========================================
print('\n--- Validating sex rules ---')
if not demographics['sex'].isin(['M', 'F']).all():
    invalid_sex = demographics[~demographics['sex'].isin(['M', 'F'])]
    print("Invalid sex value(s) found:")
    print(invalid_sex)
else:
    print("All sex values are valid.")

# Column sex has accidental spaces in values, some of the values are uppercase and some are lowercase. And some have full name like female instead of F. 
demographics['sex'] = demographics['sex'].str.strip().str.upper().replace({'FEMALE': 'F', 'MALE': 'M'})

#checking again for invalid sex values after cleaning
print('\n--- Validating again sex rules ---')
if not demographics['sex'].isin(['M', 'F']).all():
    invalid_sex = demographics[~demographics['sex'].isin(['M', 'F'])]
    print("Invalid sex value(s) found:")
    print(invalid_sex)
else:
    print("All sex values are valid.")

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
print('n --- Validating arm rules ---')
if demographics['arm'].isin(['A', 'B']).all() == False:
    invalid_arm = demographics[~demographics['arm'].isin(['A', 'B'])]
    print("Invalid arm(s) found:")
    print(invalid_arm)
else:
    print("All arm values are valid.")  

# ====================================================================================
# PHASE 2: DATA CLEANING & VALIDATION - ADVERSE EVENT DATASET
# ====================================================================================