"""Slapshot Media daily site update. Runs on GitHub Actions.

morning (before noon ET): log yesterday's results, load the next game day, refresh lines
evening:                   refresh lines only

Writes data.json. The site (index.html) reads it. Never changes the formula.
"""
import json, os, sys, unicodedata, urllib.request
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data.json")
PICKS = os.path.join(ROOT, "data", "picks.json")
ODDS_KEY = os.environ.get("ODDS_API_KEY", "")
BOOKS = {"betmgm": "V", "fanduel": "E", "draftkings": "B"}

NICK = {"ducks": "ANA", "bruins": "BOS", "sabres": "BUF", "flames": "CGY", "hurricanes": "CAR", "blackhawks": "CHI",
        "avalanche": "COL", "blue jackets": "CBJ", "stars": "DAL", "red wings": "DET", "oilers": "EDM", "panthers": "FLA",
        "kings": "LAK", "wild": "MIN", "canadiens": "MTL", "predators": "NSH", "devils": "NJD", "islanders": "NYI",
        "rangers": "NYR", "senators": "OTT", "flyers": "PHI", "penguins": "PIT", "sharks": "SJS", "kraken": "SEA",
        "blues": "STL", "lightning": "TBL", "maple leafs": "TOR", "mammoth": "UTA", "utah": "UTA", "canucks": "VAN",
        "golden knights": "VGK", "capitals": "WSH", "jets": "WPG"}


def abbr(name):
    n = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().lower()
    for k in sorted(NICK, key=len, reverse=True):  # "golden knights" before "knights", "maple leafs" etc.
        if k in n:
            return NICK[k]
    return None


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "slapshot-media-site/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def fmt_time(utc):
    t = datetime.fromisoformat(utc.replace("Z", "+00:00")).astimezone(ET)
    return t.strftime("%-I:%M %p")


def label(day, n, opening=False):
    d = datetime.strptime(day, "%Y-%m-%d")
    s = d.strftime("%a %b ") + str(d.day)
    return f"{s}{' · Opening night' if opening else ''} · {n} game{'s' if n != 1 else ''} · times ET"


# ---------- model (only used after the saved October picks run out) ----------
def model_games(day):
    """Formula from the playbook. November: overall GF/GP, GA/GP. December on: home/road splits."""
    sched = [g for g in get(f"https://api-web.nhle.com/v1/score/{day}").get("games", [])
             if g.get("gameType", 2) == 2]
    if not sched:
        return []
    st = {}
    for t in get(f"https://api-web.nhle.com/v1/standings/{day}")["standings"]:
        a = t["teamAbbrev"]["default"] if isinstance(t["teamAbbrev"], dict) else t["teamAbbrev"]
        st[a] = t
    split = datetime.strptime(day, "%Y-%m-%d").month not in (11,)
    out = []
    for g in sched:
        a, h = g["awayTeam"]["abbrev"], g["homeTeam"]["abbrev"]
        A, H = st[a], st[h]
        if split:
            a_gf = A["roadGoalsFor"] / max(A["roadGamesPlayed"], 1); a_ga = A["roadGoalsAgainst"] / max(A["roadGamesPlayed"], 1)
            h_gf = H["homeGoalsFor"] / max(H["homeGamesPlayed"], 1); h_ga = H["homeGoalsAgainst"] / max(H["homeGamesPlayed"], 1)
        else:
            a_gf = A["goalFor"] / max(A["gamesPlayed"], 1); a_ga = A["goalAgainst"] / max(A["gamesPlayed"], 1)
            h_gf = H["goalFor"] / max(H["gamesPlayed"], 1); h_ga = H["goalAgainst"] / max(H["gamesPlayed"], 1)
        ag = (a_gf + h_ga) / 2
        hg = (h_gf + a_ga) / 2
        ap = round(ag / (ag + hg) * 100, 1)
        out.append({"t": fmt_time(g["startTimeUTC"]), "a": a, "h": h, "ag": round(ag, 2), "hg": round(hg, 2),
                    "ap": ap, "hp": round(100 - ap, 1)})
    return out


def games_for(day, picks):
    if day in picks:
        return [dict(g) for g in picks[day]]
    if day > max(picks):
        return model_games(day)
    return []


def next_game_day(today, picks):
    for i in range(0, 14):
        d = (today + timedelta(days=i)).isoformat()
        if games_for(d, picks):
            return d
    return None


