"""
Plotly Chart Factory
Consistent, interactive chart functions with premium dark theming.
"""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# ── Shared Theme ────────────────────────────────────────────────

COLORS = {
    "primary": "#6C63FF",
    "secondary": "#a5b4fc",
    "accent": "#818cf8",
    "success": "#4ade80",
    "warning": "#fbbf24",
    "error": "#f87171",
    "bg": "#0E1117",
    "card_bg": "#1A1F2E",
    "text": "#e2e8f0",
    "muted": "#64748b",
}

PALETTE = ["#6C63FF", "#a78bfa", "#818cf8", "#c084fc", "#e879f9",
           "#f472b6", "#fb7185", "#f97316", "#fbbf24", "#4ade80",
           "#2dd4bf", "#22d3ee", "#38bdf8", "#60a5fa", "#93c5fd"]

LAYOUT_DEFAULTS = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#e2e8f0", size=12),
    margin=dict(l=40, r=20, t=40, b=40),
    hoverlabel=dict(bgcolor="#1e293b", font_color="#f1f5f9", bordercolor="#334155"),
    xaxis=dict(gridcolor="rgba(148,163,184,0.08)", zerolinecolor="rgba(148,163,184,0.08)"),
    yaxis=dict(gridcolor="rgba(148,163,184,0.08)", zerolinecolor="rgba(148,163,184,0.08)"),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
)


def _apply_layout(fig, title: str = "", height: int = 400):
    fig.update_layout(**LAYOUT_DEFAULTS, title=dict(text=title, font=dict(size=14, color="#e2e8f0"), x=0.02), height=height)
    return fig


# ── Line / Area Charts ─────────────────────────────────────────

def monthly_revenue_line(df: pd.DataFrame, title: str = "Monthly Revenue Trend", height: int = 400):
    if df.empty:
        return go.Figure()
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["YearMonth"], y=df["Revenue"], mode="lines+markers",
        line=dict(color=COLORS["primary"], width=2.5),
        marker=dict(size=6, color=COLORS["primary"]),
        fill="tozeroy", fillcolor="rgba(108,99,255,0.08)",
        hovertemplate="<b>%{x}</b><br>Revenue: £%{y:,.0f}<extra></extra>",
        name="Revenue",
    ))
    return _apply_layout(fig, title, height)


def monthly_revenue_area(df: pd.DataFrame, title: str = "Revenue Area", height: int = 400):
    if df.empty:
        return go.Figure()
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["YearMonth"], y=df["Revenue"], mode="lines",
        line=dict(color=COLORS["primary"], width=2),
        fill="tozeroy", fillcolor="rgba(108,99,255,0.15)",
        hovertemplate="<b>%{x}</b><br>Revenue: £%{y:,.0f}<extra></extra>",
        name="Revenue",
    ))
    return _apply_layout(fig, title, height)


def cumulative_revenue_chart(df: pd.DataFrame, title: str = "Cumulative Revenue", height: int = 400):
    if df.empty:
        return go.Figure()
    dfc = df.copy().sort_values("YearMonth")
    dfc["Cumulative"] = dfc["Revenue"].cumsum()
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dfc["YearMonth"], y=dfc["Cumulative"], mode="lines",
        line=dict(color="#4ade80", width=2.5),
        fill="tozeroy", fillcolor="rgba(74,222,128,0.08)",
        hovertemplate="<b>%{x}</b><br>Cumulative: £%{y:,.0f}<extra></extra>",
        name="Cumulative",
    ))
    return _apply_layout(fig, title, height)


def mom_growth_chart(df: pd.DataFrame, title: str = "Month-over-Month Growth %", height: int = 380):
    if df.empty or "MoM_Growth_Pct" not in df.columns:
        return go.Figure()
    dfc = df.dropna(subset=["MoM_Growth_Pct"]).copy()
    colors = [COLORS["success"] if v >= 0 else COLORS["error"] for v in dfc["MoM_Growth_Pct"]]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=dfc["YearMonth"], y=dfc["MoM_Growth_Pct"],
        marker_color=colors,
        hovertemplate="<b>%{x}</b><br>Growth: %{y:.1f}%<extra></extra>",
        name="Growth %",
    ))
    fig.add_hline(y=0, line_dash="dash", line_color=COLORS["muted"], line_width=1)
    return _apply_layout(fig, title, height)


