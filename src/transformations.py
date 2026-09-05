import pandas as pd

def create_flight_fact_table(df: pd.DataFrame) -> pd.DataFrame:

    #Create canonical flight operations table

    fact = pd.DataFrame()

    #identification

    fact["flight_date"] = df["FL_DATE"]
    fact["carrier"] = df["OP_UNIQUE_CARRIER"]
    fact["flight_number"] = df["OP_CARRIER_FL_NUM"]

    #route
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

    #Scheduled and actual times
    fact["scheduled_departure_hhmm"] = df["CRS_DEP_TIME"]
    fact["actual_departure_hhmm"] = df["DEP_TIME"]
    fact["scheduled_arrival_hhmm"] = df["CRS_ARR_TIME"]
    fact["actual_arrival_hhmm"] = df["ARR_TIME"]
    fact["scheduled_duration_min"] = df["CRS_ELAPSED_TIME"]
    fact["actual_duration_min"] = df["ACTUAL_ELAPSED_TIME"]

    fact["air_time_min"] = df["AIR_TIME"]
    fact["taxi_out_min"] = df["TAXI_OUT"]
    fact["taxi_in_min"] = df["TAXI_IN"]

    #delays
    fact["departure_delay_min"] = df["DEP_DELAY"]
    fact["arrival_delay_min"] = df["ARR_DELAY"]
    fact["departure_delayed_15"] = df["DEP_DEL15"]
    fact["arrival_delayed_15"] = df["ARR_DEL15"]
    fact["departure_delay_category"] = df["DEP_DELAY_CATEGORY"]
    fact["arrival_delay_category"] = df["ARR_DELAY_CATEGORY"]

    #Status
    fact["flight_status"] = df["FLIGHT_STATUS"]
    fact["is_completed"] = df["IS_COMPLETED"]
    fact["is_cancelled"] = df["IS_CANCELLED"]
    fact["is_diverted"] = df["IS_DIVERTED"]

    #geography and distance
    fact["distance_miles"] = df["DISTANCE"]

    #Calendor shit
    fact["year"] = df["YEAR"]
    fact["month"] = df["MONTH"]
    fact["day"] = df["DAY"]
    fact["day_of_week"] = df["DAY_OF_WEEK"]
    fact["day_of_week_num"] = df["DAY_OF_WEEK_NUM"]
    fact["is_weekend"] = df["IS_WEEKEND"]

    

    return fact

