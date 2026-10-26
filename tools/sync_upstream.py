"""Prepare a reviewable upstream import without changing the live catalog."""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import subprocess

FIELDS = ("hitokoto", "type", "from", "from_who")
LABELS = {"a": "动画", "b": "漫画", "c": "游戏"}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def identity(row):
    return tuple(row[field] for field in FIELDS)


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def escape(value):
    return value.replace("|", "\\|").replace("\r", " ").replace("\n", " ")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream", type=Path, required=True)
    parser.add_argument("--current", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    revision = subprocess.check_output(
        ["git", "-C", str(args.upstream), "rev-parse", "HEAD"], text=True
    ).strip()
    current_bytes = args.current.read_bytes()
    current = json.loads(current_bytes)
    current_ids = {identity(row) for row in current}
    output = args.output
    assert not output.exists(), "Use a new output directory; review files will not be overwritten"
    output.mkdir(parents=True)
    summary = {
        "upstream": "https://github.com/hitokoto-osc/sentences-bundle",
        "revision": revision,
        "fields": list(FIELDS),
        "current_count": len(current),
        "current_sha256": hashlib.sha256(current_bytes).hexdigest(),
        "categories": {},
        "live_catalog_changed": False,
    }
    sections = []
    source_index = []
    for path in sorted((args.upstream / "sentences").glob("*.json")):
        category = path.stem
        rows = read_json(path)
        normalized = []
        seen = set()
        removed_fields = set()
        for row in rows:
            assert row["type"] == category, (path, "category mismatch")
            converted = {field: row[field] for field in FIELDS}
            for field in ("hitokoto", "type", "from"):
                assert isinstance(converted[field], str), (path, field)
            assert converted["from_who"] is None or isinstance(converted["from_who"], str)
            removed_fields.update(set(row) - set(FIELDS))
            key = identity(converted)
            if key not in seen:
                seen.add(key)
                normalized.append(converted)
        write_json(output / "normalized" / path.name, normalized)
        grouped = collections.defaultdict(list)
        for row in normalized:
            grouped[row["from"]].append(row)
        summary["categories"][category] = {
            "upstream_count": len(rows),
            "normalized_count": len(normalized),
            "exact_duplicates_removed": len(rows) - len(normalized),
            "source_count": len(grouped),
            "exact_matches_in_current": sum(identity(r) in current_ids for r in normalized),
            "metadata_fields_removed": sorted(removed_fields),
        }
        if category not in LABELS:
            continue
        lines = [f"## {LABELS[category]}（{len(grouped)} 个出处，{len(normalized)} 条）", "",
                 "| 编号 | 出处原名 | 官方条数 | 线上已有完全相同 | 待选新增 |",
                 "| --- | --- | ---: | ---: | ---: |"]
        for number, (source, members) in enumerate(
            sorted(grouped.items(), key=lambda item: (-len(item[1]), item[0].casefold(), item[0])), 1
        ):
            code = f"{category.upper()}{number:03d}"
            matches = sum(identity(row) in current_ids for row in members)
            record = {"code": code, "category": category, "source": source,
                      "total": len(members), "current_exact": matches, "new": len(members) - matches}
            source_index.append(record)
            lines.append(f"| {code} | {escape(source) or '（空出处）'} | {len(members)} | {matches} | {len(members)-matches} |")
        sections.extend(lines + [""])
    current_only = []
    for category in LABELS:
        official_names = {r["source"] for r in source_index if r["category"] == category}
        counts = collections.Counter(r["from"] for r in current if r["type"] == category and r["from"] not in official_names)
        for name, count in sorted(counts.items()):
            current_only.append({"category": category, "source": name, "count": count})
    summary["current_acg_sources_not_in_upstream"] = current_only
    write_json(output / "summary.json", summary)
    write_json(output / "acg-sources.json", source_index)
    preamble = ["# 一言官方句库出处筛选表", "",
        f"上游版本：`{revision}`。官方仓库：{summary['upstream']}。", "",
        "这里只列动画 a、漫画 b、游戏 c；其他官方分类也已转换，保存在 normalized/，暂未启用。",
        "请按编号或作品名指定保留／排除，例如：保留 A001、C001；其余不要。也可以按系列筛选。",
        "同一作品的大小写、中文别名、不同季等写法没有自动合并，请把希望保留的别名一并说明。",
        "“线上已有完全相同”按四个字段完全一致统计；文字相同但出处或说话人不同仍算不同记录。",
        "候选编号只对本次上游版本固定。当前 cat.json、自定义内容和线上服务均未改动。", "",
        "格式保持 hitokoto、type、from、from_who；仅删除上游元数据和完全重复的记录。", ""]
    if current_only:
        sections += ["## 线上已有、官方当前无同名出处", "",
                     "以下内容不会自动删除，筛选时可单独决定：", "",
                     "| 分类 | 出处 | 线上条数 |", "| --- | --- | ---: |"]
        for row in current_only:
            sections.append(f"| {LABELS[row['category']]} | {escape(row['source'])} | {row['count']} |")
    (output / "出处筛选表.md").write_text("\n".join(preamble + sections) + "\n", encoding="utf-8")
    assert args.current.read_bytes() == current_bytes, "Live catalog unexpectedly changed"
    print(json.dumps({"revision": revision, "current_count": len(current),
                      "candidate_count": sum(x["normalized_count"] for x in summary["categories"].values()),
                      "acg_sources": len(source_index), "output": str(output)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
