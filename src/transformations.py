import pandas as pd

import airportsdata
from zoneinfo import ZoneInfo


def add_airport_timezones(df: pd.DataFrame) -> pd.DataFrame:

    airports = airportsdata.load("IATA")

    df = df.copy()

    df["ORIGIN_TIMEZONE"] = df["ORIGIN"].map(
        lambda x: airports[x]["tz"] if x in airports else None
    )

    df["DEST_TIMEZONE"] = df["DEST"].map(
        lambda x: airports[x]["tz"] if x in airports else None
    )

    return df


def create_local_timestamp(
    flight_date: pd.Series,
    hhmm: pd.Series
) -> pd.Series:

    hhmm = pd.to_numeric(hhmm, errors="coerce")

    hours = hhmm // 100
    minutes = hhmm % 100

    timestamp = (
        pd.to_datetime(flight_date, errors="coerce")
        + pd.to_timedelta(hours, unit="h")
        + pd.to_timedelta(minutes, unit="m")
    )

    return timestamp


def localize_airport_timestamps(
    df: pd.DataFrame,
    timestamp_column: str,
    timezone_column: str,
    output_column: str
) -> pd.DataFrame:

    df = df.copy()

    localized = pd.Series(
        index=df.index,
        dtype="object"
    )

    for timezone in df[timezone_column].dropna().unique():

        mask = df[timezone_column] == timezone

        localized.loc[mask] = [
            timestamp.replace(tzinfo=ZoneInfo(timezone))
            if pd.notna(timestamp)
            else pd.NaT
            for timestamp in df.loc[mask, timestamp_column]
        ]

    df[output_column] = localized

    return df


