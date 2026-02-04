# v2 – Green-Running Pace Analysis

## Purpose and idea
- v2 focuses on pace, not the outcomes
- isolates laps to see where drivers could actually run at speed

## Problem that I'm trying to solve
Raw lap averages include:
- Caution laps
- Pit entry / exit laps
- Restart stack-ups

These distort true pace and outlier values make the data dirty

## Approach
- Flatten to a lap-level table
- Find the green laps using lap time behavior (with params) rather than flag labels alone

For the 2023 Truck race at Daytona:
- Valid laps were 30–200s  
- Green running window: 45-70s

## Outputs
Per driver using green laps only to find:
- Average lap time
- Best lap
- Lap to lap consistency 

This shows the driver and the cars capability without cautions

## Run
From root:
```bash
python3 -m src.v2.green_running_pace
# or
python3 src/v2/green_running_pace.py