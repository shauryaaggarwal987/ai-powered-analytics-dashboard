"""
Metrics Computation Service
Deterministic KPI and derived metric calculations from loaded data.
"""
import pandas as pd
from services.data_loader import (
    load_monthly_revenue,
    load_country_revenue,
    load_top_products,
    load_month_country,
    load_cleaned_data_summary,
)


def format_currency(value: float, symbol: str = "£") -> str:
    """Format a number as currency with appropriate abbreviation."""
    if abs(value) >= 1_000_000:
        return f"{symbol}{value / 1_000_000:,.2f}M"
    elif abs(value) >= 1_000:
        return f"{symbol}{value / 1_000:,.1f}K"
    else:
        return f"{symbol}{value:,.2f}"


def format_number(value: float) -> str:
    """Format a number with commas."""
    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:,.2f}M"
    elif abs(value) >= 1_000:
        return f"{value / 1_000:,.1f}K"
    else:
        return f"{value:,.0f}"


def get_overview_kpis() -> dict:
    """Compute KPI metrics for the executive overview."""
    summary = load_cleaned_data_summary()
    monthly = load_monthly_revenue()
    country = load_country_revenue()
    products = load_top_products()

    kpis = {}

    # From cleaned data summary
    if summary and "error" not in summary:
        kpis["total_revenue"] = summary["total_revenue"]
        kpis["num_orders"] = summary["num_orders"]
        kpis["unique_customers"] = summary["unique_customers"]
        kpis["avg_order_value"] = summary["avg_order_value"]
        kpis["num_countries"] = summary["num_countries"]
        kpis["num_products"] = summary["num_products"]
        kpis["date_range"] = f"{summary['date_min']} → {summary['date_max']}"
    else:
        # Fallback from aggregated data
        kpis["total_revenue"] = float(monthly["Revenue"].sum()) if not monthly.empty else 0
        kpis["num_countries"] = len(country) if not country.empty else 0
        kpis["num_products"] = len(products) if not products.empty else 0
        kpis["num_orders"] = 0
        kpis["unique_customers"] = 0
        kpis["avg_order_value"] = 0
        kpis["date_range"] = f"{monthly['YearMonth'].min()} → {monthly['YearMonth'].max()}" if not monthly.empty else "N/A"

    # Best performers from aggregated data
    if not monthly.empty:
        best_month_row = monthly.loc[monthly["Revenue"].idxmax()]
        kpis["best_month"] = best_month_row["YearMonth"]
        kpis["best_month_revenue"] = float(best_month_row["Revenue"])
        kpis["num_months"] = len(monthly)
    else:
        kpis["best_month"] = "N/A"
        kpis["best_month_revenue"] = 0
        kpis["num_months"] = 0

    if not country.empty:
        kpis["best_country"] = country.iloc[0]["Country"]
        kpis["best_country_revenue"] = float(country.iloc[0]["Revenue"])
    else:
        kpis["best_country"] = "N/A"
        kpis["best_country_revenue"] = 0

    if not products.empty:
        kpis["best_product"] = products.iloc[0]["Description"]
        kpis["best_product_revenue"] = float(products.iloc[0]["Revenue"])
    else:
        kpis["best_product"] = "N/A"
        kpis["best_product_revenue"] = 0

    return kpis


def compute_mom_changes(monthly_df: pd.DataFrame) -> pd.DataFrame:
    """Compute month-over-month revenue change and growth rate."""
    if monthly_df.empty or len(monthly_df) < 2:
        return monthly_df
    df = monthly_df.copy().sort_values("YearMonth").reset_index(drop=True)
    df["PrevRevenue"] = df["Revenue"].shift(1)
    df["MoM_Change"] = df["Revenue"] - df["PrevRevenue"]
    df["MoM_Growth_Pct"] = (df["MoM_Change"] / df["PrevRevenue"] * 100).round(2)
    df["Cumulative_Revenue"] = df["Revenue"].cumsum()
    return df


def compute_rolling_average(monthly_df: pd.DataFrame, window: int = 3) -> pd.DataFrame:
    """Add a rolling average column to monthly data."""
    df = monthly_df.copy().sort_values("YearMonth").reset_index(drop=True)
    df[f"Rolling_{window}M_Avg"] = df["Revenue"].rolling(window=window, min_periods=1).mean()
    return df


def compute_country_shares(country_df: pd.DataFrame) -> pd.DataFrame:
    """Add revenue percentage share to country data."""
    df = country_df.copy()
    total = df["Revenue"].sum()
    df["Share_Pct"] = (df["Revenue"] / total * 100).round(2) if total > 0 else 0
    df["Cumulative_Share"] = df["Share_Pct"].cumsum()
    return df


def compute_product_shares(products_df: pd.DataFrame) -> pd.DataFrame:
    """Add revenue percentage share to product data."""
    df = products_df.copy()
    total = df["Revenue"].sum()
    df["Share_Pct"] = (df["Revenue"] / total * 100).round(2) if total > 0 else 0
    df["Cumulative_Share"] = df["Share_Pct"].cumsum()
    return df


def get_trend_insights(monthly_df: pd.DataFrame) -> dict:
    """Generate deterministic narrative insights from monthly data."""
    if monthly_df.empty:
        return {}
    df = monthly_df.copy().sort_values("YearMonth")
    insights = {}
    best_idx = df["Revenue"].idxmax()
    worst_idx = df["Revenue"].idxmin()
    insights["peak_month"] = df.loc[best_idx, "YearMonth"]
    insights["peak_revenue"] = float(df.loc[best_idx, "Revenue"])
    insights["lowest_month"] = df.loc[worst_idx, "YearMonth"]
    insights["lowest_revenue"] = float(df.loc[worst_idx, "Revenue"])
    insights["avg_monthly"] = float(df["Revenue"].mean())
    insights["std_monthly"] = float(df["Revenue"].std())
    insights["total_months"] = len(df)
    insights["total_revenue"] = float(df["Revenue"].sum())
    if len(df) >= 2:
        first_half = df.head(len(df) // 2)["Revenue"].mean()
        second_half = df.tail(len(df) // 2)["Revenue"].mean()
        if first_half > 0:
            insights["trend_direction"] = "upward" if second_half > first_half else "downward"
            insights["trend_change_pct"] = round((second_half - first_half) / first_half * 100, 1)
        else:
            insights["trend_direction"] = "stable"
            insights["trend_change_pct"] = 0
    return insights


def get_country_insights(country_df: pd.DataFrame, top_n: int = 5) -> dict:
    """Generate deterministic narrative insights from country data."""
    if country_df.empty:
        return {}
    df = compute_country_shares(country_df)
    top = df.head(top_n)
    insights = {
        "top_country": df.iloc[0]["Country"],
        "top_country_share": float(df.iloc[0]["Share_Pct"]),
        "top_n_share": float(top["Share_Pct"].sum()),
        "num_countries": len(df),
        "total_revenue": float(df["Revenue"].sum()),
    }
    return insights
