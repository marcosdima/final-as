import json, sys, re
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
d = json.load(open(r"docs\uml_data.json", encoding="utf-8"))

for diagram in d["clases"]:
    classes = [c["name"] for c in diagram["classes"]]
    inherits = [(r["from"], r["to"]) for r in diagram["rels"] if r["kind"] == "inherit"]
    others = [(r["from"], r["to"], r["kind"]) for r in diagram["rels"] if r["kind"] != "inherit"]
    children = {}
    for ch, pa in inherits:
        children.setdefault(pa, []).append(ch)
    is_child = {ch for ch, _ in inherits}
    roots = [c for c in classes if c not in is_child]
    print(f"=== {diagram['file']}  ({len(classes)} clases)")
    print(f"    herencia: {inherits}")
    print(f"    raices  : {roots}")
    print(f"    otras   : {others}")
    if len(classes) > 12:
        for c in diagram["classes"]:
            at = [(a["name"], a["type"]) for a in c["attrs"]]
            print(f"      - {c['name']}: attrs={at}")
    print()