def rolling_average_chart(df: pd.DataFrame, window: int = 3, title: str = "", height: int = 400):
    if df.empty:
        return go.Figure()
    col_name = f"Rolling_{window}M_Avg"
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["YearMonth"], y=df["Revenue"], mode="lines+markers",
        line=dict(color=COLORS["primary"], width=1.5, dash="dot"),
        marker=dict(size=4, color=COLORS["primary"]),
        hovertemplate="<b>%{x}</b><br>Revenue: £%{y:,.0f}<extra></extra>",
        name="Monthly Revenue",
        opacity=0.5,
    ))
    if col_name in df.columns:
        fig.add_trace(go.Scatter(
            x=df["YearMonth"], y=df[col_name], mode="lines",
            line=dict(color=COLORS["warning"], width=2.5),
            hovertemplate=f"<b>%{{x}}</b><br>{window}M Avg: £%{{y:,.0f}}<extra></extra>",
            name=f"{window}-Month Avg",
        ))
    ttl = title or f"Revenue with {window}-Month Rolling Average"
    return _apply_layout(fig, ttl, height)


def country_comparison_lines(df: pd.DataFrame, countries: list, title: str = "Country Revenue Comparison", height: int = 420):
    if df.empty:
        return go.Figure()
    fig = go.Figure()
    for i, country in enumerate(countries):
        cdf = df[df["Country"] == country]
        if cdf.empty:
            continue
        color = PALETTE[i % len(PALETTE)]
        fig.add_trace(go.Scatter(
            x=cdf["YearMonth"], y=cdf["Revenue"], mode="lines+markers",
            line=dict(color=color, width=2),
            marker=dict(size=5, color=color),
            hovertemplate=f"<b>{country}</b><br>%{{x}}: £%{{y:,.0f}}<extra></extra>",
            name=country,
        ))
    return _apply_layout(fig, title, height)


# ── Bar Charts ─────────────────────────────────────────────────

def top_countries_bar(df: pd.DataFrame, top_n: int = 10, title: str = "Top Countries by Revenue", height: int = 400):
    if df.empty:
        return go.Figure()
    dfc = df.head(top_n).sort_values("Revenue")
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=dfc["Country"], x=dfc["Revenue"], orientation="h",
        marker=dict(color=dfc["Revenue"], colorscale=[[0, "#312e81"], [0.5, "#6C63FF"], [1, "#c4b5fd"]]),
        hovertemplate="<b>%{y}</b><br>Revenue: £%{x:,.0f}<extra></extra>",
        name="Revenue",
    ))
    return _apply_layout(fig, title, height)


def top_products_bar(df: pd.DataFrame, top_n: int = 10, title: str = "Top Products by Revenue", height: int = 420):
    if df.empty:
        return go.Figure()
    dfc = df.head(top_n).sort_values("Revenue")
    # Truncate long descriptions
    dfc = dfc.copy()
    dfc["Label"] = dfc["Description"].apply(lambda x: x[:35] + "…" if len(str(x)) > 35 else x)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=dfc["Label"], x=dfc["Revenue"], orientation="h",
        marker=dict(color=dfc["Revenue"], colorscale=[[0, "#312e81"], [0.5, "#818cf8"], [1, "#e9d5ff"]]),
        hovertemplate="<b>%{y}</b><br>Revenue: £%{x:,.0f}<extra></extra>",
        name="Revenue",
    ))
    return _apply_layout(fig, title, height)


def revenue_share_stacked(df: pd.DataFrame, top_n: int = 8, title: str = "Revenue Composition by Country", height: int = 420):
    if df.empty:
        return go.Figure()
    top_countries = df.groupby("Country")["Revenue"].sum().nlargest(top_n).index.tolist()
    dfc = df.copy()
    dfc["CountryGroup"] = dfc["Country"].apply(lambda x: x if x in top_countries else "Others")
    pivot = dfc.groupby(["YearMonth", "CountryGroup"])["Revenue"].sum().reset_index()
    fig = px.bar(pivot, x="YearMonth", y="Revenue", color="CountryGroup",
                 color_discrete_sequence=PALETTE, barmode="stack")
    fig.update_traces(hovertemplate="<b>%{fullData.name}</b><br>%{x}: £%{y:,.0f}<extra></extra>")
    return _apply_layout(fig, title, height)


