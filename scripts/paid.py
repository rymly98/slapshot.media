"""One-off: 2025-26 regular-season stats for the 2026-27 highest-paid players."""
import json, urllib.request
REQ = json.load(open("data/paid-request.json")); NAMES = REQ["names"]; SID = REQ.get("season", "20252026")
u = ("https://api.nhle.com/stats/rest/en/skater/summary?isAggregate=true&isGame=false&limit=-1"
     f"&cayenneExp=seasonId={SID}%20and%20gameTypeId=2")
rows = json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "slapshot"})))["data"]
out = {}
for n in NAMES:
    r = next((r for r in rows if r["skaterFullName"].lower() == n.lower()), None)
    out[n] = None if not r else {k: r.get(k) for k in ("playerId", "teamAbbrevs", "gamesPlayed", "goals", "assists", "points", "plusMinus")}
json.dump(out, open("data/paid-2025-26.json" if SID == "20252026" else f"data/paid-{SID}.json", "w"), indent=1)
print(out)
