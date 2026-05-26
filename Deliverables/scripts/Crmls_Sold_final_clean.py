# %% [markdown]
# week 1-2

# %%
import pandas as pd
# 1. Read merged listing dataset
import pandas as pd
df1 = pd.read_csv("CRMLSSold_merged.csv", low_memory=False)
# Append Check 
# =========================
print("=== APPEND CHECK ===")
print("Row count of combined/appended dataset:", df1.shape[0])

# %%
# 2. Unique property types
print("\n=== UNIQUE PROPERTY TYPES ===")
property_type_counts = df1["PropertyType"].value_counts(dropna=False)
print(property_type_counts)

property_type_table = property_type_counts.reset_index()
property_type_table.columns = ["PropertyType", "Count"]

# %%
df = pd.read_csv("CRMLSSold_residential.csv")
print("\n=== PropertyType Check ===")
print(df["PropertyType"].value_counts(dropna=False))

# %%
# 4. Missing value summary
missing_summary = pd.DataFrame({
    "column": df.columns,
    "null_count": df.isnull().sum().values,
    "null_pct": (df.isnull().mean().values * 100).round(2)
})

missing_summary["flag_above_90pct_null"] = missing_summary["null_pct"] > 90
missing_summary = missing_summary.sort_values(by="null_count", ascending=False)

# %%
print("\n=== MISSING VALUE SUMMARY ===")
print(missing_summary)

print("\n=== COLUMNS ABOVE 90% NULL ===")
high_null_cols = missing_summary[missing_summary["flag_above_90pct_null"]]
print(high_null_cols)

# %%
# 5. Numeric distribution summary
target_numeric_cols = ["ListPrice", "LivingArea", "DaysOnMarket"]

summary_rows = []

for col in target_numeric_cols:
    if col in df.columns:
        s = pd.to_numeric(df[col], errors="coerce")
        summary_rows.append({
            "column": col,
            "count_non_null": s.notna().sum(),
            "min": s.min(),
            "p5": s.quantile(0.05),
            "p25": s.quantile(0.25),
            "median": s.median(),
            "mean": s.mean(),
            "p75": s.quantile(0.75),
            "p95": s.quantile(0.95),
            "max": s.max()
        })
    else:
        summary_rows.append({
            "column": col,
            "count_non_null": None,
            "min": None,
            "p5": None,
            "p25": None,
            "median": None,
            "mean": None,
            "p75": None,
            "p95": None,
            "max": None
        })

numeric_summary = pd.DataFrame(summary_rows)

print("\n=== NUMERIC DISTRIBUTION SUMMARY ===")
print(numeric_summary)

# %% [markdown]
# ●	What is the Residential vs. other property type share? 

# %%
prop_counts = df["PropertyType"].value_counts(dropna=False)
total = len(df)

print("\n=== PropertyType Distribution ===")
print(prop_counts)
prop_pct = (prop_counts / total * 100).round(2)

print("\n=== PropertyType Share (%) ===")
print(prop_pct)

# %% [markdown]
# ●	What are the median and average close prices? 

# %%

mean_price = df["ClosePrice"].mean()
median_price = df["ClosePrice"].median()

print("\n=== ClosePrice Summary ===")
print(f"Average (Mean): {round(mean_price, 2)}")
print(f"Median: {round(median_price, 2)}")
print("\n=== ClosePrice Distribution ===")
print(df["ClosePrice"].describe())

# %% [markdown]
# ●	What does the Days on Market distribution look like? 

# %%
import matplotlib.pyplot as plt

plt.hist(df["DaysOnMarket"], bins=100)
plt.xlabel("Days on Market")
plt.ylabel("Frequency")
plt.title("Distribution of Days on Market")
plt.show()

# %% [markdown]
# ●	What percentage of homes sold above vs. below list price? 

# %%
above = (df["ClosePrice"] > df["ListPrice"]).sum()
below = (df["ClosePrice"] < df["ListPrice"]).sum()
equal = (df["ClosePrice"] == df["ListPrice"]).sum()

total = len(df)

