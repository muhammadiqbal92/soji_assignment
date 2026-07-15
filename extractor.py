import pdfplumber
import json
from google import genai
from google.genai import types
from pydantic import BaseModel
from typing import List, Optional

class ApplicabilityRules(BaseModel):
    aircraft_models: List[str]
    msn_constraints: Optional[List[str]] 
    excluded_if_modifications: Optional[List[str]]
    required_modifications: Optional[List[str]]

class ADExtraction(BaseModel):
    ad_id: str
    applicability_rules: ApplicabilityRules

def extract_text_from_pdf(pdf_path: str) -> str:
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        return text
    except Exception as e:
        print(f"Failed to read PDF: {e}")
        return ""

def parse_ad_rules(pdf_text: str, api_key: str) -> dict:
    client = genai.Client(api_key=api_key)
    
    system_instruction = """
    You are an expert aviation regulatory data extraction system. 
    Read the Airworthiness Directive (AD) text and extract the applicability rules into strict JSON.
    1. aircraft_models: Be specific (e.g., "A320-214", "MD-11F").
    2. msn_constraints: List of MSNs. If it's a range, format as "START-END" (e.g. "4500-4600"). If none, return null.
    3. excluded_if_modifications: List of mods/SBs that EXEMPT the aircraft (e.g. "mod 24591"). Look for words like "except" or "does not apply to".
    4. required_modifications: Mods required for the AD to apply. If applies to all, return empty list [].
    """

    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=pdf_text,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            response_schema=ADExtraction,
            temperature=0.0
        ),
    )
    
    return json.loads(response.text)