# Salamai — Checklist di controllo PRIMA della prima messa in tensione

**Stato:** bozza per doppia revisione ChatGPT + Claude Code; **non è un verbale di collaudo né una certificazione di sicurezza**.  
**Data bozza:** 27/10/2026  
**Impianto:** quadro di controllo camera asciugatura salami, 230 V AC + 12 V DC.

## Uso della checklist

- Compilare **a quadro completamente disalimentato**, con linea di alimentazione sezionata a monte e assenza di tensione accertata mediante strumento idoneo.
- **[B] Bloccante**: un `NO`, una verifica non eseguita o un dato ignoto **impediscono la prima alimentazione dell'insieme interessato**. Non segnare `OK` per deduzione.
- **[T] Tecnico abilitato/competente**: controllo strumentale o valutazione elettrica su circuiti a 230 V da demandare a persona qualificata. Non eseguire prove di isolamento su elettronica collegata.
- **[C] Consigliato**: migliora affidabilità/manutenzione, senza sostituire i controlli bloccanti.
- Annotare `OK / NO / N.A.`, valori misurati, data ed eventuale foto o numero del morsetto. In caso di `NO`, indicare la correzione e ripetere il controllo.
- Questa checklist termina **prima** della messa in tensione. La prova funzionale in tensione (prima 12 V, poi 230 V, poi carichi uno per volta) richiede un **piano di collaudo separato**.

**Attenzione alle revisioni:** la versione del repository GitHub consultata il 27/10/2026 conserva ancora riferimenti a Cat6 FTP, presa CEE e nessun F1/F2; le modifiche locali non committate possono essere successive. La checklist segue le decisioni discusse: Cat5e UTP 24 AWG, W1 diretto alla stufa, F1/F2, soppressione bobine integrata. Prima dell'uso riconciliare tutto con lo **schema realmente assemblato**.

### Registro

| Campo | Valore |
|---|---|
| Revisione schema-quadro.html usata | |
| Revisione scatola-x6.html usata | |
| Revisione distinta base usata | |
| Data e luogo verifica | |
| Esecutore controllo meccanico / 12 V | |
| Tecnico responsabile verifiche 230 V | |
| Esito finale | ☐ NON AUTORIZZATO ☐ AUTORIZZATO dopo chiusura di tutti i bloccanti |

## A. Documentazione, componenti e stato sicuro

- [ ] **[B] A01** Confrontato il cablaggio **filo per filo** con l'ultima versione degli schemi, non con documenti storici: sigle Q1, T1, A1, A3, D1, X0/X2/X3, KM1–KM6, W1/W3/W5/W6, X6, F1/F2.
- [ ] **[B] A02** Risolte tutte le differenze tra schemi e distinta base (Cat5e UTP al posto di Cat6 FTP; niente schermature; cavo stufa W1 diretto; F1/F2 introdotti; bobine con diodo interno senza diodi esterni).
- [ ] **[B] A03** Trovati e letti i dati di targa dei componenti effettivamente montati; tensione/corrente previste compatibili con l'impiego e con i collegamenti.
- [ ] **[B] A04 [T]** Linea di rete sezionata **a monte del quadro**; verificata l'assenza di tensione, compresi i morsetti d'ingresso che possono restare attivi se si apre solo Q1.
- [ ] **[C] A05** Identificati e marcati cavi e morsetti; nessun conduttore spellato libero o trattenuto soltanto dal rame.

## B. Armadio, guide, canaline e connessioni

- [ ] **[B] B01** Alimentatore, relè, contattori, contatore, morsetti e portafusibili fissati; guide, finecorsa/fermi, coperture, distanze e accessibilità corretti.
- [ ] **[B] B02** Collegamenti a 230 V separati dai segnali/12 V secondo caratteristiche d'isolamento, percorso e distanze; nessun filo a bassa tensione con isolamento inadatto mescolato ai 230 V.
- [ ] **[B] B03** Sezioni, tipi di cavo e terminali adatti al relativo morsetto; un solo conduttore per foro salvo esplicita autorizzazione del produttore; puntalini crimpati e serrati correttamente.
- [ ] **[B] B04 [T]** Catena di alimentazione KM1–KM6 con puntalini doppi 2×1,5 mm² e morsetti realmente compatibili: verifica non limitata al fatto che il puntalino entra o sembra tenere.
- [ ] **[B] B05** Pressacavi/fermacavi presenti e serrati, cavi protetti da tagli, spigoli, trazione, condensa e zone calde; scatole in camera con ingressi adatti all'umidità.
- [ ] **[C] B06** Spazio sufficiente sulla guida 3 per F1/F2, separazione dai contattori 230 V, accesso ai fusibili e alle relative etichette.

