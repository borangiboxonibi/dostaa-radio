"""Dostaa Radio — songs.txt -> songs.json

songs.txt line format (pipe-delimited):
  id|title|film|year|singers|tags|contributor|kn
  - id          11-char YouTube video ID
  - tags        comma list: mass, melody, classic, folk, dard, karaoke ...
  - contributor optional, defaults to "Praveen BABA"
  - kn          optional Kannada-script title (shown large, Roman below)

Song numbers are PERMANENT. numbers.json is an append-only lock
(id -> no). A song keeps its number forever; deleting a line leaves a
gap instead of renumbering everything. New songs get max+1.
Never hand-edit or delete numbers.json.
"""
import json, os
from collections import Counter

LOCK = "numbers.json"

lock = {}
if os.path.exists(LOCK):
    lock = json.load(open(LOCK, encoding="utf-8"))
elif os.path.exists("songs.json"):
    # first run: seed the lock from the currently published numbering
    for s in json.load(open("songs.json", encoding="utf-8")):
        if s.get("id") and s.get("no"):
            lock[s["id"]] = s["no"]
    print(f"seeded {LOCK} from songs.json ({len(lock)} numbers)")

nxt = max(lock.values(), default=0) + 1
out, seen, added = [], set(), 0

for line in open("songs.txt", encoding="utf-8"):
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    p = [x.strip() for x in line.split("|")]
    if len(p) < 6:
        print("SKIP (needs 6+ fields):", line[:60]); continue
    vid, title, film, year, singers, tags = p[:6]
    if len(vid) != 11:
        print("SKIP (bad id):", line[:60]); continue
    if vid in seen:
        continue
    seen.add(vid)
    by = p[6] if len(p) > 6 and p[6] else "Praveen BABA"
    kn = p[7] if len(p) > 7 and p[7] else None
    if vid not in lock:
        lock[vid] = nxt; nxt += 1; added += 1
    taglist = [t.strip() for t in tags.split(",") if t.strip()]
    song = {
        "no": lock[vid], "id": vid, "title": title, "film": film,
        "year": int(year) if year.isdigit() else None,
        "singers": singers, "tags": taglist,
        "karaoke": "karaoke" in taglist,
        "by": by, "hot": True,
    }
    if kn:
        song["kn"] = kn
    out.append(song)

out.sort(key=lambda s: s["no"])
json.dump(out, open("songs.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(dict(sorted(lock.items(), key=lambda kv: kv[1])),
          open(LOCK, "w", encoding="utf-8"), indent=0)

nums = [s["no"] for s in out]
gaps = (max(nums) - len(nums)) if nums else 0
print(f"{len(out)} songs live | numbers 1-{max(nums) if nums else 0} | {gaps} retired gaps | {added} new")
for name, c in Counter(s["by"] for s in out).most_common():
    print(f"  {c:>4}  {name}")
