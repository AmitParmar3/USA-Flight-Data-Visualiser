import pandas as pd
import numpy as np


"""
Itinerary Analysis Module.

Calculates total itinerary metrics for 2-leg candidate connection journeys.
"""


def calculate_itinerary_metrics(
    flight_fact: pd.DataFrame,
    candidate_connections: pd.DataFrame = None,
    min_connection_min: float = 45.0,
) -> pd.DataFrame:
    """
    Construct two-leg itinerary metrics from candidate_connections.

    DISTINCTION NOTICE:
    -------------------
    These are modeled two-leg itineraries derived from flight operations.
    They are NOT observed passenger itineraries, PNRs, bookings, or observed
    missed connections. Do not describe them as passenger connection
    success/failure.

    This function operates memory-efficiently by constructing only the required
    result columns without making unnecessary full-size copies of the inputs.

    Parameters:
        flight_fact (pd.DataFrame): The flight fact dataframe. (For backward 
            compatibility, if candidate_connections is None, this is treated 
            as candidate_connections).
        candidate_connections (pd.DataFrame): The candidate connections dataframe.
        min_connection_min (float): Minimum scheduled connection time in minutes.
    """
    
    # Handle backward compatibility where only connections_df was passed
    if candidate_connections is None:
        candidate_connections = flight_fact

    if candidate_connections.empty:
        return pd.DataFrame()

    # Journey time = outbound arrival - inbound departure
    # Calculate directly to avoid copying the 27M row DataFrame
    total_scheduled_journey_time = (
        candidate_connections["outbound_scheduled_arrival_utc"]
        - candidate_connections["inbound_scheduled_departure_utc"]
    ).dt.total_seconds() / 60.0

    # Flight time = journey time - scheduled connection time
    total_scheduled_flight_time = (
        total_scheduled_journey_time
        - candidate_connections["scheduled_connection_time_min"]
    )

    # Actual connection buffer for risk bands
    actual_buffer = (
        candidate_connections["actual_connection_time_min"] - min_connection_min
    )

    # Risk bands based on actual connection buffer:
    # < 0       = Operationally Infeasible
    # 0–14      = Critical
    # 15–29     = High
    # 30–59     = Moderate
    # 60+       = Low
    risk_bands = pd.cut(
        actual_buffer,
        bins=[-np.inf, 0, 15, 30, 60, np.inf],
        labels=[
            "Operationally Infeasible",
            "Critical",
            "High",
            "Moderate",
            "Low"
        ],
        right=False
    )

    # Assemble the final DataFrame memory-efficiently by only keeping required columns
    itinerary_metrics = pd.DataFrame({
        "inbound_flight_id": candidate_connections["inbound_flight_id"],
        "outbound_flight_id": candidate_connections["outbound_flight_id"],
        "origin": candidate_connections["origin"],
        "connection_airport": candidate_connections["connection_airport"],
        "destination": candidate_connections["destination"],
        "inbound_carrier": candidate_connections["inbound_carrier"],
        "outbound_carrier": candidate_connections["outbound_carrier"],
        "same_carrier": candidate_connections["is_same_carrier"],
        "scheduled_connection_time_min": candidate_connections["scheduled_connection_time_min"],
        "actual_connection_time_min": candidate_connections["actual_connection_time_min"],
        "connection_buffer_min": candidate_connections["connection_buffer_min"],
        "inbound_arrival_delay_min": candidate_connections["inbound_arrival_delay_min"],
        "outbound_departure_delay_min": candidate_connections["outbound_departure_delay_min"],
        "total_scheduled_journey_time_min": total_scheduled_journey_time,
        "total_scheduled_flight_time_min": total_scheduled_flight_time,
        "connection_risk_band": risk_bands,
    })

    return itinerary_metrics
