from duckdb import df
import pandas as pd

def calculate_overall_metrics(df: pd.DataFrame) -> pd.DataFrame:

    #Calaculating overall metrics for the flight data

    total_flights = len(df)
    comepleted_flights = df["is_completed"].sum()
    cancelled_flights = df["is_cancelled"].sum()
    diverted_flights = df["is_diverted"].sum()

    departure_eligible = (
        df["departure_delay_min"].notna().sum()
    )

    arrival_eligible = (
        df["arrival_delay_min"].notna().sum()
    )

    departure_delayed = (
        df["departure_delayed_15"] == 1
    ).sum()


    arrival_delayed = (
        df["arrival_delayed_15"] == 1
    ).sum()


    metrics =pd.DataFrame({
            "total_flights": [total_flights],
            "completed_flights": [comepleted_flights],
            "cancelled_flights": [cancelled_flights],
            "diverted_flights": [diverted_flights],

            "cancellation_rate": (
                cancelled_flights / total_flights 
                if total_flights > 0 else 0
            ),

            "diversion_rate": (
                diverted_flights / total_flights 
                if total_flights > 0 else 0
            ),

            "departure_delay_rate": (
                departure_delayed / departure_eligible 
                if departure_eligible > 0 else 0
            ),

            "arrival_delay_rate": (
                arrival_delayed / arrival_eligible 
                if arrival_eligible > 0 else 0
            ),

            "average_departure_delay": (
                df["departure_delay_min"].mean()
            ),

            "average_arrival_delay": (
                df["arrival_delay_min"].mean()
            )
    
        })

    return pd.DataFrame(metrics)

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
