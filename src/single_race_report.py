import csv
from nascar_io import load_weekend_feed, get_race
from metrics import position_deltas, top_movers, chaos_score

# Configured paths, edit JSON_PATH if adding a new file
JSON_PATH = "weekend-feed-5392.json"
OUT_PATH = "output/single_race_summary.txt"
CSV_PATH = "output/driver_deltas_5392.csv"

# Start m of pipeline
def main():
    data = load_weekend_feed(JSON_PATH)
    race = get_race(data)
    
    # Pull race metadata + chaos
    name = race["race_name"]
    track = race["track_name"]
    cs = chaos_score(race)

    # Compute drivers delta and movers
    rows = position_deltas(race)
    top_gainers, top_losers = top_movers(race, n=5)

    # Writing CSV output 
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["driver", "start", "finish", "delta"])
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    # Building the text summary
    lines = []
    lines.append(f"Race: {name}")
    lines.append(f"Track: {track}")
    lines.append(f"Chaos score: {cs:.2f}")
    lines.append(f"CSV: {CSV_PATH}")
    lines.append("")

    # Top gainers and losers
    lines.append("Top gainers:")
    for x in top_gainers:
        lines.append(f"{x['driver']} | {x['start']} -> {x['finish']} | {x['delta']:+d}")
    lines.append("")
    lines.append("Top losers:")
    for x in top_losers:
        lines.append(f"{x['driver']} | {x['start']} -> {x['finish']} | {x['delta']:+d}")
    lines.append("")

    # Write summary file and print it
    text = "\n".join(lines)

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(text)

    print(text)

if __name__ == "__main__":
    main()