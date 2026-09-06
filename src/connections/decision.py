import pandas as pd
import numpy as np

"""
Decision Engine Module.

Ranks candidate two-leg itineraries according to specified objectives.

DISTINCTION NOTICE:
-------------------
These are modeled operational itineraries derived from flight operations.
They are NOT observed passenger bookings, PNRs, or actual passenger missed connections.
The balanced score is a normalized ranking metric and does not represent
a true probability of successful passenger travel.
"""

REQUIRED_COLUMNS = [
    "total_scheduled_journey_time_min",
    "scheduled_connection_time_min",
    "connection_buffer_min",
    "inbound_arrival_delay_min",
    "outbound_departure_delay_min",
    "connection_risk_band"
]

RISK_BAND_ORDER = {
    "Low": 5,
    "Moderate": 4,
    "High": 3,
    "Critical": 2,
    "Operationally Infeasible": 1
}

def validate_decision_input(itinerary_df: pd.DataFrame, objective: str, top_n: int):
    if objective not in ["fastest", "reliable", "risk", "balanced"]:
        raise ValueError("objective must be one of 'fastest', 'reliable', 'risk', 'balanced'")
    if top_n <= 0:
        raise ValueError("top_n must be positive")
    
    if not itinerary_df.empty:
        missing = [col for col in REQUIRED_COLUMNS if col not in itinerary_df.columns]
        if missing:
            raise ValueError(f"Missing required itinerary columns: {missing}")

def normalize_series(series: pd.Series) -> pd.Series:
    """Min-max normalization to 0-1. Handles edge cases like constant values."""
    s_min = series.min()
    s_max = series.max()
    if pd.isna(s_min) or pd.isna(s_max) or s_min == s_max:
        return pd.Series(0.5, index=series.index)
    return (series - s_min) / (s_max - s_min)

def calculate_itinerary_score(
    itinerary_df: pd.DataFrame,
    objective: str = "balanced",
) -> pd.DataFrame:
    """
    Calculates scoring and ranking info for the given itinerary DataFrame based on the objective.
    Does NOT select top N. Memory-efficient implementation avoids full deep copies.
    """
    objective = objective.lower()
    validate_decision_input(itinerary_df, objective, 1)

    # Use a shallow copy to prevent modifying the original dataframe
    # and to preserve memory efficiency.
    df = itinerary_df.copy(deep=False)
    
    if df.empty:
        df["objective"] = objective
        df["ranking_score"] = np.nan
        df["rank"] = np.nan
        return df

    df["objective"] = objective

    if objective == "fastest":
        df = df.sort_values(
            by=["total_scheduled_journey_time_min", "scheduled_connection_time_min"],
            ascending=[True, True]
        )
        df["ranking_score"] = np.nan

    elif objective == "reliable":
        df = df.sort_values(
            by=["connection_buffer_min", "inbound_arrival_delay_min", "outbound_departure_delay_min"],
            ascending=[False, True, True]
        )
        df["ranking_score"] = np.nan

    elif objective == "risk":
        risk_mapped = df["connection_risk_band"].map(RISK_BAND_ORDER).fillna(0).astype(float)
        sort_key = pd.DataFrame({
            "risk_score": risk_mapped,
            "buffer": df["connection_buffer_min"],
            "journey": df["total_scheduled_journey_time_min"]
        })
        sorted_idx = sort_key.sort_values(
            by=["risk_score", "buffer", "journey"],
            ascending=[False, False, True]
        ).index
        df = df.loc[sorted_idx]
        df["ranking_score"] = np.nan

    elif objective == "balanced":
        # 40% journey efficiency (lower journey time = better)
        # 35% connection reliability (using delay and risk)
        # 25% connection buffer (higher buffer = better)
        
        # 1. Journey (40%) - Inverted so lower time is higher score
        norm_journey = 1.0 - normalize_series(df["total_scheduled_journey_time_min"])
        
        # 2. Buffer (25%)
        norm_buffer = normalize_series(df["connection_buffer_min"])
        
        # 3. Reliability (35%)
        # Combine delays (lower is better) and risk band (higher is better)
        delays = df["inbound_arrival_delay_min"].fillna(0) + df["outbound_departure_delay_min"].fillna(0)
        norm_delay = 1.0 - normalize_series(delays)
        
        risk_mapped = df["connection_risk_band"].map(RISK_BAND_ORDER).fillna(0).astype(float)
        norm_risk = (risk_mapped - 1) / 4.0 # Map 1-5 scale to 0-1
        
        norm_reliability = (0.5 * norm_delay) + (0.5 * norm_risk)
        
        score = (0.40 * norm_journey + 0.35 * norm_reliability + 0.25 * norm_buffer) * 100.0
        
        df["ranking_score"] = score.round(2)
        df = df.sort_values(by="ranking_score", ascending=False)
        
    # Rank is 1-indexed
    df["rank"] = np.arange(1, len(df) + 1)
    
    return df

def rank_itineraries(
    itinerary_df: pd.DataFrame,
    objective: str = "balanced",
    top_n: int = 10,
) -> pd.DataFrame:
    """
    Returns the top N candidate itineraries ranked according to the selected objective.
    """
    validate_decision_input(itinerary_df, objective, top_n)
    
    if itinerary_df.empty:
        return calculate_itinerary_score(itinerary_df, objective)
        
    scored_df = calculate_itinerary_score(itinerary_df, objective)
    return scored_df.head(top_n)
