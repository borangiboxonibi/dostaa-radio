"""Dostaa Radio — verify songs.txt against what each YouTube video ACTUALLY is.

Run after adding/editing songs, BEFORE rebuild.py:
    python3 audit.py            # checks new/changed songs (cached results reused)
    python3 audit.py --all      # re-checks every video (e.g. to catch deleted uploads)

For every song it fetches the video's real title + channel (YouTube oEmbed,
no API key) and checks:
  - the video exists and allows embedding          -> else DEAD / BLOCKED
  - the song title appears in the video title       -> else TITLE MISMATCH
  - the film appears in the video title             -> sets fv (film verified)
  - red flags: remix, karaoke, teaser, jukebox, Telugu/Tamil/Hindi/Bhojpuri/Tulu

Results go to verified.json. Where the video title is only in Kannada script
or abbreviates the film (e.g. "GGVV", "KGF"), a human can confirm it by adding
"manual_tv": true / "manual_fv": true (+ "note") to that id in verified.json.

Results go to verified.json. rebuild.py copies tv/fv into songs.json, and the
site's film quiz ONLY uses songs with fv=true, so a wrong film can never be
asked. Exit code 1 if anything is DEAD/BLOCKED/TITLE MISMATCH, so fix those
lines before pushing.
"""
import json, os, re, sys, time, difflib, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

CACHE = "verified.json"
RED = re.compile(r"remix|karaoke|teaser|trailer|jukebox|mashup|non ?stop|back to back|"
                 r"\btelugu\b|\btamil\b|\bhindi\b|bhojpuri|\btulu\b|\bmalayalam\b", re.I)

def norm(s):
    s = re.sub(r"[^a-z0-9 ]", " ", (s or "").lower())
    for a, b in [("aa","a"),("ee","i"),("oo","u"),("th","t"),("dh","d"),("bh","b"),("sh","s"),
                 ("kh","k"),("gh","g"),("ph","f"),("w","v"),("z","j"),("ii","i"),("uu","u"),("y","i")]:
        s = s.replace(a, b)
    s = re.sub(r"(.)\1", r"\1", s)
    return re.sub(r"\s+", "", s)

def score(needle, hay):
    n, h = norm(needle), norm(hay)
    if not n: return 0.0
    if n in h: return 1.0
    L, best = len(n), 0.0
    for i in range(0, max(1, len(h) - L + 1)):
        best = max(best, difflib.SequenceMatcher(None, n, h[i:i+L]).ratio())
    return best

def oembed(vid):
    u = "https://www.youtube.com/oembed?format=json&url=https://www.youtube.com/watch?v=" + vid
    for _ in range(3):
        try:
            with urllib.request.urlopen(u, timeout=20) as r:
                j = json.load(r)
                return {"status": "ok", "yt_title": j.get("title", ""), "channel": j.get("author_name", "")}
        except urllib.error.HTTPError as e:
            if e.code in (401, 403): return {"status": "blocked"}
            if e.code in (400, 404): return {"status": "dead"}
            time.sleep(2)
        except Exception:
            time.sleep(2)
    return {"status": "error"}

songs = []
for line in open("songs.txt", encoding="utf-8"):
    line = line.strip()
    if not line or line.startswith("#"): continue
    p = [x.strip() for x in line.split("|")]
    if len(p) >= 6: songs.append({"id": p[0], "title": p[1], "film": p[2]})

cache = json.load(open(CACHE, encoding="utf-8")) if os.path.exists(CACHE) else {}
todo = [s["id"] for s in songs if "--all" in sys.argv or s["id"] not in cache or cache[s["id"]].get("status") != "ok"]
if todo:
    print(f"checking {len(todo)} video(s) on YouTube…")
    with ThreadPoolExecutor(6) as ex:
        for vid, res in zip(todo, ex.map(oembed, todo)):
            cache[vid] = {**cache.get(vid, {}), **res}

problems = {"DEAD": [], "BLOCKED": [], "TITLE MISMATCH": [], "RED FLAG": [], "FILM NOT IN VIDEO TITLE": []}
for s in songs:
    c = cache.get(s["id"], {})
    st = c.get("status")
    if st == "dead": problems["DEAD"].append(s); c.update(tv=False, fv=False); continue
    if st == "blocked": problems["BLOCKED"].append(s); c.update(tv=False, fv=False); continue
    if st != "ok": continue
    yt = c["yt_title"]
    w = s["title"].split()
    lead2 = " ".join(w[:2]) if len(w) >= 2 else ""
    c["tv"] = (score(s["title"], yt) >= 0.8 or (len(norm(lead2)) >= 8 and score(lead2, yt) >= 0.9)
               or (len(norm(w[0] if w else "")) >= 7 and score(w[0], yt) == 1.0) or bool(c.get("manual_tv")))
    c["fv"] = bool(s["film"]) and (score(s["film"], yt) >= 0.8 or bool(c.get("manual_fv")))
    c["checked_title"], c["checked_film"] = s["title"], s["film"]
    if not c["tv"]: problems["TITLE MISMATCH"].append(s)
    if RED.search(yt): problems["RED FLAG"].append(s)
    if c["tv"] and not c["fv"]: problems["FILM NOT IN VIDEO TITLE"].append(s)

json.dump({k: cache[k] for k in sorted(cache)}, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

ok = sum(1 for s in songs if cache.get(s["id"], {}).get("tv"))
fv = sum(1 for s in songs if cache.get(s["id"], {}).get("fv"))
print(f"\n{len(songs)} songs | title verified: {ok} | film verified (quiz-eligible): {fv}")
for k, lst in problems.items():
    if not lst: continue
    print(f"\n== {k} ({len(lst)})" + ("  [info only: song stays, just excluded from quiz]" if k.startswith("FILM") else ""))
    for s in lst[:60]:
        print(f"  {s['id']}  {s['title']} | {s['film']}\n      video: {cache.get(s['id'], {}).get('yt_title', '-')[:100]}")
bad = problems["DEAD"] + problems["BLOCKED"] + problems["TITLE MISMATCH"]
sys.exit(1 if bad else 0)
