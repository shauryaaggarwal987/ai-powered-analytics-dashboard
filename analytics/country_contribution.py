import pandas as pd

DATA_PATH = "data/processed/online_retail_cleaned.csv"
OUT_PATH = "data/processed/country_revenue.csv"

df = pd.read_csv(DATA_PATH, low_memory=False)
df["Invoice"] = df["Invoice"].astype(str).str.strip()
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

country_rev = (
    df.groupby("Country")["Revenue"]
      .sum()
      .reset_index()
      .sort_values("Revenue", ascending=False)
)

country_rev.to_csv(OUT_PATH, index=False)
print("Saved:", OUT_PATH)
print(country_rev.head())
