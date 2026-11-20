# Cortei in Italia – Radar QN

Mappa interattiva delle manifestazioni in corso o annunciate, città per città. Nel tooltip ci sono lo stato (in corso o annunciata) e gli avvenimenti principali: niente numeri e niente nomi di testate.

- Mappa: `mappa/index.html` → https://cosimofire.github.io/cortei-italia/mappa/
- Indice con anteprime e codice per il CMS: https://cosimofire.github.io/cortei-italia/
- Dati letti dalla mappa: `data/cortei.csv` (**solo righe verificate dalla redazione**)

## Come funziona

La mappa non pubblica in automatico quello che trova nelle notizie: la catena è in tre passaggi.

```
RSS testate ──► strumenti/analizza_notizie.py ──► data/candidati.csv   (segnalazioni da verificare)
                                                         │
                                         lettura e verifica sulle fonti originali
                                                         ▼
                                                  data/cortei.csv  ──► mappa/index.html
```

1. **Analisi** (`python strumenti/analizza_notizie.py --ore 12`)
   - legge i feed RSS di ANSA e le ricerche di Google News (corteo, cortei, manifestazione, presidio, sciopero, cariche);
   - tiene solo le notizie che parlano di proteste e toglie i doppioni;
   - riconosce le città con il dizionario `data/citta.csv` (capoluoghi più alcune città, coordinate controllate dentro i confini provinciali ISTAT). I nomi che sono anche parole comuni (Bari, Como, Lodi, Prato, Latina, Fermo…) sono segnalati come «ambigui»;
   - classifica ogni notizia come `accaduto`, `annunciato` o `da capire` in base al lessico, e segnala le parole che indicano tensioni (cariche, scontri, fermi). **È un indizio, non un giudizio**: titoli come «Il corteo in centro» non dicono se è già partito;
   - scrive `data/candidati.csv` e stampa un riepilogo per città, con le città **NUOVE** (non ancora sulla mappa) in evidenza.
2. **Verifica redazionale**: per ogni città si aprono le notizie e si scrive la riga di `data/cortei.csv`:

   | colonna | contenuto |
   |---|---|
   | `citta` | nome come in `data/citta.csv` (un punto per città) |
   | `stato` | `in corso` se almeno una fonte racconta che la manifestazione si sta svolgendo, `annunciato` se c'è solo il programma, `concluso` |
   | `avvenimenti` | frasi brevi separate da ` \| `, **senza cifre** (né stime né orari) e **senza nomi di testate**. Si scrive solo ciò che le fonti riportano come fatto |
   | `fonti` | testate, separate da virgola (uso interno, non mostrate) |
   | `link` | URL delle notizie, separati da spazio (non mostrati, servono per il controllo) |
   | `aggiornato` | ora della verifica redazionale, `gg/mm/aaaa hh:mm` |

3. **Controllo formale** prima di pubblicare: `python strumenti/analizza_notizie.py --verifica` (città esistente, stato valido, fonte e link presenti, data nel formato giusto, nessuna cifra e nessuna testata negli avvenimenti).

Una città che non c'è nel dizionario si aggiunge a `data/citta.csv` e si ricontrolla con `python strumenti/prepara_confini.py <province.geojson>`, che segnala le coordinate fuori dalla provincia.

## Regole di rigore applicate

- Pallino pieno solo se almeno una fonte racconta lo svolgimento; altrimenti pallino vuoto («annunciata»).
- Nel testo pubblico niente numeri (stime di partecipazione, orari) e niente testate: le fonti restano nelle colonne `fonti` e `link`, per il controllo interno.
- Quando le fonti non concordano su un dettaglio, il dettaglio non entra.
- Le cariche, i fermi o i feriti entrano solo con una fonte che li riporti come fatto, non come voce.
- La nota sotto la mappa chiarisce che non è l'elenco completo delle piazze.

## File

- `strumenti/analizza_notizie.py`: analisi delle notizie e controllo del CSV (solo libreria standard Python).
- `strumenti/compila_20nov.py`: la compilazione del 20 novembre 2026, con i testi scritti dopo la lettura delle fonti (esempio di come si costruisce `cortei.csv`; non rieseguirlo durante gli aggiornamenti, sovrascriverebbe il CSV).
- `strumenti/conteggio.py`: scrive `conteggio.md`, le cinque righe con i numeri aggregati, calcolate da `data/cortei.csv`.
- `strumenti/AGGIORNAMENTO.md`: la procedura dell'aggiornamento orario (20 novembre, fino alle 20).
- `strumenti/prepara_confini.py`: confini regionali semplificati (`data/regioni.json`) e controllo delle coordinate.
- `assets/`: stile e funzioni condivise Radar.

`data/candidati.csv` (le segnalazioni grezze dello script) non è pubblicato: si rigenera in locale.

Fonte dei confini: ISTAT, limiti amministrativi delle province 2023.
