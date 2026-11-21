"""One-off: why are some team leaders wrong? Compare skater/summary vs club-stats."""
import json, urllib.request
get=lambda u: json.load(urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"slapshot"}),timeout=30))
rows=get("https://api.nhle.com/stats/rest/en/skater/summary?isAggregate=true&isGame=false&limit=-1&cayenneExp=seasonId=20262027%20and%20gameTypeId=2")
out={"summary_rows":len(rows["data"]),"summary_total":rows.get("total"),"teams":{}}
by={r["playerId"]:r for r in rows["data"]}
for t in ["OTT","MIN","CBJ","VGK","NYI","PIT"]:
    ro=get(f"https://api-web.nhle.com/v1/roster/{t}/current")
    ids=[p["id"] for k in ("forwards","defensemen") for p in ro.get(k,[])]
    cs=get(f"https://api-web.nhle.com/v1/club-stats/{t}/now")
    sk=cs.get("skaters",[])
    out["teams"][t]={"roster":len(ids),"found_in_summary":sum(i in by for i in ids),
      "club_keys":list(sk[0].keys()) if sk else None,
      "club_top_goals":[(s["firstName"]["default"]+" "+s["lastName"]["default"],s["playerId"],s["goals"],s["assists"],s["points"],s["playerId"] in ids) for s in sorted(sk,key=lambda s:-s["goals"])[:4]]}
json.dump(out,open("data/leaderdiag.json","w"),indent=1)
