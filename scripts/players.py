"""One-off: career regular-season totals + bio for given player ids."""
import json, urllib.request
get=lambda u: json.load(urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"slapshot"}),timeout=30))
out={}
for pid in json.load(open("data/players-request.json"))["ids"]:
    d=get(f"https://api-web.nhle.com/v1/player/{pid}/landing")
    out[str(pid)]={"name":d["firstName"]["default"]+" "+d["lastName"]["default"],"birthDate":d.get("birthDate"),"team":d.get("currentTeamAbbrev"),
      "position":d.get("position"),"career":d.get("careerTotals",{}).get("regularSeason"),
      "seasons":[s for s in d.get("seasonTotals",[]) if s.get("leagueAbbrev")=="NHL" and s.get("gameTypeId")==2]}
json.dump(out,open("data/players.json","w"),indent=1)
print({k:(v["name"],v["career"]) for k,v in out.items()})
