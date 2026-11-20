"""Prepara i confini regionali (da province ISTAT 2023) e verifica che ogni città
del dizionario data/citta.csv cada dentro la propria provincia."""
import csv, json, sys
from pathlib import Path
from shapely.geometry import shape, mapping, Point
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from shapely.geometry import MultiPolygon

QUI = Path(__file__).resolve().parent.parent
SRC = Path(sys.argv[1])
d = json.loads(SRC.read_text(encoding="utf-8"))
prov = {f["properties"]["prov_acr"]: shape(f["geometry"]) for f in d["features"]}
reg = {}
for f in d["features"]:
    reg.setdefault(f["properties"]["reg_name"], []).append(shape(f["geometry"]).buffer(0))

errori = 0
with open(QUI / "data" / "citta.csv", encoding="utf-8") as fh:
    for r in csv.DictReader(fh, delimiter=";"):
        p = Point(float(r["lon"].replace(",", ".")), float(r["lat"].replace(",", ".")))
        g = prov.get(r["sigla"])
        if g is None:
            print("SIGLA SCONOSCIUTA", r["citta"], r["sigla"]); errori += 1
        elif not g.buffer(0.01).contains(p):
            print("FUORI PROVINCIA", r["citta"], r["sigla"], round(g.distance(p), 3)); errori += 1
print("città controllate, errori:", errori)

def rnd(c):
    if isinstance(c[0], (int, float)): return [round(c[0], 3), round(c[1], 3)]
    return [rnd(x) for x in c]
feats = []
for nome, gs in sorted(reg.items()):
    g = unary_union(gs).simplify(0.008, preserve_topology=True)
    # d3-geo vuole gli anelli esterni in senso orario (il contrario di RFC 7946)
    parti = [g] if g.geom_type == "Polygon" else list(g.geoms)
    # via gli scogli ridotti a poligoni degeneri dalla semplificazione (d3 li leggerebbe come "tutto il globo")
    parti = [orient(x, -1.0) for x in parti if x.area > 2e-4 and x.is_valid]
    g = parti[0] if len(parti) == 1 else MultiPolygon(parti)
    m = mapping(g)
    feats.append({"type": "Feature", "properties": {"regione": nome},
                  "geometry": {"type": m["type"], "coordinates": rnd(m["coordinates"])}})
out = QUI / "data" / "regioni.json"
out.write_text(json.dumps({"type": "FeatureCollection", "features": feats}, separators=(",", ":")), encoding="utf-8")
print("regioni:", len(feats), "kB:", out.stat().st_size // 1024)