above_pct = round(above / total * 100, 2)
below_pct = round(below / total * 100, 2)
equal_pct = round(equal / total * 100, 2)

print("\n=== Sold Price vs List Price ===")
print(f"Above List Price: {above_pct}%")
print(f"Below List Price: {below_pct}%")
print(f"Equal to List Price: {equal_pct}%")

# %% [markdown]
# ● Are there any apparent date consistency issues (e.g., close date before listing date)? 

# %%
df["PurchaseContractDate"] = pd.to_datetime(df["PurchaseContractDate"], errors="coerce")


close_before_list = (df["CloseDate"] < df["ListingContractDate"]).sum()
purchase_before_list = (df["PurchaseContractDate"] < df["ListingContractDate"]).sum()
close_before_purchase = (df["CloseDate"] < df["PurchaseContractDate"]).sum()

total = len(df)

print("\n=== Date Consistency Check ===")
print(f"Close < Listing: {close_before_list} ({round(close_before_list/total*100,4)}%)")
print(f"Purchase < Listing: {purchase_before_list} ({round(purchase_before_list/total*100,4)}%)")
print(f"Close < Purchase: {close_before_purchase} ({round(close_before_purchase/total*100,4)}%)")

# %% [markdown]
# A very small number of records show date inconsistencies, such as close or purchase dates occurring before the listing date. These issues affect less than 0.1% of the dataset and are likely due to data entry errors, so they should be addressed during data cleaning.

# %% [markdown]
# ●	Which counties have the highest median prices? 

# %%
county_median = (
    df.groupby("CountyOrParish")["ClosePrice"]
    .median()
    .sort_values(ascending=False))

print("\n=== Median Close Price by County ===")
print(county_median.head(10))

# %% [markdown]
# week-3

# %%
# Step 1 – Fetch the mortgage rate data from FRED import pandas as pd 
import pandas as pd
url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US" 
mortgage = pd.read_csv(url, parse_dates=['observation_date']) 
mortgage.columns = ['date', 'rate_30yr_fixed'] 

# %%
# step 2 – Resample weekly rates to monthly averages 
mortgage['year_month'] = mortgage['date'].dt.to_period('M')
mortgage_monthly = (
    mortgage.groupby('year_month')['rate_30yr_fixed']
    .mean()
    .reset_index()
)
print(mortgage_monthly.head())

# %%
# Step 3 – Create a matching year_month key on the MLS datasets
# Sold dataset — key off CloseDate 
import pandas as pd
sold = pd.read_csv("CRMLSSold_residential.csv")
# Listings dataset — key off ListingContractDate 
listings = pd.read_csv("CRMLSlisting_residential.csv")
sold['year_month'] = pd.to_datetime(sold['CloseDate']).dt.to_period('M')
listings['year_month'] = pd.to_datetime(listings['ListingContractDate'], errors='coerce'
).dt.to_period('M')

#step 4 - Merge
sold_with_rates = sold.merge(mortgage_monthly, on='year_month', how='left')
listings_with_rates = listings.merge(mortgage_monthly, on='year_month', how='left') 

# Step 5 – Validate the merge 
print("=== Validation Check ===")
print("Missing rates in sold:", sold_with_rates['rate_30yr_fixed'].isnull().sum())
print("Missing rates in listings:", listings_with_rates['rate_30yr_fixed'].isnull().sum())

# %%
# step 6 - Preview
print("=== SOLD WITH RATES ===")
print(sold_with_rates[['CloseDate', 'year_month', 'ClosePrice', 'rate_30yr_fixed']].head())

print("\n=== LISTINGS WITH RATES ===")
print(listings_with_rates[['ListingContractDate', 'year_month', 'ListPrice', 'rate_30yr_fixed']].head())

# %%
import pandas as pd
df = pd.read_csv("CRMLSSold_with_rates.csv")
print(df.shape)  

# %% [markdown]
# week 4-5

# %% [markdown]
# Step 1  Process Date Fields

# %%

