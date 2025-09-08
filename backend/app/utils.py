import json
import re
import logging

def clean_and_parse_json(text: str):
    """Enhanced JSON parsing with better error handling"""
    if not text:
        return {}
    
    text = text.strip()
    
    # Method 1: Try direct parsing first
    try:
        parsed = json.loads(text)
        logging.info("Successfully parsed JSON directly")
        return parsed
    except json.JSONDecodeError as e:
        logging.warning(f"Direct JSON parsing failed: {e}")
    
    # Method 2: Look for JSON in fenced code blocks
    fenced_pattern = r'``````'
    fenced_match = re.search(fenced_pattern, text, re.DOTALL | re.IGNORECASE)
    if fenced_match:
        try:
            parsed = json.loads(fenced_match.group(1))
            logging.info("Successfully parsed JSON from fenced code block")
            return parsed
        except json.JSONDecodeError as e:
            logging.warning(f"Fenced code block JSON parsing failed: {e}")
    
    # Method 3: Extract first complete JSON object
    brace_start = text.find('{')
    if brace_start != -1:
        brace_count = 0
        for i, char in enumerate(text[brace_start:], brace_start):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    candidate = text[brace_start:i+1]
                    try:
                        # Clean problematic escape sequences
                        cleaned = candidate.replace('\n', '\\n').replace('\t', '\\t').replace('\r', '')
                        # Remove trailing commas before closing braces/brackets
                        cleaned = re.sub(r',\s*([}\]])', r'\1', cleaned)
                        parsed = json.loads(cleaned)
                        logging.info("Successfully parsed JSON using brace extraction")
                        return parsed
                    except json.JSONDecodeError as e:
                        logging.warning(f"Brace extraction JSON parsing failed: {e}")
                        continue
    
    # Method 4: Fallback - return the text wrapped in a structure
    logging.warning(f"Could not parse JSON, returning text wrapper for: {text[:100]}...")
    return {"text_answer": text, "charts": []}

def extract_first_json(text: str):
    """Alternative JSON extraction function with multiple fallback methods"""
    if not text:
        return None
    
    text = text.strip()
    
    # Try multiple patterns
    patterns = [
        # Fenced code blocks with optional json tag
        r'``````',
        # Just the JSON object (non-greedy)
        r'(\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})',
        # Greedy JSON object match
        r'(\{.*\})',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
        for match in matches:
            try:
                # Clean problematic characters
                cleaned = match.replace('\n', '\\n').replace('\t', '\\t').replace('\r', '')
                # Remove any trailing commas before closing braces/brackets
                cleaned = re.sub(r',\s*([}\]])', r'\1', cleaned)
                return json.loads(cleaned)
            except json.JSONDecodeError:
                continue
    
    # Final attempt - try to parse the whole text
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None
