"""One-off health check: runs the real update on a scratch copy and tests the November/December model path. Never touches data.json."""
import json, os, sys, shutil, tempfile, importlib.util
from datetime import datetime, timedelta
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec=importlib.util.spec_from_file_location("U",os.path.join(ROOT,"scripts","update.py")); U=importlib.util.module_from_spec(spec); spec.loader.exec_module(U)
out={"checks":[]}
def check(name,fn):
    try: r=fn(); out["checks"].append([name,"OK",r])
    except Exception as e: out["checks"].append([name,"FAIL",repr(e)])
today=datetime.now(U.ET).date()
def find_day():
    for i in range(0,10):
        d=(today+timedelta(days=i)).isoformat()
        if [g for g in U.get(f"https://api-web.nhle.com/v1/score/{d}").get("games",[]) if g.get("gameType")==2]: return d
day=find_day()
def model(split):
    g=U.model_games(day,split=split); assert g, "no games"
    for x in g: assert abs(x["ap"]+x["hp"]-100)<0.2 and 0<x["ap"]<100
    return [f'{x["a"]}@{x["h"]} {x["ap"]}-{x["hp"]}' for x in g[:4]]
check(f"Nov model (season overall) {day}",lambda: model(False))
check(f"Dec model (home/road) {day}",lambda: model(True))
check("Future day standings fallback",lambda: len(U.model_games((today+timedelta(days=3)).isoformat())))
tmp=tempfile.mkdtemp(); shutil.copy(U.DATA,os.path.join(tmp,"data.json")); U.DATA=os.path.join(tmp,"data.json")
def full():
    try: U.main()
    except SystemExit as e:
        if e.code not in (0,None,2): raise
    d=json.load(open(U.DATA))
    need={"games":lambda v:isinstance(v,list),"R":lambda v:len(v)>0,"S":lambda v:len(v)>=32,"ST":lambda v:len(v["t"])>=32 and len(v["t"][0])>=11,"RG":lambda v:len(v["g"])>0}
    bad=[k for k,f in need.items() if k not in d or not f(d[k])]
    assert not bad, f"missing/bad: {bad}"
    return {"gameday":d.get("gameday"),"games":len(d["games"]),"race_thru":d["RG"]["thru"],"standings_teams":len(d["ST"]["t"])}
sys.argv=["update.py","morning"]
check("Full morning update (scratch copy)",full)
out["ok"]=all(c[1]=="OK" for c in out["checks"]); out["ran"]=datetime.now(U.ET).strftime("%Y-%m-%d %H:%M ET")
json.dump(out,open(os.path.join(ROOT,"data","selftest.json"),"w"),indent=1); print(json.dumps(out,indent=1))
