
# Step 1 – Fetch the mortgage rate data from FRED import pandas as pd 
import pandas as pd
url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US" 
mortgage = pd.read_csv(url, parse_dates=['observation_date']) 
mortgage.columns = ['date', 'rate_30yr_fixed'] 

# step 2 – Resample weekly rates to monthly averages 
mortgage['year_month'] = mortgage['date'].dt.to_period('M')
mortgage_monthly = (
    mortgage.groupby('year_month')['rate_30yr_fixed']
    .mean()
    .reset_index()
)
print(mortgage_monthly.head())

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

# step 6 - Preview
print("=== SOLD WITH RATES ===")
print(sold_with_rates[['CloseDate', 'year_month', 'ClosePrice', 'rate_30yr_fixed']].head())

print("\n=== LISTINGS WITH RATES ===")
print(listings_with_rates[['ListingContractDate', 'year_month', 'ListPrice', 'rate_30yr_fixed']].head())
