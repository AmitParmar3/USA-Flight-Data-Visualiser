import pandas as pd


def calculate_airport_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate operational performance metrics by airport.

    Airports are retained regardless of traffic volume.
    Sample-size categories are added to distinguish
    statistically stronger estimates from smaller samples.
    """

    departures = (
        df.groupby("origin")
        .agg(
            departure_flights=("flight_id", "count"),

            departure_delayed_15=(
                "departure_delayed_15",
                lambda x: (x == 1).sum()
            ),

            departure_eligible=(
                "departure_delay_min",
                "count"
            ),

            departure_cancellations=(
                "is_cancelled",
                "sum"
            ),

            departure_diversions=(
                "is_diverted",
                "sum"
            ),

            average_departure_delay=(
                "departure_delay_min",
                "mean"
            ),

            average_positive_departure_delay=(
                "departure_delay_min",
                lambda x: x[x > 0].mean()
            ),
        )
        .reset_index()
        .rename(columns={"origin": "airport"})
    )

    arrivals = (
        df.groupby("destination")
        .agg(
            arrival_flights=("flight_id", "count"),

            arrival_delayed_15=(
                "arrival_delayed_15",
                lambda x: (x == 1).sum()
            ),

            arrival_eligible=(
                "arrival_delay_min",
                "count"
            ),

            arrival_cancellations=(
                "is_cancelled",
                "sum"
            ),

            arrival_diversions=(
                "is_diverted",
                "sum"
            ),

            average_arrival_delay=(
                "arrival_delay_min",
                "mean"
            ),

            average_positive_arrival_delay=(
                "arrival_delay_min",
                lambda x: x[x > 0].mean()
            ),
        )
        .reset_index()
        .rename(columns={"destination": "airport"})
    )

    # Combine departure and arrival statistics
    airport_metrics = departures.merge(
        arrivals,
        on="airport",
        how="outer"
    )

    # Airports may exist only as origins or only as destinations
    numeric_columns = airport_metrics.columns[
        airport_metrics.columns != "airport"
    ]

    airport_metrics[numeric_columns] = (
        airport_metrics[numeric_columns]
        .fillna(0)
    )

    # Total airport traffic
    airport_metrics["total_flights"] = (
        airport_metrics["departure_flights"]
        + airport_metrics["arrival_flights"]
    )

    # Delay rates
    airport_metrics["departure_delay_rate"] = (
        airport_metrics["departure_delayed_15"]
        / airport_metrics["departure_eligible"].replace(0, pd.NA)
    )

    airport_metrics["arrival_delay_rate"] = (
        airport_metrics["arrival_delayed_15"]
        / airport_metrics["arrival_eligible"].replace(0, pd.NA)
    )

    # Cancellation rates
    airport_metrics["departure_cancellation_rate"] = (
        airport_metrics["departure_cancellations"]
        / airport_metrics["departure_flights"].replace(0, pd.NA)
    )

    airport_metrics["arrival_cancellation_rate"] = (
        airport_metrics["arrival_cancellations"]
        / airport_metrics["arrival_flights"].replace(0, pd.NA)
    )

    # Diversion rates
    airport_metrics["departure_diversion_rate"] = (
        airport_metrics["departure_diversions"]
        / airport_metrics["departure_flights"].replace(0, pd.NA)
    )

    airport_metrics["arrival_diversion_rate"] = (
        airport_metrics["arrival_diversions"]
        / airport_metrics["arrival_flights"].replace(0, pd.NA)
    )

    # Sample-size classification
    airport_metrics["reliability_sample"] = pd.cut(
        airport_metrics["total_flights"],
        bins=[
            0,
            100,
            500,
            1000,
            5000,
            float("inf")
        ],
        labels=[
            "Very Small",
            "Small",
            "Moderate",
            "Large",
            "Very Large"
        ],
        include_lowest=True
    )

    return airport_metrics


def calculate_airport_performance(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate origin and destination operational performance metrics by airport.
    """

    origin_metrics = (
        df.groupby("origin")
        .agg(
            departure_flights=("flight_id", "count"),
            departure_delay_rate=("departure_delayed_15", "mean"),
            departure_severe_60_rate=("departure_severe_60", "mean"),
            departure_severe_120_rate=("departure_severe_120", "mean"),
            departure_cancellation_rate=("is_cancelled", "mean"),
            departure_diversion_rate=("is_diverted", "mean"),
            average_departure_delay=("departure_delay_min", "mean"),
        )
        .reset_index()
        .rename(columns={"origin": "airport"})
    )

    destination_metrics = (
        df.groupby("destination")
        .agg(
            arrival_flights=("flight_id", "count"),
            arrival_delay_rate=("arrival_delayed_15", "mean"),
            arrival_severe_60_rate=("arrival_severe_60", "mean"),
            arrival_severe_120_rate=("arrival_severe_120", "mean"),
            arrival_cancellation_rate=("is_cancelled", "mean"),
            arrival_diversion_rate=("is_diverted", "mean"),
            average_arrival_delay=("arrival_delay_min", "mean"),
        )
        .reset_index()
        .rename(columns={"destination": "airport"})
    )

    airport_metrics = origin_metrics.merge(
        destination_metrics,
        on="airport",
        how="outer"
    )

    return airport_metrics

