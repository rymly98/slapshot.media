"""One-off: is the 100-row cap real, and do league-wide top lists change with the full list?"""
import json, urllib.request
get=lambda u: json.load(urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"slapshot"}),timeout=30))
B="https://api.nhle.com/stats/rest/en/skater/summary?isAggregate=true&isGame=false&cayenneExp=seasonId=20262027%20and%20gameTypeId=2"
cap=get(B+"&limit=-1")["data"]
full=[];s=0
while True:
    d=get(B+f"&start={s}&limit=100")["data"]
    full+=d
    if len(d)<100: break
    s+=100
srt=get(B+'&limit=100&sort=%5B%7B%22property%22:%22points%22,%22direction%22:%22DESC%22%7D%5D')["data"]
top=lambda rows:[(r["skaterFullName"],r["points"]) for r in sorted(rows,key=lambda r:(-r["points"],-r["goals"]))[:10]]
json.dump({"cap_rows":len(cap),"full_rows":len(full),"sorted_rows":len(srt),"top10_capped":top(cap),"top10_full":top(full),"top10_sorted":top(srt)},open("data/feedcheck.json","w"),indent=1)
