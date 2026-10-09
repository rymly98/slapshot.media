"""One-off: current standings."""
import json, urllib.request, datetime
get=lambda u: json.load(urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"slapshot"}),timeout=30))
s=get("https://api-web.nhle.com/v1/standings/now")["standings"]
out={"asof":datetime.datetime.utcnow().isoformat(),"teams":{t["teamAbbrev"]["default"]:{"gp":t["gamesPlayed"],"w":t["wins"],"l":t["losses"],"otl":t["otLosses"],"pts":t["points"],"gf":t["goalFor"],"ga":t["goalAgainst"],"rw":t.get("regulationWins"),"date":t.get("date")} for t in s}}
json.dump(out,open("data/standings-now.json","w"),indent=1); print("ok")
