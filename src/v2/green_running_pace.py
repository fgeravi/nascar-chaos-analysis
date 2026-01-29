import json
from pathlib import Path
import pandas as pd

RAW_PATH = Path("data/raw/lap_times_2023_3_5343.json")

# Lap-time bounds and window for green running laps
GREEN_MIN = 45
GREEN_MAX = 70
VALID_MIN = 30
VALID_MAX = 200

# Filling in flag_state for laps with no certain event by keeping the last known state forward
def build_lap_flag_table(flags: list[dict]) -> pd.DataFrame:
    f = pd.DataFrame(flags).copy()
    f = f.rename(columns={"LapsCompleted": "lap", "FlagState": "flag_state"})
    f["lap"] = pd.to_numeric(f["lap"], errors="coerce")
    f["flag_state"] = pd.to_numeric(f["flag_state"], errors="coerce")
    f = f.dropna(subset=["lap", "flag_state"]).sort_values("lap")

    max_lap = int(f["lap"].max())
    lap_index = pd.DataFrame({"lap": range(0, max_lap + 1)})
    lap_flags = lap_index.merge(f, on="lap", how="left").sort_values("lap")
    lap_flags["flag_state"] = lap_flags["flag_state"].ffill()
    return lap_flags

# FLatten nested drivers to laps structure into "row per driver per lap" table
def flatten_laps(drivers: list[dict]) -> pd.DataFrame:
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
    df = pd.DataFrame(rows)
    for c in ["lap", "lap_time", "lap_speed", "running_pos"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df.dropna(subset=["lap", "driver_id"]).reset_index(drop=True)

# Loading feeds, normalize lap/level rows and ataching FlagState per lap
def main():
    data = json.load(RAW_PATH.open("r", encoding="utf-8"))
    df = flatten_laps(data["laps"])
    lap_flags = build_lap_flag_table(data["flags"])
    df = df.merge(lap_flags, on="lap", how="left")

    # Filtr junk values, impossible times
    df = df.dropna(subset=["lap_time"])
    df = df[(df["lap_time"] >= VALID_MIN) & (df["lap_time"] <= VALID_MAX)]

    # Separate true race pace for better comparisons
    df_green = df[(df["lap_time"] >= GREEN_MIN) & (df["lap_time"] <= GREEN_MAX)].copy()

    print("Total valid laps:", len(df))
    print("Green-running laps:", len(df_green))
    print("Unique drivers:", df_green["driver_id"].nunique())

    g = df_green.groupby(["driver_id", "name"])["lap_time"]
    metrics = g.agg(["count", "mean", "min", "std"]).reset_index()
    metrics = metrics.rename(columns={
        "count": "green_laps",
        "mean": "avg_green_lap",
        "min": "best_green_lap",
        "std": "std_green_lap",
    }).sort_values("avg_green_lap")

    print(f"\nTop 15 by avg GREEN-RUNNING lap (lap_time {GREEN_MIN}-{GREEN_MAX}s):")
    print(metrics.head(15).to_string(index=False))

    # Showing some laps that were excluded to verify
    excluded = df[df["lap_time"] > GREEN_MAX].head(8)[["lap","lap_time","flag_state","driver_id","name"]]
    print("\nExample excluded (non-green-running) laps:")
    print(excluded.to_string(index=False))

if __name__ == "__main__":
    main()