date_cols = [
    "CloseDate",
    "PurchaseContractDate",
    "ListingContractDate",
    "ContractStatusChangeDate"
]
print(df[date_cols].dtypes)
print(df[date_cols].head(3))

# %%
# Convert the date column to datetime.
for col in date_cols:
    df[col] = pd.to_datetime(df[col], errors="coerce")
print(df[date_cols].dtypes)
print(df[date_cols].head(5))

# %%
# create date consistency flags

# A. listing date is after close date
df["listing_after_close_flag"] = (
    df["ListingContractDate"].notna() &
    df["CloseDate"].notna() &
    (df["ListingContractDate"] > df["CloseDate"])
)

# B. purchase date is after close date
df["purchase_after_close_flag"] = (
    df["PurchaseContractDate"].notna() &
    df["CloseDate"].notna() &
    (df["PurchaseContractDate"] > df["CloseDate"])
)

# C. negative timeline:
# listing date is after purchase date
df["negative_timeline_flag"] = (
    df["ListingContractDate"].notna() &
    df["PurchaseContractDate"].notna() &
    (df["ListingContractDate"] > df["PurchaseContractDate"])
)

#  check flag counts
print("Flag counts:")
print("listing_after_close_flag:", df["listing_after_close_flag"].sum())
print("purchase_after_close_flag:", df["purchase_after_close_flag"].sum())
print("negative_timeline_flag:", df["negative_timeline_flag"].sum())
print()

# %%
print("Rows with listing_after_close_flag = 1")
print(df.loc[df["listing_after_close_flag"] == 1,
             ["ListingContractDate", "PurchaseContractDate", "CloseDate"]].head())

print("\nRows with purchase_after_close_flag = 1")
print(df.loc[df["purchase_after_close_flag"] == 1,
             ["ListingContractDate", "PurchaseContractDate", "CloseDate"]].head())

print("\nRows with negative_timeline_flag = 1")
print(df.loc[df["negative_timeline_flag"] == 1,
             ["ListingContractDate", "PurchaseContractDate", "CloseDate"]].head())

# %%
# High-Missing Columns (≥90%)
missing_pct = df.isnull().mean() * 100
high_missing_cols = missing_pct[missing_pct >= 90].index.tolist()
print("High-missing cols:", len(high_missing_cols))

# Non-analytical Column
extra_drop = [
    "BuyerAgentAOR", "ListAgentAOR",
    "ListAgentEmail",
    "ListAgentFirstName", "ListAgentLastName",
    "ListAgentFullName",
    "BuyerAgentFirstName", "BuyerAgentLastName",
    "CoListAgentFirstName", "CoListAgentLastName",
    "BuyerOfficeAOR", "BuyerAgencyCompensationType", "BuyerAgencyCompensation"
]
extra_drop = [col for col in extra_drop if col in df.columns]
print("Manual drop cols:", len(extra_drop))

before_cols = df.shape[1]
# Execute Deletion
df = df.drop(columns=high_missing_cols)
df = df.drop(columns=extra_drop)

after_cols = df.shape[1]

print("===== Check Deletion =====")
print("Before:", before_cols)
print("After:", after_cols)
print("Removed:", before_cols - after_cols)

# %%
# ---------- Duplicate Column Check ----------
# 1. Suffix duplicates (.1, .2, etc.)
suffix_dups = [col for col in df.columns if col.endswith((".1", ".2", ".3"))]

# 2. Duplicate column names
name_dups = df.columns[df.columns.duplicated()].tolist()

# 3. Duplicate content columns
content_dups = []
cols = df.columns

for i in range(len(cols)):
    for j in range(i + 1, len(cols)):
        if df[cols[i]].equals(df[cols[j]]):
            content_dups.append((cols[i], cols[j]))

# ---------- Print Summary ----------
print("===== Duplicate Column Summary =====")
print(f"Suffix duplicates (.1 etc): {len(suffix_dups)}")
print(f"Duplicate column names: {len(name_dups)}")
print(f"Duplicate content pairs: {len(content_dups)}")

print("\n===== Duplicate Content Examples =====")