# ── Donut / Treemap ────────────────────────────────────────────

def country_donut(df: pd.DataFrame, top_n: int = 10, title: str = "Revenue Share by Country", height: int = 400):
    if df.empty:
        return go.Figure()
    top = df.head(top_n).copy()
    others_rev = df.iloc[top_n:]["Revenue"].sum() if len(df) > top_n else 0
    if others_rev > 0:
        others_row = pd.DataFrame([{"Country": "Others", "Revenue": others_rev}])
        top = pd.concat([top, others_row], ignore_index=True)
    fig = go.Figure(go.Pie(
        labels=top["Country"], values=top["Revenue"],
        hole=0.55,
        marker=dict(colors=PALETTE[:len(top)]),
        textinfo="label+percent",
        textfont=dict(size=11),
        hovertemplate="<b>%{label}</b><br>Revenue: £%{value:,.0f}<br>Share: %{percent}<extra></extra>",
    ))
    return _apply_layout(fig, title, height)


def country_treemap(df: pd.DataFrame, top_n: int = 15, title: str = "Revenue Treemap", height: int = 450):
    if df.empty:
        return go.Figure()
    dfc = df.head(top_n).copy()
    fig = px.treemap(dfc, path=["Country"], values="Revenue",
                     color="Revenue", color_continuous_scale=["#312e81", "#6C63FF", "#c4b5fd"])
    fig.update_traces(hovertemplate="<b>%{label}</b><br>Revenue: £%{value:,.0f}<extra></extra>")
    return _apply_layout(fig, title, height)


def product_treemap(df: pd.DataFrame, top_n: int = 15, title: str = "Product Revenue Treemap", height: int = 450):
    if df.empty:
        return go.Figure()
    dfc = df.head(top_n).copy()
    fig = px.treemap(dfc, path=["Description"], values="Revenue",
                     color="Revenue", color_continuous_scale=["#1e1b4b", "#818cf8", "#e9d5ff"])
    fig.update_traces(hovertemplate="<b>%{label}</b><br>Revenue: £%{value:,.0f}<extra></extra>")
    return _apply_layout(fig, title, height)


# ── Heatmaps ───────────────────────────────────────────────────

def month_country_heatmap(df: pd.DataFrame, top_n_countries: int = 12, title: str = "Month × Country Revenue Heatmap", height: int = 480):
    if df.empty:
        return go.Figure()
    top_countries = df.groupby("Country")["Revenue"].sum().nlargest(top_n_countries).index.tolist()
    dfc = df[df["Country"].isin(top_countries)]
    pivot = dfc.pivot_table(index="Country", columns="YearMonth", values="Revenue", fill_value=0)
    pivot = pivot.loc[top_countries]  # maintain rank order
    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=pivot.columns.tolist(),
        y=pivot.index.tolist(),
        colorscale=[[0, "#0f172a"], [0.3, "#312e81"], [0.6, "#6C63FF"], [1, "#c4b5fd"]],
        hovertemplate="<b>%{y}</b><br>%{x}: £%{z:,.0f}<extra></extra>",
        colorbar=dict(title="Revenue", tickformat=",.0f"),
    ))
    return _apply_layout(fig, title, height)


def month_product_heatmap(df: pd.DataFrame, top_n_products: int = 12, title: str = "Month × Product Revenue Heatmap", height: int = 480):
    if df.empty:
        return go.Figure()
    top_prods = df.groupby("Description")["Revenue"].sum().nlargest(top_n_products).index.tolist()
    dfc = df[df["Description"].isin(top_prods)]
    pivot = dfc.pivot_table(index="Description", columns="YearMonth", values="Revenue", fill_value=0)
    # Truncate names
    pivot.index = [x[:30] + "…" if len(x) > 30 else x for x in pivot.index]
    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=pivot.columns.tolist(),
        y=pivot.index.tolist(),
        colorscale=[[0, "#0f172a"], [0.3, "#1e1b4b"], [0.6, "#818cf8"], [1, "#e9d5ff"]],
        hovertemplate="<b>%{y}</b><br>%{x}: £%{z:,.0f}<extra></extra>",
        colorbar=dict(title="Revenue", tickformat=",.0f"),
    ))
    return _apply_layout(fig, title, height)


