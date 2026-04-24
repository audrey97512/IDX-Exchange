# %%
import pandas as pd
df = pd.read_csv("CRMLSSold_with_rates.csv")
print(df.shape)  

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
#  convert True/False to 1/0
df["listing_after_close_flag"] = df["listing_after_close_flag"].astype(int)
df["purchase_after_close_flag"] = df["purchase_after_close_flag"].astype(int)
df["negative_timeline_flag"] = df["negative_timeline_flag"].astype(int)

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
    "ListOfficeName", "BuyerOfficeName", "CoListOfficeName",
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

# Drop true duplicate column
df = df.drop(columns=["ListingKeyNumeric"])
print("Dropped ListingKeyNumeric (duplicate of ListingKey)")

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

# %% [markdown]
# Step 3: Outlier Check (Invalid Values)

# %%

# Invalid value flags 
# -------------------------------

df["invalid_close_price_flag"] = (df["ClosePrice"] <= 0).astype(int)
df["invalid_living_area_flag"] = (df["LivingArea"] <= 0).astype(int)
df["invalid_days_on_market_flag"] = (df["DaysOnMarket"] < 0).astype(int)
df["invalid_bedrooms_flag"] = (df["BedroomsTotal"] < 0).astype(int)
df["invalid_bathrooms_flag"] = (df["BathroomsTotalInteger"] < 0).astype(int)

# overall flag
df["invalid_numeric_flag"] = df[
    [
        "invalid_close_price_flag",
        "invalid_living_area_flag",
        "invalid_days_on_market_flag",
        "invalid_bedrooms_flag",
        "invalid_bathrooms_flag"
    ]
].max(axis=1)

# count
print("Invalid Value Counts:")
print(df[
    [
        "invalid_close_price_flag",
        "invalid_living_area_flag",
        "invalid_days_on_market_flag",
        "invalid_bedrooms_flag",
        "invalid_bathrooms_flag",
        "invalid_numeric_flag"
    ]
].sum())

# %%
# preview rows with any invalid numeric issue
invalid_rows = df[df["invalid_numeric_flag"] == 1]

print("Rows with any invalid numeric issue:")
print(invalid_rows[
    [
        "ClosePrice",
        "LivingArea",
        "DaysOnMarket",
        "BedroomsTotal",
        "BathroomsTotalInteger"
    ]
].head(10))

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

# 5. Overall Objectives
df["invalid_geo_flag"] = (
    df["missing_geo_flag"] |
    df["zero_geo_flag"] |
    df["invalid_longitude_flag"] |
    df["out_of_ca_flag"]
)

# Convert to 0 / 1
geo_cols = [
    "missing_geo_flag",
    "zero_geo_flag",
    "invalid_longitude_flag",
    "out_of_ca_flag",
    "invalid_geo_flag"
]

for col in geo_cols:
    df[col] = df[col].astype(int)
print("Geographic Issues Count:")
for col in geo_cols:
    print(f"{col}: {df[col].sum()}")

# %% [markdown]
# There are 15,906 records with geographic issues. Most of them are missing latitude or 
# longitude (15,822). A few records have zero values,invalid longitude, or are outside 
# California. Missing coordinates are the main problem.


