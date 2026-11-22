"""One-off: every team's goals, assists and points leaders this season (ties kept).

Uses the per-team club-stats feed (the league-wide summary feed caps at 100 rows),
limited to each team's current roster, same as the daily update's leaders.
"""
import json, datetime, urllib.request
get = lambda u: json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "slapshot"}), timeout=30))
sid = json.load(open("data/allleaders-request.json")).get("season", "20262027")
teams = sorted(s["teamAbbrev"]["default"] for s in get("https://api-web.nhle.com/v1/standings/now")["standings"])

out = {"asof": None, "teams": {}}
allp = []
for t in teams:
    sk = get(f"https://api-web.nhle.com/v1/club-stats/{t}/{sid}/2").get("skaters", [])
    ro = get(f"https://api-web.nhle.com/v1/roster/{t}/current")
    ids = {p["id"] for k in ("forwards", "defensemen") for p in ro.get(k, [])}
    pl = [s for s in sk if s["playerId"] in ids] or sk
    rows = [{"first": r["firstName"]["default"], "last": r["lastName"]["default"], "gp": r["gamesPlayed"],
             "g": r["goals"], "a": r["assists"], "p": r["points"]} for r in pl]
    allp += [dict(r, team=t) for r in rows]
    d = {}
    for k in "gap":
        m = max((r[k] for r in rows), default=0)
        d[k] = {"n": m, "who": sorted([r for r in rows if r[k] == m], key=lambda r: -r["p"])}
    out["teams"][t] = d

out["league"] = {k: [[f'{r["first"]} {r["last"]}', r["team"], r[k]] for r in sorted(allp, key=lambda r: (-r[k], -r["p"]))[:25]] for k in "gap"}
out["asof"] = datetime.datetime.utcnow().isoformat()
json.dump(out, open("data/allleaders.json", "w"), indent=1)
print(len(out["teams"]))
