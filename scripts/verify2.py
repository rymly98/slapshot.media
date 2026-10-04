"""One-off: 2025-26 final standings from a second NHL endpoint."""
import json, urllib.request
get=lambda u: json.load(urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"slapshot"}),timeout=30))
out={}
for d in ["2026-04-20","2026-04-25","2026-05-01"]:
    try:
        st=get(f"https://api-web.nhle.com/v1/standings/{d}")["standings"]
        out={t["teamAbbrev"]["default"]:{"gp":t["gamesPlayed"],"pts":t["points"],"pct":t["pointPctg"]} for t in st}
        if all(v["gp"]==82 for v in out.values()): out["_date"]=d; break
    except Exception as e: out["_err"]=str(e)
json.dump(out,open("data/verify2.json","w"),indent=1); print("ok")
