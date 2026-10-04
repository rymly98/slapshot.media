"""One-off: top skaters of the 2026-27 season so far, with bio."""
import json, urllib.request
get=lambda u: json.load(urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"slapshot"}),timeout=30))
rows=get("https://api.nhle.com/stats/rest/en/skater/summary?isAggregate=false&isGame=false&limit=-1&cayenneExp=seasonId=20262027%20and%20gameTypeId=2")["data"]
rows.sort(key=lambda r:(-r["points"],-r["goals"],-r["plusMinus"]))
out=[]
for r in rows[:12]:
    d=get(f"https://api-web.nhle.com/v1/player/{r['playerId']}/landing")
    out.append({"id":r["playerId"],"name":r["skaterFullName"],"team":d.get("currentTeamAbbrev") or r.get("teamAbbrevs"),"gp":r["gamesPlayed"],"g":r["goals"],"a":r["assists"],"p":r["points"],"pm":r["plusMinus"],
      "ppp":r.get("ppPoints"),"gwg":r.get("gameWinningGoals"),"shots":r.get("shots"),
      "birthCity":(d.get("birthCity") or {}).get("default"),"birthProv":(d.get("birthStateProvince") or {}).get("default"),"birthCountry":d.get("birthCountry"),
      "height":d.get("heightInInches"),"weight":d.get("weightInPounds"),"birthDate":d.get("birthDate"),"pos":d.get("position")})
json.dump(out,open("data/week-stars.json","w"),indent=1); print(json.dumps(out)[:3000])
