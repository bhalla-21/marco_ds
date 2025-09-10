import pandas as pd
import os
import json
import logging
import time
import random
from app.llm_client import call_openai_json  # CHANGED
from app.prompts import build_insight_and_charting_prompt, build_synthesis_prompt, build_simple_answer_prompt
from app.chart_generator import render_chart

DATA_PATH = os.path.join(os.path.dirname(__file__), "../data/synthetic_financials.csv")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def _as_str(s: pd.Series) -> pd.Series:
    return s.astype('string')

def _iexact(s: pd.Series, value: str) -> pd.Series:
    return _as_str(s).str.lower().eq(value.lower())

def _icontains(s: pd.Series, value: str) -> pd.Series:
    return _as_str(s).str.contains(value, case=False, na=False)

def load_financials():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Dataset not found at {DATA_PATH}. Please ensure it exists.")
    df = pd.read_csv(DATA_PATH)
    return df

def get_dynamic_data(brand_text=None, region=None, country_text=None, kpi_text=None, 
                     leg_cat_text=None, market_type_text=None, months=None, 
                     bu_text=None, area=None, bsp_text=None, brand_segment_text=None):
    df = load_financials()
    mask = pd.Series(True, index=df.index)

    if brand_text:
        mask &= _iexact(df["brand_text"], brand_text)
    if region:
        mask &= _iexact(df["region"], region)
    if country_text:
        mask &= _iexact(df["country_text"], country_text)
    if kpi_text:
        mask &= _iexact(df["kpi_text"], kpi_text)
    if leg_cat_text:
        mask &= _iexact(df["leg_cat_text"], leg_cat_text)
    if market_type_text:
        mask &= _iexact(df["market_type_text"], market_type_text)
    if months:
        mask &= df["month"].isin(months)
    if bu_text:
        mask &= _iexact(df["bu_text"], bu_text)
    if area:
        mask &= _iexact(df["area"], area)
    if bsp_text:
        mask &= _iexact(df["bsp_text"], bsp_text)
    if brand_segment_text:
        mask &= _iexact(df["brand_segment_text"], brand_segment_text)

    result_df = df[mask].copy()
    if result_df.empty:
        logging.warning("Query returned an empty DataFrame. The requested combination of filters may not exist in the dataset.")
    return result_df

def get_aggregated_data(group_by_cols, agg_cols, **filters):
    df = get_dynamic_data(**filters)
    if df.empty:
        return df
    grouped_df = df.groupby(group_by_cols).agg(agg_cols).reset_index()
    return grouped_df

def get_performance_summary(filters):
    df = get_dynamic_data(**filters)
    if df.empty:
        return df
    summary = df.groupby(['kpi_text']).agg({
        'Act': 'sum',
        'rf': 'sum', 
        'py': 'sum'
    }).reset_index()
    summary['vs_rf'] = ((summary['Act'] - summary['rf']) / summary['rf'] * 100).round(2)
    summary['vs_py'] = ((summary['Act'] - summary['py']) / summary['py'] * 100).round(2)
    return summary

def get_benchmark_data(base_filters, benchmark_type="py"):
    if benchmark_type == "py":
        if 'months' in base_filters and base_filters['months']:
            py_months = [month - 100 for month in base_filters['months']]
            benchmark_filters = base_filters.copy()
            benchmark_filters['months'] = py_months
            return get_dynamic_data(**benchmark_filters)
    return pd.DataFrame()

def _render_charts_if_needed(result_obj: dict) -> dict:
    """Pass through - main.py will handle chart rendering"""
    return {"text_answer": result_obj.get("text_answer", ""), "charts": result_obj.get("charts", [])}

