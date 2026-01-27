import json

# Load JSON file
with open("weekend-feed-5392.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Extracting data and results from race
race = data["weekend_race"][0]
results = race["results"]

print("Driver position changes:\n")

# Looping through drivers and extracting fields
for r in results:
    driver = r["driver_fullname"]
    start = r["starting_position"]
    finish = r["finishing_position"]
    delta = start - finish

    # Formatting
    print(f"{driver:25s}  Start: {start:2d}  Finish: {finish:2d}  Δ: {delta:+3d}")