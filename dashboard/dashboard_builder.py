import os
import shutil
import json
import uuid
from datetime import datetime

# Define paths relative to this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "template")
OUTPUT_BASE_DIR = os.path.join(BASE_DIR, "output")
MAP_PATH = os.path.join(BASE_DIR, "../docs/template_map.json")

class DashboardBuilder:
    def __init__(self, spec_dict):
        self.spec = spec_dict
        # Create a unique run ID for the output folder
        self.run_id = datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + str(uuid.uuid4())[:8]
        self.output_dir = os.path.join(OUTPUT_BASE_DIR, self.run_id)
        self.template_map = self._load_map()

    def _load_map(self):
        print(f"Loading template map from: {MAP_PATH}")
        if not os.path.exists(MAP_PATH):
            raise FileNotFoundError(f"Template map not found at {MAP_PATH}")
        with open(MAP_PATH, "r") as f:
            return json.load(f)

    def _copy_template(self):
        print(f"Copying template from {TEMPLATE_DIR} to {self.output_dir}")
        if not os.path.exists(TEMPLATE_DIR):
            raise FileNotFoundError(f"Template directory not found at {TEMPLATE_DIR}")
        
        # Ensure output base directory exists
        os.makedirs(OUTPUT_BASE_DIR, exist_ok=True)
        # Copy the entire template directory tree
        shutil.copytree(TEMPLATE_DIR, self.output_dir)
        print("Template copied successfully.")

    def _update_filter(self, filter_map, target_values, report_filters):
        """
        Updates an existing filter object's 'In' values.
        It finds the filter by the mapped name (e.g., 'Filter_YearMonth').
        """
        filter_name = filter_map.get("name")
        if not filter_name:
            return

        for f_obj in report_filters:
            if f_obj.get("name") == filter_name:
                # Navigate to the 'In' array inside the nested structure
                # The path typically is: filter -> Where -> [0] -> Condition -> In -> Values
                try:
                    where_clause = f_obj["filter"]["Where"][0]
                    in_clause = where_clause["Condition"]["In"]
                    
                    # Rebuild the 'Values' array
                    new_values = []
                    for val in target_values:
                        new_values.append([{"Literal": {"Value": f"'{val}'"}}])
                    
                    in_clause["Values"] = new_values
                    print(f"Updated filter '{filter_name}' with values: {target_values}")
                except KeyError as e:
                    print(f"Warning: Could not update filter '{filter_name}' due to missing key in structure: {e}")
                return
        
        print(f"Warning: Filter object '{filter_name}' not found in template.")

    def _update_visuals(self, visuals_map, spec_visuals, report_containers):
        """
        Updates title text and toggles visual visibility based on the spec.
        (Note: For the mock PBIP structure, we aren't literally deleting visuals, 
        but we can demonstrate finding and modifying their configurations).
        """
        # Update Title
        title_map = visuals_map.get("title_textbox")
        if title_map and self.spec.get("dashboard_title"):
            title_name = title_map.get("name")
            marker = title_map.get("marker")
            new_title = self.spec.get("dashboard_title")

            for container in report_containers:
                if container.get("name") == title_name:
                    # Very specific path navigation for Power BI textboxes
                    try:
                        general_props = container["config"]["singleVisual"]["objects"]["general"][0]["properties"]
                        text_expr = general_props["text"]["expr"]["Literal"]
                        if text_expr["Value"] == f"'{marker}'":
                           text_expr["Value"] = f"'{new_title}'"
                           print(f"Updated Dashboard Title to: '{new_title}'")
                    except KeyError:
                        pass # Ignore if structure doesn't match perfectly in this basic mock

        # (Toggle Slots logic would go here, e.g., removing container if visible=False)
        # For this scope, the core requirement is modifying the existing filters and titles.

    def generate(self):
        """
        Main execution flow: Copy template, modify exact elements, save.
        """
        print(f"Starting dashboard generation for run: {self.run_id}")
        
        # 1. Copy the template folder
        self._copy_template()
        
        # 2. Setup Parse Paths
        report_path_rel = self.template_map.get("report_file_path")
        target_report_file = os.path.join(self.output_dir, report_path_rel)
             
        # 3. Load the target JSON 
        with open(target_report_file, "r") as f:
            report_data = json.load(f)
             
        # 4. Deterministic Editing
        # We assume modifying the first section/page per the map for this implementation
        page_name = self.template_map.get("page_name")
        sections = report_data.get("sections", [])
        
        target_section = None
        for sec in sections:
            if sec.get("name") == page_name:
                target_section = sec
                break

        if target_section:
            # Edit Filters
            filters_map = self.template_map.get("objects", {}).get("filters", {})
            spec_filters = self.spec.get("filters", {})
            report_filters = target_section.get("filters", [])
            
            if "YearMonth" in filters_map and "YearMonth" in spec_filters:
                self._update_filter(filters_map["YearMonth"], spec_filters["YearMonth"], report_filters)
                
            if "Country" in filters_map and "Country" in spec_filters:
                self._update_filter(filters_map["Country"], spec_filters["Country"], report_filters)
                
            # Edit Visuals/Title
            visuals_map = self.template_map.get("objects", {}).get("visuals", {})
            spec_visuals = self.spec.get("visuals_config", {})
            report_containers = target_section.get("visualContainers", [])
            
            self._update_visuals(visuals_map, spec_visuals, report_containers)

        # 5. Save Modified JSON
        with open(target_report_file, "w") as f:
            json.dump(report_data, f, indent=2)
            
        print("Modifications saved successfully.")
        return self.output_dir


