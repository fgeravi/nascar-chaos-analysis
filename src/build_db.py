import csv
import sqlite3

DB_PATH = "output/nascar.db"
CSV_PATH = "output/driver_deltas_5392.csv"
RACE_ID = 5392
RACE_NAME = "Food City 500"
TRACK_NAME = "Bristol Motor Speedway"

# Will change upon new data input, this runs one case and is not a constant
CHAOS_SCORE = 71.20

# Pipeline
def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Creating table for races
    cur.execute("""
        CREATE TABLE IF NOT EXISTS races (
            race_id INTEGER PRIMARY KEY,
            race_name TEXT,
            track_name TEXT,
            chaos_score REAL
        )
    """)

    # Create driver deltas table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS driver_deltas (
            race_id INTEGER,
            driver TEXT,
            start INTEGER,
            finish INTEGER,
            delta INTEGER,
            PRIMARY KEY (race_id, driver)
        )
    """)

    # Insert race metadata
    cur.execute(
        "INSERT OR REPLACE INTO races (race_id, race_name, track_name, chaos_score) VALUES (?, ?, ?, ?)",
        (RACE_ID, RACE_NAME, TRACK_NAME, CHAOS_SCORE)
    )

    # Read CSV into memory
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = []
        for r in reader:
            rows.append((RACE_ID, r["driver"], int(r["start"]), int(r["finish"]), int(r["delta"])))

    # Bulk insert driver rows
    cur.executemany(
        "INSERT OR REPLACE INTO driver_deltas (race_id, driver, start, finish, delta) VALUES (?, ?, ?, ?, ?)",
        rows
    )

# Save and confirmation output where database is written
    conn.commit()
    conn.close()

    print(DB_PATH)

if __name__ == "__main__":
    main()