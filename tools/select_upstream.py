"""Select known works and watched Bangumi titles, keeping live record order."""
import argparse
import difflib
import hashlib
import json
from pathlib import Path
import unicodedata


def normalize(name):
    return "".join(c for c in unicodedata.normalize("NFKC", name).casefold() if c.isalnum())


# Explicit aliases; fuzzy similarities are suggestions only, never auto-selected.
ALIASES = {
    "多啦A梦": "哆啦A梦",
    "我的恋爱物语果然有问题": "我的青春恋爱物语果然有问题",
    "青春期猪头少年不会梦到兔女郎学姐": "青春猪头少年不会梦到兔女郎学姐",
    "JOJO的奇妙冒险 黄金之风": "JOJO的奇妙冒险",
    "JOJO的奇妙冒险·战斗潮流": "JOJO的奇妙冒险",
    "终末之诗（文言）": "终末之诗",
    "终末之诗（中文）": "终末之诗",
    "Minecraft闪烁标语": "Minecraft",
    "東方永夜抄": "东方永夜抄",
    "永不枯萎的世界与终结之花": "永不枯萎的世界与终焉之花",
    "理与迷宫的少女": "美少女万华镜·理与迷宫的少女",
    "白色相簿II": "白色相簿2",
}
ALIAS_LOOKUP = {normalize(k): normalize(v) for k, v in ALIASES.items()}
LABELS = {"a": "动画", "b": "漫画", "c": "游戏"}
FIELDS = ("hitokoto", "type", "from", "from_who")


def canonical(name):
    key = normalize(name)
    return ALIAS_LOOKUP.get(key, key)


def identity(row):
    return tuple(row[k] for k in FIELDS)


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def cell(text):
    return text.replace("|", "\\|").replace("\n", " ").replace("\r", " ")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--current", type=Path, required=True)
    parser.add_argument("--bangumi", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists(), "Output already exists"
    args.output.mkdir(parents=True)
    baseline_bytes = args.current.read_bytes()
    baseline = json.loads(baseline_bytes)
    watched = read(args.bangumi)
    known = {}
    for row in baseline:
        known.setdefault(canonical(row["from"]), row["from"])
    titles = {}
    for subject in watched["subjects"]:
        for field in ("name_cn", "name"):
            if subject.get(field):
                titles.setdefault(canonical(subject[field]), []).append(subject)
    sources = read(args.snapshot / "acg-sources.json")
    accepted, remaining = [], []
    fuzzy_keys = list(titles)
    for source in sources:
        key = canonical(source["source"])
        row = dict(source)
        if key in known:
            row.update(reason="已有作品", matched=known[key])
            accepted.append(row)
        elif key in titles:
            subjects = titles[key]
            first = subjects[0]
            row.update(reason="Bangumi已看", matched=first["name_cn"] or first["name"],
                       bangumi_subject_ids=sorted({s["id"] for s in subjects}))
            accepted.append(row)
        else:
            suggestions = difflib.get_close_matches(key, fuzzy_keys, n=1, cutoff=0.67)
            row["possible_match"] = (titles[suggestions[0]][0]["name_cn"] or titles[suggestions[0]][0]["name"]) if suggestions else ""
            if source["source"] == "明日方舟：终末地":
                row["possible_match"] = "与已有《明日方舟》不同游戏，未自动纳入"
            if source["source"] == "蔚蓝档案":
                row["possible_match"] = "已看《蔚蓝档案 动画版》，这里分类为游戏，请确认"
            if source["source"] == "猫和老鼠":
                row["possible_match"] = "已看同名动画，这里分类为游戏，请确认"
            remaining.append(row)
    selected = {(r["category"], r["source"]) for r in accepted}
    seen = {identity(r) for r in baseline}
    additions = []
    for category in LABELS:
        for row in read(args.snapshot / "normalized" / (category + ".json")):
            if (category, row["from"]) in selected and identity(row) not in seen:
                additions.append(row)
                seen.add(identity(row))
    catalog = baseline + additions
    assert catalog[:len(baseline)] == baseline
    write(args.output / "自动纳入作品.json", accepted)
    write(args.output / "剩余待选作品.json", remaining)
    write(args.output / "upstream-selected.json", additions)
    write(args.output / "cat.candidate.json", catalog)
    stats = {
        "baseline_sha256": hashlib.sha256(baseline_bytes).hexdigest(),
        "baseline_count": len(baseline), "watched_count": watched["count"],
        "accepted_sources": len(accepted), "remaining_sources": len(remaining),
        "existing_work_sources": sum(r["reason"] == "已有作品" for r in accepted),
        "watched_work_sources": sum(r["reason"] == "Bangumi已看" for r in accepted),
        "additions": len(additions), "result_count": len(catalog),
        "custom_m_preserved": sum(r["type"] == "m" for r in baseline),
        "categories": {},
    }
    for category, label in LABELS.items():
        stats["categories"][category] = {
            "accepted_sources": sum(r["category"] == category for r in accepted),
            "remaining_sources": sum(r["category"] == category for r in remaining),
            "additions": sum(r["type"] == category for r in additions),
        }
    write(args.output / "selection-summary.json", stats)
    lines = ["# 一言：剩余待选作品", "",
        f"已按现有作品与 Bangumi 的 {watched['count']} 条已看收藏筛选。",
        f"自动纳入 {len(accepted)} 个原始出处，剩余 {len(remaining)} 个待选。",
        "相似名称只作为提示；动画与同名游戏不会直接混同。编号沿用上一份表，可继续按编号、作品名或系列选择。", "",
        "Bangumi 来源：https://bgm.tv/anime/list/866060/collect", ""]
    for category, label in LABELS.items():
        rows = [r for r in remaining if r["category"] == category]
        lines += [f"## {label}（{len(rows)} 个待选出处）", "",
                  "| 编号 | 出处 | 可新增句数 | 待确认关系或相似名称 |",
                  "| --- | --- | ---: | --- |"]
        for row in rows:
            lines.append(f"| {row['code']} | {cell(row['source'])} | {row['new']} | {cell(row['possible_match'])} |")
        lines.append("")
    (args.output / "剩余待选作品.md").write_text("\n".join(lines), encoding="utf-8")
    lines = ["# 自动纳入的作品", "", "已有句子保持原顺序，新句子仅追加；自定义内容不删除。", "",
             "| 编号 | 官方出处 | 纳入依据 | 匹配作品 |",
             "| --- | --- | --- | --- |"]
    for row in accepted:
        lines.append(f"| {row['code']} | {cell(row['source'])} | {row['reason']} | {cell(row['matched'])} |")
    (args.output / "自动纳入作品.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    assert args.current.read_bytes() == baseline_bytes
    print(json.dumps(stats, ensure_ascii=False))


if __name__ == "__main__":
    main()
