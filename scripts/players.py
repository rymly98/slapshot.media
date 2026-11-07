"""One-off: career regular-season totals + bio for given player ids."""
import json, urllib.request, urllib.parse
get=lambda u: json.load(urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"slapshot"}),timeout=30))
out={}
req=json.load(open("data/players-request.json"))
ids=list(req.get("ids",[]))
if req.get("names"):
    rows=get("https://api.nhle.com/stats/rest/en/skater/summary?isAggregate=true&isGame=false&limit=-1&cayenneExp=seasonId=20252026%20and%20gameTypeId=2")["data"]
    for n in req["names"]:
        ids+= [r["playerId"] for r in rows if r["skaterFullName"].lower()==n.lower()][:1]
for team,name in req.get("roster",[]):
    ro=get(f"https://api-web.nhle.com/v1/roster/{team}/current")
    ids+=[p["id"] for k in ("forwards","defensemen","goalies") for p in ro.get(k,[]) if f'{p["firstName"]["default"]} {p["lastName"]["default"]}'.lower()==name.lower()][:1]
for n in req.get("search",[]):
    hits=get("https://search.d3.nhle.com/api/v1/search/player?culture=en-us&limit=20&q="+urllib.parse.quote(n)+"&active=false")
    ids+=[int(h["playerId"]) for h in hits if h.get("name","").lower()==n.lower()][:1]
for pid in ids:
    d=get(f"https://api-web.nhle.com/v1/player/{pid}/landing")
    out[str(pid)]={"name":d["firstName"]["default"]+" "+d["lastName"]["default"],"birthDate":d.get("birthDate"),"team":d.get("currentTeamAbbrev"),
      "position":d.get("position"),"bio":{k:d.get(k) for k in ("birthCity","birthStateProvince","birthCountry","heightInInches","weightInPounds","headshot")},"career":d.get("careerTotals",{}).get("regularSeason"),
      "seasons":[s for s in d.get("seasonTotals",[]) if s.get("leagueAbbrev")=="NHL" and s.get("gameTypeId") in (2,3)]}
json.dump(out,open("data/players.json","w"),indent=1)
print({k:(v["name"],v["career"]) for k,v in out.items()})
