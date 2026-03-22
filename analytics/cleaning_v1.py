import pandas as pd

RAW_PATH = "../data/raw/online_retail_II.csv"

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
    print("\nSample cleaned data:")
    print(df_clean.head())
