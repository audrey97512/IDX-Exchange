# %%
import pandas as pd
import numpy as np
df = pd.read_csv("CRMLSListing_with_rates.csv")
print("listing shape:", df.shape)

# %%
# 2. Define Cleaning Function
def remove_high_missing(df, label, threshold=90):
    print(f"\n========== {label} ==========")
    print(f"Original shape: {df.shape}")
    
    before_cols = df.shape[1]
    
    missing_pct = df.isnull().mean() * 100
    high_missing = missing_pct[missing_pct >= threshold]
    num_high_missing = len(high_missing)
    
    print(f"\nColumns with >= {threshold}% missing:")
    print(high_missing.sort_values(ascending=False))
    
    print(f"\nNumber of high-missing columns: {num_high_missing}")
    
    df_clean = df.drop(columns=high_missing.index)
    
    after_missing_cols = df_clean.shape[1]
    print(f"Columns AFTER high-missing drop: {after_missing_cols}")
    print("-" * 40)
    
    return df_clean, high_missing.index.tolist()


# 3. Cleaning Executed (listing)
df_listing_clean, high_missing_cols = remove_high_missing(df, "listing")


# 4. Manual Deletion (Extra)
extra_drop = [
    "ListAgentEmail",
    "ListAgentFirstName", "ListAgentLastName", "ListAgentFullName",
    "CoListAgentFirstName", "CoListAgentLastName",
    "BuyerAgentFirstName", "BuyerAgentLastName",
    "BuyerAgentMlsId", "BuyerAgencyCompensationType",
    "ListOfficeName", "BuyerOfficeName", "CoListOfficeName",
    "BuyerOfficeAOR", "BuyerOfficeName.1",
    "PropertyType.1",
    "ListAgentFirstName.1", "ListAgentLastName.1",
    "CloseDate.1",
    "UnparsedAddress.1",
    "DaysOnMarket.1", "Longitude.1", "Latitude.1",
    "ListPrice.1", "LivingArea.1",
]

num_extra = len(extra_drop)

before_all = df_listing_clean.shape[1]
df_listing_clean = df_listing_clean.drop(columns=extra_drop, errors="ignore")
after_all = df_listing_clean.shape[1]

# 5. summary
# =========================
print("\n===== FINAL CLEANING SUMMARY =====")
print(f"Original columns: {before_all}")
print(f"High-missing columns removed: {len(high_missing_cols)}")
print(f"Extra columns removed: {num_extra}")
print(f"Remaining columns: {after_all}")



