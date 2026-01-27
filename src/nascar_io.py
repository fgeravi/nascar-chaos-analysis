import json

# Load results non-ASCII
def load_weekend_feed(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# Access the weekend_race list
def get_race(data, index=0):
    return data["weekend_race"][index]