"""Dostaa Radio — songs.json + verified.json -> specials.json

Specials are themed playlists (festivals, legends, stars, moods) built ONLY
from songs already on air, so every play is an embedded YouTube play that
counts for the official channel. Nothing is hosted here.

How membership is decided:
  - stars / legends : regex over the verified YouTube title + singers,
                      then manual "add" / "drop" ids for edge cases
  - festivals       : hand-curated id lists ("ids")
  - moods           : tag or regex rules

Workflow (after adding songs):
  python3 audit.py  ->  python3 rebuild.py  ->  python3 build_specials.py  ->  git push

A special with fewer than MIN songs is skipped (except "coming" teasers).
"""
import json, re

MIN = 6
S = json.load(open("songs.json", encoding="utf-8"))
V = json.load(open("verified.json", encoding="utf-8"))
by_id = {s["id"]: s for s in S}

def hay(s):
    v = V.get(s["id"], {})
    return " | ".join([v.get("yt_title", ""), s.get("singers", ""), s.get("title", "")]).lower()

def rx_match(rx, drop=()):
    r = re.compile(rx, re.I)
    return [s["id"] for s in S if r.search(hay(s)) and s["id"] not in drop]

def annavru():
    """Dr. Rajkumar — but not Puneeth/Shiva/Raghavendra Rajkumar or S.A. Rajkumar (composer)."""
    out = []
    for s in S:
        h = hay(s)
        for m in re.finditer(r"raj ?kumar|rajkumra|annavru", h):
            pre = h[max(0, m.start() - 14):m.start()]
            if re.search(r"puneet|puneeth|shiv|raghavendra|vinay|yuva|s\.? ?a\.? ?$|s a $", pre):
                continue
            out.append(s["id"]); break
    return out

# ---------------------------------------------------------------- festivals
RAJYOTSAVA = [
    "7iLvW-UYmsg", "izMVVAc9KKE", "lnYptjdQbyo", "48T3gr4AFJo", "C5yYfF_pNSY", "BqHtPNjmwD0",
    "fXPnnroHEOE", "R3ogWZ_VBx0", "ziNXOdlPLLE", "K5plr3yThCo", "EgoJz1UxUXU", "Y2u5WAntdu4",
    "hHGDq9nVHhA", "kn9Sv7uaUDE", "EpwtGYuUzno", "9qafenBpqYs", "d2X87-HU5bU", "IY1ScTWqCx8",
    "WD2MlG0Q4bI",
]
DASARA = [
    "mYKpAg6azx4", "mlkJKMYTfMw", "rbZMsUdg3ig", "pHXay38W28E", "fRYPwNnGYHc", "gRB9S-pqKk8",
    "tvv_lA3rHLk", "zmHsP1CN_aA", "O_SPC0-VUJc",
]

