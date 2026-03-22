import pandas as pd

DATA_PATH = "data/processed/online_retail_cleaned.csv"
OUT_PATH = "data/processed/monthly_revenue.csv"

df = pd.read_csv(DATA_PATH, low_memory=False)
df["Invoice"] = df["Invoice"].astype(str).str.strip()
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

df["YearMonth"] = df["InvoiceDate"].dt.to_period("M").astype(str)

monthly = (
    df.groupby("YearMonth")["Revenue"]
      .sum()
      .reset_index()
      .sort_values("YearMonth")
)

monthly.to_csv(OUT_PATH, index=False)
print("Saved:", OUT_PATH)
print(monthly.head())
