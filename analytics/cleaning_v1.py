import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_PATH = os.path.join(BASE_DIR, "../data/raw/online_retail_II.csv")
OUT_PATH = os.path.join(BASE_DIR, "../data/processed/online_retail_cleaned.csv")

def clean_data(path):
    df = pd.read_csv(path)

    # Remove invalid quantities and prices
    df = df[df["Quantity"] > 0]
    df = df[df["Price"] > 0]

    # Convert InvoiceDate to datetime
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

    # Create Revenue column
    df["Revenue"] = df["Quantity"] * df["Price"]

    return df

if __name__ == "__main__":
    df_clean = clean_data(RAW_PATH)

    print("Cleaned dataset shape:", df_clean.shape)
    
    # Save the cleaned dataset
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    df_clean.to_csv(OUT_PATH, index=False)
    print(f"Saved cleaned data to {OUT_PATH}")
    
    print("\nSample cleaned data:")
    print(df_clean.head())
