import pandas as pd


"""
Itinerary Analysis Module.

Calculates total itinerary metrics for 2-leg candidate connection journeys.
"""


def calculate_itinerary_metrics(
    connections_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate origin-to-destination total itinerary performance metrics.

    Parameters:
        connections_df (pd.DataFrame): Candidate connection pairs.

    Returns:
        pd.DataFrame: Aggregated itinerary performance by (origin, destination, connection_airport).
    """
    if connections_df.empty:
        return pd.DataFrame()

    df = connections_df.copy()

    # Total scheduled travel time = (outbound scheduled arrival) - (inbound scheduled departure)
    df["total_scheduled_travel_time_min"] = (
        df["outbound_scheduled_arrival_utc"] - df["inbound_scheduled_departure_utc"]
    ).dt.total_seconds() / 60.0

    itinerary_metrics = (
        df.groupby(["origin", "connection_airport", "destination", "is_same_carrier"])
        .agg(
            total_candidate_options=("inbound_flight_id", "count"),
            average_scheduled_connection_time=(
                "scheduled_connection_time_min",
                "mean",
            ),
            average_total_travel_time=(
                "total_scheduled_travel_time_min",
                "mean",
            ),
            average_inbound_arrival_delay=(
                "inbound_arrival_delay_min",
                "mean",
            ),
            average_outbound_departure_delay=(
                "outbound_departure_delay_min",
                "mean",
            ),
        )
        .reset_index()
    )

    return itinerary_metrics

