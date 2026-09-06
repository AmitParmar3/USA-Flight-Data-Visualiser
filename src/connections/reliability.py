import pandas as pd
import numpy as np


def calculate_connection_reliability(
    connections_df: pd.DataFrame,
    minimum_transfer_time_min: float = 45,
) -> pd.DataFrame:
    """
    Aggregate operational reliability of candidate connections.

    This is modeled operational feasibility, not observed passenger
    connection success.
    """

    if connections_df.empty:
        return pd.DataFrame()

    actual_buffer = connections_df["connection_buffer_min"]

    total = len(connections_df)
    valid = int(actual_buffer.notna().sum())

    # Actual buffer < 0 means the connection fell below the
    # minimum 45-minute transfer requirement.
    infeasible = int((actual_buffer < 0).sum())
    feasible = valid - infeasible

    return pd.DataFrame([{
        "total_connections": total,
        "valid_connections": valid,
        "operationally_feasible": feasible,
        "operationally_infeasible": infeasible,
        "operational_feasibility_rate": (
            feasible / valid if valid else np.nan
        ),
        "operational_risk_rate": (
            infeasible / valid if valid else np.nan
        ),
        "median_connection_buffer_min": actual_buffer.median(),
        "mean_connection_buffer_min": actual_buffer.mean(),
    }])


def calculate_missed_connection_risk(
    connections_df: pd.DataFrame,
    minimum_transfer_time_min: float = 45,
) -> pd.DataFrame:
    """
    Calculate aggregated modeled connection risk.

    Not an observed passenger missed-connection rate.
    """

    if connections_df.empty:
        return pd.DataFrame()

    buffer = connections_df["connection_buffer_min"]

    valid = int(buffer.notna().sum())

    risk = int((buffer < 0).sum())

    return pd.DataFrame([{
        "total_connections": len(connections_df),
        "valid_connections": valid,
        "modeled_at_risk_connections": risk,
        "modeled_connection_risk_rate": (
            risk / valid if valid else np.nan
        ),
    }])


def calculate_connection_reliability_by_group(
    connections_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Aggregate connection reliability by airport, carrier pair,
    and scheduled connection-time bucket.
    """

    if connections_df.empty:
        return pd.DataFrame()

    df = connections_df[
        [
            "connection_airport",
            "inbound_carrier",
            "outbound_carrier",
            "scheduled_connection_time_min",
            "connection_buffer_min",
        ]
    ]

    buffer = df["connection_buffer_min"]

    # Create useful scheduled-buffer categories.
    buckets = pd.cut(
        df["scheduled_connection_time_min"],
        bins=[0, 60, 90, 120, 180, 240, float("inf")],
        labels=[
            "45-59",
            "60-89",
            "90-119",
            "120-179",
            "180-239",
            "240+",
        ],
        right=False,
    )

    # Work on grouped aggregates rather than creating a 27M-row copy.
    grouped = (
        df.assign(
            scheduled_buffer_bucket=buckets,
            operationally_infeasible=buffer < 0,
        )
        .groupby(
            [
                "connection_airport",
                "inbound_carrier",
                "outbound_carrier",
                "scheduled_buffer_bucket",
            ],
            observed=True,
        )
        .agg(
            candidate_connections=("connection_buffer_min", "size"),
            operationally_infeasible=(
                "operationally_infeasible",
                "sum",
            ),
            median_actual_buffer_min=(
                "connection_buffer_min",
                "median",
            ),
            mean_actual_buffer_min=(
                "connection_buffer_min",
                "mean",
            ),
        )
        .reset_index()
    )

    grouped["operational_risk_rate"] = (
        grouped["operationally_infeasible"]
        / grouped["candidate_connections"]
    )

    grouped["operational_feasibility_rate"] = (
        1 - grouped["operational_risk_rate"]
    )

    return grouped