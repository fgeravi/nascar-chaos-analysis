import json
from pathlib import Path
import pandas as pd

# Loading raw NASCAR data
RAW_PATH = Path("data/raw/lap_times_2023_3_5343.json")

def main():
    data = json.load(RAW_PATH.open("r", encoding="utf-8"))

    drivers = data["laps"]   # Drivers
    flags = data["flags"]    # Flag events

    rows = []
    for d in drivers:
        driver_id = d.get("NASCARDriverID")
        name = d.get("FullName")
        manufacturer = d.get("Manufacturer")

        for laprec in d.get("Laps", []):
            rows.append({
                "driver_id": driver_id,
                "name": name,
                "manufacturer": manufacturer,
                "lap": laprec.get("Lap"),
                "lap_time": laprec.get("LapTime"),
                "lap_speed": laprec.get("LapSpeed"),
                "running_pos": laprec.get("RunningPos"),
            })

    # Creating dataframe
    df = pd.DataFrame(rows)
    df["lap"] = pd.to_numeric(df["lap"], errors="coerce")
    df["lap_time"] = pd.to_numeric(df["lap_time"], errors="coerce")
    df["lap_speed"] = pd.to_numeric(df["lap_speed"], errors="coerce")
    df["running_pos"] = pd.to_numeric(df["running_pos"], errors="coerce")

    print("Rows:", len(df))
    print("Columns:", list(df.columns))
    print(df.head(12).to_string(index=False))

    # Grouping of lap times, pace and consistency metrics
    g = df.dropna(subset=["lap_time"]).groupby(["driver_id", "name"])

    metrics = g["lap_time"].agg(["count", "mean", "min", "std"]).reset_index()
    metrics = metrics.rename(columns={
        "count": "laps",
        "mean": "avg_lap",
        "min": "best_lap",
        "std": "std_lap",
    }).sort_values("avg_lap")

    print("\nTop 15 by avg lap (lower is faster):")
    print(metrics.head(15).to_string(index=False))

    # Showing initial flags
    print("\nFirst 10 flag events:")
    for f in flags[:10]:
        print(f)

if __name__ == "__main__":
    main()


# NOTE:
# This script is exploratory and intentionally shows raw/unfiltered lap data.
# Some averages may be distorted by caution laps, pit laps, or timing anomalies.
# The cleaned analysis is handled in green_running_pace.py.