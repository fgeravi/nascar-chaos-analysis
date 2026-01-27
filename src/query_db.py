import sqlite3

# Configuration
DB_PATH = "output/nascar.db"
RACE_ID = 5392

def main():
    
    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Print functions
    print("Race metadata:")
    for row in cur.execute("""
        SELECT race_id, race_name, track_name, chaos_score
        FROM races
        WHERE race_id = ?
    """, (RACE_ID,)):
        print(row)

    print("\nTop 10 position gainers:")
    for row in cur.execute("""
        SELECT driver, start, finish, delta
        FROM driver_deltas
        WHERE race_id = ?
        ORDER BY delta DESC
        LIMIT 10
    """, (RACE_ID,)):
        print(row)

    print("\nTop 10 position losers:")
    for row in cur.execute("""
        SELECT driver, start, finish, delta
        FROM driver_deltas
        WHERE race_id = ?
        ORDER BY delta ASC
        LIMIT 10
    """, (RACE_ID,)):
        print(row)

    conn.close()

if __name__ == "__main__":
    main()