#!/usr/bin/env python3
"""
Parsea los archivos PlantUML (.puml) del proyecto y genera uml_data.json
para alimentar el visor interactivo de docs/casos_de_uso.html.

Salida:
  - cu      : diagramas de casos de uso  (CU/*.puml)
  - clases  : diagramas de clases        (Clases/*.puml)
  - detalle : clases individuales        (Clases/por_clase/*.puml)
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "uml_data.json"


def read(p: Path) -> str:
    """Lee como UTF-8 tolerando acentos corruptos (cp1252/latin-1 fallback)."""
    raw = p.read_bytes()
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("latin-1")


# ---------------------------------------------------------------- CU ----------
def parse_cu(path: Path) -> dict:
    txt = read(path)
    title = ""
    m = re.search(r'@startuml\s+(\S+)', txt)
    if m:
        title = m.group(1)

    actors, ucs, a_links, uc_links = [], [], [], []

    for m in re.finditer(r'^\s*actor\s+"([^"]+)"\s+as\s+(\w+)', txt, re.M):
        actors.append({"id": m.group(2), "name": m.group(1)})

    # rectangle "Titulo del paquete" {
    m = re.search(r'rectangle\s+"([^"]+)"\s*\{', txt)
    if m:
        title = m.group(1)

    for m in re.finditer(r'^\s*usecase\s+"([^"]+)"\s+as\s+(\w+)', txt, re.M):
        label = m.group(1)
        alias = m.group(2)
        cm = re.match(r'(CU-\d+)\s*[:\-]\s*(.*)', label)
        ucs.append({
            "id": alias,
            "code": cm.group(1) if cm else "",
            "name": cm.group(2) if cm else label,
        })

    # actor --> usecase
    for m in re.finditer(r'^\s*(\w+)\s*-->\s*(\w+)\s*$', txt, re.M):
        if any(a["id"] == m.group(1) for a in actors):
            a_links.append({"from": m.group(1), "to": m.group(2)})

    # usecase .> usecase : <<include>> / <<extend>>   (acepta .>  ..>  .down.>  etc.)
    for m in re.finditer(
        r'^\s*(\w+)\s*\.[a-z]*\.?>\s*(\w+)\s*:\s*<<(\w+)>>', txt, re.M | re.I
    ):
        uc_links.append({"from": m.group(1), "to": m.group(2), "kind": m.group(3).lower()})

    return {
        "file": path.name,
        "title": title,
        "actors": actors,
        "usecases": ucs,
        "actor_links": a_links,
        "uc_links": uc_links,
    }


# ------------------------------------------------------------- Clases ---------
def strip_block(txt: str) -> str:
    """Elimina bloques note ... end note para no interferir con el resto."""
    out, depth, in_note = [], 0, False
    for line in txt.splitlines():
        if re.match(r'^\s*note\b', line, re.I):
            in_note = True
            continue
        if in_note:
            if re.match(r'^\s*end\s+note\b', line, re.I):
                in_note = False
            continue
        out.append(line)
    return "\n".join(out)


def parse_clases(path: Path) -> dict:
    txt = read(path)

    m = re.search(r'@startuml\s+(\S+)', txt)
    name = m.group(1) if m else path.stem

    # Notas -> mapear a su clase objetivo
    notes = []
    for m in re.finditer(
        r'note\s+(?:bottom|top|left|right)?\s*(?:of\s+(\w+))?\s*\n(.*?)end\s+note',
        txt, re.I | re.S,
    ):
        target = m.group(1) or ""
        body = re.sub(r'\s+', ' ', m.group(2)).strip()
        if body:
            notes.append({"target": target, "text": body})

    body = strip_block(txt)
    classes, rels = [], []

    # class Nombre [ #COLOR ] { ... }
    for m in re.finditer(
        r'^\s*(?:abstract\s+|interface\s+)?class\s+(\w+)(?:\s+#([0-9A-Fa-f]{6}))?\s*\{([^}]*)\}',
        body, re.M | re.S,
    ):
        cname, color, inner = m.group(1), m.group(2), m.group(3)
        attrs, methods = [], []
        for line in inner.splitlines():
            line = line.strip()
            if not line or line.startswith("'"):
                continue
            mm = re.match(r'^([+\-#~])?\s*([^\(:]+?)\s*(?:\(([^)]*)\))?\s*(?::\s*(.+))?$', line)
            if not mm:
                continue
            vis = mm.group(1) or "+"
            nm = mm.group(2).strip()
            if "(" in line:
                methods.append({"vis": vis, "name": nm,
                                "params": mm.group(3) or "", "ret": (mm.group(4) or "").strip()})
            else:
                attrs.append({"vis": vis, "name": nm, "type": (mm.group(4) or "").strip()})
        classes.append({"name": cname, "stereo": "class",
                        "color": color, "attrs": attrs, "methods": methods})

    # enum Nombre { ... }
    for m in re.finditer(r'^\s*enum\s+(\w+)\s*\{([^}]*)\}', body, re.M | re.S):
        vals = [v.strip() for v in m.group(2).splitlines() if v.strip() and not v.strip().startswith("'")]
        classes.append({"name": m.group(1), "stereo": "enum", "color": None,
                        "attrs": [{"vis": " ", "name": v, "type": ""} for v in vals],
                        "methods": []})

    # Clases mencionadas sin cuerpo (referencias sueltas)
    defined = {c["name"] for c in classes}
    for line in body.splitlines():
        line = line.strip()
        if not line or line.startswith("'"):
            continue
        mm = re.match(r'^(?:abstract\s+|interface\s+)?class\s+(\w+)(?:\s+#\w{6})?$', line)
        if mm and mm.group(1) not in defined:
            classes.append({"name": mm.group(1), "stereo": "class", "color": None,
                            "attrs": [], "methods": []})
            defined.add(mm.group(1))

    # ------------------------------------------------------- relaciones
    # Todas las flechas PlantUML:  <-- -- -->  .. ..>  *-- o--  <|-- --|>
    ARROW = r'(<\|--|--\|>|\.\.>|-->|\*--|o--|\.\.|\--)'

    def _kind(arrow: str) -> str:
        if arrow in ("<|--", "--|>"):
            return "inherit"
        if arrow in ("*--", "o--"):
            return "compose"          # composición / agregación (rombo)
        if arrow in ("..>", ".."):
            return "depend"
        return "assoc"

    _seen: set = set()

    def _add(a: str, b: str, arrow: str, cf: str, ct: str, lab) -> None:
        # el triángulo de herencia apunta al padre:
        #   A <|-- B  ->  B hereda de A   /   B --|> A  ya viene en ese orden
        if arrow == "<|--":
            a, b = b, a
        kind = _kind(arrow)
        label = (lab or "").replace("\\n", " ").strip().rstrip(">").strip()
        key = (a, b, kind, label, cf or "", ct or "")
        if key in _seen:
            return
        _seen.add(key)
        rels.append({"from": a, "to": b, "kind": kind,
                     "cf": cf or "", "ct": ct or "", "label": label})

    # A "card" ARROW "card" B : etiqueta
    for m in re.finditer(
        rf'^\s*(\w+)\s+"([^"]*)"\s*{ARROW}\s+"([^"]*)"\s+(\w+)\s*(?::\s*(.*?))?\s*>?\s*$',
        body, re.M,
    ):
        a, cf, arrow, ct, b, lab = m.groups()
        _add(a, b, arrow, cf, ct, lab)

    # A ARROW B : etiqueta   (sin cardinalidad: dependencias, herencia, self-loops)
    for m in re.finditer(
        rf'^\s*(\w+)\s*{ARROW}\s*(\w+)\s*(?::\s*(.*?))?\s*>?\s*$', body, re.M
    ):
        a, arrow, b, lab = m.groups()
        _add(a, b, arrow, "", "", lab)

    # Clases referenciadas en relaciones (o como destino de nota) pero nunca
    # declaradas: PlantUML las dibuja vacías, acá también para que el grafo
    # esté completo (p. ej. Alumno/Docente/Preceptor en 08_diagrama_general).
    referenced = set()
    for r in rels:
        referenced.add(r["from"])
        referenced.add(r["to"])
    for nt in notes:
        if nt["target"]:
            referenced.add(nt["target"])
    for n in sorted(referenced - defined):
        if n in ("class", "enum", "abstract", "interface"):
            continue
        classes.append({"name": n, "stereo": "class", "color": None,
                        "attrs": [], "methods": []})
        defined.add(n)

    return {"file": path.name, "title": name, "classes": classes,
            "rels": rels, "notes": notes}


# --------------------------------------------------------------- main ---------
def main() -> None:
    cu = [parse_cu(p) for p in sorted((ROOT / "CU").glob("*.puml"))]
    clases = [parse_clases(p) for p in sorted((ROOT / "Clases").glob("*.puml"))]
    detalle = [parse_clases(p) for p in sorted((ROOT / "Clases" / "por_clase").glob("*.puml"))]

    data = {"cu": cu, "clases": clases, "detalle": detalle}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")

    n_cu = sum(len(d["usecases"]) for d in cu)
    n_cls = sum(len(d["classes"]) for d in clases)
    n_det = sum(len(d["classes"]) for d in detalle)
    print(f"OK -> {OUT.relative_to(ROOT)}")
    print(f"  diagramas CU     : {len(cu)}  ({n_cu} casos de uso)")
    print(f"  diagramas clases : {len(clases)}  ({n_cls} clases)")
    print(f"  clases detalle   : {len(detalle)}  ({n_det} clases)")


if __name__ == "__main__":
    main()