## C. Rete 230 V, interruttore e distribuzione

- [ ] **[B][T] C01** Arrivo L/N/PE verificato: Q1 (Gewiss 1P+N C10) collegato secondo marcature; linea di alimentazione e protezione a monte idonee, compresa la verifica del differenziale 30 mA esistente.
- [ ] **[B] C02** X0: ponticelli L e N separati (gruppi 1–2 e 3–4); nessun ponte L–N o L–PE, nemmeno accidentalmente.
- [ ] **[B] C03** Eastron SDM120 inserito sul percorso fase secondo morsetti reali IN/OUT; alimentazione T1 prelevata dal ramo protetto previsto; nessun errore tra L e N.
- [ ] **[B] C04** Solo i contatti di potenza KM1–KM6 commutano la rete verso i carichi; i contatti K1–K6 della Waveshare portano **esclusivamente +12 V alle bobine**.
- [ ] **[B] C05** X2: sei uscite di fase commutate correttamente attribuite; neutri dei carichi collegati soltanto alla distribuzione N prevista; nessuno scambio con PE.
- [ ] **[B] C06** Il cablaggio W1 verso la stufa è a **cinque conduttori** (tre fasi commutate della *stessa alimentazione monofase*, N comune, PE); nessuna presa/spina CEE residua negli schemi o nel montaggio.
- [ ] **[B][T] C07 — PUNTO APERTO DI SICUREZZA** Il circuito dell'antiribaltamento S5 della stufa, previsto nelle note **sul neutro comune**, è stato riesaminato e giudicato sicuro da un tecnico qualificato, oppure riprogettato. Interrompere il solo neutro **non toglie tensione alle parti interne**: il semplice spegnimento delle lampade non supera questa verifica.
- [ ] **[B][T] C08** Approvate protezione termica, prevenzione surriscaldamento e gestione del contattore eventualmente incollato. Il contatore SDM120 può segnalare un'anomalia ma **non interrompe fisicamente** il guasto; l'assenza di termostato indipendente resta un rischio da valutare.
- [ ] **[B] C09** Verificati sulla stufa fissaggio, isolamento e tenuta del cavo vicino alle lampade/parti calde; PE fissato alla massa metallica; nessuna guaina ordinaria esposta a temperature incompatibili.

## D. Terra di protezione e involucro metallico

- [ ] **[B][T] D01** PE in arrivo X0 effettivamente collegato alla piastra, alle guide DIN e ai morsetti PE X2/X3 previsti; non confidare nella sola apparenza del contatto meccanico.
- [ ] **[B][T] D02** Misurata e registrata la continuità PE delle masse metalliche: piastra, **ogni guida**, carcassa stufa e altre masse di classe I; metodo e limiti validati dal tecnico.
- [ ] **[B] D03** PE e 0 V DC non confusi; eventuale collegamento funzionale della RS485 a PE verificato sul manuale della Waveshare, non presunto.
- [ ] **[B] D04** Con Cat5e **UTP** nessuna schermatura FTP fittizia collegata ai morsetti di terra; eventuali morsetti PE ora liberi identificati correttamente.

## E. Distribuzione 12 V e portafusibili F1/F2

