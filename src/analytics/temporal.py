import pandas as pd


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


def calculate_departure_time_metrics(df: pd.DataFrame) -> pd.DataFrame:
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


def calculate_day_of_week_performance(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate operational performance by day of week.
    """

    day_metrics = (
        df.groupby(["day_of_week_num", "day_of_week"])
        .agg(
            total_flights=("flight_id", "count"),
            completed_flights=("is_completed", "sum"),
            cancelled_flights=("is_cancelled", "sum"),
            diverted_flights=("is_diverted", "sum"),

            departure_delay_rate=("departure_delayed_15", "mean"),
            arrival_delay_rate=("arrival_delayed_15", "mean"),

            departure_severe_60_rate=("departure_severe_60", "mean"),
            arrival_severe_60_rate=("arrival_severe_60", "mean"),

            cancellation_rate=("is_cancelled", "mean"),
            diversion_rate=("is_diverted", "mean"),

            average_departure_delay=("departure_delay_min", "mean"),
            average_arrival_delay=("arrival_delay_min", "mean"),

            average_delay_recovery=("delay_recovery_min", "mean"),
        )
        .reset_index()
        .sort_values("day_of_week_num")
    )

    return day_metrics


def calculate_time_of_day_performance(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate operational performance by scheduled departure period.
    """

    df = df.copy()

    def classify_time(hhmm):
        if pd.isna(hhmm):
            return "Unknown"

        hhmm = int(hhmm)
        hour = hhmm // 100

        if 0 <= hour < 6:
            return "00:00-05:59"
        elif 6 <= hour < 9:
            return "06:00-08:59"
        elif 9 <= hour < 12:
            return "09:00-11:59"
        elif 12 <= hour < 15:
            return "12:00-14:59"
        elif 15 <= hour < 18:
            return "15:00-17:59"
        elif 18 <= hour < 21:
            return "18:00-20:59"
        else:
            return "21:00-23:59"

    df["departure_time_period"] = df["scheduled_departure_hhmm"].apply(
        classify_time
    )

    time_order = [
        "00:00-05:59",
        "06:00-08:59",
        "09:00-11:59",
        "12:00-14:59",
        "15:00-17:59",
        "18:00-20:59",
        "21:00-23:59",
        "Unknown",
    ]

    df["departure_time_period"] = pd.Categorical(
        df["departure_time_period"],
        categories=time_order,
        ordered=True,
    )

    time_metrics = (
        df.groupby("departure_time_period", observed=False)
        .agg(
            total_flights=("flight_id", "count"),
            completed_flights=("is_completed", "sum"),
            cancelled_flights=("is_cancelled", "sum"),
            diverted_flights=("is_diverted", "sum"),

            departure_delay_rate=("departure_delayed_15", "mean"),
            arrival_delay_rate=("arrival_delayed_15", "mean"),

            departure_severe_60_rate=("departure_severe_60", "mean"),
            arrival_severe_60_rate=("arrival_severe_60", "mean"),

            cancellation_rate=("is_cancelled", "mean"),
            diversion_rate=("is_diverted", "mean"),

            average_departure_delay=("departure_delay_min", "mean"),
            average_arrival_delay=("arrival_delay_min", "mean"),

            average_delay_recovery=("delay_recovery_min", "mean"),
        )
        .reset_index()
    )

    return time_metrics

