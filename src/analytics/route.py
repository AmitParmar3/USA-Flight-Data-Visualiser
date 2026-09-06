import pandas as pd


def calculate_route_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate operational performance metrics by route.

    One row represents one origin-destination route.
    """

    route_metrics = (
        df.groupby(["origin", "destination", "route"])
        .agg(
            total_flights=("flight_id", "count"),

            completed_flights=(
                "is_completed",
                "sum"
            ),

            cancelled_flights=(
                "is_cancelled",
                "sum"
            ),

            diverted_flights=(
                "is_diverted",
                "sum"
            ),

            departure_delayed_15=(
                "departure_delayed_15",
                lambda x: (x == 1).sum()
            ),

            arrival_delayed_15=(
                "arrival_delayed_15",
                lambda x: (x == 1).sum()
            ),

            departure_eligible=(
                "departure_delay_min",
                "count"
            ),

            arrival_eligible=(
                "arrival_delay_min",
                "count"
            ),

            average_departure_delay=(
                "departure_delay_min",
                "mean"
            ),

            average_arrival_delay=(
                "arrival_delay_min",
                "mean"
            ),

            average_positive_arrival_delay=(
                "arrival_delay_min",
                lambda x: x[x > 0].mean()
            ),

            median_arrival_delay=(
                "arrival_delay_min",
                "median"
            ),

            severe_delays_60=(
                "arrival_delay_min",
                lambda x: (x >= 60).sum()
            ),

            severe_delays_120=(
                "arrival_delay_min",
                lambda x: (x >= 120).sum()
            ),

            average_distance_miles=(
                "distance_miles",
                "mean"
            ),

            average_scheduled_duration=(
                "scheduled_duration_min",
                "mean"
            ),
        )
        .reset_index()
    )

    # Delay rates

    route_metrics["departure_delay_rate"] = (
        route_metrics["departure_delayed_15"]
        / route_metrics["departure_eligible"].replace(0, pd.NA)
    )

    route_metrics["arrival_delay_rate"] = (
        route_metrics["arrival_delayed_15"]
        / route_metrics["arrival_eligible"].replace(0, pd.NA)
    )

    route_metrics["severe_delay_rate_60"] = (
        route_metrics["severe_delays_60"]
        / route_metrics["arrival_eligible"].replace(0, pd.NA)
    )

    route_metrics["severe_delay_rate_120"] = (
        route_metrics["severe_delays_120"]
        / route_metrics["arrival_eligible"].replace(0, pd.NA)
    )

    # Cancellation and diversion rates

    route_metrics["cancellation_rate"] = (
        route_metrics["cancelled_flights"]
        / route_metrics["total_flights"]
    )

    route_metrics["diversion_rate"] = (
        route_metrics["diverted_flights"]
        / route_metrics["total_flights"]
    )

    # Sample-size classification

    route_metrics["route_sample"] = pd.cut(
        route_metrics["total_flights"],
        bins=[
            0,
            10,
            50,
            100,
            500,
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

    return route_metrics


def calculate_carrier_route_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate operational performance metrics for each
    carrier operating on each origin-destination route.

    Grain:
        One row = one carrier + one route.
    """

    carrier_route_metrics = (
        df.groupby(
            ["carrier", "origin", "destination", "route"]
        )
        .agg(
            total_flights=("flight_id", "count"),

            completed_flights=(
                "is_completed",
                "sum"
            ),

            cancelled_flights=(
                "is_cancelled",
                "sum"
            ),

            diverted_flights=(
                "is_diverted",
                "sum"
            ),

            departure_delayed_15=(
                "departure_delayed_15",
                lambda x: (x == 1).sum()
            ),

            arrival_delayed_15=(
                "arrival_delayed_15",
                lambda x: (x == 1).sum()
            ),

            departure_eligible=(
                "departure_delay_min",
                "count"
            ),

            arrival_eligible=(
                "arrival_delay_min",
                "count"
            ),

            average_departure_delay=(
                "departure_delay_min",
                "mean"
            ),

            average_arrival_delay=(
                "arrival_delay_min",
                "mean"
            ),

            average_positive_arrival_delay=(
                "arrival_delay_min",
                lambda x: x[x > 0].mean()
            ),

            median_arrival_delay=(
                "arrival_delay_min",
                "median"
            ),

            severe_delays_60=(
                "arrival_delay_min",
                lambda x: (x >= 60).sum()
            ),

            severe_delays_120=(
                "arrival_delay_min",
                lambda x: (x >= 120).sum()
            ),

            average_distance_miles=(
                "distance_miles",
                "mean"
            ),

            average_scheduled_duration=(
                "scheduled_duration_min",
                "mean"
            ),
        )
        .reset_index()
    )

    # Delay rates

    carrier_route_metrics["departure_delay_rate"] = (
        carrier_route_metrics["departure_delayed_15"]
        / carrier_route_metrics["departure_eligible"]
        .replace(0, pd.NA)
    )

    carrier_route_metrics["arrival_delay_rate"] = (
        carrier_route_metrics["arrival_delayed_15"]
        / carrier_route_metrics["arrival_eligible"]
        .replace(0, pd.NA)
    )

    carrier_route_metrics["severe_delay_rate_60"] = (
        carrier_route_metrics["severe_delays_60"]
        / carrier_route_metrics["arrival_eligible"]
        .replace(0, pd.NA)
    )

    carrier_route_metrics["severe_delay_rate_120"] = (
        carrier_route_metrics["severe_delays_120"]
        / carrier_route_metrics["arrival_eligible"]
        .replace(0, pd.NA)
    )

    # Cancellation and diversion rates

    carrier_route_metrics["cancellation_rate"] = (
        carrier_route_metrics["cancelled_flights"]
        / carrier_route_metrics["total_flights"]
    )

    carrier_route_metrics["diversion_rate"] = (
        carrier_route_metrics["diverted_flights"]
        / carrier_route_metrics["total_flights"]
    )

    # Sample-size classification

    carrier_route_metrics["route_sample"] = pd.cut(
        carrier_route_metrics["total_flights"],
        bins=[
            0,
            10,
            50,
            100,
            500,
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

    return carrier_route_metrics


def calculate_route_performance(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate operational performance metrics for each origin-destination route.
    """

    route_metrics = (
        df.groupby(["origin", "destination", "route"])
        .agg(
            total_flights=("flight_id", "count"),
            completed_flights=("is_completed", "sum"),
            cancelled_flights=("is_cancelled", "sum"),
            diverted_flights=("is_diverted", "sum"),

            departure_delay_rate=("departure_delayed_15", "mean"),
            arrival_delay_rate=("arrival_delayed_15", "mean"),

            departure_severe_60_rate=("departure_severe_60", "mean"),
            arrival_severe_60_rate=("arrival_severe_60", "mean"),

            departure_severe_120_rate=("departure_severe_120", "mean"),
            arrival_severe_120_rate=("arrival_severe_120", "mean"),

            cancellation_rate=("is_cancelled", "mean"),
            diversion_rate=("is_diverted", "mean"),

            average_departure_delay=("departure_delay_min", "mean"),
            median_departure_delay=("departure_delay_min", "median"),

            average_arrival_delay=("arrival_delay_min", "mean"),
            median_arrival_delay=("arrival_delay_min", "median"),

            average_scheduled_duration=("scheduled_duration_min", "mean"),
            average_actual_duration=("actual_duration_min", "mean"),

            average_duration_deviation=("duration_deviation_min", "mean"),
            average_delay_recovery=("delay_recovery_min", "mean"),

            distance_miles=("distance_miles", "mean"),
        )
        .reset_index()
    )

    return route_metrics

