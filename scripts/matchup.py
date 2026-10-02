"""One-off: matchup breakdown data (top scorers, last season head-to-head) for two teams."""
import json, urllib.request
get=lambda u: json.load(urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"slapshot"}),timeout=30))
req=json.load(open("data/matchup-request.json")); A,H=req["a"],req["h"]
rows=get("https://api.nhle.com/stats/rest/en/skater/summary?isAggregate=true&isGame=false&limit=-1&cayenneExp=seasonId=20252026%20and%20gameTypeId=2")["data"]
by={r["playerId"]:r for r in rows}
out={"top":{},"h2h":[]}
for t in (A,H):
    ro=get(f"https://api-web.nhle.com/v1/roster/{t}/current")
    pl=[by[p["id"]] for k in ("forwards","defensemen") for p in ro.get(k,[]) if p["id"] in by]
    pl.sort(key=lambda r:(-r["points"],-r["goals"]))
    out["top"][t]=[{"name":r["skaterFullName"],"gp":r["gamesPlayed"],"g":r["goals"],"a":r["assists"],"p":r["points"],"pm":r["plusMinus"]} for r in pl[:5]]
for g in get(f"https://api-web.nhle.com/v1/club-schedule-season/{H}/20252026")["games"]:
    if g.get("gameType")==2 and A in (g["awayTeam"]["abbrev"],g["homeTeam"]["abbrev"]):
        out["h2h"].append({"date":g["gameDate"],"away":g["awayTeam"]["abbrev"],"as":g["awayTeam"].get("score"),"home":g["homeTeam"]["abbrev"],"hs":g["homeTeam"].get("score"),"last":(g.get("gameOutcome") or {}).get("lastPeriodType")})
json.dump(out,open("data/matchup.json","w"),indent=1); print(json.dumps(out))
