# app/prompts.py
def build_query_planner_prompt(user_question: str, df_schema: str):
    """
    Enhanced prompt for complex business questions
    """
    available_time_period = "The available data covers 2025 with months from January to December (202501-202512)."
    
    return f"""
Your task is to act as a JSON generator for business intelligence queries. Your ONLY output must be a single, valid JSON object.

The data table schema is:
{df_schema}

{available_time_period}
Available Regions: HQ, LA, AMEA, EU
Available Countries: USA, Germany, France, Brazil, China, Mexico, Canada, UK, and 40+ other markets
Available KPIs: Net Revenue, Volume (MM) Kgs, Gross Profit (MM) Kgs, Operating Income
Available Categories: Chocolate, Biscuits, Cakes and Pastries, Meals, Beverages, Candy
Available Market Types: Developed Markets, Emerging Markets
Available Brands: Oreo, Milka, LU, TUC, Ritz, Chips Ahoy!, Jacobs, belVita, Cadbury Purple, Cote d'Or, Freia/Marabou, and 20+ other brands

Special Instructions:
- "MDLZ performance" refers to overall company performance across all brands, so set brand_text to null
- Use specific brand names only when explicitly mentioned (e.g., "Oreo performance")

Analyze the user question and generate a JSON object with these keys:
- "brand_text": specific brand name or null for all brands
- "region": HQ/LA/AMEA/EU or null for all regions  
- "country_text": specific country or null for all countries
- "kpi_text": specific KPI or null for all KPIs
- "leg_cat_text": category like "Chocolate", "Biscuits" or null
- "market_type_text": "Developed Markets"/"Emerging Markets" or null
- "months": list of integers in YYYYMM format or null for all months
- "analysis_type": "performance_overview", "trend_analysis", "pnl_analysis", or "category_analysis"

Examples:
- "MDLZ performance for July" -> months: [202507], analysis_type: "performance_overview"
- "France's long term PnL" -> country_text: "France", analysis_type: "pnl_analysis"  
- "Brazil chocolate trends" -> country_text: "Brazil", leg_cat_text: "Chocolate", analysis_type: "trend_analysis"

User Question: "{user_question}"
JSON Output:
"""

def build_insight_and_charting_prompt(user_question: str, data_json: str):
    prompt = f"""
You are a senior business analyst for Mondelez International.

User Question: "{user_question}"
Data: """ + data_json + """

CRITICAL INSTRUCTIONS:
- Respond with EXACTLY ONE JSON object and NOTHING ELSE
- Must include 2-3 charts in the charts array  
- No text before or after the JSON
- No multiple JSON objects
- No trailing comments or explanations

REQUIRED JSON STRUCTURE (copy this format exactly):
{{
  "text_answer": "## Executive Summary\\n\\nBased on the analysis of available data...\\n\\n## Performance Analysis\\n\\nDetailed findings show...\\n\\n### Key Performance Metrics\\n\\n| Metric | Current | vs Plan | vs PY |\\n|--------|---------|---------|-------|\\n| Net Revenue | $XXX.XM | +X.X% | +X.X% |\\n| Operating Income | $XXX.XM | +X.X% | +X.X% |\\n\\n## Strategic Recommendations\\n\\nBased on the analysis...",
  "charts": [
    {{
      "chart_type": "combination",
      "title": "Revenue vs Volume Performance",
      "data": [
        {{"label": "Oct 2025", "Act": 150.25, "py": 120.30, "rf": 145.00}},
        {{"label": "Nov 2025", "Act": 175.40, "py": 140.20, "rf": 160.50}},
        {{"label": "Dec 2025", "Act": 165.30, "py": 135.10, "rf": 155.20}}
      ]
    }},
    {{
      "chart_type": "bar",
      "title": "Brand Performance Comparison",
      "data": [
        {{"label": "Oreo", "value": 245.80}},
        {{"label": "Milka", "value": 198.45}},
        {{"label": "LU", "value": 167.20}}
      ]
    }}
  ]
}}

CHART TYPES AVAILABLE:
- "bar": Simple bar chart with label/value pairs
- "line": Line chart for trends (use Act/rf/py or value fields)
- "combination": Bars + line overlay (use Act/rf/py fields)
- "pie": Composition analysis with label/value pairs

FORMATTING RULES:
- Use actual numbers from the dataset - never use placeholder values like "XXX.X"
- Replace null values with 0 in chart data
- Use literal numbers only (no expressions or calculations)
- Create proper markdown tables with | separators in text_answer
- Include specific insights with real data points
- Charts must be JSON objects, never strings

RESPOND WITH PURE JSON ONLY:
"""
    return prompt

def build_synthesis_prompt(user_question: str, batch_summary: str):
    """
    A new prompt to synthesize analysis from multiple batches into a single response.
    """
    return f"""
You are a senior business analyst for Mondelez International. Your task is to combine a series of partial analyses into a single, comprehensive report.

User's original question: "{user_question}"

Here are the analyses from different data batches:
{batch_summary}

CRITICAL INSTRUCTIONS:
- Respond with a single, valid JSON object and NOTHING ELSE.
- The JSON object must have a "text_answer" key and a "charts" key.
- The "text_answer" should be a unified report, combining insights from all batches. It should have a clear structure with an Executive Summary, Detailed Analysis, and Strategic Recommendations. It MUST include markdown tables to summarize key data points across all batches where appropriate.
- The "charts" array should contain 2-3 chart specifications. These charts should represent a synthesis of data across all batches (e.g., a trend line over time, a comparison of top performers across the entire dataset). Do NOT include charts for a single batch.

Example JSON Structure (copy this format exactly):
{{
  "text_answer": "## Executive Summary\\n\\nBased on a comprehensive analysis of all data batches, key findings include...\\n\\n## Performance Analysis\\n\\nDetailed breakdown of performance across all months...\\n\\n### Key Metrics Table\\n\\n| Metric | Total Value | vs Plan % | vs PY % |\\n|--------|-------------|-----------|---------|\\n| Net Revenue | $1.23B | +5.4% | +7.2% |\\n| Operating Income | $450M | +3.1% | +2.9% |\\n\\n## Strategic Recommendations\\n\\nBased on the consolidated data, it is recommended to...",
  "charts": [
    {{
      "chart_type": "line",
      "title": "Monthly Revenue Trend (Actual vs Plan)",
      "data": [
        {{"label": "Jan 2025", "Act": 150.25, "rf": 145.00}},
        {{"label": "Feb 2025", "Act": 175.40, "rf": 160.50}},
        {{"label": "Mar 2025", "Act": 190.10, "rf": 185.00}}
      ]
    }}
  ]
}}

RESPOND WITH PURE JSON ONLY:
"""
    return prompt
