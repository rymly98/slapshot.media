import json, urllib.request
def get(u):
    with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent":"slapshot"}), timeout=30) as r:
        return json.load(r)
req = json.load(open("data/gamelogs-request.json"))
out = {"players": {}, "standings": []}
for pid in req["players"]:
    games = []
    for s in req["seasons"]:
        try:
            d = get(f"https://api-web.nhle.com/v1/player/{pid}/game-log/{s}/2")
            for g in d.get("gameLog", []):
                g["season"] = s
                games.append(g)
        except Exception as e:
            games.append({"error": str(e), "season": s})
    out["players"][str(pid)] = games
st = get("https://api-web.nhle.com/v1/standings/now")
for t in st["standings"]:
    out["standings"].append({k: t.get(k) for k in ["teamAbbrev","gamesPlayed","goalFor","goalAgainst","wins","losses","otLosses","points","homeGamesPlayed","homeGoalsFor","homeGoalsAgainst","roadGamesPlayed","roadGoalsFor","roadGoalsAgainst"]})
json.dump(out, open("data/gamelogs.json","w"), indent=1)
