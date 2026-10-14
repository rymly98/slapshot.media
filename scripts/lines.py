"""One-off: forward lines at 5v5 built from NHL.com shift charts + play-by-play."""
import json, urllib.request, datetime, collections, time
def get(u):
    for i in range(3):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"slapshot"}),timeout=40))
        except Exception as e: err=e; time.sleep(2)
    raise err
req=json.load(open("data/lines-request.json"))
d=datetime.date.fromisoformat(req.get("from","2026-09-29")); end=datetime.date.fromisoformat(req["to"])
games=[]
while d<=end:
    for g in get(f"https://api-web.nhle.com/v1/score/{d}").get("games",[]):
        if g.get("gameType")==2 and g.get("gameState") in ("OFF","FINAL"): games.append(g["id"])
    d+=datetime.timedelta(days=1)
sec=lambda p,mmss:(p-1)*1200+int(mmss.split(":")[0])*60+int(mmss.split(":")[1])
TOI=collections.Counter(); GF=collections.Counter(); GA=collections.Counter(); GP=collections.defaultdict(set)
NAME={}; TEAMOF={}; skipped=[]
for gid in games:
    try:
        box=get(f"https://api-web.nhle.com/v1/gamecenter/{gid}/boxscore")
        pbp=get(f"https://api-web.nhle.com/v1/gamecenter/{gid}/play-by-play")
        sh=get(f"https://api.nhle.com/stats/rest/en/shiftcharts?cayenneExp=gameId={gid}")["data"]
    except Exception as e: skipped.append([gid,str(e)]); continue
    pos={}; side={}
    for s,key in (("away","awayTeam"),("home","homeTeam")):
        ab=box[key]["abbrev"]; side[s]=ab
        for grp,tag in (("forwards","F"),("defense","D"),("goalies","G")):
            for p in box["playerByGameStats"][key][grp]:
                pos[p["playerId"]]=tag; NAME[p["playerId"]]=p["name"]["default"]; TEAMOF[p["playerId"]]=ab
    on=collections.defaultdict(set)   # second -> set(playerId)
    for s in sh:
        if s.get("typeCode")!=517 or not s.get("startTime") or not s.get("endTime") or s["period"]>3: continue
        a=sec(s["period"],s["startTime"]); b=sec(s["period"],s["endTime"])
        for t in range(a,b): on[t].add(s["playerId"])
    def state(t):
        st={}
        for ab in side.values():
            ps=[p for p in on.get(t,()) if TEAMOF.get(p)==ab]
            st[ab]={"F":tuple(sorted(p for p in ps if pos.get(p)=="F")),"S":sum(pos.get(p) in("F","D") for p in ps),"G":sum(pos.get(p)=="G" for p in ps)}
        return st
    for t in range(0,3600):
        st=state(t)
        if all(v["S"]==5 and v["G"]==1 for v in st.values()):
            for ab,v in st.items():
                if len(v["F"])==3: TOI[(ab,v["F"])]+=1; GP[(ab,v["F"])].add(gid)
    for pl in pbp.get("plays",[]):
        if pl.get("typeDescKey")!="goal" or pl["periodDescriptor"]["number"]>3 or pl.get("situationCode")!="1551": continue
        t=sec(pl["periodDescriptor"]["number"],pl["timeInPeriod"]); st=state(max(0,t-1))
        tid=pl["details"]["eventOwnerTeamId"]; scorer=box["awayTeam"]["abbrev"] if box["awayTeam"]["id"]==tid else box["homeTeam"]["abbrev"]
        for ab,v in st.items():
            if len(v["F"])==3: (GF if ab==scorer else GA)[(ab,v["F"])]+=1
lines=[{"team":k[0],"ids":list(k[1]),"names":[NAME[i] for i in k[1]],"toi":round(v/60,1),"gf":GF[k],"ga":GA[k],"gp":len(GP[k])} for k,v in TOI.items() if v>=300]
lines.sort(key=lambda x:(-(x["gf"]-x["ga"]),-x["gf"],-x["toi"]))
json.dump({"asof":datetime.datetime.utcnow().isoformat(),"games":len(games),"skipped":skipped,"lines":lines},open("data/lines.json","w"),indent=1)
print(len(games),len(lines),skipped[:3])
