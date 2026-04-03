import pandas as pd
import numpy as np
from pathlib import Path
df1 = pd.read_csv("CRMLSSold202602.csv")
df2 = pd.read_csv("CRMLSSold202603.csv")
df = pd.concat([df1, df2], ignore_index=True)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
print("=== SHAPE ===")
print(df.shape)
print("\n=== HEAD ===")
print(df.head(3))
print("\n=== COLUMNS ===")
print(df.columns)

print("\n=== INFO ===")
print(df.info())
print("\n=== DESCRIBE NUMERIC ===")
print(df.describe().round(2))
cat_cols = df.select_dtypes(include=['object', 'string']).columns
print(df[cat_cols].describe())

##Missing Value Analysis
missing = df.isnull().sum().sort_values(ascending=False)
missing_percent = (missing / len(df) * 100).round(2)

missing_df = pd.DataFrame({
    "Missing Count": missing,
    "Missing %": missing_percent
})

print(missing_df.head(20))
#Variables with very high missing rates (above 90%) were
# removed because they contain too little useful information. 
# Agent-related fields and IDs were also excluded since they are 
# not relevant to property analysis. Some variables, like building
#  area, were considered but not used due to too many missing values.

print("\n=== CLEANING DATA ===")
drop_cols = [
    "ElementarySchoolDistrict",
    "CoveredSpaces",
    "MiddleOrJuniorSchoolDistrict",
    "TaxYear",
    "BelowGradeFinishedArea",
    "BusinessType"
]
df = df.drop(columns=[col for col in drop_cols if col in df.columns])
#This step removes columns with high missing values or low analytical relevance
#  to improve data quality and simplify further analysis.

threshold = len(df) * 0.2
df = df.dropna(thresh=threshold, axis=1)
print("After cleaning shape:", df.shape)

#Analysis of Key MLS Fields
key_num_cols = [
    'ListPrice',
    'ClosePrice',
    'LivingArea',
    'BedroomsTotal',
    'BathroomsTotalInteger',
    'DaysOnMarket'
]

key_cat_cols = [
    'PropertyType',
    'City'
]
print("\n=== KEY NUMERIC SUMMARY ===")
print(df[key_num_cols].describe().round(2))

print("\n=== CATEGORICAL SUMMARY ===")
print(df[key_cat_cols].describe())

for col in key_cat_cols:
    print(f"\n--- {col} TOP VALUES ---")
    print(df[col].value_counts().head(10))
#The dataset mainly consists of residential properties, with 
# fewer commercial types. It covers many cities, but listings are
#  concentrated in major urban areas, showing an imbalance in both 
# property type and location.
print("\n=== PRICE PER SQFT ===")
df['PricePerSqft'] = df['ClosePrice'] / df['LivingArea']
print(df['PricePerSqft'].describe().round(2))

df['PriceDiff'] = df['ClosePrice'] - df['ListPrice']

print("\n=== PRICE DIFFERENCE ===")
print(df['PriceDiff'].describe().round(2))
#On average, properties are sold slightly above the
#  listing price, with a mean price difference of about 
# $9,214. However, the median is 0, indicating that most 
# properties are sold at or near the listing price. This
#  suggests that while some properties are sold at a premium, 
#the overall market remains relatively balanced.
print("\n=== DAYS ON MARKET ===")
print(df['DaysOnMarket'].describe().round(2))
##The average time on market is about 50 days, but the 
# median is only 24 days. This indicates that most properties 
# are sold relatively quickly, while a few listings remain on 
# the market for a long time and increase the average.
