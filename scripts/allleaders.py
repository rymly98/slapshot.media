"""One-off: every team's goals, assists and points leaders this season (ties kept)."""
import json, urllib.request
get=lambda u: json.load(urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"slapshot"}),timeout=30))
sid=json.load(open("data/allleaders-request.json")).get("season","20262027")
rows=get("https://api.nhle.com/stats/rest/en/skater/summary?isAggregate=false&isGame=false&limit=-1"
         f"&cayenneExp=seasonId={sid}%20and%20gameTypeId=2")["data"]
by={}
for r in rows:
    t=r.get("teamAbbrevs")
    if t and "," not in t: by.setdefault(t,[]).append(r)
out={"asof":None,"teams":{}}
for t,pl in sorted(by.items()):
    d={}
    for k,key in (("g","goals"),("a","assists"),("p","points")):
        m=max(r[key] for r in pl)
        d[k]={"n":m,"who":[{"name":r["skaterFullName"],"gp":r["gamesPlayed"],"g":r["goals"],"a":r["assists"],"p":r["points"]} for r in pl if r[key]==m]}
    out["teams"][t]=d
lg=sorted(rows,key=lambda r:-r["points"])[:5]
out["league"]={k:sorted(((r["skaterFullName"],r["teamAbbrevs"],r[key]) for r in rows),key=lambda x:-x[2])[:25] for k,key in (("g","goals"),("a","assists"),("p","points"))}
import datetime; out["asof"]=datetime.datetime.utcnow().isoformat()
json.dump(out,open("data/allleaders.json","w"),indent=1); print(len(out["teams"]))
