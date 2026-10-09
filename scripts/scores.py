"""One-off: all final scores Sep 29 to today, plus fresh standings."""
import json, urllib.request, datetime
get=lambda u: json.load(urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"slapshot"}),timeout=30))
d=datetime.date(2026,9,29); end=datetime.date.fromisoformat(json.load(open("data/scores-request.json"))["to"]); out=[]
while d<=end:
    for g in get(f"https://api-web.nhle.com/v1/score/{d}").get("games",[]):
        if g.get("gameType")==2: out.append({"d":str(d),"a":g["awayTeam"]["abbrev"],"as":g["awayTeam"].get("score"),"h":g["homeTeam"]["abbrev"],"hs":g["homeTeam"].get("score"),"state":g.get("gameState"),"last":(g.get("gameOutcome") or {}).get("lastPeriodType")})
    d+=datetime.timedelta(days=1)
s=get("https://api-web.nhle.com/v1/standings/now")["standings"]
st={t["teamAbbrev"]["default"]:{"gp":t["gamesPlayed"],"w":t["wins"],"l":t["losses"],"otl":t["otLosses"],"pts":t["points"],"gf":t["goalFor"],"ga":t["goalAgainst"],"rw":t.get("regulationWins")} for t in s}
json.dump({"asof":datetime.datetime.utcnow().isoformat(),"games":out,"standings":st},open("data/scores.json","w"),indent=1); print(len(out))
