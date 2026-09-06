import pandas as pd


def calculate_delay_cause_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate the contribution of each BTS delay cause.
    """

    delay_columns = {
        "carrier": "carrier_delay",
        "weather": "weather_delay",
        "nas": "nas_delay",
        "security": "security_delay",
        "late_aircraft": "late_aircraft_delay"
    }

    metrics = []

    for cause, column in delay_columns.items():

        total_delay_minutes = df[column].sum()

        affected_flights = (
            df[column] > 0
        ).sum()

        metrics.append({
            "delay_cause": cause,
            "affected_flights": affected_flights,
            "total_delay_minutes": total_delay_minutes,
            "average_delay_minutes": (
                df.loc[df[column] > 0, column].mean()
            )
        })

    result = pd.DataFrame(metrics)

    total_cause_delay = result["total_delay_minutes"].sum()

    result["delay_minutes_share"] = (
        result["total_delay_minutes"] / total_cause_delay
        if total_cause_delay > 0
        else 0
    )

    return result


def calculate_carrier_delay_cause_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate delay-cause contribution by carrier.
    """

    delay_columns = {
        "carrier_delay": "carrier_delay",
        "weather_delay": "weather_delay",
        "nas_delay": "nas_delay",
        "security_delay": "security_delay",
        "late_aircraft_delay": "late_aircraft_delay"
    }

    metrics = []

    for carrier, group in df.groupby("carrier"):

        total_cause_delay = 0

        for cause, column in delay_columns.items():

            total_delay = group[column].sum()
            affected_flights = (group[column] > 0).sum()

            metrics.append({
                "carrier": carrier,
                "delay_cause": cause,
                "affected_flights": affected_flights,
                "total_delay_minutes": total_delay
            })

            total_cause_delay += total_delay

        # Add total attributed delay to each carrier's records
        for row in metrics:
            if row["carrier"] == carrier:
                row["total_cause_delay_minutes"] = total_cause_delay

    result = pd.DataFrame(metrics)

    result["delay_minutes_share"] = (
        result["total_delay_minutes"]
        / result["total_cause_delay_minutes"]
    )

    return result


def calculate_delay_cause_performance(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate aggregate contribution of BTS delay causes.
    """

    cause_columns = {
        "carrier_delay_min": "carrier_delay",
        "weather_delay_min": "weather_delay",
        "nas_delay_min": "nas_delay",
        "security_delay_min": "security_delay",
        "late_aircraft_delay_min": "late_aircraft_delay",
    }

    available_columns = {
        output: column
        for column, output in cause_columns.items()
        if column in df.columns
    }

    if not available_columns:
        raise ValueError("No BTS delay-cause columns found.")

    records = []

    for column, cause_name in available_columns.items():

        series = pd.to_numeric(df[column], errors="coerce")

        records.append(
            {
                "delay_cause": cause_name,
                "flights_with_cause": series.notna().sum(),
                "total_delay_minutes": series.sum(),
                "average_delay_minutes_per_affected_flight": series.mean(),
                "median_delay_minutes_per_affected_flight": series.median(),
            }
        )

    cause_metrics = pd.DataFrame(records)

    total_delay = cause_metrics["total_delay_minutes"].sum()

    if total_delay > 0:
        cause_metrics["share_of_delay_minutes"] = (
            cause_metrics["total_delay_minutes"] / total_delay
        )
    else:
        cause_metrics["share_of_delay_minutes"] = 0

    return cause_metrics.sort_values(
        "total_delay_minutes",
        ascending=False,
    ).reset_index(drop=True)

