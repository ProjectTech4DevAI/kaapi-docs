"""Build src/data/validator-metrics.json from a guardrails eval run.

usage: python3 scripts/gen_metrics.py <path/to/breakdown.json> <run-date> [git-sha] [pii_side_by_side/metrics.json] [content_safety/breakdown.json]

If a content-safety breakdown (argv[5]) is given, it replaces content_safety (use "" to skip argv[4]).
If the PII metrics file is given, it replaces pii_remover (message-level scores, per-language value recall).
"""
import csv, json, pathlib, sys

EXPOSED = ["content_safety", "pii_remover", "topic_relevance_llm", "gender_assumption_bias"]
LANG = {"en": "English", "hi": "Hindi (Devanagari)", "hi-Latn": "Hinglish"}
PII_LANG = {"en": "English", "hi": "Hindi", "hinglish": "Hinglish", "kn": "Kannada", "mr": "Marathi", "te": "Telugu"}
CONFIG = {"TR-EDU": "Education", "TR-HEALTH": "Healthcare"}  # others are single-config: skipped
pct = lambda x: None if x is None else round(x * 100)

def group(d, names):
    return [dict(name=names.get(k, k), rows=m["rows_run"], recall=pct(m["recall"]), precision=pct(m["precision"]))
            for k, m in d.items() if k in names]

def pii_groups(path):
    """Message-level recall/precision per language: positive = has_pii, flagged = text changed."""
    c = {}
    for r in csv.DictReader(open(path)):
        k = c.setdefault(r["lang"], dict(tp=0, fp=0, fn=0, n=0))
        flagged, pos = r["output"] != r["message"], r["has_pii"] == "yes"
        k["n"] += 1
        k["tp"] += flagged and pos
        k["fp"] += flagged and not pos
        k["fn"] += pos and not flagged
    return [dict(name=PII_LANG[l], rows=k["n"], recall=round(100 * k["tp"] / (k["tp"] + k["fn"])),
                 precision=round(100 * k["tp"] / (k["tp"] + k["fp"]))) for l, k in c.items()]

src, date = sys.argv[1], sys.argv[2]
sha = sys.argv[3] if len(sys.argv) > 3 else None
data = json.load(open(src))
out = {"_run": {"date": date, "sha": sha}}
for v in EXPOSED:
    o, b = data[v]["overall"], data[v]["breakdown"]
    out[v] = dict(rows=o["rows_run"], accuracy=pct(o["accuracy"]), precision=pct(o["precision"]),
                  recall=pct(o["recall"]), f1=pct(o["f1"]), latency_ms=o["latency_p50_ms"],
                  groups=group(b.get("config_ref", {}), CONFIG) + group(b.get("language", {}), LANG))
if len(sys.argv) > 4 and sys.argv[4]:
    p = json.load(open(sys.argv[4]))
    m, ours = p["meta"], p["ours"]["message"]
    tp, fp, fn, tn = (ours[k] for k in ("tp", "fp", "fn", "tn"))
    out["pii_remover"] = dict(rows=m["rows"], accuracy=round(100 * (tp + tn) / m["rows"]), precision=pct(ours["precision"]),
        recall=pct(ours["recall"]), f1=pct(ours["f1"]), latency_ms=m["latency_ms"]["p50"],
        groups=pii_groups(pathlib.Path(sys.argv[4]).with_name("predictions.csv")))
    out["pii_remover"]["date"] = m["date"]
if len(sys.argv) > 5:
    cs = json.load(open(sys.argv[5]))["content_safety"]
    o, b = cs["overall"], cs["breakdown"]
    out["content_safety"] = dict(rows=o["rows_run"], accuracy=pct(o["accuracy"]), precision=pct(o["precision"]),
        recall=pct(o["recall"]), f1=pct(o["f1"]), latency_ms=o["latency_p50_ms"], groups=group(b["language"], LANG),
        date=sys.argv[5].split("/runs/")[1].split("/")[0])
dst = pathlib.Path(__file__).resolve().parent.parent / "src/data/validator-metrics.json"
dst.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
print("wrote", dst)
