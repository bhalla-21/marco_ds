import re
import logging

def classify_question_type(question_text: str) -> str:
    """
    Classify question as 'simple' (fact-based) or 'analytical' (complex analysis)
    """
    question = question_text.lower().strip()
    tokens = question.split()
    
    # Simple question indicators
    simple_patterns = [
        r'^what\s+is\s+the\s+',
        r'^how\s+much\s+',
        r'^what\s+was\s+the\s+',
        r'^what\s+were\s+the\s+',
        r'total\s+',
        r'net\s+revenue\s+of\s+',
        r'revenue\s+for\s+',
        r'sales\s+of\s+',
        r'volume\s+of\s+',
        r'profit\s+of\s+'
    ]
    
    # Analytical question indicators  
    analytical_keywords = [
        'analyze', 'analysis', 'trend', 'trends', 'compare', 'comparison', 'vs', 'versus',
        'drivers', 'driving', 'performance', 'insights', 'breakdown', 'summary',
        'summarize', 'deep dive', 'detailed', 'comprehensive', 'dashboard',
        'benchmark', 'which brands', 'top brands', 'bottom brands'
    ]
    
    # Check for simple patterns first
    for pattern in simple_patterns:
        if re.search(pattern, question):
            # Additional check: if question is short and asks for specific metrics
            if len(tokens) <= 15 and any(metric in question for metric in 
                ['net revenue', 'revenue', 'profit', 'volume', 'sales', 'earnings', 'operating income']):
                logging.info(f"Question classified as SIMPLE: {question_text}")
                return 'simple'
    
    # Check for analytical keywords
    if any(keyword in question for keyword in analytical_keywords):
        logging.info(f"Question classified as ANALYTICAL: {question_text}")
        return 'analytical'
    
    # Default classification based on length and complexity
    if len(tokens) <= 12 and any(metric in question for metric in 
        ['net revenue', 'revenue', 'profit', 'volume', 'sales']):
        logging.info(f"Question classified as SIMPLE (fallback): {question_text}")
        return 'simple'
    else:
        logging.info(f"Question classified as ANALYTICAL (fallback): {question_text}")
        return 'analytical'