# ── Distribution / Special Charts ──────────────────────────────

def revenue_distribution_box(df: pd.DataFrame, title: str = "Monthly Revenue Distribution", height: int = 380):
    if df.empty:
        return go.Figure()
    fig = go.Figure()
    fig.add_trace(go.Box(
        y=df["Revenue"], name="Monthly Revenue",
        marker_color=COLORS["primary"],
        boxmean="sd",
        hovertemplate="Revenue: £%{y:,.0f}<extra></extra>",
    ))
    return _apply_layout(fig, title, height)


def pareto_chart(df: pd.DataFrame, value_col: str = "Revenue", label_col: str = "Description",
                 top_n: int = 15, title: str = "Pareto Analysis", height: int = 420):
    if df.empty:
        return go.Figure()
    dfc = df.head(top_n).copy().reset_index(drop=True)
    total = dfc[value_col].sum()
    dfc["CumPct"] = (dfc[value_col].cumsum() / total * 100).round(1)
    dfc["Label"] = dfc[label_col].apply(lambda x: x[:25] + "…" if len(str(x)) > 25 else x)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=dfc["Label"], y=dfc[value_col], name="Revenue",
        marker_color=COLORS["primary"],
        hovertemplate="<b>%{x}</b><br>Revenue: £%{y:,.0f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=dfc["Label"], y=dfc["CumPct"], name="Cumulative %",
        mode="lines+markers",
        line=dict(color=COLORS["warning"], width=2),
        marker=dict(size=6, color=COLORS["warning"]),
        yaxis="y2",
        hovertemplate="<b>%{x}</b><br>Cumulative: %{y:.1f}%<extra></extra>",
    ))
    fig.update_layout(yaxis2=dict(overlaying="y", side="right", range=[0, 105],
                                   showgrid=False, title="Cumulative %", ticksuffix="%",
                                   color="#fbbf24"))
    return _apply_layout(fig, title, height)


def product_comparison_lines(df: pd.DataFrame, products: list, title: str = "Product Trend Comparison", height: int = 420):
    if df.empty:
        return go.Figure()
    fig = go.Figure()
    for i, product in enumerate(products):
        pdf = df[df["Description"] == product]
        if pdf.empty:
            continue
        color = PALETTE[i % len(PALETTE)]
        label = product[:30] + "…" if len(product) > 30 else product
        fig.add_trace(go.Scatter(
            x=pdf["YearMonth"], y=pdf["Revenue"], mode="lines+markers",
            line=dict(color=color, width=2), marker=dict(size=5, color=color),
            hovertemplate=f"<b>{label}</b><br>%{{x}}: £%{{y:,.0f}}<extra></extra>",
            name=label,
        ))
    return _apply_layout(fig, title, height)


def seasonality_heatmap(df: pd.DataFrame, title: str = "Revenue Seasonality", height: int = 350):
    """Create a year × month heatmap for seasonality patterns."""
    if df.empty:
        return go.Figure()
    dfc = df.copy()
    dfc["Year"] = dfc["YearMonth"].str[:4]
    dfc["Month"] = dfc["YearMonth"].str[5:7]
    pivot = dfc.pivot_table(index="Year", columns="Month", values="Revenue", fill_value=0)
    month_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    month_nums = [f"{i:02d}" for i in range(1, 13)]
    # Reindex to ensure all months shown
    pivot = pivot.reindex(columns=month_nums, fill_value=0)
    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=month_labels[:len(pivot.columns)],
        y=pivot.index.tolist(),
        colorscale=[[0, "#0f172a"], [0.3, "#312e81"], [0.7, "#6C63FF"], [1, "#c4b5fd"]],
        hovertemplate="<b>%{y}-%{x}</b><br>Revenue: £%{z:,.0f}<extra></extra>",
        colorbar=dict(title="Revenue", tickformat=",.0f"),
    ))
    return _apply_layout(fig, title, height)
