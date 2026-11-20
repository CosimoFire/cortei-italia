# Compilazione redazionale del 20/11/2026: testi scritti a mano dopo la lettura delle fonti.
# Scrive data/cortei.csv. I link delle notizie locali sono presi da data/candidati.csv
# (uscita di analizza_notizie.py) cercando il titolo, per non ricopiarli a mano.
# Regole dei testi: niente numeri (né stime, né orari) e niente nomi di testate.
# Fonti e link restano nelle colonne fonti/link per il controllo interno: la mappa non li mostra.
import csv, sys
from datetime import datetime
VERIFICA = datetime.now().strftime("%d/%m/%Y %H:%M")  # ora della verifica redazionale
sys.stdout.reconfigure(encoding="utf-8")
C = list(csv.DictReader(open("data/candidati.csv", encoding="utf-8"), delimiter=";"))
def g(frammento):
    for r in C:
        if frammento in r["titolo"]: return r["url"]
    raise SystemExit("link non trovato: " + frammento)
SKY = "https://tg24.sky.it/cronaca/2026/11/20/sciopero-oggi-20-novembre-diretta"
SKYP = "https://tg24.sky.it/cronaca/2026/11/18/sciopero-20-novembre-2026-manifestazioni-cortei-proteste"
FQL = "https://www.ilfattoquotidiano.it/cronaca/live-post/2026/11/20/sciopero-generale-cortei-italia-oggi-diretta/8578220/"
FQ = "https://www.ilfattoquotidiano.it/2026/11/19/sciopero-generale-cgil-studenti-venerdi-20-novembre-cosa-si-ferma-perche-protesta-notizie/8577223/"
AK = "https://www.adnkronos.com/cronaca/sciopero-generale-20-novembre-2026-diretta_3u6CoOImHMPXfKkNV4xx2g"
AKC = "https://www.adnkronos.com/economia/sciopero-generale-20-novembre-cortei-cobas_3RCqdxrPkZa9aA6L9TMl28"
ANSA = "https://www.ansa.it/sito/notizie/economia/2026/11/20/oggi-lo-sciopero-in-piazza-lavoratori-e-studenti.-cgil-la-manovra-va-cambiata_01d5c5ed-72b4-4546-acc1-472847a25848.html"
IC, AN = "in corso", "annunciato"
R = [
 ("Roma", IC, [
   "Corteo nazionale della Cgil partito da piazza Vittorio Emanuele II verso via dei Fori Imperiali, con Maurizio Landini in testa",
   "Corteo degli studenti partito da Porta San Paolo (Piramide) verso il Colosseo. Da piazzale Aldo Moro, alla Sapienza, annunciati il corteo universitario e quello dei Cobas verso il ministero dell'Istruzione",
   "Il collettivo Cambiare Rotta ha occupato il dipartimento di Fisica della Sapienza. Previsti presìdi in piazza Santi Apostoli e davanti al ministero"],
   "Adnkronos, Sky TG24, Il Fatto Quotidiano, ANSA", [AK, SKY, FQL, ANSA]),
 ("Milano", IC, [
   "Corteo degli studenti partito da largo Cairoli e diretto in piazza Duomo",
   "Corteo provinciale della Cgil da piazzale Cadorna, che per un tratto si unisce a quello degli studenti. Comizio in piazza XXV Aprile con Maria Grazia Gabrielli (segreteria nazionale Cgil)",
   "Slogan contro guerra, riarmo e legge di Bilancio"],
   "Sky TG24, Il Fatto Quotidiano, Corriere della Sera", [SKY, FQL, FQ, g("Milano contro il carovita")]),
 ("Torino", IC, [
   "Corteo della Cgil partito dalla zona di Porta Susa (piazza XVIII Dicembre) e diretto in piazza Solferino, dove parla Luigi Giove (Cgil)",
   "Nello spezzone sociale movimenti, universitari e realtà vicine al centro sociale Askatasuna. Chiusi gli accessi alla stazione di Porta Susa, treni regolari",
   "Annunciati il corteo dei collettivi studenteschi Cambiare Rotta e Osa da piazza Arbarello e, in serata, un presidio contro il riarmo in piazza Castello"],
   "ANSA, Sky TG24, Il Fatto Quotidiano", [g("Migliaia in piazza a Torino"), g("Spezzone sociale corteo Torino"), SKY, FQL]),
 ("Genova", IC, [
   "Corteo della Cgil partito dalla Stazione Marittima e diretto in Prefettura. Interviene Alessandro Pagano, segretario della Camera del lavoro",
   "Studenti dei collettivi Osa e Cambiare Rotta in corteo da piazza De Ferrari a piazza Corvetto, insieme ai portuali del Calp"],
   "ANSA, Sky TG24, Il Fatto Quotidiano", [g("partito il corteo Cgil a Genova"), SKY, FQL]),
 ("Bologna", IC, [
   "Corteo della Cgil partito da piazza dei Martiri verso il centro, con Michele De Palma (Cgil)",
   "In prima fila i lavoratori della Kemet di Sasso Marconi, i cui posti di lavoro sono a rischio. In corteo il sindaco Matteo Lepore e il presidente della Regione Michele de Pascale",
   "Sindacati di base e collettivi studenteschi sfilano su percorsi separati. Presidio dei Cobas Scuola davanti all'Ufficio scolastico regionale"],
   "Sky TG24, Il Fatto Quotidiano, Adnkronos", [SKY, FQL, FQ, AKC]),
 ("Napoli", IC, [
   "Corteo di studenti e Cgil partito da piazza Mancini dietro lo striscione «Fight for our future, not their wars». Arrivo in piazza Matteotti, dove parla Susy Esposito (Fisac Cgil)",
   "Segnalato un secondo corteo di studenti e Usb. Anche i Cobas avevano annunciato il concentramento in piazza Mancini"],
   "Sky TG24, Il Fatto Quotidiano, Corriere del Mezzogiorno, Adnkronos", [SKY, FQL, g("Sciopero a Napoli, due cortei"), AKC]),
 ("Perugia", IC, [
   "Corteo provinciale della Cgil da piazza Partigiani a piazza IV Novembre, dove confluiscono altri cortei",
   "Comizio annunciato di Daniela Barbaresi (Cgil)"],
   "ANSA, Sky TG24", [g("quasi un migliaio in corteo a Perugia"), SKY, SKYP]),
 ("Aosta", IC, [
   "Lavoratori e studenti in corteo dalla Cogne Acciai Speciali (via Paravera) a piazza Deffeyes, con interventi davanti alla Regione"],
   "ANSA, Sky TG24", [g("in corteo ad Aosta"), SKY]),
 ("Potenza", IC, [
   "Corteo della Cgil partito da piazza XVIII Agosto verso piazza Matteotti. Intervengono Antonio Pepe (Filctem-Cgil) e Vincenzo Esposito (Cgil Potenza)"],
   "Sky TG24", [SKY, SKYP]),
 ("Matera", IC, [
   "Mobilitazione in contemporanea con il corteo di Potenza. Percorso e partecipazione non sono indicati"],
   "Sky TG24", [SKY]),
 ("Reggio Emilia", IC, [
   "Corteo di lavoratori e studenti. Dalla piazza Samuele Lodi (Fiom-Cgil): «Non dobbiamo investire sulle armi, ma sul futuro del nostro Paese»"],
   "Sky TG24, Stampa Reggiana", [SKY, g("a Reggio Emilia il corteo di lavoratori e studenti")]),
 ("Modena", IC, ["Cgil e studenti in corteo contro carovita e riarmo"], "ModenaToday", [g("quasi 4mila")]),
 ("Parma", IC, ["Partito il corteo per lo sciopero generale"], "ParmaDaily", [g("anche a Parma")]),
 ("Piacenza", IC, ["Corteo della Cgil in centro, con musica, contro il carovita. Tra gli slogan «Tassate i paperoni»"],
   "Piacenzasera", [g("Musica e corteo")]),
 ("Padova", IC, ["Il corteo dello sciopero generale sfila in centro"], "Il Mattino di Padova", [g("sfila il corteo in centro a Padova")]),
 ("Treviso", IC, ["Lavoratori, studenti e pensionati in corteo. Annunciato l'intervento di Lara Ghiglione (Cgil)"],
   "Tribuna di Treviso, Sky TG24", [g("A Treviso lavoratori"), SKYP]),
 ("Trento", IC, ["Corteo regionale di Cgil e studenti partito da via Verdi, ha attraversato il centro passando per via Rosmini"],
   "ANSA, L'Adige", [g("corteo della Cgil e degli studenti a Trento"), g("il corteo attraversa via Rosmini")]),
 ("Udine", IC, ["Studenti in piazza contro le guerre e i tagli alla scuola"], "UdineToday", [g("Studenti in piazza a Udine")]),
 ("Varese", IC, ["Lavoratori e studenti in corteo dalla stazione, con lo slogan della Cgil «Il futuro è adesso»"],
   "VareseNews", [g("Lavoratori e studenti in corteo a Varese"), g("a Varese il corteo sta per partire")]),
 ("Brescia", IC, ["Cortei per le strade della città. I Cobas avevano annunciato il concentramento in piazza Cesare Battisti"],
   "Giornale di Brescia, Adnkronos", [g("sono due i cortei per le strade di Brescia"), AKC]),
 ("Mantova", IC, ["Corteo per lo sciopero generale in centro, con divieti e deviazioni al traffico"], "Gazzetta di Mantova",
   [g("Il corteo dello sciopero generale del 20 novembre a Mantova"), g("ecco i divieti e le deviazioni")]),
 ("Alessandria", IC, ["Molti giovani in piazza contro il carovita e la legge di Bilancio"], "La Stampa", [g("molti giovani in piazza ad Alessandria")]),
 ("Siena", IC, ["Il presidente della Toscana Eugenio Giani alla testa del corteo per lo sciopero generale"], "La Nazione", [g("Giani guida")]),
 ("Pisa", IC, ["Occupato il Polo Carmignani dell'Università. I Cobas avevano annunciato un corteo con gli studenti da piazza Guerrazzi"],
   "PisaToday, Adnkronos", [g("Polo Carmignani"), AKC]),
 ("L'Aquila", IC, ["Manifestazione partita da Colle Sapone"], "News Town", [g("in centinaia alla manifestazione")]),
 ("Bari", IC, [
   "Studenti dei collettivi Cambiare Rotta e Osa in corteo dietro lo slogan «Il presente in frantumi»",
   "Annunciati il corteo della Cgil da piazza Giovanni XXIII a piazza del Carmine e quello dei Cobas da piazza Federico II di Svevia"],
   "ANSA, Sky TG24, Adnkronos", [g("Cambiare rotta e Osa in corteo a Bari"), SKYP, AKC]),
 ("Palermo", IC, ["Partito sulle note di «Bella ciao» il corteo annunciato da piazza Marina a piazza Verdi. Annunciato l'intervento di Serena Sorrentino (Cgil)"],
   "la Repubblica, Sky TG24", [g("Bella Ciao"), SKYP]),
 ("Reggio Calabria", IC, ["Al via il corteo della Cgil per salari più alti e lavoro stabile"], "Il Reggino", [g("A Reggio al via il corteo")]),
 ("Cosenza", IC, ["Presìdi in mattinata: studenti e lavoratori si uniranno poi in corteo. I Cobas avevano annunciato la partenza da piazza Loreto"],
   "Gazzetta del Sud, Adnkronos", [g("due presìdi in mattinata"), AKC]),
 ("Catanzaro", AN, ["Corteo della Cgil annunciato da piazza Matteotti a piazza Luigi Rossi"], "Sky TG24, LaC News24", [SKYP, g("da Catanzaro a Reggio")]),
 ("Firenze", AN, ["Annunciati il corteo della Cgil da piazza dell'Indipendenza, con Gesmundo (Cgil), e quello dei Cobas da piazza Bambini di Beslan"],
   "Sky TG24, Adnkronos, la Repubblica, Corriere Fiorentino", [SKYP, AKC, g("due cortei a Firenze"), g("Cresce la mobilitazione")]),
 ("Cagliari", AN, ["Manifestazione regionale della Cgil annunciata in piazza Giovanni XXIII, con Christian Ferrari (Cgil)"],
   "Sky TG24, Vistanet", [SKYP, g("manifestazione regionale a Cagliari")]),
 ("Trieste", AN, ["Corteo regionale della Cgil annunciato dal giardino pubblico di via Giulia"], "Sky TG24, RaiNews", [SKYP, g("a Trieste la manifestazione regionale")]),
 ("Mestre", AN, ["Corteo della Cgil annunciato dalla stazione di Mestre. Segnalati cortei anche a Venezia"],
   "Sky TG24, VeneziaToday", [SKYP, g("cortei a Mestre e Venezia")]),
 ("Ancona", AN, ["Corteo della Cgil annunciato da piazza Pertini a piazza del Plebiscito"], "Sky TG24", [SKYP]),
 ("Isernia", AN, ["Manifestazione della Cgil annunciata in piazza della Repubblica"], "Sky TG24", [SKYP]),
 ("Pescara", AN, ["Annunciati un corteo sindacale e uno studentesco"], "IlPescara", [g("due cortei in città il 20 novembre")]),
 ("Verona", AN, ["Corteo annunciato con partenza dalla stazione"], "L'Arena", [g("Corteo dalla stazione")]),
 ("Novara", AN, ["Corteo della Cgil annunciato in centro, dedicato alle crisi aziendali del territorio"], "La Stampa", [g("A Novara in piazza")]),
 ("Como", AN, ["Annunciati più cortei in città"], "QuiComo, La Provincia di Como", [g("a Como tre cortei"), g("mattinata di proteste a Como")]),
 ("Livorno", AN, ["Cortei di studenti e lavoratori annunciati contro riarmo e carovita"], "LivornoToday", [g("oggi a Livorno i cortei")]),
 ("Lucca", AN, ["Annunciati dai Cobas un concentramento sindacale in piazzale Verdi e uno studentesco in piazza San Michele"], "Adnkronos", [AKC]),
 ("Viterbo", AN, ["Corteo di Cobas e studenti annunciato da Porta Romana"], "Adnkronos", [AKC]),
 ("Brindisi", AN, ["Corteo dei Cobas annunciato con partenza dalla stazione"], "Adnkronos", [AKC]),
 ("San Salvo", AN, ["Presidio di Cobas e studenti annunciato in mattinata, con un possibile corteo"], "Adnkronos", [AKC]),
 ("Ravenna", AN, ["Corteo della Cgil annunciato contro il carovita"], "Settesere", [g("tre cortei a Ravenna")]),
 ("Forlì", AN, ["Corteo della Cgil annunciato contro la legge di Bilancio"], "Settesere, ForlìToday", [g("tre cortei a Ravenna"), g("il corteo contro la legge di bilancio")]),
 ("Rimini", AN, ["Corteo della Cgil annunciato contro il carovita"], "Settesere", [g("tre cortei a Ravenna")]),
 ("Cuneo", AN, ["Manifestazione annunciata per lo sciopero generale"], "Unione Monregalese", [g("anche a Cuneo")]),
 ("Enna", AN, ["Corteo annunciato per lo sciopero generale"], "StartNews", [g("Corteo anche a Enna")]),
 ("Ascoli Piceno", AN, ["Manifestazione annunciata per la Palestina e contro il riarmo"], "La Nuova Riviera", [g("per la Palestina")]),
 ("Vibo Valentia", AN, ["Corteo della Cgil annunciato contro la manovra"], "Il Vibonese", [g("anche a Vibo")]),
]
with open("data/cortei.csv", "w", encoding="utf-8", newline="") as fh:
    w = csv.writer(fh, delimiter=";", quoting=csv.QUOTE_MINIMAL)
    w.writerow(["citta", "stato", "avvenimenti", "fonti", "link", "aggiornato"])
    for citta, stato, ev, fonti, link in R:
        assert all(";" not in e and "|" not in e for e in ev), citta
        w.writerow([citta, stato, " | ".join(ev), fonti, " ".join(link), VERIFICA])
print(len(R), "righe,", sum(1 for r in R if r[1] == IC), "in corso")