# ---------------------------------------------------------------- shelves
shelves = [
 {"id": "habba", "kn": "ಹಬ್ಬದ ಹವಾ", "en": "Habba Hava", "items": [
   {"id": "rajyotsava", "al": "rajyotsava kannada rajyothsava ರಾಜ್ಯೋತ್ಸವ ಕನ್ನಡ", "kn": "ರಾಜ್ಯೋತ್ಸವ ಸ್ಪೆಷಲ್", "en": "Rajyotsava Special",
    "skn": "ಎದೆ ತಟ್ಟಿ ಹೇಳು, ನಾನು ಕನ್ನಡಿಗ", "sen": "Kannada pride, full volume",
    "theme": "flag", "date": "11-01", "live": ["2026-10-01", "2026-11-30"], "ids": RAJYOTSAVA, "hero": True},
   {"id": "dasara", "al": "dasara dussehra navaratri mysuru ದಸರಾ ನವರಾತ್ರಿ", "kn": "ದಸರಾ ಸ್ಪೆಷಲ್", "en": "Dasara Special",
    "skn": "ನಾಡ ಹಬ್ಬದ ಹಾಡುಗಳು", "sen": "Naada Habba songs",
    "theme": "gold", "live": ["2026-10-01", "2026-10-22"], "ids": DASARA},
   {"id": "deepavali", "kn": "ದೀಪಾವಳಿ ಸ್ಪೆಷಲ್", "en": "Deepavali Special", "skn": "ಬರ್ತಾ ಇದೆ", "sen": "Coming soon",
    "theme": "ember", "coming": "Nov"},
   {"id": "sankranti", "kn": "ಸಂಕ್ರಾಂತಿ ಸ್ಪೆಷಲ್", "en": "Sankranti Special", "skn": "ಬರ್ತಾ ಇದೆ", "sen": "Coming soon",
    "theme": "leaf", "coming": "Jan"},
   {"id": "yugadi", "kn": "ಯುಗಾದಿ ಸ್ಪೆಷಲ್", "en": "Yugadi Special", "skn": "ಬರ್ತಾ ಇದೆ", "sen": "Coming soon",
    "theme": "leaf", "coming": "soon"},
   {"id": "ganesha", "kn": "ಗಣೇಶ ಸ್ಪೆಷಲ್", "en": "Ganesha Special", "skn": "ಬರ್ತಾ ಇದೆ", "sen": "Coming soon",
    "theme": "ember", "coming": "soon"},
 ]},
 {"id": "legends", "kn": "ದಿಗ್ಗಜರು", "en": "The Legends", "items": [
   {"id": "annavru", "al": "rajkumar dr rajkumar annavru rajanna ಅಣ್ಣಾವ್ರು ರಾಜ್‌ಕುಮಾರ್ ರಾಜ್‍ಕುಮಾರ್", "kn": "ಅಣ್ಣಾವ್ರ ಸ್ಪೆಷಲ್", "en": "Annavru Special", "skn": "ಗಾನ ಗಂಧರ್ವ", "sen": "Gaana Gandharva",
    "theme": "royal", "ids": [i for i in annavru() if i not in ("zmHsP1CN_aA",)]},
   {"id": "vishnu", "al": "vishnuvardhan vishnu dada saahasa simha ವಿಷ್ಣುವರ್ಧನ್ ವಿಷ್ಣು", "kn": "ವಿಷ್ಣು ದಾದಾ ಸ್ಪೆಷಲ್", "en": "Vishnu Dada Special", "skn": "ಸಾಹಸ ಸಿಂಹ", "sen": "Saahasa Simha",
    "theme": "royal", "ids": rx_match(r"vishnuvardhan|vishnuvardan|vishnu ?dada|sahasa ?simha")},
   {"id": "shankarnag", "al": "shankar nag shankarnag ಶಂಕರ್ ನಾಗ್", "kn": "ಶಂಕರ್ ನಾಗ್ ಸ್ಪೆಷಲ್", "en": "Shankar Nag Special", "skn": "ಆಟೋ ರಾಜ", "sen": "Auto Raja",
    "theme": "royal", "ids": rx_match(r"shankar ?nag")},
   {"id": "appu", "al": "appu puneeth puneeth rajkumar power star ಅಪ್ಪು ಪುನೀತ್", "kn": "ಅಪ್ಪು ಸ್ಪೆಷಲ್", "en": "Appu Special", "skn": "ಪವರ್ ಸ್ಟಾರ್", "sen": "Power Star",
    "theme": "royal", "ids": rx_match(r"puneeth|puneet|\bappu\b|power ?star")},
 ]},
 {"id": "stars", "kn": "ಸ್ಟಾರ್ ಹವಾ", "en": "Star Power", "items": [
   {"id": "dboss", "al": "darshan d boss dboss challenging star ದರ್ಶನ್ ಡಿ ಬಾಸ್", "kn": "ಡಿ ಬಾಸ್ ಸ್ಪೆಷಲ್", "en": "D Boss Special", "skn": "ಚಾಲೆಂಜಿಂಗ್ ಸ್ಟಾರ್", "sen": "Challenging Star",
    "theme": "red", "ids": rx_match(r"darshan|d ?boss|challenging star")},
   {"id": "kiccha", "al": "sudeep sudeepa kiccha kichcha ಸುದೀಪ್ ಕಿಚ್ಚ", "kn": "ಕಿಚ್ಚ ಸ್ಪೆಷಲ್", "en": "Kiccha Special", "skn": "ಅಭಿನಯ ಚಕ್ರವರ್ತಿ", "sen": "Abhinaya Chakravarthy",
    "theme": "red", "ids": rx_match(r"sudeep|kiccha|kichcha")},
   {"id": "shivanna", "al": "shivanna shivarajkumar shiva rajkumar ಶಿವಣ್ಣ ಶಿವರಾಜ್‌ಕುಮಾರ್", "kn": "ಶಿವಣ್ಣ ಸ್ಪೆಷಲ್", "en": "Shivanna Special", "skn": "ಹ್ಯಾಟ್ರಿಕ್ ಹೀರೋ", "sen": "Hat-trick Hero",
    "theme": "red", "ids": rx_match(r"shiva ?raj ?kumar|shivrajkumar|shiv raj ?kumar|shivanna")},
   {"id": "yash", "al": "yash rocky rocking star ಯಶ್ ರಾಕಿ", "kn": "ರಾಕಿ ಭಾಯ್ ಸ್ಪೆಷಲ್", "en": "Rocky Bhai Special", "skn": "ರಾಕಿಂಗ್ ಸ್ಟಾರ್", "sen": "Rocking Star",
    "theme": "red", "ids": rx_match(r"\byash\b|rocking star|rocky bhai")},
   {"id": "rakshit", "al": "rakshit shetty rakshith ರಕ್ಷಿತ್ ಶೆಟ್ಟಿ", "kn": "ರಕ್ಷಿತ್ ಶೆಟ್ಟಿ ಸ್ಪೆಷಲ್", "en": "Rakshit Shetty Special", "skn": "ಸಿಂಪಲ್ ಸ್ಟಾರ್", "sen": "Simple Star",
    "theme": "red", "ids": rx_match(r"rakshit+h? shetty")},
   {"id": "ganesh", "al": "ganesh golden star ಗಣೇಶ್ ಗೋಲ್ಡನ್ ಸ್ಟಾರ್", "kn": "ಗೋಲ್ಡನ್ ಸ್ಟಾರ್ ಸ್ಪೆಷಲ್", "en": "Golden Star Special", "skn": "ಗಣಿ ಹವಾ", "sen": "Golden Star Ganesh",
    "theme": "red", "ids": rx_match(r"golden star|golden \*|golden ⭐|(?<!bvm )\bganesh\b(?! reddy)")},
   {"id": "ravichandran", "al": "ravichandran crazy star ravi ರವಿಚಂದ್ರನ್ ಕ್ರೇಜಿ", "kn": "ಕ್ರೇಜಿ ಸ್ಟಾರ್ ಸ್ಪೆಷಲ್", "en": "Crazy Star Special", "skn": "ಕನಸುಗಾರ", "sen": "Ravichandran",
    "theme": "red", "ids": rx_match(r"ravichandran|crazy star")},
   {"id": "upendra", "al": "upendra uppi real star ಉಪೇಂದ್ರ ಉಪ್ಪಿ", "kn": "ಉಪ್ಪಿ ಸ್ಪೆಷಲ್", "en": "Uppi Special", "skn": "ರಿಯಲ್ ಸ್ಟಾರ್", "sen": "Real Star",
    "theme": "red", "ids": rx_match(r"upendra|\buppi\b")},
   {"id": "queens", "al": "ramya radhika pandit rachita ram malashri sudharani kalpana rashmika ರಮ್ಯಾ ರಾಧಿಕಾ ರಚಿತಾ ಮಾಲಾಶ್ರೀ", "kn": "ಸ್ಯಾಂಡಲ್‌ವುಡ್ ಕ್ವೀನ್ಸ್", "en": "Sandalwood Queens", "skn": "ಹೀರೋಯಿನ್ ಹವಾ", "sen": "Heroines on screen",
    "theme": "rose", "ids": rx_match(r"\bramya\b|radhika pandit|rachita|rachitha|malashri|sudharani|kalpana|aarathi|jayanthi|rashmika|ashika")},
 ]},
 {"id": "mood", "kn": "ಮೂಡ್ ಏನು?", "en": "What's the mood?", "items": [
   {"id": "hamsalekha", "al": "hamsalekha hamsaleka ಹಂಸಲೇಖ", "kn": "ಹಂಸಲೇಖ ಹವಾ", "en": "Hamsalekha Hava", "skn": "ನಾದಬ್ರಹ್ಮನ ಹಾಡುಗಳು", "sen": "The Naadabrahma hits",
    "theme": "plum", "ids": rx_match(r"hamsalekha|hamsaleka")},
   {"id": "spb", "al": "spb balu balasubrahmanyam sp balasubrahmanyam ಎಸ್‌ಪಿಬಿ ಬಾಲು", "kn": "ಎಸ್‌ಪಿಬಿ ಗಾನ", "en": "SPB Gaana", "skn": "ಬಾಲು ಸರ್ ದನಿ", "sen": "The voice of Balu sir",
    "theme": "plum", "ids": rx_match(r"\bspb\b|s\.? ?p\.? ?b\b|balasubrahmanyam|balasubramanyam|s\.p\.b")},
   {"id": "rain", "al": "rain male mungaru ಮಳೆ ಮುಂಗಾರು", "kn": "ಮಳೆ ಹಾಡು", "en": "Male Haadu", "skn": "ಮಳೆ ಬಂದ್ರೆ ಇದೇ ಬೇಕು", "sen": "For when it rains",
    "theme": "plum", "ids": rx_match(r"\bmale\b|maleye|mungaru|malebillu|male billu|\bmegha\b|varsha", drop=("IY1ScTWqCx8", "U_n7sIGxYJI"))},
   {"id": "dard", "al": "love failure sad dard ಲವ್ ಫೇಲ್ಯೂರ್", "kn": "ಲವ್ ಫೇಲ್ಯೂರ್", "en": "Love Failure", "skn": "ಎದೆ ಒಡೆದ ಹಾಡುಗಳು", "sen": "Heartbreak hits",
    "theme": "plum", "ids": [s["id"] for s in S if "dard" in (s.get("tags") or [])]},
   {"id": "night", "al": "night drive ನೈಟ್ ಡ್ರೈವ್", "kn": "ನೈಟ್ ಡ್ರೈವ್", "en": "Night Drive", "skn": "ಏರ್‌ಪೋರ್ಟ್ ರೋಡ್, 12 ಗಂಟೆ", "sen": "Airport Road, midnight",
    "theme": "plum", "ids": [s["id"] for s in S if "melody" in (s.get("tags") or []) and (s.get("year") or 0) >= 2005]},
 ]},
]

# ---------------------------------------------------------------- write
out, report = [], []
for sh in shelves:
    items = []
    for it in sh["items"]:
        ids = [i for i in dict.fromkeys(it.get("ids", [])) if i in by_id]
        it = dict(it); it["ids"] = ids
        if it.get("coming"):
            it["ids"] = []; items.append(it); report.append(f"  {it['id']:13} coming ({it['coming']})"); continue
        if len(ids) < MIN:
            report.append(f"  {it['id']:13} SKIPPED ({len(ids)} < {MIN})"); continue
        items.append(it); report.append(f"  {it['id']:13} {len(ids):3} songs")
    out.append({k: sh[k] for k in ("id", "kn", "en")} | {"items": items})

json.dump({"v": 1, "shelves": out}, open("specials.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print("specials.json written\n" + "\n".join(report))
