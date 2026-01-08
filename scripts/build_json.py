import csv, json, os

ROOT = os.path.dirname(os.path.dirname(__file__))

def read_csv(path):
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def split_pipe(s):
    s = (s or "").strip()
    if not s:
        return []
    return [x.strip() for x in s.split("|") if x.strip()]

def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

def empty_to_none(s):
    s = (s or "").strip()
    return s if s else None

def main():
    artists_rows = read_csv(os.path.join(ROOT, "data", "artists.csv"))
    works_rows   = read_csv(os.path.join(ROOT, "data", "works.csv"))
    ex_rows      = read_csv(os.path.join(ROOT, "data", "exhibitions.csv"))

    artists = []
    for r in artists_rows:
        a = {
            "id": r["id"].strip(),
            "name": r["name"].strip(),
            "aliases": split_pipe(r.get("aliases", "")),
            "blurb": empty_to_none(r.get("blurb", "")),
            "tags": split_pipe(r.get("tags", "")),
            "era": empty_to_none(r.get("era", "")),
            "region": empty_to_none(r.get("region", "")),
        }
        if not a["aliases"]: a.pop("aliases", None)
        if not a["tags"]: a.pop("tags", None)
        if a["blurb"] is None: a.pop("blurb", None)
        if a["era"] is None: a.pop("era", None)
        if a["region"] is None: a.pop("region", None)
        artists.append(a)

    works = []
    for r in works_rows:
        w = {
            "id": r["id"].strip(),
            "title": r["title"].strip(),
            "artistId": r["artistId"].strip(),
            "year": empty_to_none(r.get("year", "")),
            "tags": split_pipe(r.get("tags", "")),
            "blurb": empty_to_none(r.get("blurb", "")),
        }
        if w["year"] is None: w.pop("year", None)
        if not w["tags"]: w.pop("tags", None)
        if w["blurb"] is None: w.pop("blurb", None)
        works.append(w)

    exhibitions = []
    for r in ex_rows:
        e = {
            "id": r["id"].strip(),
            "title": r["title"].strip(),
            "venue": r["venue"].strip(),
            "startDate": r["startDate"].strip(),
            "endDate": r["endDate"].strip(),
            "artistIds": split_pipe(r.get("artistIds", "")),
            "url": empty_to_none(r.get("url", "")),
            "area": empty_to_none(r.get("area", "")),
            "tags": split_pipe(r.get("tags", "")),
        }
        if e["url"] is None: e.pop("url", None)
        if e["area"] is None: e.pop("area", None)
        if not e["tags"]: e.pop("tags", None)
        exhibitions.append(e)

    artist_ids = {a["id"] for a in artists}
    for w in works:
        if w["artistId"] not in artist_ids:
            raise SystemExit(f"works.csv: artistId not found -> {w['artistId']} (work {w['id']})")
    for ex in exhibitions:
        for aid in ex["artistIds"]:
            if aid not in artist_ids:
                raise SystemExit(f"exhibitions.csv: artistId not found -> {aid} (ex {ex['id']})")

    write_json(os.path.join(ROOT, "artists.json"), {"artists": artists})
    write_json(os.path.join(ROOT, "works.json"), {"works": works})
    write_json(os.path.join(ROOT, "exhibitions.json"), {"exhibitions": exhibitions})

    print("✅ built: artists.json works.json exhibitions.json")

if __name__ == "__main__":
    main()
