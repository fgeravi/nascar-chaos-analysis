# NASCAR Chaos Interpreter, Version 1.0

A small program representing a reproducible data pipeline using NASCAR weekend feed JSON data.

## What this project does
- Loads NASCAR race weekend results from a JSON file
- Computes a chaos score from race-level signals (cautions, caution laps, lead changes, leaders)
- Shows driver starting positions, finishing positions, and position change
- Exports results to CSV
- Loads results into a SQLite database
- Runs SQL queries to find who gained the most positions and who lost the most

This project is intentionally intended to use strictly software to interpret race data.

## Folder structure
- `src/` – analysis and pipeline scripts  
- `src/v2/` – additional pace focused analysis modules
- `output/` – generated results (CSV, text summary, SQLite DB)  
- `scratch/` – early scratch work  
- `weekend-feed-5392.json` – sample input data (NASCAR weekend-feed JSON)

## How to run
From the project root:

```bash
PYTHONPATH=src python3 src/single_race_report.py
PYTHONPATH=src python3 src/build_db.py
PYTHONPATH=src python3 src/query_db.py