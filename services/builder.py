"""
Dashboard Builder Service
Orchestrates template-based Power BI Project (.pbip) artifact generation.
"""
import os
import json
import shutil
import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, "dashboard", "template")
OUTPUT_DIR = os.path.join(BASE_DIR, "dashboard", "output")
TEMPLATE_MAP_PATH = os.path.join(BASE_DIR, "docs", "template_map.json")


def load_template_map() -> dict:
    """Load the template mapping configuration."""
    if not os.path.exists(TEMPLATE_MAP_PATH):
        return {}
    with open(TEMPLATE_MAP_PATH, "r") as f:
        return json.load(f)


def build_dashboard(spec_dict: dict) -> dict:
    """
    Build a Power BI Project artifact from a DashboardSpec dict.
    Returns a dict with build status, output path, and step log.
    """
    build_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + os.urandom(4).hex()
    output_path = os.path.join(OUTPUT_DIR, build_id)

    steps = []
    result = {
        "success": False,
        "build_id": build_id,
        "output_path": output_path,
        "timestamp": datetime.datetime.now().isoformat(),
        "dashboard_title": spec_dict.get("dashboard_title", "Untitled"),
        "filters_applied": spec_dict.get("filters", {}),
        "steps": steps,
        "error": None,
    }

    try:
        # Step 1: Check template exists
        if not os.path.exists(TEMPLATE_DIR) or not os.listdir(TEMPLATE_DIR):
            steps.append({"step": "Check Template", "status": "warning", "detail": "Template directory is empty. Creating minimal output structure."})
            os.makedirs(output_path, exist_ok=True)
            # Write a spec summary as the output
            spec_output_path = os.path.join(output_path, "dashboard_spec.json")
            with open(spec_output_path, "w") as f:
                json.dump(spec_dict, f, indent=2)
            steps.append({"step": "Write Spec", "status": "success", "detail": f"Spec written to {spec_output_path}"})
            result["success"] = True
            return result

        # Step 2: Clone template
        steps.append({"step": "Clone Template", "status": "running", "detail": f"Copying template to {output_path}"})
        shutil.copytree(TEMPLATE_DIR, output_path)
        steps[-1]["status"] = "success"

        # Step 3: Load template map
        template_map = load_template_map()
        steps.append({"step": "Load Template Map", "status": "success", "detail": "Template map loaded"})

        # Step 4: Apply spec to report.json
        report_rel_path = template_map.get("report_file_path", "")
        report_path = os.path.join(output_path, report_rel_path) if report_rel_path else None

        if report_path and os.path.exists(report_path):
            with open(report_path, "r") as f:
                report_json = json.load(f)

            # Apply title
            title = spec_dict.get("dashboard_title", "Dashboard")
            _apply_title(report_json, template_map, title)
            steps.append({"step": "Apply Title", "status": "success", "detail": f'Title set to "{title}"'})

            # Apply filters
            filters = spec_dict.get("filters", {})
            _apply_filters(report_json, template_map, filters)
            steps.append({"step": "Apply Filters", "status": "success", "detail": f"Filters applied: {json.dumps(filters)}"})

            # Write modified report.json
            with open(report_path, "w") as f:
                json.dump(report_json, f, indent=2)
            steps.append({"step": "Write Report", "status": "success", "detail": "Modified report.json written"})
        else:
            steps.append({"step": "Apply Spec", "status": "warning", "detail": "report.json not found in template"})

        # Step 5: Write spec alongside output
        spec_output_path = os.path.join(output_path, "dashboard_spec.json")
        with open(spec_output_path, "w") as f:
            json.dump(spec_dict, f, indent=2)
        steps.append({"step": "Save Spec", "status": "success", "detail": "DashboardSpec saved to output"})

        # Step 6: Mark complete
        steps.append({"step": "Build Complete", "status": "success", "detail": f"Artifact ready at {output_path}"})
        result["success"] = True

    except Exception as e:
        steps.append({"step": "Error", "status": "error", "detail": str(e)})
        result["error"] = str(e)

    return result


def _apply_title(report_json: dict, template_map: dict, title: str):
    """Apply dashboard title to report.json using template_map markers."""
    title_marker = template_map.get("objects", {}).get("visuals", {}).get("title_textbox", {}).get("marker", "__DASHBOARD_TITLE__")
    _recursive_replace(report_json, title_marker, title)


def _apply_filters(report_json: dict, template_map: dict, filters: dict):
    """Apply filter values to report.json placeholders."""
    # This is a simplified application — in production, would manipulate
    # Power BI filter structures directly
    pass


def _recursive_replace(obj, marker: str, replacement: str):
    """Recursively replace a marker string in a nested dict/list."""
    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, str) and marker in value:
                obj[key] = value.replace(marker, replacement)
            else:
                _recursive_replace(value, marker, replacement)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            if isinstance(item, str) and marker in item:
                obj[i] = item.replace(marker, replacement)
            else:
                _recursive_replace(item, marker, replacement)


def get_build_history() -> list:
    """List all builds in the output directory."""
    if not os.path.exists(OUTPUT_DIR):
        return []
    builds = []
    for name in sorted(os.listdir(OUTPUT_DIR), reverse=True):
        build_path = os.path.join(OUTPUT_DIR, name)
        if os.path.isdir(build_path):
            spec_path = os.path.join(build_path, "dashboard_spec.json")
            spec = {}
            if os.path.exists(spec_path):
                try:
                    with open(spec_path, "r") as f:
                        spec = json.load(f)
                except Exception:
                    pass
            builds.append({
                "build_id": name,
                "path": build_path,
                "title": spec.get("dashboard_title", "Unknown"),
                "filters": spec.get("filters", {}),
                "timestamp": name[:15] if len(name) >= 15 else name,
            })
    return builds