def call_llm_with_retry(prompt, max_retries=3):
    """Call LLM with exponential backoff retry for 503 errors and enhanced error handling"""
    for attempt in range(max_retries):
        try:
            logging.info(f"LLM API call attempt {attempt + 1}")
            response = call_openai_json(prompt)
            
            # Check if response is valid
            if response is None:
                raise Exception("API returned None response")
            
            if not isinstance(response, str) or len(response.strip()) == 0:
                raise Exception("API returned empty or invalid response")
            
            logging.info(f"LLM API call successful on attempt {attempt + 1}")
            return response
            
        except Exception as e:
            error_msg = str(e).lower()
            logging.warning(f"API call attempt {attempt + 1} failed: {e}")
            
            # Check for specific retry conditions
            should_retry = any(keyword in error_msg for keyword in [
                '503', 'overloaded', 'unavailable', 'timeout', 'connection', 'rate limit'
            ])
            
            if should_retry and attempt < max_retries - 1:
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                logging.warning(f"Retrying in {wait_time:.1f}s... (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
                continue
            else:
                logging.error(f"All retry attempts failed. Final error: {e}")
                break
    
    return None  # Explicitly return None if all attempts failed

def simple_fact_answer(user_question: str, df: pd.DataFrame):
    """
    Generate simple, direct answers for factual questions
    """
    if df.empty:
        return {"text_answer": "No data found for your query.", "charts": []}
    
    logging.info(f"Generating simple answer for: {user_question}")
    
    # Pre-aggregate data for quick facts
    try:
        if 'brand_text' in df.columns and 'Act' in df.columns:
            # Group by brand and KPI for brand-specific questions
            summary_df = df.groupby(['brand_text', 'kpi_text']).agg({
                'Act': 'sum',
                'rf': 'sum',
                'py': 'sum'
            }).reset_index()
        elif 'kpi_text' in df.columns and 'Act' in df.columns:
            # Group by KPI only
            summary_df = df.groupby(['kpi_text']).agg({
                'Act': 'sum',
                'rf': 'sum',
                'py': 'sum'
            }).reset_index()
        else:
            # Fallback - use raw data sample
            summary_df = df.head(10)
        
        # Convert to simple JSON for LLM
        summary_json = summary_df.to_json(orient='records')
        
        # Simple prompt for direct answers
        simple_prompt = build_simple_answer_prompt(user_question, summary_json)
        
        # Use retry logic for API calls
        llm_response_str = call_llm_with_retry(simple_prompt)
        
        if not llm_response_str:
            # Fallback to basic summary
            if 'Act' in summary_df.columns:
                total_value = summary_df['Act'].sum()
                return {
                    "text_answer": f"Based on available data, the total value is {total_value:,.2f}M.",
                    "charts": []
                }
            else:
                return {"text_answer": "Unable to provide a specific answer with available data.", "charts": []}
        
        # Parse JSON response
        result = json.loads(llm_response_str)
        result = _render_charts_if_needed(result)
        
        logging.info("Simple fact answer generated successfully")
        return result
        
    except json.JSONDecodeError as e:
        logging.error(f"JSON parsing error in simple answer: {e}")
        return {"text_answer": "Answer generated but formatting failed. Please try again.", "charts": []}
    except Exception as e:
        logging.error(f"Simple fact answer generation failed: {e}")
        # Final fallback
        if 'Act' in df.columns:
            total_value = df['Act'].sum()
            return {
                "text_answer": f"Based on the available data, the total value is approximately {total_value:,.2f}M.",
                "charts": []
            }
        return {"text_answer": "I'm unable to provide a specific answer with the available data.", "charts": []}

def optimized_single_analysis(user_question: str, df: pd.DataFrame):
    """Optimized analysis for datasets under 1000 rows - designed for your 750-row dataset"""
    if df.empty:
        return {"text_answer": "No data available for analysis.", "charts": []}
    
    logging.info(f"Starting optimized single analysis for {len(df)} rows")
    
    # Determine sampling strategy based on query type
    is_complex_query = any(word in user_question.lower() for word in [
        'dashboard', 'top', 'bottom', 'rank', 'compare all', 'benchmark', 'vs', 'summarize', 'total market'
    ])
    
    # Aggressive sampling for complex queries
    if is_complex_query and len(df) > 200:
        # Sample only recent data and key brands
        if 'month' in df.columns:
            df_sorted = df.sort_values('month', ascending=False)
            sample_df = df_sorted.head(150)  # Reduced from 500
        else:
            sample_df = df.sample(n=150, random_state=42)
        logging.info(f"Complex query detected - using {len(sample_df)} rows from {len(df)} total")
        df = sample_df
    elif len(df) > 300:
        # Regular sampling for simple queries
        sample_df = df.head(300)
        logging.info(f"Using {len(sample_df)} representative rows from {len(df)} total rows")
        df = sample_df
    
    # Convert to JSON for LLM
    try:
        batch_json = df.to_json(orient='records')
        prompt = build_insight_and_charting_prompt(user_question, batch_json)
        
        # Add debug logging
        logging.info(f"Prompt length: {len(prompt)} characters")
        
        # Use retry logic for API calls - ENHANCED ERROR HANDLING
        llm_response_str = call_llm_with_retry(prompt)
        
        # Check if LLM response is None or empty
        if not llm_response_str:
            logging.error("LLM returned None or empty response")
            return {"text_answer": "Unable to process request due to service issues. Please try a simpler query or try again later.", "charts": []}
        
        # Add debug logging for LLM response
        logging.info(f"Raw LLM Response (first 500 chars): {llm_response_str[:500]}")
        
        # Parse JSON response with additional error handling
        try:
            result = json.loads(llm_response_str)
        except json.JSONDecodeError as json_error:
            logging.error(f"JSON parsing failed: {json_error}")
            logging.error(f"Raw response that failed to parse: {llm_response_str[:1000]}")
            return {"text_answer": "Analysis completed but response formatting failed. Please try again.", "charts": []}
        
        # Validate result structure
        if not isinstance(result, dict):
            logging.error(f"LLM returned non-dict result: {type(result)}")
            return {"text_answer": "Invalid response format received. Please try again.", "charts": []}
        
        # Debug chart specifications
        if 'charts' in result:
            logging.info(f"Chart specs found: {len(result.get('charts', []))}")
            logging.info(f"Chart spec types: {[type(spec) for spec in result.get('charts', [])]}")
        
        # Process charts safely
        result = _render_charts_if_needed(result)
        
        logging.info("Optimized single analysis completed successfully")
        return result
        
    except Exception as e:
        logging.error(f"Optimized analysis failed with exception: {e}", exc_info=True)
        return {"text_answer": f"Analysis encountered an error: {str(e)}. Please try a simpler query.", "charts": []}

def comprehensive_analysis(user_question: str, df: pd.DataFrame, batch_size_rows=400):
    """Multi-batch analysis for very large datasets (>1000 rows)"""
    if df.empty:
        return {"total_batches": 0, "batch_results": [], "original_data_count": 0}
    
    num_rows = len(df)
    
    # For datasets under 1000 rows, use optimized single analysis
    if num_rows <= 1000:
        logging.info(f"Dataset ({num_rows} rows) fits single analysis, redirecting to optimized function...")
        result = optimized_single_analysis(user_question, df)
        return {
            "total_batches": 1,
            "batch_results": [result],
            "original_data_count": num_rows
        }
    
    # Multi-batch processing for very large datasets
    batch_results = []
    batches = [df[i:i + batch_size_rows] for i in range(0, num_rows, batch_size_rows)]
    logging.info(f"Large dataset - processing {num_rows} rows across {len(batches)} batches...")
    
    for i, batch_df in enumerate(batches):
        if batch_df.empty:
            continue
            
        try:
            batch_json = batch_df.to_json(orient='records')
            prompt = build_insight_and_charting_prompt(user_question, batch_json)
            
            # Use retry logic
            llm_response_str = call_llm_with_retry(prompt)
            
            if llm_response_str:
                result = json.loads(llm_response_str)
                result = _render_charts_if_needed(result)
                batch_results.append(result)
                logging.info(f"Successfully processed batch {i+1} of {len(batches)}")
            else:
                batch_results.append({"text_answer": f"Batch {i+1} failed due to service issues", "charts": []})
                
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse JSON for batch {i+1}. Error: {e}")
            batch_results.append({"text_answer": f"Error parsing JSON for batch {i+1}", "charts": []})
        except Exception as e:
            logging.error(f"Failed to process batch {i+1}. Error: {e}")
            batch_results.append({"text_answer": f"Error processing batch {i+1}: {str(e)}", "charts": []})
    
    return {
        "total_batches": len(batches),
        "batch_results": batch_results,
        "original_data_count": num_rows
    }

def synthesize_comprehensive_analysis(synthesis_data):
    """Synthesis step for multi-batch analysis"""
    if synthesis_data["total_batches"] == 1:
        # Single batch, return directly
        return synthesis_data["batch_results"][0] if synthesis_data["batch_results"] else {"text_answer": "No results", "charts": []}
    
    # Multi-batch synthesis
    batch_summary = ""
    for i, result in enumerate(synthesis_data['batch_results']):
        batch_summary += f"\n\n--- Analysis from Batch {i+1} ---\n"
        batch_summary += result.get("text_answer", "")
    
    prompt = build_synthesis_prompt(
        user_question="Synthesize the following batch analyses into a single, cohesive response with an executive summary, charts, and tables.",
        batch_summary=batch_summary
    )
    
    try:
        final_response_str = call_llm_with_retry(prompt)
        if final_response_str:
            final_response_data = json.loads(final_response_str)
            final_response_data = _render_charts_if_needed(final_response_data)
            return final_response_data
    except Exception as e:
        logging.error(f"Failed to parse final synthesis JSON: {e}")
    
    return {"text_answer": "Synthesis completed with errors. Please try a more specific query.", "charts": []}

def query_dispatcher(user_question: str, **filters):
    """Legacy function - maintained for backwards compatibility"""
    df = get_dynamic_data(**filters)
    if df.empty:
        logging.error("No data found for the given filters. Cannot proceed with analysis.")
        return {"text_answer": "I'm sorry, I could not find any data that matches your request. Please check your query parameters.", "charts": []}
    
    # Use optimized analysis for all cases now
    return optimized_single_analysis(user_question, df)
