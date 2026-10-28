import pandas as pd
import numpy as np

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
