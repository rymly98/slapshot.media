"""One-off: top 2025-26 point scorers on the current rosters of the given teams."""
import json, urllib.request
get=lambda u: json.load(urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"slapshot"}),timeout=30))
req=json.load(open("data/stars-request.json"))
rows=get("https://api.nhle.com/stats/rest/en/skater/summary?isAggregate=true&isGame=false&limit=-1&cayenneExp=seasonId=20252026%20and%20gameTypeId=2")["data"]
by={r["playerId"]:r for r in rows}
out=[]
for t in req["teams"]:
    ro=get(f"https://api-web.nhle.com/v1/roster/{t}/current")
    for k in ("forwards","defensemen"):
        for p in ro.get(k,[]):
            r=by.get(p["id"])
            if r: out.append({"team":t,"id":p["id"],"name":r["skaterFullName"],"pos":r.get("positionCode"),"gp":r["gamesPlayed"],"g":r["goals"],"a":r["assists"],"p":r["points"],"pm":r["plusMinus"],"ppp":r.get("ppPoints")})
out.sort(key=lambda r:(-r["p"],-r["g"]))
json.dump(out[:40],open("data/stars.json","w"),indent=1)
print(out[:15])
