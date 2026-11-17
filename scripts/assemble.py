"""Ensambla docs/casos_de_uso.html a partir de _part1.html + uml_data.json + _part2.js."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"

part1 = (DOCS / "_part1.html").read_text(encoding="utf-8")
data = (DOCS / "uml_data.json").read_text(encoding="utf-8")
part2 = (DOCS / "_part2.js").read_text(encoding="utf-8")

assert "/*__UML_DATA__*/" in part1, "falta placeholder de datos"
assert "/*__UML_JS__*/" in part1, "falta placeholder de JS"

out = part1.replace("/*__UML_DATA__*/", data).replace("/*__UML_JS__*/", part2)
(DOCS / "casos_de_uso.html").write_text(out, encoding="utf-8")

kb = len(out.encode("utf-8")) / 1024
print(f"OK -> casos_de_uso.html  ({kb:.0f} KB)")
print("placeholders restantes:", out.count("__UML_"))
