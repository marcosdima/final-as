"""Ensambla docs/casos_de_uso.html a partir de _part1.html + uml_data.json + _part2.js.

También inyecta la API key de Groq (leída de db/bot/.env) en el placeholder
/*__GROQ_KEY__*/ para que el prototipo de chat funcione sin configuración extra.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
ENV = ROOT / "db" / "bot" / ".env"

part1 = (DOCS / "_part1.html").read_text(encoding="utf-8")
data = (DOCS / "uml_data.json").read_text(encoding="utf-8")
part2 = (DOCS / "_part2.js").read_text(encoding="utf-8")

assert "/*__UML_DATA__*/" in part1, "falta placeholder de datos"
assert "/*__UML_JS__*/" in part1, "falta placeholder de JS"
assert "/*__GROQ_KEY__*/" in part1, "falta placeholder de la key de Groq"

# --- API key de Groq desde db/bot/.env ---
groq_key = ""
if ENV.exists():
    m = re.search(r"^GROQ_API_KEY=(\S+)", ENV.read_text(encoding="utf-8"), re.M)
    if m:
        groq_key = m.group(1).strip()
if not groq_key:
    print("AVISO: no se encontró GROQ_API_KEY en db/bot/.env — el chat pedirá la key a mano")

out = (
    part1.replace("/*__UML_DATA__*/", data)
    .replace("/*__GROQ_KEY__*/", json.dumps(groq_key))
    .replace("/*__UML_JS__*/", part2)
)
(DOCS / "casos_de_uso.html").write_text(out, encoding="utf-8")

kb = len(out.encode("utf-8")) / 1024
print(f"OK -> casos_de_uso.html  ({kb:.0f} KB)")
print("placeholders restantes:", out.count("__UML_"))
print("key groq inyectada:", "sí" if groq_key else "no")
