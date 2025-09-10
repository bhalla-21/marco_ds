# Load .env before any imports that read environment variables
from dotenv import load_dotenv
load_dotenv()

import pandas as pd
import json
import logging
import os
from fastapi import FastAPI, Body, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from app.models import ChatRequest, RichChatResponse
from app.data_loader import (
    load_financials, get_dynamic_data, optimized_single_analysis, simple_fact_answer,
    comprehensive_analysis, synthesize_comprehensive_analysis, 
    get_benchmark_data, get_performance_summary
)
from app.prompts import build_query_planner_prompt, build_insight_and_charting_prompt
from app.llm_client import call_openai_json as call_gemini  # Uses your Gemini client
from app.chart_generator import render_chart
from app.utils import clean_and_parse_json
from app.question_classifier import classify_question_type  # NEW IMPORT
from app.question_validator import is_valid_business_question, get_polite_refusal_message  # NEW IMPORT

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI(title="MDLZ Visual LLM Backend")

# Pre-load data and schema
df = load_financials()
df_schema = df.head(0).to_string()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat", response_model=RichChatResponse)
def chat_endpoint(request: ChatRequest = Body(...)):
    """
    Process a user's question with validation and routing for business relevance
    """
    try:
        logging.info(f"Received new question: \"{request.message.text}\"")
        
        # STEP 0: VALIDATE QUESTION RELEVANCE - NEW ADDITION
        is_valid, reason = is_valid_business_question(request.message.text)
        
        if not is_valid:
            logging.info(f"Question rejected: {reason}")
            refusal_response = get_polite_refusal_message(request.message.text, reason)
            return RichChatResponse(
                text_answer=refusal_response["text_answer"],
                charts=refusal_response["charts"]
            )

        # Step 1: Query Planning (Gemini JSON-only response)
        planner_prompt = build_query_planner_prompt(request.message.text, df_schema)
        
        try:
            query_plan_str = call_gemini(planner_prompt)
            logging.info(f"LLM Query Plan Response (Raw): {query_plan_str}")
        except Exception as e:
            logging.error(f"Query planning failed: {e}")
            return RichChatResponse(
                text_answer="Sorry, I'm having trouble understanding your request. Please try rephrasing your question.",
                error="Query planning service unavailable"
            )

        try:
            query_plan = clean_and_parse_json(query_plan_str)
            logging.info(f"Successfully parsed query plan: {query_plan}")
        except (json.JSONDecodeError, ValueError) as e:
            logging.error(f"Failed to parse Query Plan JSON. Error: {e}. Raw response was: {query_plan_str}")
            return RichChatResponse(
                text_answer="Sorry, I had trouble understanding how to find the data for your question.",
                error="Query plan generation failed"
            )

        # Step 2: Fetch data
        for key, value in list(query_plan.items()):
            if value == 0:
                query_plan[key] = None

        fetched_df = get_dynamic_data(
            brand_text=query_plan.get("brand_text"),
            region=query_plan.get("region"),
            country_text=query_plan.get("country_text"),
            kpi_text=query_plan.get("kpi_text"),
            leg_cat_text=query_plan.get("leg_cat_text"),
            market_type_text=query_plan.get("market_type_text"),
            months=query_plan.get("months")
        )

        if fetched_df.empty:
            logging.warning(f"No data found for query plan: {query_plan}")
            return RichChatResponse(
                text_answer="I couldn't find any data matching your request. Please try asking about a different brand, country, or time period.",
                error="No data found"
            )
        else:
            logging.info(f"Fetched {len(fetched_df)} rows for analysis")

        # Step 3: Analysis - WITH QUESTION TYPE ROUTING
        question_type = classify_question_type(request.message.text)
        logging.info(f"Question classified as: {question_type}")

        if question_type == 'simple':
            # Fast path for simple questions
            logging.info(f"Using simple answer path for {len(fetched_df)} rows")
            try:
                llm_response_data = simple_fact_answer(request.message.text, fetched_df)
                text_answer = llm_response_data.get("text_answer", "Simple answer generated.")
                chart_specs = llm_response_data.get("charts", [])
                logging.info("Simple answer path completed successfully")
            except Exception as e:
                logging.error(f"Simple answer path failed: {e}")
                text_answer = "The specific value you requested is not readily available in our current dataset."
                chart_specs = []

        elif len(fetched_df) > 1000:
            # Only use multi-batch for very large datasets
            logging.info(f"Very large dataset ({len(fetched_df)} rows), using multi-batch analysis")
            try:
                synthesis_data = comprehensive_analysis(request.message.text, fetched_df)
                llm_response_data = synthesize_comprehensive_analysis(synthesis_data)
                text_answer = llm_response_data.get("text_answer", "Comprehensive analysis completed.")
                chart_specs = llm_response_data.get("charts", [])
                logging.info(f"Multi-batch analysis completed across {synthesis_data['total_batches']} batches")
            except Exception as e:
                logging.error(f"Multi-batch analysis failed: {e}, falling back to optimized analysis")
                llm_response_data = optimized_single_analysis(request.message.text, fetched_df.head(500))
                text_answer = llm_response_data.get("text_answer", "Analysis completed with limited data.")
                chart_specs = llm_response_data.get("charts", [])
        else:
            # Optimized path for your 750-row dataset - ANALYTICAL QUESTIONS
            logging.info(f"Standard dataset ({len(fetched_df)} rows), using optimized single-call analysis")
            
            try:
                llm_response_data = optimized_single_analysis(request.message.text, fetched_df)
                
                # Add safety check
                if llm_response_data is None:
                    llm_response_data = {"text_answer": "Service temporarily unavailable. Please try again.", "charts": []}
                
                text_answer = llm_response_data.get("text_answer", "Analysis completed.")
                chart_specs = llm_response_data.get("charts", [])
                logging.info("Optimized single-call analysis completed successfully")
            except Exception as e:
                logging.error(f"Optimized analysis failed: {e}, trying fallback")
                try:
                    # Fallback with smaller dataset
                    limited_df = fetched_df.head(300)
                    synthesis_prompt = build_insight_and_charting_prompt(
                        request.message.text, limited_df.to_json(orient='records')
                    )
                    llm_response_str = call_gemini(synthesis_prompt)
                    llm_response_data = clean_and_parse_json(llm_response_str)
                    text_answer = llm_response_data.get("text_answer", "Analysis completed with limited data.")
                    chart_specs = llm_response_data.get("charts", [])
                except Exception as fallback_error:
                    logging.error(f"Fallback analysis also failed: {fallback_error}")
                    text_answer = "I encountered an issue analyzing your data. Please try with a more specific query."
                    chart_specs = []

        # Step 4: Render charts to base64 - FIXED CHART HANDLING
        rendered_charts = []
        if chart_specs:
            logging.info(f"Attempting to render {len(chart_specs)} charts.")
            for i, spec in enumerate(chart_specs):
                try:
                    # Handle both string and dict chart specs
                    if isinstance(spec, str):
                        logging.info(f"Rendering chart {i}: String spec (length: {len(spec)})")
                        # Try to parse string as JSON
                        try:
                            spec_dict = json.loads(spec)
                            chart_image_base64 = render_chart(spec_dict)
                        except json.JSONDecodeError:
                            logging.warning(f"Chart {i} is a string but not valid JSON, skipping")
                            continue
                    elif isinstance(spec, dict):
                        logging.info(f"Rendering chart {i}: {spec.get('title', 'No title')}")
                        chart_image_base64 = render_chart(spec)
                    else:
                        logging.warning(f"Chart {i} is neither string nor dict: {type(spec)}")
                        continue
                        
                    if chart_image_base64:
                        rendered_charts.append(chart_image_base64)
                        logging.info(f"Chart {i} rendered successfully, base64 length: {len(chart_image_base64)}")
                    else:
                        logging.warning(f"Chart {i} returned None - render_chart failed silently")
                        
                except Exception as e:
                    logging.error(f"Error rendering chart {i}: {str(e)}", exc_info=True)
                    continue
            logging.info(f"Successfully rendered {len(rendered_charts)} out of {len(chart_specs)} charts.")
        else:
            logging.info("No chart specifications provided by LLM.")

        # Step 5: Response
        logging.info(f"Final response - Text length: {len(text_answer)}, Charts count: {len(rendered_charts)}")
        return RichChatResponse(text_answer=text_answer, charts=rendered_charts)

    except Exception as e:
        logging.critical(f"An unhandled exception occurred in the chat endpoint: {e}", exc_info=True)
        return RichChatResponse(text_answer="", error=f"An unexpected server error occurred: {str(e)}")

# Health check
@app.get("/api/health")
def healthcheck():
    return {"status": "ok", "message": "MDLZ Visual LLM Backend is running."}

# Static handling and 404 fallback
@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc: HTTPException):
    path = request.url.path
    if path.startswith("/static/"):
        filepath = os.path.join('static', path[8:])
        if os.path.isfile(filepath):
            return FileResponse(filepath)
    if not path.startswith("/api/"):
        if os.path.exists("static/index.html"):
            return FileResponse('static/index.html')
    return {"detail": "Not Found"}

app.mount("/", StaticFiles(directory="static", html=True), name="static")
