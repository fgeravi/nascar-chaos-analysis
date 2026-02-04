# NASCAR Chaos Interpreter, Version: 2.0

A small program representing a reproducible data pipeline using NASCAR weekend feed JSON data.

## What this project does
- Loads NASCAR race weekend results from a JSON file
- Calculates a chaos score from race-level signals (cautions, caution laps, lead changes, leaders)
- Shows driver starting positions, finishing positions, and position change
- Exports results to a CSV 
- Loads results into a SQLite database
- Runs SQL queries to find who gained the most positions and who lost the most

This project is intentionally intended to use strictly software to interpret race data.

## Versions
- v1 focuses on race-level chaos metrics like flags/cautions and position delta
- v2 gives lap-level, green-running pace analysis to find true driver performance and car speed, removing signal noise from the calculations of lap times

## Folder structure
- `src/` – analysis and pipeline scripts  
- `src/v2/` – pace-focused analysis modules (v2)
- `output/` – generated results (CSV, text summary, SQLite DB)  
- `scratch/` – early scratch work  
- `weekend-feed-5392.json` – sample input data (NASCAR weekend-feed JSON)

## How to run (v1 pipeline)
From the project root:

```bash
PYTHONPATH=src python3 src/single_race_report.py
PYTHONPATH=src python3 src/build_db.py
PYTHONPATH=src python3 src/query_db.py