def create_flight_timestamps(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()

    df["SCHEDULED_DEPARTURE_LOCAL"] = create_local_timestamp(
        df["FL_DATE"],
        df["CRS_DEP_TIME"]
    )

    df["ACTUAL_DEPARTURE_LOCAL"] = create_local_timestamp(
        df["FL_DATE"],
        df["DEP_TIME"]
    )

    df = localize_airport_timestamps(
        df,
        "SCHEDULED_DEPARTURE_LOCAL",
        "ORIGIN_TIMEZONE",
        "SCHEDULED_DEPARTURE_AWARE"
    )

    df = localize_airport_timestamps(
        df,
        "ACTUAL_DEPARTURE_LOCAL",
        "ORIGIN_TIMEZONE",
        "ACTUAL_DEPARTURE_AWARE"
    )

    df["SCHEDULED_DEPARTURE_UTC"] = df[
        "SCHEDULED_DEPARTURE_AWARE"
    ].apply(
        lambda x:
        x.astimezone(ZoneInfo("UTC"))
        if pd.notna(x)
        else pd.NaT
    )

    df["ACTUAL_DEPARTURE_UTC"] = df[
        "ACTUAL_DEPARTURE_AWARE"
    ].apply(
        lambda x:
        x.astimezone(ZoneInfo("UTC"))
        if pd.notna(x)
        else pd.NaT
    )

    df["SCHEDULED_ARRIVAL_UTC"] = (
        df["SCHEDULED_DEPARTURE_UTC"]
        + pd.to_timedelta(
            df["CRS_ELAPSED_TIME"],
            unit="m"
        )
    )

    df["SCHEDULED_ARRIVAL_AWARE"] = pd.Series(
        [
            (
                utc_time.astimezone(
                    ZoneInfo(dest_tz)
                )
                if pd.notna(utc_time)
                and pd.notna(dest_tz)
                else pd.NaT
            )
            for utc_time, dest_tz in zip(
                df["SCHEDULED_ARRIVAL_UTC"],
                df["DEST_TIMEZONE"]
            )
        ],
        index=df.index,
        dtype="object"
    )

    df["SCHEDULED_ARRIVAL_LOCAL"] = (
        df["SCHEDULED_ARRIVAL_AWARE"]
        .apply(
            lambda x:
            x.replace(tzinfo=None)
            if pd.notna(x)
            else pd.NaT
        )
    )

    df["ACTUAL_ARRIVAL_UTC"] = (
        df["ACTUAL_DEPARTURE_UTC"]
        + pd.to_timedelta(
            df["ACTUAL_ELAPSED_TIME"],
            unit="m"
        )
    )

    df["ACTUAL_ARRIVAL_AWARE"] = pd.Series(
        [
            (
                utc_time.astimezone(
                    ZoneInfo(dest_tz)
                )
                if pd.notna(utc_time)
                and pd.notna(dest_tz)
                else pd.NaT
            )
            for utc_time, dest_tz in zip(
                df["ACTUAL_ARRIVAL_UTC"],
                df["DEST_TIMEZONE"]
            )
        ],
        index=df.index,
        dtype="object"
    )

    df["ACTUAL_ARRIVAL_LOCAL"] = (
        df["ACTUAL_ARRIVAL_AWARE"]
        .apply(
            lambda x:
            x.replace(tzinfo=None)
            if pd.notna(x)
            else pd.NaT
        )
    )

    return df


def create_flight_fact_table(df: pd.DataFrame) -> pd.DataFrame:

    fact = pd.DataFrame()

    fact["flight_date"] = df["FL_DATE"]
    fact["carrier"] = df["OP_UNIQUE_CARRIER"]
    fact["flight_number"] = df["OP_CARRIER_FL_NUM"]

    fact["origin"] = df["ORIGIN"]
    fact["destination"] = df["DEST"]
    fact["route"] = df["ROUTE"]

    fact["flight_id"] = (
        fact["flight_date"].dt.strftime("%Y%m%d")
        + "_"
        + fact["carrier"]
        + "_"
        + fact["flight_number"].astype("Int64").astype(str)
        + "_"
        + fact["origin"]
        + "_"
        + fact["destination"]
    )

    fact["scheduled_departure_hhmm"] = df["CRS_DEP_TIME"]
    fact["actual_departure_hhmm"] = df["DEP_TIME"]
    fact["scheduled_arrival_hhmm"] = df["CRS_ARR_TIME"]
    fact["actual_arrival_hhmm"] = df["ARR_TIME"]

    fact["scheduled_duration_min"] = df["CRS_ELAPSED_TIME"]
    fact["actual_duration_min"] = df["ACTUAL_ELAPSED_TIME"]

    fact["air_time_min"] = df["AIR_TIME"]
    fact["taxi_out_min"] = df["TAXI_OUT"]
    fact["taxi_in_min"] = df["TAXI_IN"]

    fact["departure_delay_min"] = df["DEP_DELAY"]
    fact["arrival_delay_min"] = df["ARR_DELAY"]

    fact["departure_delayed_15"] = df["DEP_DEL15"]
    fact["arrival_delayed_15"] = df["ARR_DEL15"]

    fact["departure_delay_category"] = df["DEP_DELAY_CATEGORY"]
    fact["arrival_delay_category"] = df["ARR_DELAY_CATEGORY"]

    fact["carrier_delay"] = df["CARRIER_DELAY"]
    fact["weather_delay"] = df["WEATHER_DELAY"]
    fact["nas_delay"] = df["NAS_DELAY"]
    fact["security_delay"] = df["SECURITY_DELAY"]
    fact["late_aircraft_delay"] = df["LATE_AIRCRAFT_DELAY"]

    fact["flight_status"] = df["FLIGHT_STATUS"]
    fact["is_completed"] = df["IS_COMPLETED"]
    fact["is_cancelled"] = df["IS_CANCELLED"]
    fact["is_diverted"] = df["IS_DIVERTED"]

    fact["distance_miles"] = df["DISTANCE"]

    fact["year"] = df["YEAR"]
    fact["month"] = df["MONTH"]
    fact["day"] = df["DAY"]
    fact["day_of_week"] = df["DAY_OF_WEEK"]
    fact["day_of_week_num"] = df["DAY_OF_WEEK_NUM"]
    fact["is_weekend"] = df["IS_WEEKEND"]

    return fact