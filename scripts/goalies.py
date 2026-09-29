"""One-off: 2025-26 regular-season GAA for each team's projected starter (list in data/goalies-request.json)."""
import json, urllib.request
get=lambda u: json.load(urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"slapshot"}),timeout=30))
req=json.load(open("data/goalies-request.json"))
out={}
for team,name in req["starters"].items():
    ro=get(f"https://api-web.nhle.com/v1/roster/{team}/current")
    g=[p for p in ro.get("goalies",[]) if f'{p["firstName"]["default"]} {p["lastName"]["default"]}'.lower()==name.lower()]
    if not g:
        g=[p for p in ro.get("goalies",[]) if p["lastName"]["default"].lower()==name.split()[-1].lower()]
    if not g: out[team]={"name":name,"error":"not on roster"}; continue
    pid=g[0]["id"]; land=get(f"https://api-web.nhle.com/v1/player/{pid}/landing")
    rows=[s for s in land.get("seasonTotals",[]) if s.get("season")==int(req["season"]) and s.get("gameTypeId")==2 and s.get("leagueAbbrev")=="NHL"]
    gp=sum(r.get("gamesPlayed",0) for r in rows)
    ga=sum(r.get("goalsAgainst",0) for r in rows)
    gaa=(sum(r.get("goalsAgainstAvg",0)*r.get("gamesPlayed",0) for r in rows)/gp) if gp else None
    ct=land.get("careerTotals",{}).get("regularSeason",{})
    out[team]={"name":name,"id":pid,"career_gp":ct.get("gamesPlayed"),"career_gaa":ct.get("goalsAgainstAvg"),"gp":gp,"gaa":round(gaa,4) if gaa else None,
               "teams":[r.get("teamName",{}).get("default") for r in rows]}
json.dump(out,open("data/goalies-2025-26.json","w"),indent=1)
print(json.dumps(out)[:3000])
