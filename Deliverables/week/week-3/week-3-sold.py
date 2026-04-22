# %%
import pandas as pd
import numpy as np
df = pd.read_csv("CRMLSSold_with_rates.csv")
print("SOLD shape:", df.shape)

# %%
# 2.Define Cleaning Function (with Statistics) 
# =========================
def remove_high_missing(df, label, threshold=90):
    
    print(f"\n========== {label} ==========")
    print(f"Original shape: {df.shape}")
    
    # Original Number of Columns
    before_cols = df.shape[1]
    
    # Calculate the missing proportion.
    missing_pct = df.isnull().mean() * 100
    
    # High-Missing Columns
    high_missing = missing_pct[missing_pct >= threshold]
    num_high_missing = len(high_missing)
    
    print(f"\nColumns with >= {threshold}% missing:")
    print(high_missing.sort_values(ascending=False))
    
    print(f"\nNumber of high-missing columns: {num_high_missing}")
    
    # Delete High Missing Values
    df_clean = df.drop(columns=high_missing.index)
    
    after_missing_cols = df_clean.shape[1]
    
    print(f"Columns AFTER high-missing drop: {after_missing_cols}")
    print("-" * 40)
    
    return df_clean, high_missing.index.tolist()


# 3.Cleaning Executed (SOLD)
# =========================
df_sold_clean, high_missing_cols = remove_high_missing(df, "SOLD")


# 4. Manual Deletion (Extra)
# =========================
extra_drop = [
    # Categorical columns
    "BuyerAgentAOR", "ListAgentAOR",
    "ListAgentEmail",
    "ListAgentFirstName", "ListAgentLastName",
    "ListAgentFullName",
    "BuyerAgentFirstName", "BuyerAgentLastName",
    "CoListAgentFirstName", "CoListAgentLastName",
    "ListOfficeName", "BuyerOfficeName", "CoListOfficeName",
    "BuyerOfficeAOR","BuyerAgencyCompensationType","BuyerAgencyCompensation"
 
    
]

num_extra = len(extra_drop)

# Merge and Delete (Deduplication)
all_drop = list(set(high_missing_cols + extra_drop))

# delete
before_all = df_sold_clean.shape[1]
df_sold_clean = df_sold_clean.drop(columns=extra_drop, errors="ignore")
after_all = df_sold_clean.shape[1]

# 5. summary
# =========================
print("\n===== FINAL CLEANING SUMMARY =====")
print(f"Original columns: {before_all}")
print(f"High-missing columns removed: {len(high_missing_cols)}")
print(f"Extra columns removed: {num_extra}")
print(f"Total unique columns removed: {len(all_drop)}")
print(f"Remaining columns: {after_all}")



