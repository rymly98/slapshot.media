"""One-off: home/road GF/GA per game — last season since Jan 1 (October model inputs) vs this season so far."""
import json, urllib.request
get=lambda u: json.load(urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"slapshot"}),timeout=30))
teams=sorted({t["teamAbbrev"]["default"] for t in get("https://api-web.nhle.com/v1/standings/2026-10-17")["standings"]})
def split(t,season,lo,hi):
    S={"hgp":0,"hgf":0,"hga":0,"rgp":0,"rgf":0,"rga":0}
    for g in get(f"https://api-web.nhle.com/v1/club-schedule-season/{t}/{season}")["games"]:
        if g.get("gameType")!=2 or g.get("gameState") not in ("OFF","FINAL") or not (lo<=g["gameDate"]<=hi): continue
        home=g["homeTeam"]["abbrev"]==t; me=g["homeTeam"] if home else g["awayTeam"]; op=g["awayTeam"] if home else g["homeTeam"]
        k="h" if home else "r"; S[k+"gp"]+=1; S[k+"gf"]+=me["score"]; S[k+"ga"]+=op["score"]
    return S
out={t:{"last":split(t,"20252026","2026-01-01","2026-06-30"),"now":split(t,"20262027","2026-09-01","2026-10-17")} for t in teams}
json.dump(out,open("data/splits.json","w"),indent=1); print(len(out))
