import json
import os
import argparse
from pathlib import Path
import pandas as pd

# Default input
DEFAULT_INFILE = "data/raw/lap_times_2023_3_5343.json"

# Defaults 
DEFAULT_GREEN_MIN = 45
DEFAULT_GREEN_MAX = 70
DEFAULT_VALID_MIN = 30
DEFAULT_VALID_MAX = 200


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


# Flatten nested drivers->laps structure into "row per driver per lap" table
def flatten_laps(drivers: list[dict]) -> pd.DataFrame:
    rows = []
    for d in drivers:
        driver_id = d.get("NASCARDriverID")
        name = d.get("FullName")
        manufacturer = d.get("Manufacturer")
        for laprec in d.get("Laps", []):
            rows.append(
                {
                    "driver_id": driver_id,
                    "name": name,
                    "manufacturer": manufacturer,
                    "lap": laprec.get("Lap"),
                    "lap_time": laprec.get("LapTime"),
                    "lap_speed": laprec.get("LapSpeed"),
                    "running_pos": laprec.get("RunningPos"),
                }
            )
    df = pd.DataFrame(rows)
    for c in ["lap", "lap_time", "lap_speed", "running_pos"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df.dropna(subset=["lap", "driver_id"]).reset_index(drop=True)


def parse_args():
    p = argparse.ArgumentParser(description="Green-running pace analysis (lap-level).")
    p.add_argument(
        "--infile",
        default=DEFAULT_INFILE,
        help=f"Path to lap-times JSON (default: {DEFAULT_INFILE})",
    )
    p.add_argument(
        "--outdir",
        default=None,
        help="If set, writes CSV outputs to this folder (ex: output/v2_daytona_trucks)",
    )

    p.add_argument("--green-min", type=float, default=DEFAULT_GREEN_MIN)
    p.add_argument("--green-max", type=float, default=DEFAULT_GREEN_MAX)
    p.add_argument("--valid-min", type=float, default=DEFAULT_VALID_MIN)
    p.add_argument("--valid-max", type=float, default=DEFAULT_VALID_MAX)

    p.add_argument("--excluded-n", type=int, default=8, help="How many excluded laps to show/save")
    return p.parse_args()


# Loading feeds, normalize lap-level rows and attaching FlagState per lap
def main():
    args = parse_args()

    infile = Path(args.infile)
    if not infile.exists():
        raise FileNotFoundError(f"Input file not found: {infile}")

    data = json.load(infile.open("r", encoding="utf-8"))
    df = flatten_laps(data["laps"])
    lap_flags = build_lap_flag_table(data["flags"])
    df = df.merge(lap_flags, on="lap", how="left")

    # Filter junk values, impossible times
    df = df.dropna(subset=["lap_time"])
    df = df[(df["lap_time"] >= args.valid_min) & (df["lap_time"] <= args.valid_max)].copy()

    # Mark green-running laps (behavior-based window)
    df["is_green_running"] = (df["lap_time"] >= args.green_min) & (df["lap_time"] <= args.green_max)
    df_green = df[df["is_green_running"]].copy()

    print("Total valid laps:", len(df))
    print("Green-running laps:", len(df_green))
    print("Unique drivers:", df_green["driver_id"].nunique())

    g = df_green.groupby(["driver_id", "name"])["lap_time"]
    metrics = g.agg(["count", "mean", "min", "std"]).reset_index()
    metrics = metrics.rename(
        columns={
            "count": "green_laps",
            "mean": "avg_green_lap",
            "min": "best_green_lap",
            "std": "std_green_lap",
        }
    ).sort_values("avg_green_lap")

    # Uncertainty for mean pace (SEM + 95% CI)
    metrics["sem_green_lap"] = metrics["std_green_lap"] / (metrics["green_laps"] ** 0.5)

    z = 1.96  # 95% norm approximation
    metrics["ci95_low_green_lap"] = metrics["avg_green_lap"] - z * metrics["sem_green_lap"]
    metrics["ci95_high_green_lap"] = metrics["avg_green_lap"] + z * metrics["sem_green_lap"]
    metrics["ci95_halfwidth_green_lap"] = z * metrics["sem_green_lap"]

    print(f"\nTop 15 by avg GREEN-RUNNING lap (lap_time {int(args.green_min)}-{int(args.green_max)}s):")
    print(metrics.head(15).to_string(index=False))

    # Show excluded laps (too low like pits, and impossible lap times)
    excluded = df[~df["is_green_running"]].head(args.excluded_n)[
        ["lap", "lap_time", "flag_state", "driver_id", "name"]
    ]
    print("\nExample excluded (non-green-running) laps:")
    print(excluded.to_string(index=False))

    # Ability to write outputs if requested
    if args.outdir:
        outdir = Path(args.outdir)
        outdir.mkdir(parents=True, exist_ok=True)

        metrics_path = outdir / "green_pace_summary.csv"
        green_long_path = outdir / "green_laps_long.csv"
        excluded_path = outdir / "excluded_laps_sample.csv"

        metrics.to_csv(metrics_path, index=False)
        df_green.to_csv(green_long_path, index=False)
        excluded.to_csv(excluded_path, index=False)

        print(f"\nWrote: {metrics_path}")
        print(f"Wrote: {green_long_path}")
        print(f"Wrote: {excluded_path}")


if __name__ == "__main__":
    main()