for col1, col2 in content_dups:
    print(f"\nComparing: {col1} vs {col2}")
    print(df[[col1, col2]].head(5))

# %%
#---------- Drop Duplicate Columns ----------
df = df.drop(columns=["ListingKeyNumeric"])
print("Dropped ListingKeyNumeric (duplicate of ListingKey)")

# Remove duplicate rows 
# =========================
before = len(df)
df = df.drop_duplicates()
after = len(df)

print("\n[Sold]")
print(f"Before : {before:,} rows")
print(f"After  : {after:,} rows")
print(f"Removed: {before - after:,} duplicate rows")
print(df[["latfilled", "lonfilled"]].isnull().mean())
#Although latfilled and lonfilled appeared identical in some cases, further
# inspection showed that they primarily consist of missing values and represent data 
# quality flags rather than true duplicate variables. Therefore, they were not removed
#  as duplicate columns.

# %%
#Check to ensure that the data type is correct
num_cols = [
    "ClosePrice",
    "ListPrice",
    "LivingArea",
    "DaysOnMarket",
    "BedroomsTotal",
    "BathroomsTotalInteger"
]

print(df[num_cols].dtypes)
for col in num_cols:
    print(f"\n--- {col} sample values ---")
    print(df[col].head(3))
for col in num_cols:
    print(f"{col} missing after conversion:", df[col].isna().sum())

# %%
# numeric columns
numeric_cols = [
    "ClosePrice",
    "OriginalListPrice",
    "ListPrice",
    "LivingArea",
    "LotSizeAcres",
    "DaysOnMarket",
    "YearBuilt",
    "BathroomsTotalInteger",
    "BedroomsTotal",
    "Latitude",
    "Longitude",
    "AssociationFee",
    "ParkingTotal",
    "GarageSpaces",
    "LotSizeSquareFeet",
    "rate_30yr_fixed"
]
# convert to numeric
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")
# check data types
print("\nNumeric Column Types:")
print(df[numeric_cols].dtypes)

# preview
print("\nNumeric Columns Preview:")
print(df[numeric_cols].head(3))

# %% [markdown]
# Step 3: Outlier Check (Invalid Values)

# %%
# Invalid value flags 
# -------------------------------

df["invalid_close_price_flag"] = (df["ClosePrice"] <= 0)
df["invalid_living_area_flag"] = (df["LivingArea"] <= 0)
df["invalid_days_on_market_flag"] = (df["DaysOnMarket"] < 0)
df["invalid_bedrooms_flag"] = (df["BedroomsTotal"] < 0)
df["invalid_bathrooms_flag"] = (df["BathroomsTotalInteger"] < 0)


# count
print("Invalid Value Counts:")
print(df[
    [
        "invalid_close_price_flag",
        "invalid_living_area_flag",
        "invalid_days_on_market_flag",
        "invalid_bedrooms_flag",
        "invalid_bathrooms_flag"
    ]
].sum())

# %% [markdown]
# Step 4：Geographic Data Checks

# %%
# -------------------------------
# Geographic flags
# -------------------------------

# 1️ Missing Values
df["missing_geo_flag"] = (
    df["Latitude"].isna() | df["Longitude"].isna()
)

# 2️.Zero Values ​​(Dummy Data)
df["zero_geo_flag"] = (
    (df["Latitude"] == 0) | (df["Longitude"] == 0)
)

# 3.Incorrect longitude direction (California should be negative).
df["invalid_longitude_flag"] = (
    df["Longitude"] > 0
)

# 4️. Outside the California area (approximate range)
df["out_of_ca_flag"] = (
    (df["Latitude"] < 32) | (df["Latitude"] > 42) |
    (df["Longitude"] < -125) | (df["Longitude"] > -114)
)

# Count issues
print("Geographic Issues Count:")
print("missing_geo_flag:", df["missing_geo_flag"].sum())
print("zero_geo_flag:", df["zero_geo_flag"].sum())
print("invalid_longitude_flag:", df["invalid_longitude_flag"].sum())
print("out_of_ca_flag:", df["out_of_ca_flag"].sum())


