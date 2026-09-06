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



def calculate_day_of_week_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate operational performance metrics by day of week.
    """

    day_metrics = (
        df.groupby(
            ["day_of_week_num", "day_of_week"]
        )
        .agg(
            total_flights=("flight_id", "count"),

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

            average_arrival_delay=(
                "arrival_delay_min",
                "mean"
            ),

            average_positive_arrival_delay=(
                "arrival_delay_min",
                lambda x: x[x > 0].mean()
            ),

            severe_delays_60=(
                "arrival_delay_min",
                lambda x: (x >= 60).sum()
            ),
        )
        .reset_index()
    )

    day_metrics["departure_delay_rate"] = (
        day_metrics["departure_delayed_15"]
        / day_metrics["departure_eligible"].replace(0, pd.NA)
    )

    day_metrics["arrival_delay_rate"] = (
        day_metrics["arrival_delayed_15"]
        / day_metrics["arrival_eligible"].replace(0, pd.NA)
    )

    day_metrics["severe_delay_rate_60"] = (
        day_metrics["severe_delays_60"]
        / day_metrics["arrival_eligible"].replace(0, pd.NA)
    )

    day_metrics["cancellation_rate"] = (
        day_metrics["cancelled_flights"]
        / day_metrics["total_flights"]
    )

    day_metrics["diversion_rate"] = (
        day_metrics["diverted_flights"]
        / day_metrics["total_flights"]
    )

    return day_metrics

def calculate_departure_time_metrics(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Calculate operational performance metrics
    by scheduled departure time bucket.
    """

    data = df.copy()

    data["departure_hour"] = (
        data["scheduled_departure"].dt.hour
    )

    def classify_departure_time(hour):
        if 0 <= hour < 6:
            return "Overnight"
        elif 6 <= hour < 9:
            return "Early Morning"
        elif 9 <= hour < 12:
            return "Morning"
        elif 12 <= hour < 15:
            return "Midday"
        elif 15 <= hour < 18:
            return "Afternoon"
        elif 18 <= hour < 21:
            return "Evening"
        else:
            return "Night"

    data["departure_time_bucket"] = (
        data["departure_hour"]
        .apply(classify_departure_time)
    )

    time_metrics = (
        data.groupby("departure_time_bucket")
        .agg(
            total_flights=("flight_id", "count"),

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

            average_positive_departure_delay=(
                "departure_delay_min",
                lambda x: x[x > 0].mean()
            ),

            average_positive_arrival_delay=(
                "arrival_delay_min",
                lambda x: x[x > 0].mean()
            ),

            severe_delays_60=(
                "arrival_delay_min",
                lambda x: (x >= 60).sum()
            ),
        )
        .reset_index()
    )

    bucket_order = [
        "Overnight",
        "Early Morning",
        "Morning",
        "Midday",
        "Afternoon",
        "Evening",
        "Night"
    ]

    time_metrics["departure_time_bucket"] = pd.Categorical(
        time_metrics["departure_time_bucket"],
        categories=bucket_order,
        ordered=True
    )

    time_metrics = time_metrics.sort_values(
        "departure_time_bucket"
    )

    time_metrics["departure_delay_rate"] = (
        time_metrics["departure_delayed_15"]
        / time_metrics["departure_eligible"].replace(0, pd.NA)
    )

    time_metrics["arrival_delay_rate"] = (
        time_metrics["arrival_delayed_15"]
        / time_metrics["arrival_eligible"].replace(0, pd.NA)
    )

    time_metrics["severe_delay_rate_60"] = (
        time_metrics["severe_delays_60"]
        / time_metrics["arrival_eligible"].replace(0, pd.NA)
    )

    time_metrics["cancellation_rate"] = (
        time_metrics["cancelled_flights"]
        / time_metrics["total_flights"]
    )

    time_metrics["diversion_rate"] = (
        time_metrics["diverted_flights"]
        / time_metrics["total_flights"]
    )

    return time_metrics


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