import pandas as pd


def calculate_overall_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate overall operational metrics for flight data.
    """

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

    metrics = pd.DataFrame({
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

