"""
Radar – QN · Analisi delle notizie sui cortei in Italia

Legge i flussi RSS delle testate, tiene solo le notizie che parlano di cortei,
presìdi, manifestazioni o scioperi, riconosce le città citate e scrive
data/candidati.csv: un elenco di SEGNALAZIONI DA VERIFICARE, non di fatti.

La mappa non legge mai questo file. Legge solo data/cortei.csv, che compila
la redazione dopo aver controllato le segnalazioni sulle fonti originali.

Uso:
    python strumenti/analizza_notizie.py              notizie delle ultime 12 ore
    python strumenti/analizza_notizie.py --ore 24     finestra più ampia
    python strumenti/analizza_notizie.py --verifica   controlla data/cortei.csv prima di pubblicare

Solo libreria standard di Python 3.9+.
"""
import argparse
import csv
import html
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

QUI = Path(__file__).resolve().parent.parent
DATI = QUI / "data"
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------- fonti
# Feed diretti delle testate + ricerche su Google News (che aggrega molte testate:
# la testata d'origine è nel titolo, dopo l'ultimo " - ").
def gnews(q):
    return "https://news.google.com/rss/search?" + urllib.parse.urlencode(
        {"q": q + " when:1d", "hl": "it", "gl": "IT", "ceid": "IT:it"})

FEEDS = [
    ("ANSA", "https://www.ansa.it/sito/notizie/cronaca/cronaca_rss.xml"),
    ("ANSA", "https://www.ansa.it/sito/notizie/economia/economia_rss.xml"),
    ("ANSA", "https://www.ansa.it/sito/notizie/politica/politica_rss.xml"),
    ("ANSA", "https://www.ansa.it/sito/ansait_rss.xml"),
    ("Google News", gnews("corteo")),
    ("Google News", gnews("cortei")),
    ("Google News", gnews("manifestazione piazza")),
    ("Google News", gnews("presidio protesta")),
    ("Google News", gnews("sciopero manifestazione")),
    ("Google News", gnews("cariche polizia manifestanti")),
]

# ---------------------------------------------------------------- lessico
PROTESTA = re.compile(
    r"\b(cortei|corteo|manifestazion[ei]|manifestant[ei]|presidi|presidio|sit-in|"
    r"fiaccolat[ae]|mobilitazion[ei]|sciopero|scioperi|protesta|proteste|in piazza|"
    r"occupat[aeio]|occupazion[ei]|blocco stradale|bloccat[aeio]|cariche|scontri|tensioni)\b", re.I)

# indizi che il fatto è già avvenuto o in corso
ACCADUTO = re.compile(
    r"\b(partit[oaie]|in corso|sfila(no)?|hanno sfilato|in migliaia|migliaia in piazza|centinaia in piazza|"
    r"è arrivat[oa]|si è concluso|si sono radunati|radunat[ie]|in piazza oggi|oggi in piazza|"
    r"cariche|caricat[ie]|scontri|tensioni|lacrimogeni|fermat[ie]|arrestat[ie]|feriti?|bloccat[aeio]|"
    r"occupat[aeio]|diretta|live)\b", re.I)
# indizi che è solo annunciato
ANNUNCIATO = re.compile(
    r"\b(domani|dopodomani|prossim[oa]|si terrà|si svolgerà|è previst[oa]|sono previst[ie]|previst[oi] per|"
    r"in programma|annunciat[oa]|annuncia(no)?|convocat[oa]|appuntamento|percorso|orari|"
    r"come cambia|cosa sapere|chi si ferma|lunedì|martedì|mercoledì|giovedì|venerdì|sabato|domenica)\b", re.I)
TENSIONI = re.compile(
    r"\b(cariche|caricat[ie]|scontri|tensioni|lacrimogeni|idranti|fermat[ie]|arrestat[ie]|denunciat[ie]|"
    r"feriti?|contus[ie]|lancio di|bombe carta|vetrine)\b", re.I)