# %% [markdown]
# There are 15,906 records with geographic issues. Most of them are missing latitude or longitude (15,822). A few records have zero values, invalid longitude, or are outside California. Missing coordinates are the main problem.

# %%
# -------------------------------
# Clean data: numeric + date + geo
# -------------------------------

before_rows = len(df)

df_clean = df[
    # numeric validity
    (df["ClosePrice"] > 0) &
    (df["LivingArea"] > 0) &
    (df["DaysOnMarket"] >= 0) &
    (
        (df["BedroomsTotal"].isna()) |
        (df["BedroomsTotal"] >= 0)
    ) &
    (
        (df["BathroomsTotalInteger"].isna()) |
        (df["BathroomsTotalInteger"] >= 0)
    ) &
    # date validity
    (df["listing_after_close_flag"] == 0) &
    (df["purchase_after_close_flag"] == 0) &
    (df["negative_timeline_flag"] == 0) &

    # geo validity
    (df["zero_geo_flag"] == 0) &
    (df["invalid_longitude_flag"] == 0) &
    (df["out_of_ca_flag"] == 0)
].copy()

after_rows = len(df_clean)

print("\nFinal Cleaning Summary:")
print("Rows before cleaning:", before_rows)
print("Rows after cleaning :", after_rows)
print("Rows removed        :", before_rows - after_rows)

# %%
flag_cols = [
    "listing_after_close_flag",
    "purchase_after_close_flag",
    "negative_timeline_flag",
    "invalid_close_price_flag",
    "invalid_living_area_flag",
    "invalid_days_on_market_flag",
    "invalid_bedrooms_flag",
    "invalid_bathrooms_flag",
    "missing_geo_flag",
    "zero_geo_flag",
    "invalid_longitude_flag",
    "out_of_ca_flag"
]

df[flag_cols].sum().sort_values(ascending=False)

# %% [markdown]
# week-6

# %%
import pandas as pd
import numpy as np

# Key Metrics to Create
# =============================

# 1. Price Ratio
df["price_ratio"] = np.where(
    df["OriginalListPrice"] > 0,
    df["ClosePrice"] / df["OriginalListPrice"],
    np.nan
)

# 2. Close-to-Original-List Ratio
df["close_to_original_list_ratio"] = np.where(
    df["OriginalListPrice"] > 0,
    df["ClosePrice"] / df["OriginalListPrice"],
    np.nan
)

# 3. Price Per Square Foot
df["price_per_sqft"] = np.where(
    df["LivingArea"] > 0,
    df["ClosePrice"] / df["LivingArea"],
    np.nan
)

# 4. Year / Month / YrMo
df["close_year"] = df["CloseDate"].dt.year
df["close_month"] = df["CloseDate"].dt.month
df["YrMo"] = df["CloseDate"].dt.to_period("M").astype(str)

# 5. Listing-to-Contract Days
df["listing_to_contract_days"] = (
    df["PurchaseContractDate"] - df["ListingContractDate"]
).dt.days

# 6. Contract-to-Close Days
df["contract_to_close_days"] = (
    df["CloseDate"] - df["PurchaseContractDate"]
).dt.days

# Sample output table
# =============================

sample_cols = [
    "CloseDate",
    "ClosePrice",
    "OriginalListPrice",
    "LivingArea",
    "price_ratio",
    "close_to_original_list_ratio",
    "price_per_sqft",
    "DaysOnMarket",
    "YrMo",
    "listing_to_contract_days",
    "contract_to_close_days"
]

print("\nSample engineered metrics:")
print(df[sample_cols].head(5))
print("Saved: Sold_county_segment_summary.csv")
#pd.read_csv("Sold_county_segment_summary.csv")

# %%
key_metrics = [
    'price_ratio',
    'price_per_sqft',
    'DaysOnMarket',
    'close_to_original_list_ratio',
    'listing_to_contract_days',
    'contract_to_close_days'
]

for m in key_metrics:
    print(f"{m}: {'exists' if m in df.columns else ' not found'}")

