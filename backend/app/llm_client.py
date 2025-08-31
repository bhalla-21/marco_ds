import os
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()


GEMINI_MODEL_NAME = "gemini-1.5-flash-latest"  # Use your preferred Gemini model


def call_gemini(prompt: str) -> str:
    # Configure with API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("Set GOOGLE_API_KEY environment variable in your .env file")
    genai.configure(api_key=api_key)

    # Instantiate the model
    model = genai.GenerativeModel(GEMINI_MODEL_NAME)
    
    # Generate content
    response = model.generate_content(prompt)
    
    # Extract the generated text from the response
    if hasattr(response, "text"):
        return response.text.strip()
    return "Could not generate a response."
