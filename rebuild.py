import json

out, seen, i = [], set(), 0
for line in open("songs.txt", encoding="utf-8"):
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    p = [x.strip() for x in line.split("|")]
    if len(p) < 6:
        print("SKIP (needs 6+ fields):", line[:60]); continue
    vid, title, film, year, singers, tags = p[:6]
    by = p[6] if len(p) > 6 and p[6] else "Praveen BABA"
    if vid in seen:
        continue
    seen.add(vid); i += 1
    out.append({
        "no": i, "id": vid, "title": title, "film": film,
        "year": int(year) if year.isdigit() else None,
        "singers": singers,
        "tags": [t.strip() for t in tags.split(",") if t.strip()],
        "by": by, "hot": True,
    })

json.dump(out, open("songs.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
from collections import Counter
print(f"{len(out)} songs, numbered 1-{len(out)}")
for name, c in Counter(s["by"] for s in out).most_common():
    print(f"  {c:>4}  {name}")
