import pandas as pd


def validate_flight_data(df: pd.DataFrame) -> dict:

    checks = {}

    checks["row_count"] = len(df)

    checks["duplicate_rows"] = (
        df.duplicated().sum()
    )

    checks["missing_flight_date"] = (
        df["FL_DATE"].isna().sum()
    )

    checks["invalid_status"] = (
        ~df["FLIGHT_STATUS"].isin(
            ["COMPLETED", "CANCELLED", "DIVERTED"]
        )
    ).sum()

    checks["negative_distance"] = (
        df["DISTANCE"] < 0
    ).sum()

    checks["negative_scheduled_duration"] = (
        df["CRS_ELAPSED_TIME"] < 0
    ).sum()

    checks["cancelled_with_delay"] = (
        (
            (df["CANCELLED"] == 1)
            & df["ARR_DELAY"].notna()
        )
    ).sum()

    checks["cancelled_and_diverted"] = (
        (
            (df["CANCELLED"] == 1)
            & (df["DIVERTED"] == 1)
        )
    ).sum()

    return checks


def validation_summary(checks: dict) -> pd.DataFrame:

# Convert validation results into a readable table.

    results = pd.DataFrame(
        [
            {
                "CHECK": check,
                "VALUE": value,
                "STATUS": "PASS" if value == 0 else "REVIEW"
            }
            for check, value in checks.items()
            if check != "row_count"
        ]
    )

    return results