# %%
# Segment summary table
# 1.Grouped by CountyOrParish
county_summary = (
    df.groupby("CountyOrParish")
    .agg(
        total_sales=("ClosePrice", "count"),
        median_close_price=("ClosePrice", "median"),
        average_close_price=("ClosePrice", "mean"),
        median_price_per_sqft=("price_per_sqft", "median"),
        average_days_on_market=("DaysOnMarket", "mean"),
        median_price_ratio=("price_ratio", "median"),
        average_listing_to_contract_days=("listing_to_contract_days", "mean"),
        average_contract_to_close_days=("contract_to_close_days", "mean")
    )
    .reset_index()
    .sort_values(by="median_close_price", ascending=False)
)
print("Saved: Sold_county_segment_summary.csv")
pd.read_csv("Sold_county_segment_summary.csv")

# %%
# =============================
# PropertyType + PropertySubType
# =============================

property_summary = (
    df.groupby(
        ["PropertyType", "PropertySubType"]
    )
    .agg(
        total_sales=("ClosePrice", "count"),
        median_close_price=("ClosePrice", "median"),
        average_close_price=("ClosePrice", "mean"),
        median_price_per_sqft=("price_per_sqft", "median"),
        average_days_on_market=("DaysOnMarket", "mean"),
        median_price_ratio=("price_ratio", "median")
    )
    .reset_index()
    .sort_values(
        by="median_close_price",
        ascending=False
    )
)
print("Saved:Sold_property_segment_summary.csv")
pd.read_csv("Sold_property_segment_summary.csv")

# %%
# # CountyOrParish + MLSAreaMajor
# =============================

county_area_summary = (
    df.groupby(
        ["CountyOrParish", "MLSAreaMajor"]
    )
    .agg(
        total_sales=("ClosePrice", "count"),
        median_close_price=("ClosePrice", "median"),
        average_close_price=("ClosePrice", "mean"),
        median_price_per_sqft=("price_per_sqft", "median"),
        average_days_on_market=("DaysOnMarket", "mean"),
        median_price_ratio=("price_ratio", "median")
    )
    .reset_index()
    .sort_values(
        by="median_close_price",
        ascending=False
    )
)
print("Saved: Sold_county_area_segment_summary.csv")
pd.read_csv("Sold_county_area_segment_summary.csv")

# %%
# =============================
# ListOfficeName + BuyerOfficeName
# =============================

office_summary = (
    df.groupby(
        ["ListOfficeName", "BuyerOfficeName"]
    )
    .agg(
        total_sales=("ClosePrice", "count"),
        median_close_price=("ClosePrice", "median"),
        average_close_price=("ClosePrice", "mean"),
        median_price_per_sqft=("price_per_sqft", "median"),
        average_days_on_market=("DaysOnMarket", "mean"),
        median_price_ratio=("price_ratio", "median")
    )
    .reset_index()
    .sort_values(
        by="total_sales",
        ascending=False
    )
)
print("Saved: Sold_office_segment_summary.csv")
pd.read_csv("Sold_office_segment_summary.csv")

# %%
required_cols = [
    "ClosePrice",
    "OriginalListPrice",
    "LivingArea",
    "CloseDate",
    "PurchaseContractDate",
    "ListingContractDate",
    "DaysOnMarket",
    "CountyOrParish"
]

missing_cols = [col for col in required_cols if col not in df.columns]

if missing_cols:
    print("Missing columns:", missing_cols)
else:
    print("All required columns exist.")

# %% [markdown]
# Week-7

# %%
df = pd.read_csv("sold_flagged_full.csv")
print(df.shape)

# %%
flag_cols = [
    "listing_after_close_flag",
    "purchase_after_close_flag",
    "negative_timeline_flag",
    "invalid_close_price_flag",
    "invalid_living_area_flag",
    "invalid_days_on_market_flag",
    "invalid_bedrooms_flag",
    "invalid_bathrooms_flag",
    "missing_geo_flag",
    "zero_geo_flag",
    "invalid_longitude_flag",
    "out_of_ca_flag"
]

df[flag_cols].sum().sort_values(ascending=False)

