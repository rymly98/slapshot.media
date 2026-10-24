"""One-off: every remaining regular-season game this season."""
import json, urllib.request, time
def get(u):
    for i in range(3):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"slapshot"}),timeout=30))
        except Exception as e: err=e; time.sleep(2)
    raise err
req=json.load(open("data/schedule-request.json")); sid=req.get("season","20262027")
teams=[t["teamAbbrev"]["default"] for t in get("https://api-web.nhle.com/v1/standings/now")["standings"]]
games={}
for t in teams:
    for g in get(f"https://api-web.nhle.com/v1/club-schedule-season/{t}/{sid}").get("games",[]):
        if g.get("gameType")!=2: continue
        games[g["id"]]={"id":g["id"],"d":g["gameDate"],"a":g["awayTeam"]["abbrev"],"h":g["homeTeam"]["abbrev"],"state":g.get("gameState")}
out={"teams":len(teams),"games":sorted(games.values(),key=lambda x:(x["d"],x["id"]))}
json.dump(out,open("data/schedule-2026-27.json","w"),indent=1)
print(len(out["games"]),sum(1 for g in out["games"] if g["state"] in ("FUT","PRE")))
