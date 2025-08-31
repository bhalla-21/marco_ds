import pandas as pd
import os

# Define the absolute path to the data file relative to this script's location
DATA_PATH = os.path.join(os.path.dirname(__file__), "../data/synthetic_financials.csv")

def load_financials():
    """Load the financial dataset into a DataFrame."""
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Dataset not found at {DATA_PATH}. Please ensure it exists.")
    df = pd.read_csv(DATA_PATH)
    return df

def get_dynamic_data(brand: str, country: str, months: list):
    """
    Fetches data from the dataframe based on a dynamic query constructed
    from the parameters provided by the LLM's query plan.
    """
    df = load_financials()
    
    # Start with a mask that is all True, then progressively filter it
    mask = pd.Series(True, index=df.index)
    
    if brand:
        mask &= (df["Brand"].str.lower() == brand.lower())
    if country:
        mask &= (df["Country"].str.lower() == country.lower())
    if months:
        mask &= (df["Month"].isin(months))
    
    # Apply the combined mask to filter the DataFrame
    result_df = df[mask]
    
    return result_df
