# AI-Powered Analytics Dashboard

An intelligent system that programmatically generates tailored Power BI dashboards (PBIP format) based on natural language requests using the Google Gemini API.

## Architecture

This project strictly adheres to a deterministic modification approach, separating the AI reasoning layer from the Dashboard generation layer.

1.  **Analytics Layer:** Processes raw transaction data into performant KPI CSV tables (`data/processed/`).
2.  **Metadata Extraction:** `allowed_values.py` extracts valid `YearMonth` and `Country` parameters to ground the LLM.
3.  **LLM Engine (Gemini):** Translates user natural language queries into a strict JSON `DashboardSpec`.
4.  **Dashboard Builder:** Reads the verified JSON spec and modifies existing objects (filters, titles) within a pre-built Power BI Master Template (`dashboard/template/`) map.

## Prerequisites

-   Python 3.9+
-   A Google Gemini API Key
-   Power BI Desktop (to view the generated `.pbip` files)

## Setup

1.  **Clone the Repository:**
    ```bash
    git clone <repository-url>
    cd ai-powered-analytics
    ```

2.  **Install Dependencies:**
    ```bash
    pip install pandas typing-extensions python-dotenv google-generativeai pydantic
    ```

3.  **Environment Variables:**
    Create a `.env` file in the root directory based on `.env.example`:
    ```env
    GOOGLE_API_KEY="your_actual_api_key_here"
    ```

4.  **Prepare Data (First Time Only):**
    Ensure raw data is in `data/raw/online_retail_II.csv`. Run the analytics pipeline:
    ```bash
    python analytics/cleaning_v1.py
    python analytics/monthly_trends.py
    python analytics/country_contribution.py
    python analytics/top_products.py
    python analytics/month_country.py
    python analytics/month_product.py
    python analytics/allowed_values.py
    ```

## How to Run the Demo

The entire end-to-end process is executed via `demo.py`.

```bash
python demo.py
```

1.  You will be prompted to enter a natural language request, e.g.:
    > *"Show me sales for France in March 2011."*
2.  The script will securely query Gemini, validate the resulting spec, and copy/modify the PBIP template.
3.  Upon success, it will output a path to the generated dashboard folder (e.g., `dashboard/output/2026.../RetailAnalysis.pbip`).
4.  Open the resulting `.pbip` file in Power BI Desktop to view the customized dashboard.

## Constraints

*   **Granularity:** Supported down to the Monthly level (YYYY-MM). Daily filtering is not supported in this version.
*   **Security:** Raw transaction data is NEVER sent to Google. Only predefined capabilities and high-level extracted dimension lists (Allowed YearMonths, Countries) are provided in the prompt context.