# %%
# Convert numeric columns
numeric_cols = [
    "ClosePrice",
    "LivingArea",
    "DaysOnMarket"
]

for col in numeric_cols:
    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )

print("\nNumeric conversion complete")
print(df[numeric_cols].dtypes)

# %%
# These flags were already created in previous weeks

rule_flags = [
    "invalid_close_price_flag",
    "invalid_living_area_flag",
    "invalid_days_on_market_flag",
    "invalid_numeric_flag"
]

for col in rule_flags:

    if col in df.columns:

        # Convert to Boolean
        df[col] = (
            df[col]
            .astype(str)
            .str.lower()
            .isin(["true", "1", "yes"])
        )
        print(f"{col} loaded successfully")

    else:
        print(f"Warning: {col} not found")


# %%
#  Define IQR outlier function

def add_iqr_flag(df, column_name):

    # Calculate quartiles
    Q1 = df[column_name].quantile(0.25)
    Q3 = df[column_name].quantile(0.75)

   
    IQR = Q3 - Q1

  
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR

   
    flag_col = f"{column_name}_iqr_outlier_flag"
 # Flag outliers
    df[flag_col] = (
        (df[column_name] < lower) |
        (df[column_name] > upper)
    )

    # Print IQR summary
    print("\n===================================")
    print(f"{column_name} IQR Summary")
    print("===================================")

    print(f"Q1: {Q1}")
    print(f"Q3: {Q3}")
    print(f"IQR: {IQR}")

    print(f"Lower Bound: {lower}")
    print(f"Upper Bound: {upper}")

    print(
        f"Outliers Flagged: {df[flag_col].sum()}"
    )

    return df

# %%
#Apply IQR outlier detection
# Apply IQR filtering to:
# ClosePrice
# LivingArea
# DaysOnMarket

df = add_iqr_flag(df, "ClosePrice")

df = add_iqr_flag(df, "LivingArea")

df = add_iqr_flag(df, "DaysOnMarket")

# %%
# Create combined IQR outlier flag
# If any numeric field is an outlier,
# mark the row as True

df["any_iqr_outlier_flag"] = (

    df["ClosePrice_iqr_outlier_flag"] |

    df["LivingArea_iqr_outlier_flag"] |

    df["DaysOnMarket_iqr_outlier_flag"]

)

print("\nCombined IQR flag created")

print(
    df["any_iqr_outlier_flag"]
    .value_counts()
)

# %%
# Create final exclusion flag- Combine:
# rule invalid records + IQR outliers
if "invalid_numeric_flag" in df.columns:

    df["exclude_from_analysis_flag"] = (

        df["invalid_numeric_flag"] |

        df["any_iqr_outlier_flag"]

    )

else:

    df["exclude_from_analysis_flag"] = (
        df["any_iqr_outlier_flag"]
    )

print("\nFinal exclusion flag created")

print(
    df["exclude_from_analysis_flag"]
    .value_counts()
)

# %%
#  Create clean filtered dataset
# Keep only records
# that are NOT excluded

df_filtered = df[
    ~df["exclude_from_analysis_flag"]
].copy()

print("\nFiltered dataset created")

print("Original rows:", len(df))

print("Filtered rows:", len(df_filtered))

# %%
# Compare before and after filtering

comparison_rows = []

fields = [
    "ClosePrice",
    "LivingArea",
    "DaysOnMarket"
]

for col in fields:

    outlier_flag_col = f"{col}_iqr_outlier_flag"

    comparison_rows.append({

        "Field": col,

        "Median Before": df[col].median(),

        "Median After": df_filtered[col].median(),

        "Mean Before": df[col].mean(),

        "Mean After": df_filtered[col].mean(),

      

    })

comparison = pd.DataFrame(comparison_rows)
print("Before vs After Filtering Comparison")

print(comparison)

# %%
print("Saved files:")

print("1. CRMLSSold_Week7_Flagged.csv")

print("2. CRMLSSold_Week7_Filtered.csv")

print("3. Week7_sold_Filtering_Comparison.csv")


