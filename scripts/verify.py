"""One-off: re-check post numbers against NHL.com."""
import json, urllib.request
get=lambda u: json.load(urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"slapshot"}),timeout=30))
out={"sched":{},"stars":[],"scores":{}}
teams=sorted({t["teamAbbrev"]["default"] for t in get("https://api-web.nhle.com/v1/standings/2026-10-03")["standings"]})
for t in teams:
    gs=get(f"https://api-web.nhle.com/v1/club-schedule-season/{t}/20262027")["games"]
    out["sched"][t]=[[g["gameDate"],g["awayTeam"]["abbrev"],g["homeTeam"]["abbrev"],g.get("startTimeUTC")] for g in gs if g.get("gameType")==2 and "2026-09-29"<=g["gameDate"]<="2026-10-11"]
rows=get("https://api.nhle.com/stats/rest/en/skater/summary?isAggregate=true&isGame=true&limit=-1&cayenneExp=gameDate%3E=%222026-09-29%22%20and%20gameDate%3C=%222026-10-03%22%20and%20gameTypeId=2")["data"]
rows.sort(key=lambda r:(-r["points"],-r["goals"]))
out["stars"]=[{k:r.get(k) for k in ("skaterFullName","gamesPlayed","goals","assists","points","plusMinus","shots","ppPoints","gameWinningGoals")} for r in rows[:15]]
for d in ["2026-09-29","2026-09-30","2026-10-01","2026-10-02","2026-10-03"]:
    out["scores"][d]=[[g["awayTeam"]["abbrev"],g["awayTeam"].get("score"),g["homeTeam"]["abbrev"],g["homeTeam"].get("score"),(g.get("gameOutcome") or {}).get("lastPeriodType")] for g in get(f"https://api-web.nhle.com/v1/score/{d}")["games"]]
json.dump(out,open("data/verify.json","w"),indent=1); print("ok")
