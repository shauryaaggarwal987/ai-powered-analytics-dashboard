"""
AI Engine Service
Wraps LLM client and dashboard spec for Streamlit-friendly usage.
"""
import sys
import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from services.data_loader import load_metadata


def parse_user_query(user_query: str) -> dict:
    """
    Parse a natural language query using Gemini and return a DashboardSpec dict.
    Returns dict with keys: success, spec_dict, raw_response, error, grounding_report
    """
    result = {
        "success": False,
        "spec_dict": None,
        "raw_response": None,
        "error": None,
        "grounding_report": None,
        "validation_errors": [],
    }

    try:
        metadata = load_metadata()

        # Build prompt using existing prompts module
        from llm_engine.prompts import build_dashboard_prompt
        from dashboard.dashboard_spec import DashboardSpec

        # Get schema
        schema_str = json.dumps(DashboardSpec.model_json_schema(), indent=2)
        full_prompt = build_dashboard_prompt(user_query, metadata, schema_str)

        # Call Gemini
        from llm_engine.gemini_client import GeminiClient
        client = GeminiClient()
        spec_dict = client.generate_dashboard_spec(user_query, full_prompt.replace(f'User Request: "{user_query}"', ''))

        result["raw_response"] = json.dumps(spec_dict, indent=2)

        # Validate with Pydantic
        try:
            validated_spec = DashboardSpec(**spec_dict)
            result["spec_dict"] = spec_dict
            result["success"] = True
        except Exception as ve:
            result["spec_dict"] = spec_dict
            result["validation_errors"] = [str(ve)]
            result["error"] = f"Validation failed: {ve}"

        # Build grounding report
        result["grounding_report"] = _build_grounding_report(spec_dict, metadata)

    except Exception as e:
        result["error"] = str(e)

    return result


def _build_grounding_report(spec_dict: dict, metadata: dict) -> dict:
    """Build a grounding verification report comparing spec against allowed values."""
    report = {
        "allowed_yearmonths_count": len(metadata.get("allowed_yearmonths", [])),
        "allowed_countries_count": len(metadata.get("allowed_countries", [])),
        "requested_yearmonths": [],
        "requested_countries": [],
        "matched_yearmonths": [],
        "unmatched_yearmonths": [],
        "matched_countries": [],
        "unmatched_countries": [],
        "all_grounded": True,
        "visual_slots": {},
    }

    allowed_ym = set(metadata.get("allowed_yearmonths", []))
    allowed_countries = set(metadata.get("allowed_countries", []))

    filters = spec_dict.get("filters", {})

    # Check YearMonths
    requested_ym = filters.get("YearMonth", [])
    report["requested_yearmonths"] = requested_ym
    for ym in requested_ym:
        if ym in allowed_ym:
            report["matched_yearmonths"].append(ym)
        else:
            report["unmatched_yearmonths"].append(ym)
            report["all_grounded"] = False

    # Check Countries
    requested_countries = filters.get("Country", [])
    report["requested_countries"] = requested_countries
    for c in requested_countries:
        if c in allowed_countries:
            report["matched_countries"].append(c)
        else:
            report["unmatched_countries"].append(c)
            report["all_grounded"] = False

    # Check visual slots
    visuals = spec_dict.get("visuals_config", {})
    for slot_name in ["slot_kpi_cards", "slot_trend", "slot_top_countries", "slot_top_products"]:
        slot_data = visuals.get(slot_name, {})
        if isinstance(slot_data, dict):
            report["visual_slots"][slot_name] = slot_data.get("visible", False)
        else:
            report["visual_slots"][slot_name] = False

    return report


def get_sample_prompts() -> list:
    """Return a list of example prompts for the UI."""
    return [
        "Show me sales performance for France in March 2011",
        "Compare Germany and France across 2011",
        "Show top products for the United Kingdom in 2011-09",
        "Create a dashboard for monthly revenue trends and top countries",
        "Focus on 2011-03 and France with products and trend visuals",
        "Show overall retail performance with all chart types",
        "Analyze EIRE sales with monthly trend for 2010",
        "Revenue breakdown for Netherlands in 2011-06",
    ]
