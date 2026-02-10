-- CSV outputs being set like tables
CREATE OR REPLACE VIEW green_pace_summary AS
SELECT *
FROM read_csv_auto('output/v3_daytona_trucks/green_pace_summary.csv');

CREATE OR REPLACE VIEW green_laps_long AS
SELECT *
FROM read_csv_auto('output/v3_daytona_trucks/green_laps_long.csv');

-- Q1: Pace compared with consistency  + include CI halfwidth for color on scatter plot
CREATE OR REPLACE VIEW q_pace_vs_consistency AS
SELECT
  name,
  green_laps,
  avg_green_lap,
  std_green_lap,
  ci95_halfwidth_green_lap
FROM green_pace_summary
ORDER BY avg_green_lap;

-- Q2: Top 10 pace with 95% CI, error bars
CREATE OR REPLACE VIEW q_top10_ci AS
SELECT
  name,
  avg_green_lap,
  ci95_low_green_lap,
  ci95_high_green_lap
FROM green_pace_summary
ORDER BY avg_green_lap
LIMIT 10;

-- Q3: Confidence comapred to sample size
CREATE OR REPLACE VIEW q_confidence_vs_n AS
SELECT
  green_laps,
  ci95_halfwidth_green_lap
FROM green_pace_summary;

-- Q4: Avg green lap time by lap number, using line plot
CREATE OR REPLACE VIEW q_avg_by_lap AS
SELECT
  lap,
  AVG(lap_time) AS avg_lap_time,
  COUNT(*) AS n
FROM green_laps_long
GROUP BY lap
ORDER BY lap;