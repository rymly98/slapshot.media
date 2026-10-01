"""One-off: 2025-26 team stats, top goal scorers (current rosters), and 2026-27 schedule-based strength of schedule."""
import json, urllib.request
get=lambda u: json.load(urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"slapshot"}),timeout=30))
req=json.load(open("data/sos-request.json"))
teams=get("https://api.nhle.com/stats/rest/en/team/summary?isAggregate=false&isGame=false&limit=-1&cayenneExp=seasonId=20252026%20and%20gameTypeId=2")["data"]
ab={t["id"]:t["triCode"] for t in get("https://api.nhle.com/stats/rest/en/team")["data"]}
st={}
for t in teams:
    a=ab.get(t["teamId"])
    st[a]={k:t.get(k) for k in ("gamesPlayed","wins","losses","otLosses","points","pointPct","goalsForPerGame","goalsAgainstPerGame","powerPlayPct","penaltyKillPct")}
sk=get("https://api.nhle.com/stats/rest/en/skater/summary?isAggregate=true&isGame=false&limit=-1&cayenneExp=seasonId=20252026%20and%20gameTypeId=2")["data"]
by={r["playerId"]:r for r in sk}
top={}
for t in req["scorers"]:
    ro=get(f"https://api-web.nhle.com/v1/roster/{t}/current")
    pl=[by[p["id"]] for k in ("forwards","defensemen") for p in ro.get(k,[]) if p["id"] in by]
    r=max(pl,key=lambda r:(r["goals"],r["points"]))
    top[t]={"name":r["skaterFullName"],"goals":r["goals"]}
sos={}
for t in sorted(st):
    sch=[g for g in get(f"https://api-web.nhle.com/v1/club-schedule-season/{t}/20262027")["games"] if g.get("gameType")==2]
    opp=[g["awayTeam"]["abbrev"] if g["homeTeam"]["abbrev"]==t else g["homeTeam"]["abbrev"] for g in sch]
    s=sum(st[o]["pointPct"] for o in opp)
    sos[t]={"games":len(opp),"sum":round(s,4),"avg":round(s/len(opp),4)}
json.dump({"stats":st,"top":top,"sos":sos},open("data/sos-2026-27.json","w"),indent=1)
print(json.dumps(sos))
