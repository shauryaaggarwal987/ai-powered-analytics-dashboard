import pandas as pd

DATA_PATH = "data/processed/online_retail_cleaned.csv"
OUT_PATH = "data/processed/top_products.csv"

df = pd.read_csv(DATA_PATH, low_memory=False)
df["Invoice"] = df["Invoice"].astype(str).str.strip()

top_products = (
    df.groupby("Description")["Revenue"]
      .sum()
      .reset_index()
      .sort_values("Revenue", ascending=False)
      .head(20)
)

top_products.to_csv(OUT_PATH, index=False)
print("Saved:", OUT_PATH)
print(top_products.head())