# ---------------------------------------------------------------- utilità
def carica_citta():
    out = []
    with open(DATI / "citta.csv", encoding="utf-8") as fh:
        for r in csv.DictReader(fh, delimiter=";"):
            nomi = [r["citta"]] + [a for a in r["alias"].split(",") if a.strip()]
            # maiuscola obbligatoria e confini di parola: "Lodi" sì, "lodi" no
            pat = r"(?<![\w’'])(" + "|".join(re.escape(n.strip()) for n in nomi) + r")(?![\w])"
            out.append(dict(r, rx=re.compile(pat), ambigua=r["ambigua"] == "1"))
    return out


def pulisci(t):
    t = html.unescape(re.sub(r"<[^>]+>", " ", t or ""))
    return re.sub(r"\s+", " ", t).strip()


def scarica(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Radar-QN analisi notizie)"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read()


def data_di(s):
    if not s:
        return None
    try:
        d = parsedate_to_datetime(s)
    except (TypeError, ValueError):
        try:
            d = datetime.fromisoformat(s.replace("Z", "+00:00"))
        except ValueError:
            return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def leggi_feed(nome, url):
    root = ET.fromstring(scarica(url))
    ns = {"a": "http://www.w3.org/2005/Atom"}
    voci = root.findall(".//item") or root.findall(".//a:entry", ns)
    for it in voci:
        def t(tag):
            el = it.find(tag) if not tag.startswith("a:") else it.find(tag, ns)
            return el.text if el is not None else ""
        titolo = pulisci(t("title") or t("a:title"))
        link = t("link") or (it.find("a:link", ns).get("href") if it.find("a:link", ns) is not None else "")
        testo = pulisci(t("description") or t("a:summary"))
        quando = data_di(t("pubDate") or t("a:updated") or t("a:published"))
        testata = nome
        src = it.find("source")
        if src is not None and src.text:
            testata = src.text.strip()
        elif nome == "Google News" and " - " in titolo:
            testata = titolo.rsplit(" - ", 1)[1]
        if nome == "Google News" and " - " in titolo:
            titolo = titolo.rsplit(" - ", 1)[0]
        yield dict(titolo=titolo, testo=testo, url=link.strip(), quando=quando, testata=testata)


def segnale(testo):
    acc, ann = bool(ACCADUTO.search(testo)), bool(ANNUNCIATO.search(testo))
    if acc and not ann:
        return "accaduto"
    if ann and not acc:
        return "annunciato"
    return "da capire"


