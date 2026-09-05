import pandas as pd

def clean_bts_flight_data(df: pd.DataFrame) -> pd.DataFrame:
    """
   Cleaning the BTS data

   """
    
    df = df.copy()

    # Column Names
    df.columns = (
        df.columns
        .str.strip()
        .str.upper()
    )

    # Date Fields

    df["FL_DATE"] = pd.to_datetime(
        df["FL_DATE"],
        errors="coerce"
    )

    #Dates

    df["YEAR"] = df["FL_DATE"].dt.year
    df["MONTH"] = df["FL_DATE"].dt.month
    df["DAY"] = df["FL_DATE"].dt.day
    df["DAY_OF_WEEK"] = df["FL_DATE"].dt.day_name()
    df["DAY_OF_WEEK_NUM"] = df["FL_DATE"].dt.dayofweek
    df["IS_WEEKEND"] = df["DAY_OF_WEEK_NUM"] >= 5


#Numericals

    numeric_columns = [
        "OP_CARRIER_FL_NUM",
        "ORIGIN_AIRPORT_ID",
        "DEST_AIRPORT_ID",
        "CRS_DEP_TIME",
        "DEP_TIME",
        "DEP_DELAY",
        "DEP_DELAY_NEW",
        "DEP_DEL15",
        "DEP_DELAY_GROUP",
        "CRS_ARR_TIME",
        "ARR_TIME",
        "ARR_DELAY",
        "ARR_DELAY_NEW",
        "ARR_DEL15",
        "TAXI_OUT",
        "TAXI_IN",
        "CRS_ELAPSED_TIME",
        "ACTUAL_ELAPSED_TIME",
        "AIR_TIME",
        "DISTANCE",
        "CANCELLED",
        "DIVERTED",
    ]

    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

# Status of Flight  
    df["FLIGHT_STATUS"] = "COMPLETED"

    df.loc[
        df["DIVERTED"] == 1,
        "FLIGHT_STATUS"
    ] = "DIVERTED"

    df.loc[
        df["CANCELLED"] == 1,
        "FLIGHT_STATUS"
    ] = "CANCELLED"

    df["IS_COMPLETED"] = (
        df["FLIGHT_STATUS"] == "COMPLETED"
    )

    df["IS_CANCELLED"] = (
        df["FLIGHT_STATUS"] == "CANCELLED"
    )

    df["IS_DIVERTED"] = (
        df["FLIGHT_STATUS"] == "DIVERTED"
    )


    # --------------------------------------------------
    # 5. Delay eligibility
    # --------------------------------------------------

    df["DEP_DELAY_ELIGIBLE"] = (
        df["DEP_DEL15"].notna()
    )

    df["ARR_DELAY_ELIGIBLE"] = (
        df["ARR_DEL15"].notna()
    )

    df["DEP_DELAYED_15"] = (
        df["DEP_DEL15"] == 1
    )

    df["ARR_DELAYED_15"] = (
        df["ARR_DEL15"] == 1
    )

    #Delay categories

    def classify_delay(delay):
        if pd.isna(delay):
            return "Not Applicable"
        if delay < 0:
            return "Early"
        if delay == 0:
            return "On Time"
        if delay < 15:
            return "1-14 min"
        if delay < 30:
            return "15-29 min"
        if delay < 60:
            return "30-59 min"
        if delay < 120:
            return "60-119 min"

        return "120+ min"

    df["DEP_DELAY_CATEGORY"] = (
        df["DEP_DELAY"].apply(classify_delay)
    )

    df["ARR_DELAY_CATEGORY"] = (
        df["ARR_DELAY"].apply(classify_delay)
    )

    #Route Identification

    df["ROUTE"] = (
        df["ORIGIN"].astype(str)
        + "-"
        + df["DEST"].astype(str)
    )

    #Remove duplicates and reset index

    df = df.drop_duplicates().reset_index(drop=True)

    return df