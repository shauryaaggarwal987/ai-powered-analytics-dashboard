import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from pydantic import ValidationError

# We import the schema to help the LLM understand the structure, 
# although in this version we might just pass the JSON schema directly as a string to the prompt.
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'dashboard'))
from dashboard_spec import DashboardSpec

# Load environment variables
load_dotenv()

class GeminiClient:
    def __init__(self, model_name="gemini-1.5-pro-latest"): # Using a capable model for JSON generation
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables. Please set it in a .env file.")
        
        genai.configure(api_key=api_key)
        
        # Configure the model to urge JSON output. 
        # (Alternatively use generation_config={"response_mime_type": "application/json"} if using newer SDK features)
        self.model = genai.GenerativeModel(model_name)

    def generate_dashboard_spec(self, prompt: str, schema_context: str) -> dict:
        """
        Takes a natural language prompt and metadata context, returns a parsed JSON spec.
        """
        full_prompt = f"""
        You are a BI Architect. Your job is to translate the user's request into a strict JSON Dashboard Specification.
        
        {schema_context}
        
        User Request: "{prompt}"
        
        Respond ONLY with a valid JSON object matching the requested schema. Do not include markdown code blocks (like ```json), just the raw JSON object.
        """

        try:
            print("Calling Gemini API...")
            response = self.model.generate_content(full_prompt)
            response_text = response.text.strip()
            
            # Clean up potential markdown formatting if the model still includes it
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            # Parse the JSON
            spec_dict = json.loads(response_text)
            return spec_dict
            
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON from Gemini response: {e}")
            print(f"Raw Response: {response.text}")
            raise
        except Exception as e:
             print(f"Gemini API Error: {e}")
             raise


