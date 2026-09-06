import pandas as pd


def calculate_carrier_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate operational performance metrics by carrier.
    """

    carrier_metrics = (
        df.groupby("carrier")
        .agg(
            total_flights=("flight_id", "count"),
            completed_flights=("is_completed", "sum"),
            cancelled_flights=("is_cancelled", "sum"),
            diverted_flights=("is_diverted", "sum"),

            departure_delayed_15=(
                "departure_delayed_15",
                "sum"
            ),

            arrival_delayed_15=(
                "arrival_delayed_15",
                "sum"
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
        )
        .reset_index()
    )

    carrier_metrics["cancellation_rate"] = (
        carrier_metrics["cancelled_flights"]
        / carrier_metrics["total_flights"]
    )

    carrier_metrics["diversion_rate"] = (
        carrier_metrics["diverted_flights"]
        / carrier_metrics["total_flights"]
    )

    carrier_metrics["departure_delay_rate"] = (
        carrier_metrics["departure_delayed_15"]
        / carrier_metrics["departure_eligible"]
    )

    carrier_metrics["arrival_delay_rate"] = (
        carrier_metrics["arrival_delayed_15"]
        / carrier_metrics["arrival_eligible"]
    )

    return carrier_metrics


def calculate_carrier_delay_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate detailed delay severity metrics by carrier.
    """

    carrier_delay = (
        df.groupby("carrier")
        .agg(
            total_flights=("flight_id", "count"),

            arrival_eligible=(
                "arrival_delay_min",
                "count"
            ),

            delayed_15=(
                "arrival_delayed_15",
                lambda x: (x == 1).sum()
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
        )
        .reset_index()
    )

    carrier_delay["arrival_delay_rate"] = (
        carrier_delay["delayed_15"]
        / carrier_delay["arrival_eligible"]
    )

    carrier_delay["severe_delay_rate_60"] = (
        carrier_delay["severe_delays_60"]
        / carrier_delay["arrival_eligible"]
    )

    carrier_delay["severe_delay_rate_120"] = (
        carrier_delay["severe_delays_120"]
        / carrier_delay["arrival_eligible"]
    )

    return carrier_delay


def calculate_carrier_performance(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate detailed carrier operational performance and recovery metrics.
    """

    carrier_metrics = (
        df.groupby("carrier")
        .agg(
            total_flights=("flight_id", "count"),
            
            completed_flights=("is_completed", "sum"),
            cancelled_flights=("is_cancelled", "sum"),
            diverted_flights=("is_diverted", "sum"),

            departure_delay_eligible=(
                "departure_delay_min",
                "count"
            ),
            arrival_delay_eligible=(
                "arrival_delay_min",
                "count"
            ),

            departure_delayed_15=(
                "departure_delayed_15",
                lambda x: (x == 1).sum()
            ),
            arrival_delayed_15=(
                "arrival_delayed_15",
                lambda x: (x == 1).sum()
            ),

            average_arrival_delay=(
                "arrival_delay_min",
                "mean"
            ),

            median_arrival_delay=(
                "arrival_delay_min",
                "median"
            ),

            average_positive_arrival_delay=(
                "arrival_delay_min",
                lambda x: x[x > 0].mean()
            ),

            severe_delays_60=(
                "arrival_delay_min",
                lambda x: (x >= 60).sum()
            ),

            severe_delays_120=(
                "arrival_delay_min",
                lambda x: (x >= 120).sum()
            ),

            average_delay_recovery=(
                "delay_recovery_min",
                "mean"
            ),

            average_departure_delay=(
                "departure_delay_min",
                "mean"
            ),
        )
        .reset_index()
    )

    carrier_metrics["cancellation_rate"] = (
        carrier_metrics["cancelled_flights"]
        / carrier_metrics["total_flights"]
    )

    carrier_metrics["diversion_rate"] = (
        carrier_metrics["diverted_flights"]
        / carrier_metrics["total_flights"]
    )

    carrier_metrics["departure_delay_rate"] = (
        carrier_metrics["departure_delayed_15"]
        / carrier_metrics["departure_delay_eligible"]
    )

    carrier_metrics["arrival_delay_rate"] = (
        carrier_metrics["arrival_delayed_15"]
        / carrier_metrics["arrival_delay_eligible"]
    )

    carrier_metrics["severe_delay_rate_60"] = (
        carrier_metrics["severe_delays_60"]
        / carrier_metrics["arrival_delay_eligible"]
    )

    carrier_metrics["severe_delay_rate_120"] = (
        carrier_metrics["severe_delays_120"]
        / carrier_metrics["arrival_delay_eligible"]
    )

    carrier_metrics["recovery_ratio"] = (
        carrier_metrics["average_delay_recovery"]
        / carrier_metrics["average_departure_delay"]
    )

    return carrier_metrics

