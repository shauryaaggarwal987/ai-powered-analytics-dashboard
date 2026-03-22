"""
Data Loading Service
Cached data loading for all processed datasets and metadata.
"""
import streamlit as st
import pandas as pd
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
CLEANED_PATH = os.path.join(PROCESSED_DIR, "online_retail_cleaned.csv")
METADATA_PATH = os.path.join(PROCESSED_DIR, "metadata.json")


@st.cache_data(ttl=600)
def load_monthly_revenue() -> pd.DataFrame:
    """Load monthly_revenue.csv → columns: YearMonth, Revenue"""
    path = os.path.join(PROCESSED_DIR, "monthly_revenue.csv")
    if not os.path.exists(path):
        return pd.DataFrame(columns=["YearMonth", "Revenue"])
    df = pd.read_csv(path)
    df["Revenue"] = pd.to_numeric(df["Revenue"], errors="coerce").fillna(0)
    return df.sort_values("YearMonth").reset_index(drop=True)


@st.cache_data(ttl=600)
def load_country_revenue() -> pd.DataFrame:
    """Load country_revenue.csv → columns: Country, Revenue"""
    path = os.path.join(PROCESSED_DIR, "country_revenue.csv")
    if not os.path.exists(path):
        return pd.DataFrame(columns=["Country", "Revenue"])
    df = pd.read_csv(path)
    df["Revenue"] = pd.to_numeric(df["Revenue"], errors="coerce").fillna(0)
    return df.sort_values("Revenue", ascending=False).reset_index(drop=True)


@st.cache_data(ttl=600)
def load_top_products() -> pd.DataFrame:
    """Load top_products.csv → columns: Description, Revenue"""
    path = os.path.join(PROCESSED_DIR, "top_products.csv")
    if not os.path.exists(path):
        return pd.DataFrame(columns=["Description", "Revenue"])
    df = pd.read_csv(path)
    df["Revenue"] = pd.to_numeric(df["Revenue"], errors="coerce").fillna(0)
    return df.sort_values("Revenue", ascending=False).reset_index(drop=True)


@st.cache_data(ttl=600)
def load_month_country() -> pd.DataFrame:
    """Load month_country_revenue.csv → columns: YearMonth, Country, Revenue"""
    path = os.path.join(PROCESSED_DIR, "month_country_revenue.csv")
    if not os.path.exists(path):
        return pd.DataFrame(columns=["YearMonth", "Country", "Revenue"])
    df = pd.read_csv(path)
    df["Revenue"] = pd.to_numeric(df["Revenue"], errors="coerce").fillna(0)
    return df.sort_values(["YearMonth", "Revenue"], ascending=[True, False]).reset_index(drop=True)


@st.cache_data(ttl=600)
def load_month_product() -> pd.DataFrame:
    """Load month_product_revenue.csv → columns: YearMonth, Description, Revenue"""
    path = os.path.join(PROCESSED_DIR, "month_product_revenue.csv")
    if not os.path.exists(path):
        return pd.DataFrame(columns=["YearMonth", "Description", "Revenue"])
    df = pd.read_csv(path)
    df["Revenue"] = pd.to_numeric(df["Revenue"], errors="coerce").fillna(0)
    return df.sort_values(["YearMonth", "Revenue"], ascending=[True, False]).reset_index(drop=True)


@st.cache_data(ttl=600)
def load_metadata() -> dict:
    """Load metadata.json with allowed values and capabilities."""
    if not os.path.exists(METADATA_PATH):
        return {
            "allowed_yearmonths": [],
            "allowed_countries": [],
            "capabilities": {"modes": [], "slots": [], "metrics": []},
        }
    with open(METADATA_PATH, "r") as f:
        return json.load(f)


@st.cache_data(ttl=600)
def load_cleaned_data_summary() -> dict:
    """Load summary statistics from the cleaned dataset (not full load for speed)."""
    if not os.path.exists(CLEANED_PATH):
        return None
    try:
        df = pd.read_csv(CLEANED_PATH, low_memory=False, usecols=["Invoice", "Customer ID", "Quantity", "Price", "Revenue", "InvoiceDate", "Country", "Description"])
        df["Invoice"] = df["Invoice"].astype(str).str.strip()
        df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")
        return {
            "total_revenue": float(df["Revenue"].sum()),
            "num_orders": int(df["Invoice"].nunique()),
            "unique_customers": int(df["Customer ID"].dropna().nunique()),
            "avg_order_value": float(df.groupby("Invoice")["Revenue"].sum().mean()),
            "num_countries": int(df["Country"].nunique()),
            "num_products": int(df["Description"].dropna().nunique()),
            "total_rows": len(df),
            "date_min": str(df["InvoiceDate"].min().date()) if df["InvoiceDate"].notna().any() else "N/A",
            "date_max": str(df["InvoiceDate"].max().date()) if df["InvoiceDate"].notna().any() else "N/A",
        }
    except Exception as e:
        return {"error": str(e)}


def get_filtered_month_country(yearmonths: list = None, countries: list = None) -> pd.DataFrame:
    """Return month-country data filtered by selected yearmonths and countries."""
    df = load_month_country()
    if yearmonths:
        df = df[df["YearMonth"].isin(yearmonths)]
    if countries:
        df = df[df["Country"].isin(countries)]
    return df


def get_filtered_month_product(yearmonths: list = None, countries: list = None) -> pd.DataFrame:
    """Return month-product data filtered by selected yearmonths."""
    df = load_month_product()
    if yearmonths:
        df = df[df["YearMonth"].isin(yearmonths)]
    return df


def get_filtered_monthly(yearmonths: list = None) -> pd.DataFrame:
    """Return monthly revenue filtered by yearmonths."""
    df = load_monthly_revenue()
    if yearmonths:
        df = df[df["YearMonth"].isin(yearmonths)]
    return df


def get_available_files() -> dict:
    """Check which processed files exist."""
    files = {
        "monthly_revenue.csv": os.path.exists(os.path.join(PROCESSED_DIR, "monthly_revenue.csv")),
        "country_revenue.csv": os.path.exists(os.path.join(PROCESSED_DIR, "country_revenue.csv")),
        "top_products.csv": os.path.exists(os.path.join(PROCESSED_DIR, "top_products.csv")),
        "month_country_revenue.csv": os.path.exists(os.path.join(PROCESSED_DIR, "month_country_revenue.csv")),
        "month_product_revenue.csv": os.path.exists(os.path.join(PROCESSED_DIR, "month_product_revenue.csv")),
        "metadata.json": os.path.exists(METADATA_PATH),
        "online_retail_cleaned.csv": os.path.exists(CLEANED_PATH),
    }
    return files