# ---------- results ----------
def log_results(data, day):
    shown = {(g["a"], g["h"]): g for g in data["games"]} if data.get("gameday") == day else {}
    if not shown:
        return 0
    done = {(r["d"], r["a"], r["h"]) for r in data["R"]}
    added = 0
    for g in get(f"https://api-web.nhle.com/v1/score/{day}").get("games", []):
        a, h = g["awayTeam"]["abbrev"], g["homeTeam"]["abbrev"]
        if (a, h) not in shown or (day, a, h) in done or g.get("gameState") not in ("OFF", "FINAL"):
            continue
        s = shown[(a, h)]
        sa, sh = g["awayTeam"]["score"], g["homeTeam"]["score"]
        per = (g.get("gameOutcome") or {}).get("lastPeriodType", "REG")
        fav = lambda k: (s.get("b", {}).get(k) or [None])[0]
        rec = {"d": day, "a": a, "h": h,
               "s": None if s["ap"] == s["hp"] else (s["h"] if s["hp"] > s["ap"] else s["a"]),
               "w": a if sa > sh else h,
               "f": f"{a} {sa} - {h} {sh}" + ("" if per == "REG" else f" {per}")}
        for k in ("V", "E", "B"):
            f = fav(k)
            rec[k] = None if f in (None, "Pick'em") else f
        data["R"].append(rec)
        added += 1
    return added


# ---------- lines ----------
def refresh_lines(data):
    if not ODDS_KEY:
        raise RuntimeError("ODDS_API_KEY secret is missing")
    odds = get("https://api.the-odds-api.com/v4/sports/icehockey_nhl/odds/?apiKey=" + ODDS_KEY +
               "&bookmakers=betmgm,fanduel,draftkings&markets=h2h&oddsFormat=american")
    day = data["gameday"]
    idx = {(g["a"], g["h"]): g for g in data["games"]}
    hit = 0
    for ev in odds:
        a, h = abbr(ev["away_team"]), abbr(ev["home_team"])
        if (a, h) not in idx:
            continue
        et_day = datetime.fromisoformat(ev["commence_time"].replace("Z", "+00:00")).astimezone(ET).date().isoformat()
        if et_day != day:
            continue
        g = idx[(a, h)]
        b = dict(g.get("b") or {})
        for bk in ev.get("bookmakers", []):
            k = BOOKS.get(bk["key"])
            if not k:
                continue
            m = next((m for m in bk.get("markets", []) if m["key"] == "h2h"), None)
            if not m:
                continue
            pr = {abbr(o["name"]): o["price"] for o in m["outcomes"]}
            if a not in pr or h not in pr:
                continue
            fmt = lambda p: f"+{p}" if p > 0 else str(p)
            if pr[a] == pr[h]:
                b[k] = ["Pick'em", fmt(pr[a])]
            else:
                t = a if pr[a] < pr[h] else h
                b[k] = [t, fmt(pr[t])]
        g["b"] = b
        hit += 1
    return hit


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ("morning" if datetime.now(ET).hour < 12 else "evening")
    data = json.load(open(DATA))
    picks = json.load(open(PICKS))
    before = json.dumps(data, sort_keys=True)
    today = datetime.now(ET).date()
    notes = []

    if mode == "morning":
        y = (today - timedelta(days=1)).isoformat()
        n = log_results(data, y)
        notes.append(f"logged {n} result(s) for {y}")
        gd = next_game_day(today, picks)
        if gd and gd != data.get("gameday"):
            games = games_for(gd, picks)
            for g in games:
                g["b"] = {}
            data["gameday"] = gd
            data["games"] = games
            data["label"] = label(gd, len(games), opening=(gd == "2026-09-29"))
            notes.append(f"loaded {len(games)} game(s) for {gd}")

    try:
        hit = refresh_lines(data)
        notes.append(f"lines found for {hit}/{len(data['games'])} game(s)")
    except Exception as e:  # keep going; the site still shows the games
        notes.append(f"LINES FAILED: {e}")

    changed = json.dumps(data, sort_keys=True) != before
    if changed:
        data["updated"] = datetime.now(ET).strftime("%Y-%m-%d %H:%M ET")
        with open(DATA, "w") as f:
            json.dump(data, f, indent=1)
    print(("CHANGED: " if changed else "NO CHANGE: ") + "; ".join(notes))
    if any("FAILED" in n for n in notes):
        sys.exit(2)


if __name__ == "__main__":
    main()
