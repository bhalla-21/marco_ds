# app/prompts.py
def build_query_planner_prompt(user_question: str, df_schema: str):
    """
    Creates a direct and explicit prompt that is AWARE of the available data range.
    """
    available_time_period = "The available data covers the period from October 2023 to December 2024."
    return f"""
Your task is to act as a JSON generator. Your ONLY output must be a single, valid JSON object. Do not provide any other text or explanation.
The data table schema is:
{df_schema}
{available_time_period}
Available Brands: Oreo, Chips Ahoy, Milka, Ritz
Available Countries: USA, Germany, Brazil, UK, France
Analyze the following user question and generate a JSON object with the keys "brand", "country", and "months" to query the table.
- If a value isn't mentioned, set it to null.
- For "months", provide a list of strings in 'YYYY-MM' format.
- Based on the user's request for "QTD" (Quarter-to-Date), "YTD", etc., select the appropriate months from the available data range (2023-10 to 2024-12).
User Question: "{user_question}"
JSON Output:
"""


def build_insight_and_charting_prompt(user_question: str, data_json: str):
    """
    Creates a prompt that asks the LLM to generate both a textual answer
    and the specifications for any required charts, including combination charts.
    """
    return f"""
You are a financial analyst. Your task is to analyze the provided JSON data and answer the user's question.
Your ONLY output must be a single, valid JSON object with two keys: "text_answer" and "charts".
User Question: "{user_question}"
Data:
{data_json}
Instructions:
1. **text_answer**: Write a comprehensive, multi-level analysis based on the data. Use markdown for formatting.
2. **charts**: Generate a list of JSON objects defining charts to visualize your analysis.
    - **Hint:** If the user's question involves analyzing both 'Revenue' and 'Volume', create a single chart object. Its `data` array should contain dictionaries with 'label', 'Revenue', and 'Volume' keys. This will create a combination chart.
    - For single-metric charts, the `data` array should contain dictionaries with 'label' and 'value' keys.
    - Each chart object must contain: `chart_type`, `title`.
JSON Output:
"""