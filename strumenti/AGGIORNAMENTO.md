# Aggiornamento ogni 30 minuti della mappa dei cortei (20 novembre 2026, dalle 12 alle 20)

Cartella: `C:\Users\cosim\Desktop\Claude\cortei-italia` · repo `CosimoFire/cortei-italia` (GitHub Pages da `main`).
La mappa online legge `data/cortei.csv`. **Non eseguire mai `strumenti/compila_20nov.py`**: riscriverebbe il CSV con la situazione delle 11.

## Passi

1. `git pull --rebase`, poi `python strumenti/analizza_notizie.py --ore 2` → aggiorna `data/candidati.csv` e stampa il riepilogo (città NUOVE e già in mappa).
2. Per ogni città **NUOVA** e per ogni città già in mappa con `stato` = `annunciato`: apri le notizie (link in `candidati.csv`, o ricerca web) e leggi il testo, non solo il titolo.
   - Nuova città con manifestazione confermata dalla notizia → aggiungi una riga. Se manca in `data/citta.csv`, aggiungila con coordinate controllate (`python strumenti/prepara_confini.py ../auto-cinesi-province/dati/province_2023.geojson` deve dare 0 errori).
   - Città annunciata che risulta svolta → `stato` = `in corso` (o `concluso` se la fonte dice che è finita) e aggiorna gli avvenimenti.
   - Città già in corso: aggiorna gli avvenimenti solo con fatti nuovi rilevanti (conclusione, comizio, blocchi, tensioni).
3. Regole per `avvenimenti` (testo pubblico):
   - massimo tre frasi brevi separate da ` | `;
   - **nessuna cifra** (né stime, né orari) e **nessun nome di testata**;
   - solo ciò che una fonte riporta come fatto; se due fonti divergono su un dettaglio, il dettaglio non entra;
   - cariche, scontri, fermi, feriti solo se riportati come fatto da una testata (non voci, non post social).
   - In `fonti` le testate e in `link` gli URL (uso interno). `aggiornato` = ora della tua verifica (`gg/mm/aaaa hh:mm`).
4. `python strumenti/analizza_notizie.py --verifica` deve dire «Nessun problema formale».
5. `python strumenti/conteggio.py` → riscrive `conteggio.md` (le cinque righe con i numeri aggregati).
6. Se `data/cortei.csv` o `conteggio.md` sono cambiati: `git add data/cortei.csv data/citta.csv conteggio.md` e commit «Aggiornamento cortei ore HH:MM», poi `git push`. Identità git già impostata in locale (noreply), non cambiarla.
7. Controlla dopo un paio di minuti che `https://cosimofire.github.io/cortei-italia/mappa/` risponda e che `https://cosimofire.github.io/cortei-italia/data/cortei.csv` contenga le nuove righe.
8. Rapporto finale breve: città aggiunte, città passate da annunciate a in corso, eventuali tensioni, il testo di `conteggio.md`, e ciò che non hai potuto verificare.

Se le fonti non si raggiungono o non c'è niente di nuovo, non pubblicare nulla e dillo nel rapporto.
