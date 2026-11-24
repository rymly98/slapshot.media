"""One-off: save PuckPedia's NHL team cap table (projected cap hit per team)."""
import urllib.request, re, json, html
UA={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15","Accept":"text/html"}
out={}
for u in ["https://puckpedia.com/teams","https://puckpedia.com/e/teams"]:
    try:
        t=urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=40).read().decode("utf-8","replace")
        open("data/puckpedia-raw.html","w").write(t)
        txt=html.unescape(re.sub(r"<[^>]+>"," ",t));txt=re.sub(r"\s+"," ",txt)
        out={"url":u,"len":len(t),"text":txt[:60000]}
        break
    except Exception as e:
        out[u]=str(e)
json.dump(out,open("data/puckpedia.json","w"),indent=1)
