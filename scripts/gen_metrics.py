"""Build src/data/validator-metrics.json from a guardrails eval run.

usage: python3 scripts/gen_metrics.py <path/to/breakdown.json> <run-date> [git-sha]
"""
import json, pathlib, sys

EXPOSED = ["content_safety", "pii_remover", "topic_relevance_llm", "gender_assumption_bias"]
LANG = {"en": "English", "hi": "Hindi (Devanagari)", "hi-Latn": "Hinglish"}
CONFIG = {"TR-EDU": "Education", "TR-HEALTH": "Healthcare"}  # others are single-config: skipped
pct = lambda x: None if x is None else round(x * 100)

def group(d, names):
    return [dict(name=names.get(k, k), rows=m["rows_run"], recall=pct(m["recall"]), precision=pct(m["precision"]))
            for k, m in d.items() if k in names]

src, date = sys.argv[1], sys.argv[2]
sha = sys.argv[3] if len(sys.argv) > 3 else None
data = json.load(open(src))
out = {"_run": {"date": date, "sha": sha}}
for v in EXPOSED:
    o, b = data[v]["overall"], data[v]["breakdown"]
    out[v] = dict(rows=o["rows_run"], accuracy=pct(o["accuracy"]), precision=pct(o["precision"]),
                  recall=pct(o["recall"]), f1=pct(o["f1"]), latency_ms=o["latency_p50_ms"],
                  groups=group(b.get("config_ref", {}), CONFIG) + group(b.get("language", {}), LANG))
dst = pathlib.Path(__file__).resolve().parent.parent / "src/data/validator-metrics.json"
dst.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
print("wrote", dst)
