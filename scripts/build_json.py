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

def to_int(s):
    s = (s or "").strip()
    if not s:
        return None
    try:
        # "1452", "1452.0" の両方に対応
        return int(float(s))
    except:
        return None

def make_tags(movement_list, medium_list, era):
    tags = []
    tags += [t for t in (movement_list or []) if t]
    tags += [t for t in (medium_list or []) if t]
    if era:
        tags.append(era)
    # 重複排除しつつ順序維持
    seen = set()
    out = []
    for t in tags:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out

def main():
    artists_rows = read_csv(os.path.join(ROOT, "data", "artists.csv"))
    works_rows   = read_csv(os.path.join(ROOT, "data", "works.csv"))
    ex_rows      = read_csv(os.path.join(ROOT, "data", "exhibitions.csv"))

    artists = []
    for r in artists_rows:
        movement = split_pipe(r.get("movement", ""))
        medium   = split_pipe(r.get("medium", ""))
        era      = empty_to_none(r.get("era", ""))

        a = {
            "id": r["id"].strip(),
            "name": r["name"].strip(),
            "aliases": split_pipe(r.get("aliases", "")),

            # 新カラム（Swift側にまだ無くてもOK）
            "birthYear": to_int(r.get("birth_year", "")),
            "deathYear": to_int(r.get("death_year", "")),
            "birthYearMin": to_int(r.get("birth_year_min", "")),
            "birthYearMax": to_int(r.get("birth_year_max", "")),
            "deathYearMin": to_int(r.get("death_year_min", "")),
            "deathYearMax": to_int(r.get("death_year_max", "")),
            "movement": movement,
            "medium": medium,

            # 既存互換
            "blurb": empty_to_none(r.get("blurb", "")),
            "era": era,
            "region": empty_to_none(r.get("region", "")),

            # 既存UI/検索が tags を使うので生成して残す
            "tags": make_tags(movement, medium, era),
        }

        # 空のものは落とす（JSONをスッキリ）
        if not a["aliases"]: a.pop("aliases", None)
        if a["birthYear"] is None: a.pop("birthYear", None)
        if a["deathYear"] is None: a.pop("deathYear", None)
        if a["birthYearMin"] is None: a.pop("birthYearMin", None)
        if a["birthYearMax"] is None: a.pop("birthYearMax", None)
        if a["deathYearMin"] is None: a.pop("deathYearMin", None)
        if a["deathYearMax"] is None: a.pop("deathYearMax", None)
        if not a["movement"]: a.pop("movement", None)
        if not a["medium"]: a.pop("medium", None)
        if not a["tags"]: a.pop("tags", None)
        if a["blurb"] is None: a.pop("blurb", None)
        if a["era"] is None: a.pop("era", None)
        if a["region"] is None: a.pop("region", None)

        artists.append(a)

    works = []
    for r in works_rows:
        movement = split_pipe(r.get("movement", ""))
        medium   = split_pipe(r.get("medium", ""))
        era      = empty_to_none(r.get("era", ""))

        w = {
            "id": r["id"].strip(),
            "title": r["title"].strip(),
            "artistId": r["artistId"].strip(),

            # 追加
            "aliases": split_pipe(r.get("aliases", "")),
            "year": empty_to_none(r.get("year", "")),
            "yearMin": to_int(r.get("year_min", "")),
            "yearMax": to_int(r.get("year_max", "")),
            "movement": movement,
            "medium": medium,
            "era": era,

            "blurb": empty_to_none(r.get("blurb", "")),

            # 既存互換：tags を生成して残す
            "tags": make_tags(movement, medium, era),
        }

        if not w["aliases"]: w.pop("aliases", None)
        if w["year"] is None: w.pop("year", None)
        if w["yearMin"] is None: w.pop("yearMin", None)
        if w["yearMax"] is None: w.pop("yearMax", None)
        if not w["movement"]: w.pop("movement", None)
        if not w["medium"]: w.pop("medium", None)
        if w["era"] is None: w.pop("era", None)
        if w["blurb"] is None: w.pop("blurb", None)
        if not w["tags"]: w.pop("tags", None)

        works.append(w)

    exhibitions = []
    for r in ex_rows:
        movement = split_pipe(r.get("movement", ""))
        era      = empty_to_none(r.get("era", ""))

        e = {
            "id": r["id"].strip(),
            "title": r["title"].strip(),
            "venue": r["venue"].strip(),
            "startDate": r["startDate"].strip(),
            "endDate": r["endDate"].strip(),

            "artistIds": split_pipe(r.get("artistIds", "")),
            "workIds": split_pipe(r.get("workIds", "")),
            "url": empty_to_none(r.get("url", "")),
            "area": empty_to_none(r.get("area", "")),
            "movement": movement,
            "era": era,

            # 互換用（任意）
            "tags": make_tags(movement, [], era),
        }

        if not e["workIds"]: e.pop("workIds", None)
        if e["url"] is None: e.pop("url", None)
        if e["area"] is None: e.pop("area", None)
        if not e["movement"]: e.pop("movement", None)
        if e["era"] is None: e.pop("era", None)
        if not e["tags"]: e.pop("tags", None)

        exhibitions.append(e)

    # バリデーション
    artist_ids = {a["id"] for a in artists}
    work_ids   = {w["id"] for w in works}

    for w in works:
        if w["artistId"] not in artist_ids:
            raise SystemExit(f"works.csv: artistId not found -> {w['artistId']} (work {w['id']})")

    for ex in exhibitions:
        for aid in ex["artistIds"]:
            if aid not in artist_ids:
                raise SystemExit(f"exhibitions.csv: artistId not found -> {aid} (ex {ex['id']})")
        for wid in ex.get("workIds", []):
            if wid not in work_ids:
                raise SystemExit(f"exhibitions.csv: workId not found -> {wid} (ex {ex['id']})")

    write_json(os.path.join(ROOT, "artists.json"), {"artists": artists})
    write_json(os.path.join(ROOT, "works.json"), {"works": works})
    write_json(os.path.join(ROOT, "exhibitions.json"), {"exhibitions": exhibitions})

    print("✅ built: artists.json works.json exhibitions.json")

if __name__ == "__main__":
    main()
