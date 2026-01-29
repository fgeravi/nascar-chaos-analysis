import json
from pathlib import Path
import pandas as pd

# Finding which FlagState values are related to true green and fully running laps
RAW_PATH = Path("data/raw/lap_times_2023_3_5343.json")

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

def flatten_laps(drivers: list[dict]) -> pd.DataFrame:
    rows = []
    for d in drivers:
        driver_id = d.get("NASCARDriverID")
        name = d.get("FullName")
        for laprec in d.get("Laps", []):
            rows.append({
                "driver_id": driver_id,
                "name": name,
                "lap": laprec.get("Lap"),
                "lap_time": laprec.get("LapTime"),
            })
    df = pd.DataFrame(rows)
    df["lap"] = pd.to_numeric(df["lap"], errors="coerce")
    df["lap_time"] = pd.to_numeric(df["lap_time"], errors="coerce")
    return df.dropna(subset=["lap", "lap_time"])

# Loading race data, flatten lap times, then give per-lap FlagState info
def main():
    data = json.load(RAW_PATH.open("r", encoding="utf-8"))
    df = flatten_laps(data["laps"])
    lap_flags = build_lap_flag_table(data["flags"])
    df = df.merge(lap_flags, on="lap", how="left")

    # Filter for junk values (impossible lap times and outliers)
    df = df[(df["lap_time"] >= 30) & (df["lap_time"] <= 200)]

    # Daytona Truck green like laps
    green_like = df[(df["lap_time"] >= 45) & (df["lap_time"] <= 70)].copy()

    print("Total clean laps:", len(df))
    print("Green-like laps:", len(green_like))
    
    # Which FlagState values dominate during race pace laps?
    print("\nFlagState distribution on green-like laps:")
    print(green_like["flag_state"].value_counts(dropna=False).head(20).to_string())

    print("\nExamples of non-green-like laps still in same FlagStates (top few):")
    top_states = green_like["flag_state"].value_counts().head(5).index.tolist()
    for st in top_states:
        sample = df[(df["flag_state"] == st) & (df["lap_time"] > 90)].head(5)[["lap", "lap_time", "flag_state", "driver_id", "name"]]
        if len(sample):
            print(f"\nFlagState={st} has >90s laps examples:")
            print(sample.to_string(index=False))

if __name__ == "__main__":
    main()
