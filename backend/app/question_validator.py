import re
import logging

def is_valid_business_question(question: str) -> tuple[bool, str]:
    """
    Validate if question is relevant to business/financial domain
    Returns: (is_valid, reason_if_invalid)
    """
    question = question.lower().strip()
    
    # Define irrelevant topics/patterns
    irrelevant_patterns = [
        # Political questions
        r'who is the (prime minister|president|pm|leader|minister)',
        r'(current|latest) (prime minister|president|pm)',
        r'capital of \w+',
        r'government of \w+',
        
        # Personal/Entertainment
        r'tell me (a joke|something funny)',
        r'(movie|film) (times|schedule|review)',
        r'celebrity (news|gossip)',
        r'(sports|game) (score|result)',
        r'latest news about \w+',
        
        # General knowledge
        r'weather in \w+',
        r'time in \w+',
        r'current time',
        r'how to (cook|drive|swim)',
        r'recipe for \w+',
        r'meaning of life',
        
        # Technical/non-business
        r'how to (code|program)',
        r'programming language',
        r'install \w+',
        r'fix my \w+',
    ]
    
    # Check for irrelevant patterns
    for pattern in irrelevant_patterns:
        if re.search(pattern, question):
            return False, "This question is outside my area of expertise"
    
    # Define business/financial keywords
    business_keywords = [
        'revenue', 'profit', 'sales', 'performance', 'growth', 'trend', 'analysis',
        'brand', 'market', 'region', 'country', 'volume', 'income', 'financial',
        'earnings', 'benchmark', 'forecast', 'budget', 'roi', 'margin', 'kpi',
        'quarter', 'monthly', 'yearly', 'qtd', 'ytd', 'mtd'
    ]
    
    # Check if question contains business-related terms
    has_business_terms = any(keyword in question for keyword in business_keywords)
    
    # Additional validation for very short or generic questions
    words = question.split()
    if len(words) < 4:
        return False, "Please provide a more specific business-related question"
    
    # If no business terms found, likely irrelevant
    if not has_business_terms:
        return False, "I can only help with business and financial questions about MDLZ data"
    
    return True, ""

def get_polite_refusal_message(question: str, reason: str) -> dict:
    """
    Generate a polite refusal message for out-of-scope questions
    """
    return {
        "text_answer": f"""I apologize, but I'm specifically designed to help with business and financial questions related to Mondelez International (MDLZ) data.

{reason}.

Here are some examples of questions I can help with:
• What is the net revenue of Oreo in 2025?
• Which brands are driving growth in the EU region?
• Analyze performance trends for chocolate category
• Compare Q1 vs Q2 performance across regions
• Show me benchmark analysis for key brands

Please feel free to ask me any business or financial question about MDLZ!""",
        "charts": []
    }
