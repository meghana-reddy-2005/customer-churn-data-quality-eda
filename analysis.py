
import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = BASE_DIR / "data" / "customer_churn_sample.csv"

df = pd.read_csv(DATA_PATH)

print("\n========== DATASET OVERVIEW ==========")

print("\nFirst 5 Records:")
print(df.head())

print("\nDataset Shape:")
print(df.shape)

print("\nColumn Names:")
print(df.columns.tolist())

print("\nData Types:")
print(df.dtypes)

print("\nDataset Information:")
df.info()

print("\n========== MISSING VALUES ==========")

missing = pd.DataFrame({
    "Missing Count": df.isnull().sum(),
    "Missing Percentage": (df.isnull().mean() * 100).round(2)
})

print(missing)

print("\n========== DUPLICATE RECORDS ==========")

print("Duplicate Rows:", df.duplicated().sum())

print("\n========== SUMMARY STATISTICS ==========")

print(df.describe(include="all").T)

print("\n========== UNIQUE VALUES ==========")

for col in df.columns:
    print(f"{col}: {df[col].nunique()} unique values")
