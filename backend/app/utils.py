# app/utils.py
import re
import json

def clean_and_parse_json(llm_output_str: str) -> dict:
    """
    Cleans the raw string output from an LLM to extract and parse a JSON object.
    It handles markdown code blocks (e.g., ``````) and other extraneous text.
    """
    # Use regex to find the JSON block within ``````
    match = re.search(r'``````', llm_output_str, re.DOTALL)
    
    json_str = ""
    if match:
        json_str = match.group(1)
    else:
        # If no markdown block is found, try to find the first '{' and last '}'
        start = llm_output_str.find('{')
        end = llm_output_str.rfind('}')
        if start != -1 and end != -1:
            json_str = llm_output_str[start:end+1]

    if not json_str:
        raise ValueError("No valid JSON object found in the LLM response.")

    # Parse the extracted string into a Python dictionary
    return json.loads(json_str)
