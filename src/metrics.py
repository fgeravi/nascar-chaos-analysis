# Position_deltas. start_pos - finish_pos. positive delta = improved, negative delta = losing ground
def position_deltas(race):
    rows = []
    for r in race["results"]:
        start_pos = r["starting_position"]
        finish_pos = r["finishing_position"]
        delta = start_pos - finish_pos
        rows.append({
            "driver": r["driver_fullname"],
            "start": start_pos,
            "finish": finish_pos,
            "delta": delta
        })
    return rows

# "Chaos" score, creating a single number to represent chaos from the JSON race data
def chaos_score(race):
    cautions = race.get("number_of_cautions", 0)
    caution_laps = race.get("number_of_caution_laps", 0)
    lead_changes = race.get("number_of_lead_changes", 0)
    leaders = race.get("number_of_leaders", 0)

    return (
        cautions * 1.5 +
        caution_laps * 0.05 +
        lead_changes * 0.8 +
        leaders * 0.6
    )

# Finding the top movement, top gained and top lost position drivers
def top_movers(race, n=5):
    rows = position_deltas(race)
    rows_sorted = sorted(rows, key=lambda x: x["delta"], reverse=True)

    top_gainers = rows_sorted[:n]
    top_losers = rows_sorted[-n:][::-1]

    return top_gainers, top_losers