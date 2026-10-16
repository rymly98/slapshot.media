"""One-off: test the team-stats pull used by update.py (The Numbers dropdown)."""
import json, sys
sys.path.insert(0, "scripts")
import update
data = {"gameday": "2026-10-16"}
n = update.add_team_stats(data)
json.dump({"n": n, "season": data.get("Sseason"), "S": data.get("S")}, open("data/verify2.json", "w"), indent=1)
print(n)
