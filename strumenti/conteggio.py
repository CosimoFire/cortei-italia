"""
Radar – QN · Conteggio aggregato dei cortei

Legge data/cortei.csv (solo righe verificate) e scrive conteggio.md con cinque righe
di testo per l'articolo. Tutti i numeri sono calcolati dal CSV: non si scrivono a mano.

Uso: python strumenti/conteggio.py
"""
import csv
import json
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

from shapely.geometry import Point, shape

QUI = Path(__file__).resolve().parent.parent
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

NORD = {"Piemonte", "Valle d'Aosta", "Lombardia", "Trentino-Alto Adige", "Veneto",
        "Friuli-Venezia Giulia", "Liguria", "Emilia-Romagna"}
CENTRO = {"Toscana", "Umbria", "Marche", "Lazio"}
ARTICOLO = {"Emilia-Romagna": "l'", "Abruzzo": "l'", "Umbria": "l'", "Piemonte": "il", "Veneto": "il",
            "Lazio": "il", "Molise": "il", "Trentino-Alto Adige": "il", "Friuli-Venezia Giulia": "il"}
LETTERE = {1: "una", 2: "due", 3: "tre", 4: "quattro", 5: "cinque", 6: "sei", 7: "sette", 8: "otto", 9: "nove", 10: "dieci"}
TENSIONI = re.compile(r"\b(cariche|caricat[ie]|scontri|tensioni|lacrimogeni|fermat[ie]|arrestat[ie]|feriti?)\b", re.I)


def n(x):
    """numeri fino a dieci in lettere, gli altri in cifre (uso giornalistico)"""
    return LETTERE.get(x, str(x))


def con_articolo(reg, maiuscola=False):
    a = ARTICOLO.get(reg, "la")
    s = (a + reg) if a.endswith("'") else (a + " " + reg)
    return s[0].upper() + s[1:] if maiuscola else s


def elenco(voci):
    return voci[0] if len(voci) == 1 else ", ".join(voci[:-1]) + " e " + voci[-1]


def main():
    reg = json.loads((QUI / "data" / "regioni.json").read_text(encoding="utf-8"))
    forme = [(f["properties"]["regione"].split("/")[0], shape(f["geometry"])) for f in reg["features"]]
    geo = {}
    with open(QUI / "data" / "citta.csv", encoding="utf-8") as fh:
        for r in csv.DictReader(fh, delimiter=";"):
            geo[r["citta"]] = Point(float(r["lon"].replace(",", ".")), float(r["lat"].replace(",", ".")))
    with open(QUI / "data" / "cortei.csv", encoding="utf-8") as fh:
        righe = list(csv.DictReader(fh, delimiter=";"))

    def regione(c):
        return min(forme, key=lambda f: f[1].distance(geo[c]))[0]

    tot = len(righe)
    svolte = sum(r["stato"] in ("in corso", "concluso") for r in righe)
    annunciate = sum(r["stato"] == "annunciato" for r in righe)
    per_reg = Counter(regione(r["citta"]) for r in righe)
    aree = Counter("Nord" if g in NORD else "Centro" if g in CENTRO else "Sud e isole"
                   for g in (regione(r["citta"]) for r in righe))
    ora = max(datetime.strptime(r["aggiornato"], "%d/%m/%Y %H:%M") for r in righe)
    teso = [r["citta"] for r in righe if TENSIONI.search(r["avvenimenti"])]

    # 1. totale e copertura
    copertura = ("almeno una in ognuna delle 20 regioni" if len(per_reg) == 20
                 else f"in {n(len(per_reg))} regioni su 20")
    r1 = (f"Sono {tot} le città italiane in cui, fino alle {ora.hour}, le cronache segnalano cortei e presìdi "
          f"per lo sciopero generale del 20 novembre contro la legge di Bilancio: {copertura}.")
    # 2. svolte / annunciate
    if annunciate:
        r2 = f"In {n(svolte)} di queste la manifestazione si è svolta o è in corso, nelle altre {n(annunciate)} è annunciata."
    else:
        r2 = "In tutte la manifestazione si è svolta o è in corso."
    # 3. aree
    nomi = {"Nord": "il Nord", "Centro": "il Centro", "Sud e isole": "il Sud e le isole"}
    ordine = sorted(aree.items(), key=lambda x: -x[1])
    prima = ordine[0]
    quota = " la metà delle piazze," if prima[1] * 2 == tot else ""
    altre = []
    for k, v in ordine[1:]:
        art = "le " + str(v) if v != 1 else "una sola"
        altre.append(f"{art} {'del Centro' if k == 'Centro' else 'del Sud e delle isole' if k == 'Sud e isole' else 'del Nord'}")
    r3 = f"{nomi[prima[0]][0].upper() + nomi[prima[0]][1:]} raccoglie{quota} {prima[1]} città, contro {elenco(altre)}."
    # 4. regioni con più città
    classifica = per_reg.most_common()
    top_n = classifica[0][1]
    top = [g for g, v in classifica if v == top_n]
    seguenti = [(g, v) for g, v in classifica if v < top_n]
    if len(top) == 1:
        r4 = f"{con_articolo(top[0], True)} è la regione con più città mobilitate, {n(top_n)}"
    else:
        r4 = f"{elenco(top)} sono le regioni con più città mobilitate, {n(top_n)} ciascuna"
    if seguenti:
        sec_n = seguenti[0][1]
        sec = [g for g, v in seguenti if v == sec_n]
        r4 += f", seguit{'a' if len(top) == 1 else 'e'} da {elenco(sec)} con {n(sec_n)}{' ciascuna' if len(sec) > 1 else ''}"
    r4 += "."
    # 5. tensioni (dal testo verificato)
    if teso:
        r5 = f"Le cronache segnalano momenti di tensione a {elenco(teso)}."
    else:
        r5 = f"Fino alle {ora.hour} le cronache non segnalano tensioni né scontri."

    testo = "\n".join([r1, r2, r3, r4, r5])
    out = QUI / "conteggio.md"
    out.write_text(f"<!-- generato da strumenti/conteggio.py il {datetime.now():%d/%m/%Y %H:%M}, dati verificati alle {ora:%H:%M} -->\n\n"
                   + testo + "\n", encoding="utf-8")
    print(testo)


if __name__ == "__main__":
    main()