- [ ] **[B] E01** Mean Well HDR-60-12 collegato alla rete su L/N; uscita +V/−V identificata e cablata senza inversioni; nessun contatto fra rete e circuito 12 V.
- [ ] **[B] E02** Su X3 ponticellati **solo** i gruppi previsti: B 1–3, A 4–6, 0 V 7–9, +12 V 10–12. Gruppi elettricamente distinti.
- [ ] **[B] E03** Waveshare, display e catena COM dei relè alimentati dal +12 V **prima dei fusibili dei rami remoti**, affinché il guasto W3/W6 non spenga tutto il quadro.
- [ ] **[B] E04** F1 interrompe **solo il +12 V verso W3**; F2 interrompe **solo il +12 V verso W6**. Nessun ponticello può bypassare F1/F2; ingressi/uscite identificati anche fisicamente.
- [ ] **[B] E05** Fusibili 5×20 mm e portafusibili UK5-HESI acquistati: verificati dati **del modello reale** (uso DC, tensione, potere d'interruzione, terminali, sezione minima, temperatura e accessori).
- [ ] **[B] E06** Correnti nominali **F1/F2 approvate** con curva tempo-corrente, assorbimenti attesi/inrush, corrente limitata dell'alimentatore e caratteristiche del cavo. **Non montare automaticamente 1 A/0,25 A: sono candidati, non valori validati.**
- [ ] **[B] E07** In W3, arancio + verde ricevono il **+12 V protetto da F1**; bianco-arancio + bianco-verde tornano allo **0 V comune**; ciascun filo da 24 AWG termina correttamente senza doppio inserimento non ammesso.
- [ ] **[B] E08** W6 ha un'unica coppia di alimentazione: +12 V **protetto da F2** e 0 V comune. W5 riceve il +12 V esclusivamente da X6, a valle di F1.
- [ ] **[B] E09** Bobine KM1–KM6: polarità +/− rispettata **in base alle marcature reali**, considerando la soppressione integrata; non aggiungere diodi esterni se già integrati.
- [ ] **[B] E10** Ognuno dei sei canali della Waveshare è collegato al contattore previsto, su contatto **NO** e non NC; identificazione univoca K1→KM1 ... K6→KM6.

## F. Cavi Cat5e, scatola X6, sensori e ventole

- [ ] **[B] F01** Cat5e UTP 4 coppie, 24 AWG: verificati sezione effettiva, materiale conduttore (rame pieno da confermare), integrità e lunghezze; nessuna schermatura trattata come conduttore.
- [ ] **[B] F02** W3: blu/bianco-blu dedicati a RS485 A/B, arancio e verde +12 V, rispettivi bianchi 0 V, marroni isolati di riserva. **Verifica alle due estremità** prima di collegare le schede.
- [ ] **[B] F03** X6: Wago 221 adatti a conduttore **rigido 24 AWG**, lunghezza di spelatura secondo modello, rame inserito fino in fondo, nessun reimpiego di trefoli o piegatura improvvisata del singolo filo.
- [ ] **[B] F04** In X6 ben distinti +12 V, 0 V, 3,3 V, RS485 A/B e segnali: nessun +12 V sui GPIO XIAO, HX711 o DS18B20; massa e alimentazione dei sensori come schema.
- [ ] **[B] F05** W5 da X6 a X4: +12 V/0 V alla coppia ventole; PWM condiviso; TACH M5 e M6 separati e riferiti alla stessa massa; pinout ventole e MOSFET verificato sul componente reale.
- [ ] **[B] F06** Polarità 12 V della breakout Seeed RS485, della sonda B1 e della sonda B5 corretta; nessun collegamento di alimentazione sui morsetti A/B RS485.
- [ ] **[B] F07** Scatole X6 e X4 asciutte, passacavi serrati, cavi fermati, guaine di sensori e cella protette, nessun contatto che possa creare corti con condensa o vibrazioni.
- [ ] **[C] F08** Resistenza terminazione bus RS485 prevista solo alle due estremità designate; indirizzi previsti B1=1, A3=2, B5=3, XIAO=4, baud rate 9600 (configurazione e comunicazione effettive da provare **dopo** accensione).
- [ ] **[C] F09** Ruolo del display D1 sul bus RS485 chiarito: niente secondo master Modbus concorrente con A1; se non pronto, lasciarlo scollegato dal bus fino al collaudo.

## G. Prove strumentali A QUADRO DISALIMENTATO

**Da svolgere con strumentazione e procedure adatte; per i circuiti 230 V serve il tecnico. Le verifiche di isolamento ad alta tensione non vanno applicate con elettronica, scaricatori o dispositivi sensibili connessi.**

- [ ] **[B][T] G01** Verifica di continuità PE eseguita con strumento/metodo appropriato, inclusi morsetti di terra e carcassa stufa. Registrare misure e punti testati.
- [ ] **[B][T] G02** Verifica assenza di cortocircuiti e collegamenti indesiderati fra L, N e PE sui circuiti predisposti, con carichi/strumenti separati ove necessario per evitare falsi esiti o danni.
- [ ] **[B][T] G03** Verifica isolamento dell'installazione 230 V effettuata **solo secondo procedura compatibile con i dispositivi collegati**, e risultato validato e registrato.
- [ ] **[B] G04** Continuità e identificazione puntuale dei cavi W1/W3/W5/W6: prova da una estremità all'altra, esclusa inversione fra +12 V/0 V/RS485/PE e fase/neutro.
- [ ] **[B] G05** Controllo elettrico dei rami F1/F2: con fusibile **rimosso**, l'uscita verso il relativo cavo deve risultare isolata dal +12 V non protetto; con fusibile inserito, continuità solo lungo il percorso previsto (test prima del collegamento dei dispositivi elettronici).
- [ ] **[B] G06** Nessun corto anomalo fra +12 V e 0 V nei cablaggi; risultati interpretati considerando condensatori d'ingresso, convertitori e carichi eventualmente connessi.
- [ ] **[C] G07** Serraggi ricontrollati secondo indicazioni dei componenti, incluse viti di PE, X0/X2/X3, SDM120, alimentatore, contattori, portafusibili e pressacavi.

## H. Autorizzazione alla prima messa in tensione (STOP / GO)

- [ ] **[B] H01** Tutte le voci `[B]` applicabili hanno esito **OK documentato**; ogni dubbio su S5, protezione termica, terra, protezioni 12 V o cablaggio di rete risolto.
- [ ] **[B][T] H02** Elettricista/tecnico qualificato ha riesaminato e autorizzato la parte a 230 V, compresi continuità PE, protezione differenziale e rischio delle modifiche alla stufa.
- [ ] **[B] H03** Fusibili corretti inseriti, carichi comandati nello stato OFF, morsetti protetti, cavi ordinati, scatole e quadro richiusi per la prova iniziale; possibilità di togliere prontamente alimentazione identificata.
- [ ] **[C] H04** Preparato un **piano distinto di prima accensione progressiva**: controllo uscita 12 V senza carichi remoti, poi elettronica, RS485, poi circuiti 230 V e singoli attuatori, con esito e misure registrati da personale idoneo.

**ESITO:** ☐ STOP — non alimentare  ☐ GO — autorizzazione al successivo collaudo controllato  
**Non conformità aperte:** _____________________________________________________  
**Misure / strumenti utilizzati:** _________________________________________________  
**Data / firma verificatore:** ____________________________________________________  
**Data / firma tecnico 230 V:** ___________________________________________________

---

## Punti progettuali ancora aperti alla data della bozza

1. Caratteristiche e valori definitivi dei fusibili F1/F2, inclusi rating DC dei portafusibili Amazon UK5-HESI; consumo dei rami da misurare in sede di collaudo.
2. Compatibilità e collegamenti reali delle derivazioni da 24 AWG su X3 e portafusibili, e classificazione rame puro vs CCA.
3. **S5 della stufa sul neutro comune**: modifica rispetto alla funzione di interruzione della fase originale; richiede valutazione specifica della sicurezza prima di applicare tensione.
4. Protezione indipendente da sovratemperatura/contattore incollato: il monitoraggio energia e gli allarmi non sono dispositivi di interruzione della potenza.
5. Disallineamento documentazione GitHub rispetto alle decisioni e all'eventuale working tree locale di Claude Code.

## Fonti del progetto consultate

- `documentazione/schema-quadro.html` — reti, ponticelli, carichi e bobine (revisione GitHub accessibile il 27/10/2026).
- `documentazione/scatola-x6.html` — reti X6, ventole, sensori, GPIO e Wago.
- `documentazione/distinta_base.md` — componenti T1, Q1, A3, D1, KM1–KM6 e cablaggi.
- `documentazione/prompt_schema_qelectrotech.md` — dettagli X0, X2, X3 e stufa.
- `documentazione/specifiche_firmware.md`; `esphome/salumi-nodo.yaml`, `esphome/salumi-camera.yaml` — stati attuatori e indirizzi Modbus.
- Discussione di progetto e revisione `revisione-alimentazione-12V.md` del 27/10/2026 (Claude Code).