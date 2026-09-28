"""One-off: for chosen teams, games Jan 1 - end of 2025-26 regular season split into 3 chronological stretches.
Drop the worst stretch (by goal diff), count the best stretch twice, recompute home/road GF/GP and GA/GP."""
import json, urllib.request
get=lambda u: json.load(urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"slapshot"}),timeout=30))
req=json.load(open("data/thirds-request.json"))
def split(games):
    s={"H":[0,0,0],"R":[0,0,0]}
    for g in games:
        k="H" if g["home"] else "R"; s[k][0]+=g["gf"]; s[k][1]+=g["ga"]; s[k][2]+=1
    return {k:{"gp":v[2],"gf_gp":round(v[0]/v[2],4) if v[2] else None,"ga_gp":round(v[1]/v[2],4) if v[2] else None} for k,v in s.items()}
out={}
for t in req["teams"]:
    sch=get(f"https://api-web.nhle.com/v1/club-schedule-season/{t}/{req['season']}")["games"]
    gs=[]
    for g in sch:
        if g.get("gameType")!=2 or g["gameDate"]<req["from"] or g.get("gameState") not in ("OFF","FINAL"): continue
        home=g["homeTeam"]["abbrev"]==t
        me,op=(g["homeTeam"],g["awayTeam"]) if home else (g["awayTeam"],g["homeTeam"])
        gs.append({"date":g["gameDate"],"home":home,"gf":me["score"],"ga":op["score"]})
    gs.sort(key=lambda g:g["date"]); n=len(gs); a,b=n//3,2*n//3
    parts=[gs[:a],gs[a:b],gs[b:]]
    info=[{"from":p[0]["date"],"to":p[-1]["date"],"gp":len(p),"gf":sum(x["gf"] for x in p),"ga":sum(x["ga"] for x in p)} for p in parts]
    diff=[i["gf"]-i["ga"] for i in info]; worst=diff.index(min(diff)); best=diff.index(max(diff))
    adj=[g for i,p in enumerate(parts) if i!=worst for g in p]+parts[best]
    out[t]={"games":n,"stretches":info,"worst":worst,"best":best,"original":split(gs),"adjusted":split(adj)}
json.dump(out,open("data/thirds-2025-26.json","w"),indent=1)
print(json.dumps(out)[:4000])
