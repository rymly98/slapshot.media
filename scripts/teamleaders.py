"""One-off: each requested team's top scorers this season, with last season's pace for comparison."""
import json, urllib.request
get=lambda u: json.load(urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"slapshot"}),timeout=30))
req=json.load(open("data/teamleaders-request.json"))
q=lambda sid: get("https://api.nhle.com/stats/rest/en/skater/summary?isAggregate=true&isGame=false&limit=-1"
                  f"&cayenneExp=seasonId={sid}%20and%20gameTypeId=2")["data"]
now={r["playerId"]:r for r in q(req.get("season","20262027"))}
last={r["playerId"]:r for r in q(req.get("last","20252026"))}
out={}
for t in req["teams"]:
    ro=get(f"https://api-web.nhle.com/v1/roster/{t}/current")
    ids=[p["id"] for k in ("forwards","defensemen") for p in ro.get(k,[])]
    pl=sorted([now[i] for i in ids if i in now],key=lambda r:(-r["points"],-r["goals"]))[:3]
    out[t]=[{"id":r["playerId"],"name":r["skaterFullName"],"gp":r["gamesPlayed"],"g":r["goals"],"a":r["assists"],"p":r["points"],
             "last":({"gp":last[r["playerId"]]["gamesPlayed"],"g":last[r["playerId"]]["goals"],"a":last[r["playerId"]]["assists"],"p":last[r["playerId"]]["points"]} if r["playerId"] in last else None)} for r in pl]
# league scoring top 10 for superlative checks
out["_league"]=[{"name":r["skaterFullName"],"team":r.get("teamAbbrevs"),"gp":r["gamesPlayed"],"g":r["goals"],"p":r["points"]} for r in sorted(now.values(),key=lambda r:(-r["points"],-r["goals"]))[:10]]
json.dump(out,open("data/teamleaders.json","w"),indent=1); print({k:[(p["name"],p["p"]) for p in v][:2] for k,v in out.items() if k!="_league"})