# ---------------------------------------------------------------- analisi
def analizza(ore):
    citta = carica_citta()
    gia = set()
    if (DATI / "cortei.csv").exists():
        with open(DATI / "cortei.csv", encoding="utf-8") as fh:
            gia = {r["citta"] for r in csv.DictReader(fh, delimiter=";")}
    limite = datetime.now(timezone.utc) - timedelta(hours=ore)
    visti, righe, errori = set(), [], []

    for nome, url in FEEDS:
        try:
            voci = list(leggi_feed(nome, url))
        except Exception as e:  # una fonte giù non deve fermare le altre
            errori.append(f"{nome}: {url[:70]}… → {e}")
            continue
        for v in voci:
            chiave = re.sub(r"\W+", "", v["titolo"].lower())[:90]
            if chiave in visti or (v["quando"] and v["quando"] < limite):
                continue
            testo = v["titolo"] + ". " + v["testo"]
            if not PROTESTA.search(testo):
                continue
            visti.add(chiave)
            trovate = [c for c in citta if c["rx"].search(testo)]
            for c in trovate or [None]:
                righe.append({
                    "citta": c["citta"] if c else "",
                    "sigla": c["sigla"] if c else "",
                    "lat": c["lat"] if c else "",
                    "lon": c["lon"] if c else "",
                    "segnale": segnale(testo),
                    "tensioni": "sì" if TENSIONI.search(testo) else "",
                    "nome_ambiguo": "sì" if c and c["ambigua"] else "",
                    "gia_in_mappa": "sì" if c and c["citta"] in gia else "",
                    "pubblicato": v["quando"].astimezone().strftime("%d/%m %H:%M") if v["quando"] else "",
                    "testata": v["testata"],
                    "titolo": v["titolo"],
                    "url": v["url"],
                })

    righe.sort(key=lambda r: (r["citta"] == "", r["citta"], r["pubblicato"]), reverse=False)
    campi = list(righe[0].keys()) if righe else ["citta"]
    with open(DATI / "candidati.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=campi, delimiter=";")
        w.writeheader()
        w.writerows(righe)

    # riepilogo in console
    print(f"\nNotizie pertinenti nelle ultime {ore} ore: {len(visti)}  →  data/candidati.csv\n")
    per_citta = {}
    for r in righe:
        per_citta.setdefault(r["citta"] or "(nessuna città riconosciuta)", []).append(r)
    for nome in sorted(per_citta, key=lambda k: (k.startswith("("), k)):
        rr = per_citta[nome]
        stato = "in mappa" if rr[0]["gia_in_mappa"] else "NUOVA"
        print(f"■ {nome}  [{stato}]" + ("  ⚠ nome ambiguo: controllare" if rr[0]["nome_ambiguo"] else ""))
        for r in rr[:6]:
            flag = " ⚠tensioni" if r["tensioni"] else ""
            print(f"   {r['pubblicato']:>11}  {r['segnale']:<10}{flag}  {r['testata']}: {r['titolo'][:110]}")
        if len(rr) > 6:
            print(f"   … altre {len(rr) - 6} in candidati.csv")
    if errori:
        print("\nFonti non raggiunte:")
        for e in errori:
            print("  -", e)
    print("\nRicorda: ogni segnalazione va aperta e verificata prima di entrare in data/cortei.csv.")


# ---------------------------------------------------------------- verifica prima di pubblicare
def verifica():
    nomi = set()
    with open(DATI / "citta.csv", encoding="utf-8") as fh:
        nomi = {r["citta"] for r in csv.DictReader(fh, delimiter=";")}
    problemi, n = [], 0
    with open(DATI / "cortei.csv", encoding="utf-8") as fh:
        rd = csv.DictReader(fh, delimiter=";")
        attese = ["citta", "stato", "avvenimenti", "fonti", "link", "aggiornato"]
        if rd.fieldnames != attese:
            problemi.append(f"intestazione: attesa {';'.join(attese)}")
        visti = set()
        for i, r in enumerate(rd, start=2):
            n += 1
            c = r.get("citta", "")
            if c not in nomi:
                problemi.append(f"riga {i}: «{c}» non è in data/citta.csv (aggiungila con le coordinate)")
            if c in visti:
                problemi.append(f"riga {i}: «{c}» compare due volte: un punto per città")
            visti.add(c)
            if r.get("stato") not in ("in corso", "annunciato", "concluso"):
                problemi.append(f"riga {i} {c}: stato deve essere «in corso», «annunciato» o «concluso»")
            if not r.get("avvenimenti", "").strip():
                problemi.append(f"riga {i} {c}: nessun avvenimento")
            if not r.get("fonti", "").strip():
                problemi.append(f"riga {i} {c}: manca la fonte")
            testo = r.get("avvenimenti", "")
            # regola Radar per questa mappa: nel testo pubblico niente numeri e niente testate
            if re.search(r"\d", testo):
                problemi.append(f"riga {i} {c}: negli avvenimenti ci sono cifre (stime, orari): toglierle")
            for t in [x.strip() for x in r.get("fonti", "").split(",") if x.strip()]:
                if re.search(r"\b" + re.escape(t) + r"\b", testo, re.I):
                    problemi.append(f"riga {i} {c}: negli avvenimenti è citata la testata «{t}»")
            link = r.get("link", "").split()
            if not link or not all(l.startswith("http") for l in link):
                problemi.append(f"riga {i} {c}: serve almeno un link verificabile alla fonte")
            if not re.fullmatch(r"\d{2}/\d{2}/\d{4} \d{2}:\d{2}", r.get("aggiornato", "")):
                problemi.append(f"riga {i} {c}: aggiornato = ora della verifica, nel formato gg/mm/aaaa hh:mm")
    print(f"Righe controllate: {n}")
    print("\n".join("  ✗ " + p for p in problemi) if problemi else "  ✓ Nessun problema formale. Il controllo dei fatti resta della redazione.")
    return 1 if problemi else 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ore", type=int, default=12, help="finestra temporale in ore (predefinito 12)")
    ap.add_argument("--verifica", action="store_true", help="controlla data/cortei.csv e termina")
    a = ap.parse_args()
    sys.exit(verifica() if a.verifica else analizza(a.ore))
