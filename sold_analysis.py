import pandas as pd
import numpy as np
from pathlib import Path
df1 = pd.read_csv("CRMLSSold202602.csv")
df2 = pd.read_csv("CRMLSSold202603.csv")
df = pd.concat([df1, df2], ignore_index=True)
df.info()

## exploratory analysis
print("=== HEAD ===")
print(df.head(5))
print("\n=== COLUMNS ===")
print(df.columns.tolist())
print("\n=== DESCRIBE ===")
print(df.describe(include="all"))

print("\n=== CLEANING DATA ===")
drop_cols = [
    "FireplacesTotal", "AboveGradeFinishedArea",
    "ElementarySchoolDistrict", "MiddleOrJuniorSchoolDistrict",
    "CoveredSpaces", "TaxYear",
]
##The primary objective is to remove columns that contain "virtually no data" or are "irrelevant to the current analysis," 
# as this helps make the Tableau workbook more lightweight.

df = df.drop(columns=[col for col in drop_cols if col in df.columns])
##Delete columns with severe missing data (< 20% non-missing values)
threshold = len(df) * 0.2
df = df.dropna(thresh=threshold, axis=1)

required_cols = [
    "ClosePrice", "ListPrice", "LivingArea",
    "CloseDate", "City", "PropertyType"
]

for col in required_cols:
    if col in df.columns:
        df = df[df[col].notna()]
##Numeric Type Conversion
numeric_cols = [
    "ClosePrice", "ListPrice", "OriginalListPrice",
    "LivingArea", "BedroomsTotal", "BathroomsTotalInteger",
    "DaysOnMarket", "Latitude", "Longitude",
    "YearBuilt", "GarageSpaces", "ParkingTotal",
    "LotSizeSquareFeet"
]

for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")
### Date Conversion
if "CloseDate" in df.columns:
    df["CloseDate"] = pd.to_datetime(df["CloseDate"], errors="coerce")

# Clean Up Outliers
df = df[df["ClosePrice"] > 0]
df = df[df["ListPrice"] > 0]
df = df[df["LivingArea"] > 0]
### Handling Y/N Fields
yn_cols = [
    "ViewYN", "WaterfrontYN", "BasementYN",
    "PoolPrivateYN", "AttachedGarageYN",
    "FireplaceYN", "NewConstructionYN"
]

for col in yn_cols:
    if col in df.columns:
        df[col] = df[col].fillna("N")
### Text Field Processing
if "City" in df.columns:
    df["City"] = df["City"].astype(str).str.strip().str.title()

if "PostalCode" in df.columns:
    df["PostalCode"] = df["PostalCode"].astype(str).str.extract(r"(\d{5})", expand=False)

if "StateOrProvince" in df.columns:
    df["StateOrProvince"] = df["StateOrProvince"].str.upper()
### Feature Engineering
df["price_per_sqft"] = df["ClosePrice"] / df["LivingArea"]
df["sale_to_list_ratio"] = df["ClosePrice"] / df["ListPrice"]
df["sale_year"] = df["CloseDate"].dt.year
df["sale_month"] = df["CloseDate"].dt.month
if "YearBuilt" in df.columns:
    df["property_age"] = pd.Timestamp.today().year - df["YearBuilt"]

df["sold_above_list"] = (df["ClosePrice"] > df["ListPrice"]).astype(int)

KEY_FIELDS = [
    "CloseDate",
    "City",
    "StateOrProvince",
    "PostalCode",
    "Latitude",
    "Longitude",
    "PropertyType",
    "PropertySubType",
    "BedroomsTotal",
    "BathroomsTotalInteger",
    "LivingArea",
    "LotSizeSquareFeet",
    "YearBuilt",
    "ListPrice",
    "OriginalListPrice",
    "ClosePrice",
    "DaysOnMarket",
    "price_per_sqft",
    "sale_to_list_ratio",
    "sale_year",
    "sale_month",
    "property_age",
    "sold_above_list"
]

df = df[[col for col in KEY_FIELDS if col in df.columns]]

print("Final shape:", df.shape)

df.to_csv("sold_final_clean.csv", index=False)
print("sold_final_clean.csv")
