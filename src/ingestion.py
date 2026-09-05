import pandas as pd

from .config import RAW_DATA_DIR


def load_bts_flight_data(year: int, month: int) -> pd.DataFrame:

    month_str = f"{month:02d}"

    month_dir = (
        RAW_DATA_DIR
        / "bts"
        / str(year)
        / month_str
    )

    csv_files = list(month_dir.glob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(
            f"No CSV file found in {month_dir}"
        )

    if len(csv_files) > 1:
        raise ValueError(
            f"Multiple CSV files found in {month_dir}: "
            f"{csv_files}"
        )

    file_path = csv_files[0]

    print(f"Loading: {file_path}")

    df = pd.read_csv(file_path)

    print(
        f"Loaded {len(df):,} rows "
        f"and {len(df.columns)} columns."
    )

    return df