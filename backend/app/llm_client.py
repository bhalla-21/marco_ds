# app/llm_client.py
import os
from google import genai
from google.genai import types as genai_types

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set")

client = genai.Client(api_key=GEMINI_API_KEY)
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

def call_openai_json(prompt: str, model: str = DEFAULT_MODEL):
    """
    Maintain the same function name used by main.py; returns a JSON string.
    """
    resp = client.models.generate_content(
        model=model,
        contents=prompt,
        config=genai_types.GenerateContentConfig(
            response_mime_type="application/json",
        ),
    )
    # resp.text is a JSON string when response_mime_type is application/json
    return resp.text
