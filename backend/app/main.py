import pandas as pd
import json
import logging
import os
from fastapi import FastAPI, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from app.models import ChatRequest, RichChatResponse
from app.data_loader import load_financials, get_dynamic_data
from app.prompts import build_query_planner_prompt, build_insight_and_charting_prompt
from app.llm_client import call_gemini
from app.chart_generator import render_chart
from app.utils import clean_and_parse_json
from dotenv import load_dotenv

# Configure basic logging to see detailed output in the terminal
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables from your .env file
load_dotenv()

app = FastAPI(title="MDLZ Visual LLM Backend")

# Pre-load data and schema on application startup for efficiency
df = load_financials()
df_schema = df.head(0).to_string()

# Configure CORS to allow cross-origin requests from your React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, restrict this to your frontend's actual domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routes first (before static file mounting)
@app.post("/chat", response_model=RichChatResponse)
def chat_endpoint(request: ChatRequest = Body(...)):
    """
    This endpoint processes a user's natural language question, plans a data query,
    fetches the data, and then generates a textual analysis with supporting visualizations.
    """
    try:
        logging.info(f"Received new question: \"{request.message.text}\"")

        # --- Step 1: Query Planning ---
        planner_prompt = build_query_planner_prompt(request.message.text, df_schema)
        query_plan_str = call_gemini(planner_prompt)
        logging.info(f"LLM Query Plan Response (Raw): {query_plan_str}")

        try:
            # Use the robust utility function to parse the LLM's response
            query_plan = clean_and_parse_json(query_plan_str)
            logging.info(f"Successfully parsed query plan: {query_plan}")
        except (json.JSONDecodeError, ValueError) as e:
            logging.error(f"Failed to parse Query Plan JSON. Error: {e}. Raw response was: {query_plan_str}")
            return RichChatResponse(text_answer="Sorry, I had trouble understanding how to find the data for your question.", error="Query plan generation failed")

        # --- Step 2: Data Fetching ---
        fetched_df = get_dynamic_data(
            brand=query_plan.get("brand"),
            country=query_plan.get("country"),
            months=query_plan.get("months")
        )

        if fetched_df.empty:
            logging.warning(f"No data found for query plan: {query_plan}")
            return RichChatResponse(text_answer="I couldn't find any data matching your request. Please try asking about a different brand, country, or time period.", error="No data found")
        else:
            logging.info(f"Successfully fetched {len(fetched_df)} rows of data.")

        # --- Step 3: Insight & Visualization Generation ---
        synthesis_prompt = build_insight_and_charting_prompt(request.message.text, fetched_df.to_json(orient='records'))
        llm_response_str = call_gemini(synthesis_prompt)
        logging.info(f"Insight & Charting Response (Raw): {llm_response_str}")

        try:
            # Use the robust parser again for the final, complex response
            llm_response_data = clean_and_parse_json(llm_response_str)
            text_answer = llm_response_data.get("text_answer", "No text answer was provided.")
            chart_specs = llm_response_data.get("charts", [])
            logging.info("Successfully parsed final answer and chart specifications.")
        except (json.JSONDecodeError, ValueError):
            logging.warning("Could not parse the final LLM response as JSON. Returning the raw text instead.")
            return RichChatResponse(text_answer=llm_response_str)

        # --- Step 4: Chart Rendering ---
        rendered_charts = []
        if chart_specs:
            logging.info(f"Attempting to render {len(chart_specs)} charts.")
            for i, spec in enumerate(chart_specs):
                chart_image_base64 = render_chart(spec)
                if chart_image_base64:
                    rendered_charts.append(chart_image_base64)
            logging.info(f"Successfully rendered {len(rendered_charts)} charts.")

        # --- Step 5: Assemble and Return the Final Response ---
        return RichChatResponse(text_answer=text_answer, charts=rendered_charts)
        
    except Exception as e:
        logging.critical(f"An unhandled exception occurred in the chat endpoint: {e}", exc_info=True)
        return RichChatResponse(text_answer="", error=f"An unexpected server error occurred: {str(e)}")

@app.get("/api/health")
def healthcheck():
    """A simple endpoint to confirm that the server is running."""
    return {"status": "ok", "message": "MDLZ Visual LLM Backend is running."}

# Mount static files at root with html=True to serve the React app properly
app.mount("/", StaticFiles(directory="static", html=True), name="static")
