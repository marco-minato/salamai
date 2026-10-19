# Camera salumi — strategia di processo (decisioni del 18/10/2026)

> Aggiornato il 18/10/2026: il ciclo segue il programma di Home Assistant; UR di
> sgocciolamento portata da 95 % a 62 %. Aggiunte le decisioni 8–12 sulla
> condensa e sul ricambio (dal documento "setpoint, umidità reale e condensa").
> Aggiunte le decisioni 17–18 (isolamento solo di porta e botola, preriscaldo
> più lungo invece di isolare la vasca).
>
> Questo file, con `specifiche_firmware.md` e `regole_supervisione.md`, verrà
> ricompilato in un'unica strategia documentata: il punto di partenza della
> stagione.

Riferimento per il firmware ESPHome della scheda Waveshare ESP32-S3-Relay-6CH
e per la prossima stagione (metà dicembre – metà febbraio, cantina a 6–8 °C).

## Il problema da risolvere

- Dal 3° giorno compare muffa bianca che in pochi giorni diventa spessa 1–1,5 cm,
  poi grigia e con cattivo odore che si sente nel prodotto finale.
- Pozza d'acqua sul pavimento e condensa sulle pareti nei primi giorni.
- In passato una ventilazione forte sotto i salami ha fatto seccare e
  schiacciare i cacciatorini.

## Diagnosi

- **Superficie dei salami sempre bagnata e aria ferma**: sono le condizioni
  ideali per la muffa spessa e "pelosa" (tipo Mucor), non per il velo bianco buono.
- **Troppa acqua che nessuno porta fuori.** L'aria della camera (10 m³ a 22 °C e
  90 %) contiene in tutto circa 0,18 L d'acqua. Ogni giorno invece entrano:
  - circa 1–1,5 L dai salami (50–60 kg, 2–3 % al giorno nei primi giorni);
  - fino a 5 L dall'umidificatore.

  Tutto il resto finisce su pareti e pavimento.
- **Pareti e umidificatore si combattono.** Le pareti fredde (cemento a
  8–10 °C) condensano e tolgono vapore all'aria. La sonda vede l'umidità
  scendere e riaccende l'umidificatore, la cui nebbia finisce di nuovo sulle
  pareti e sul pavimento.
- **Limite fisico dell'umidità alta.** A 22 °C e 90 % (procedura manuale degli
  anni scorsi) il punto di rugiada è circa 20 °C: qualunque superficie sotto i
  20 °C condensa, e le pareti della botte non ci arrivano. Il programma in HA
  usa umidità più basse (sgocciolamento 62 %, poi 72–80 %), molto più
  compatibili con le pareti fredde.

## Decisioni

1. **Togliere l'acqua invece di farla girare.** Ricambi d'aria brevi e
   frequenti fin dal giorno 1–2, decisi confrontando l'umidità assoluta della
   camera con quella della cantina. Non si va a calendario.
   - Inizio ciclo: circa 11 g/m³ tolti per ogni m³ ricambiato. Servono circa
     130 m³ al giorno, cioè circa 75 minuti al giorno di estrattore
     (raffiche di circa 3 minuti ogni ora).
   - Fine ciclo (12 °C e 80 %): circa 2,5 g/m³. Servono circa 2 ore al giorno.
   - Costo per scaldare l'aria nuova: circa mezzo kWh al giorno.
2. **L'umidificatore è una riserva**, non il motore del processo. Parte solo se
   l'umidità è sotto il target **e** la parete è sopra il punto di rugiada
   (sonda DS18B20 di parete, in basso, sulla parete della porta).
3. **Sgocciolamento a UR 62 %** (prima era 95 %): l'umidificatore resta spento,
   l'umidità la portano i salami e l'estrattore porta fuori l'acqua in eccesso.
4. **Preriscaldo di 24 ore** a camera vuota, solo con la stufa (fase 0).
   Spesa stimata circa 3–4 €.
5. **Ricircolo lento a lavoro/pausa** (metodo Zanotti):
   - ventole al minimo per un tempo breve, poi pausa;
   - tempi e PWM regolabili per ogni fase, con un tetto massimo di PWM;
   - l'aria non deve mai muovere i salami;
   - i tempi si tarano guardando il budello: superficie che si asciuga appena,
     senza fare crosta.
6. **Niente ricambio mentre un umidificatore è acceso.**
7. **Umidità con isteresi regolabile**: la risalita lenta verso la soglia alta fa
   da "pausa", mentre l'acqua dall'interno migra in superficie.
8. **Conta l'umidità misurata, non quella impostata.** Un setpoint è solo un
   obiettivo: si registrano e si confrontano sempre setpoint e misura, con
   minimi, massimi e durata degli scostamenti (non le medie giornaliere).
9. **Ricambio anche per proteggere le pareti.** Se il margine di condensa
   (T parete − rugiada) scende sotto 2 °C, l'estrattore lavora anche con UR
   nel target, ma al massimo fino a 5 punti sotto. Oltre, o se la cantina non
   asciuga più, è un **conflitto**: allarme e decisione dell'utente.
10. **Non si abbassa l'UR del prodotto per compensare una parete fredda.** Se
    target e parete sono incompatibili si agisce sulla camera (preriscaldo
    più lungo, cantina ventilata), non sul salame.
11. **Ricambio con percorso definito.** Ingresso con griglia in basso sulla
    porta, con alettina a gravità; aspirazione dal tubo nell'angolo opposto,
    oltre la zona salami; uscita con la valvola a molla. Niente farfalle
    motorizzate (i 6 relè sono già tutti usati). La cantina deve poter
    smaltire l'acqua: apertura fissa in alto sulla sua porta esterna.
12. **Lo sgocciolamento a 62 % non è validato** per questo impasto in
    budello gentile: le fonti (Zanotti 60 % al giorno 1, IGP minimi 50–70 %)
    lo rendono ragionevole, non provato. Al primo ciclo si guarda il budello:
    se fa crosta si alza.
13. **Primo obiettivo: niente condensa su pareti e pavimento.** Se le muffe
    indesiderate continuano anche senza condensa, si prenderanno altre
    decisioni (colture, pulizia, programma).
14. **A parità di risultato si sceglie la soluzione che consuma meno
    elettricità.**
15. **Sensori in più**: DS18B20 anche sul **pavimento** (stesso bus della
    sonda di parete, nessun pin in più; conta la superficie più fredda) e una
    seconda sonda RS485 S-TH-01 in **cantina**, letta direttamente
    dall'ESP32. L'aria della cantina cambia col tempo esterno (col sole più
    secca, con la nebbia più umida) ma resta più asciutta di quella della
    camera, soprattutto nei primi giorni: va misurata in continuo.
16. **Due programmi selezionabili in HA**: Morganline (quello di finora) e
    Zanotti. La scelta si fa dopo il test di preriscaldo delle pareti.
17. **Niente isolamento della vasca**: non è praticabile. Si isolano solo i
    punti deboli:
    - **porta** (multistrato, disperde molto): pannello di polistirolo sulla
      faccia interna, preferibilmente XPS (a celle chiuse, non assorbe acqua),
      coperto o almeno sigillato sui bordi perché non si impregni e non faccia
      muffa dietro. Va lasciato il foro per la griglia d'ingresso Y2 in basso,
      con i bordi sigillati, e la porta deve chiudere ancora bene;
    - **botola**: pannello sigillato sul telaio (guarnizione) e polistirolo
      anche lì, lasciando i passaggi dell'estrattore e dei pressacavi.
    Con porta e botola sigillate l'aria entra solo dalla griglia Y2 ed esce solo
    dall'estrattore: il ricambio diventa misurabile e non ci sono spifferi
    freddi a raffreddare l'angolo della porta.
18. **Preriscaldo più lungo invece di isolare**: si accetta di spendere più
    energia all'inizio per portare in temperatura il cemento. La durata
    (36–48 h o più, massimo 72 h) si fissa col test delle pareti.
    Restano centrali le decisioni 2, 3 e 9: **umidificatore spento nelle prime
    fasi** e acqua portata fuori col ricambio verso la cantina. È la correzione
    che ci si aspetta risolva le muffe; il primo ciclo lo verifica.
19. **Ricircolo forte nel preriscaldo**, a camera vuota: ventole sempre accese
    al massimo. L'aria in movimento cede calore a pareti e pavimento circa due
    volte più in fretta che ferma e non resta stratificata al soffitto. Alla
    partenza del ciclo si torna subito al ricircolo lento a lavoro/pausa
    (decisione 5). Il ricircolo non asciuga l'aria: la mescola. L'acqua che
    portano i salami la toglie solo il ricambio con la cantina; il ricircolo
    aiuta perché non lascia sacche umide negli angoli e vicino al pavimento.
20. **Carico ridotto a ~40 kg** (prima 50–60), salami e cacciatorini. Meno
    acqua da togliere nei primi giorni (circa un quarto in meno di estrattore)
    e più spazio tra i pezzi. Disposizione:
    - **salami** nella zona a destra della porta (più calda, più aria), meno
      fitti di prima; i più grossi in alto;
    - **cacciatorini** nella zona a sinistra della porta (coda del getto delle
      ventole, aria più calma), a metà altezza, lontani dalla parete sinistra,
      nella fila in fondo (davanti ci sono i pezzi interi, decisione 21);
    - per tutti: almeno 15–20 cm dalle pareti, niente sotto i 50 cm da terra,
      niente davanti alla parte bassa della porta (griglia d'ingresso), niente
      davanti e sopra la stufa, pezzi sfalsati durante lo sgocciolamento;
    - il salame campione sulla bilancia resta un salame; i cacciatorini, che
      asciugano prima, si controllano a mano;
    - la zona a sinistra è la più lontana dalla stufa: nel test di preriscaldo
      si misurano col termometro IR pavimento e angoli di quel lato, e lì va
      la sonda del pavimento se risultano i più freddi.
21. **Pezzi interi (coppa, lonzino, guanciale), da valutare per la stagione
    successiva**: stufati 3 giorni con i
    salami, poi direttamente in cantina (procedura dell'utente, confermata).
    - Nella zona a sinistra, nella fila **verso la porta**, così escono il
      giorno 3 senza passare tra salami e cacciatorini; i cacciatorini in
      fondo a sinistra.
    - Il **guanciale** (senza budello) soffre lo sgocciolamento a 22 °C /
      62 %: meglio farlo entrare alla fine dello sgocciolamento, con il
      giorno 1 (UR 72 %).
    - Escono quando finisce un ricambio, con la porta aperta il meno
      possibile. In cantina non fanno condensa: entrano più caldi dell'aria.
    - Sono compresi nei ~40 kg; dopo la loro uscita il carico cala, ma i
      ricambi li decide l'umidità misurata, non la stima.

## Ciclo (valori del programma in Home Assistant, `packages/salumi.yaml`)

Il riferimento sono i tempi, le temperature e le umidità del programma caricato
in HA (dashboard "Stagionatura"), non la vecchia procedura manuale.

| Fase | Temperatura | UR | Durata | Note |
|---|---:|---:|---|---|
| Preparazione cella (preriscaldo) | 22 °C | umidificatore spento | da avviare ~24 h prima | solo stufa, camera vuota |
| Sgocciolamento | 22 °C | **62 %** | 12 h | umidificatore di fatto spento; ricambi per togliere acqua |
| Giorno 1 | 20 °C | 72 % | 24 h | |
| Giorno 2 | 18 °C | 72 % | 24 h | |
| Giorno 3 | 18 °C | 74 % | 24 h | |
| Giorno 4 | 16 °C | 76 % | 24 h | |
| Giorno 5 | 16 °C | 78 % | 24 h | |
| Giorni 6–7 | 14 °C | 80 % | 24 h ciascuno | |
| Giorni 8–15 | 12 °C | 80 % | 24 h ciascuno | poi i salami vanno in cantina |

In tutte le fasi valgono le decisioni sopra: ricambi decisi dall'umidità
assoluta, umidificatore solo di riserva e bloccato se la parete è sotto il
punto di rugiada, ricircolo lento a lavoro/pausa.

### Condensa fase per fase (Magnus)

| Fase | Rugiada | Rischio |
|---|---:|---|
| Sgocciolamento 22 °C / 62 % | 14,4 °C | parete a 16–17 °C dopo 24 h di preriscaldo: margine ~2 °C |
| Giorno 1, 20 / 72 | 14,8 °C | **il più critico**: margine 1–2 °C |
| Giorno 2, 18 / 72 | 12,9 °C | |
| Giorno 3, 18 / 74 | 13,3 °C | |
| Giorno 4, 16 / 76 | 11,8 °C | l'aria scende più in fretta della parete: rischio in calo |
| Giorno 5, 16 / 78 | 12,2 °C | |
| Giorni 6–7, 14 / 80 | 10,6 °C | |
| Giorni 8–15, 12 / 80 | 8,7 °C | dipende da quanto si raffredda la parete |

Il vecchio primo giorno a 22 °C / 90 % aveva la rugiada a 20,3 °C: nessuna
parete della botte ci arriva, da qui la condensa.

I salami entrano a circa **18 °C** (lavorati in laboratorio, non escono dal
frigo): sopra la rugiada dello sgocciolamento, quindi sul budello non si
forma condensa. L'acqua delle prime ore è quella di superficie del budello e
quella ceduta dal salame, e va portata fuori col ricambio.

### Programma Zanotti a confronto

Valori di set del manuale Zanotti SAS/SAR MicroSAS, in HA come programma
"Zanotti" (sgocciolamento ai valori del giorno 1, giorni 6–15 a 12,5 / 80).

| Giorno | Morganline | Rugiada | Zanotti | Rugiada |
|---|---|---:|---|---:|
| Sgocciolamento | 22 / 62 | 14,4 °C | 19,5 / 60 | 11,5 °C |
| 1 | 20 / 72 | 14,8 °C | 19,5 / 60 | 11,5 °C |
| 2 | 18 / 72 | 12,9 °C | 17,5 / 65 | 10,9 °C |
| 3 | 18 / 74 | 13,3 °C | 15,5 / 69 | 9,8 °C |
| 4 | 16 / 76 | 11,8 °C | 14,5 / 73 | 9,7 °C |
| 5 | 16 / 78 | 12,2 °C | 13,5 / 77 | 9,5 °C |
| 6–7 | 14 / 80 | 10,6 °C | 12,5 / 80 | 9,1 °C |
| 8–15 | 12 / 80 | 8,7 °C | 12,5 / 80 | 9,1 °C |

- **Pro**: rugiada 2–3,5 °C più bassa nei primi 5 giorni e quasi costante
  (9–11,5 °C). Per 2 °C di margine basta una parete a ~13,5 °C invece di
  ~16,8 °C. Aria più fredda: meno calore disperso, preriscaldo più facile e
  forse più corto.
- **Contro**:
  - più ricambio: con la portata nominale ~150 min/giorno di estrattore nei
    primi giorni invece di ~95 (tabella in dashboard), di più con la portata
    reale; più aria fredda da scaldare;
  - il 60 % va ottenuto davvero: Zanotti deumidifica col freddo, noi solo
    col ricambio. Il primo giorno si starà probabilmente intorno al 63–68 %
    misurato, comunque con una rugiada più bassa di Morganline;
  - superficie più esposta alla crosta, soprattutto per i cacciatorini;
  - fermentazione più lenta partendo da 19,5 °C senza colture starter
    (il salnitro c'è); da osservare odore e consistenza al giorno 3–4.
- **Consumi**: da confrontare col contatore SDM120; nel bilancio entrano il calore per
  l'aria più fredda (Zanotti risparmia) e quello per l'aria di ricambio in
  più (Zanotti spende). Il programma va scelto a parità di risultato su
  condensa e prodotto.

## Fuori dall'impianto

- **Lavare con acqua e aceto** prima della stagione anche la **struttura in
  legno**, non solo le pareti: il legno trattiene le spore da un anno all'altro.
- **Spazzolatura**: se la muffa si ispessisce, passare i salami con un panno
  imbevuto di acqua e aceto o di salamoia.
- **Coltura di muffa** *Penicillium nalgiovense* (facoltativa): da provare su
  metà del lotto per confronto.
- **Cacciatorini** nella zona più riparata, lontani dal flusso delle ventole.

## Test a camera vuota (dopo il montaggio)

- **Riscaldamento**: tempi da 7 a 20 °C con 1, 2 o 3 lampade, e raffreddamento
  in un'ora a stufa spenta.
- **Umidificatore**: aumento di UR in 5 minuti e ritardo della sonda.
- **Ricambio**: effetto di 3 minuti di estrattore su UR e temperatura, e
  **portata reale** dal calo dell'umidità assoluta (formula in
  `specifiche_firmware.md` §6.2). Con tubo, curva e valvola un estrattore
  assiale può dare la metà della portata nominale: le stime in dashboard
  usano la nominale e sono ottimistiche.
- **Preriscaldo a confronto: 3 lampade per 5 h contro 1 lampada a lungo**
  (dopo aver isolato porta e botola). Finora: 3 × 400 W per 5 h, circa 6 kWh.
  Ipotesi dell'utente: con una sola lampada per molte ore pareti e pavimento si
  scaldano meglio, con una spesa simile.
  - Prova A, di riferimento: 3 lampade come sempre, fino a 22 °C d'aria.
  - Prova B: 1 lampada fissa finché pareti e pavimento smettono di salire;
    se l'aria non arriva a 22 °C, ultime 1–2 h con 3 lampade.
  - In entrambe le prove ventole sempre accese al massimo (decisione 19),
    così il confronto riguarda solo le lampade. Se avanza tempo, una prova B
    senza ventole mostra quanto conta il ricircolo.
  - Misure ogni ora: aria, parete, pavimento, kWh. Le sonde vanno fissate
    sulla superficie con nastro e coperte con un pezzetto di isolante, così
    leggono il muro e non l'aria.
  - Confronto al momento in cui l'aria è a 22 °C: temperatura della superficie
    più fredda (deve superare 16,4 °C) e kWh spesi. Vince la prova che arriva
    sopra soglia; a parità, quella che consuma meno (decisione 14).
  - Se vince B, il firmware avrà il parametro "lampade massime nel
    preriscaldo".
- **Preriscaldo e pareti** (il test più importante, anche se senza salami non
  è definitivo: mancano la loro massa e la loro acqua):
  - camera a 22 °C con le lampade, umidificatori spenti, estrattore fermo;
  - ogni ora: T aria, T parete (DS18B20), e con un termometro a infrarossi
    pavimento, angoli e parete di fondo;
  - risultato: dopo quante ore la superficie **più fredda** supera 16,4 °C
    (rugiada di 22/62 + 2 °C) e 16,8 °C (giorno 1: 14,8 + 2 °C). Da qui si
    decide se 24 h di preriscaldo bastano o servono 36–48 h;
  - se il pavimento o un angolo sono più freddi della parete, la sonda va
    spostata lì (per esempio all'attacco tra muro e pavimento).
  - prolungare il test oltre le 24 h (fino a 48–72 h) per vedere quando le
    superfici smettono di salire: da lì la durata del preriscaldo;
  - annotare i kWh del preriscaldo (contatore SDM120);
  - controllare col termometro IR la faccia interna della porta e la botola
    dopo l'isolamento: non devono essere più fredde delle pareti.
- **Condensa**: soglia della sonda di parete confrontata con quello che si vede.
- **Ventole**: PWM minimo a cui girano e tetto oltre il quale l'aria "corre".
  Per misurare: bastoncino d'incenso, tempo per percorrere 50 cm tra i salami
  (10 s ≈ 0,05 m/s).
- **Consumi**: potenza di riferimento di ogni carico letta dal contatore SDM120.

## Durante la stagione: dati da registrare

- Temperatura e UR della camera e della cantina, temperatura della parete,
  margine di condensa (minuti al giorno sotto 1 °C e sotto 0 °C).
- Setpoint e misura sullo stesso grafico, con minimi, massimi e minuti fuori
  fascia.
- Minuti di estrattore e di umidificatore, con stima dell'acqua tolta
  (umidità assoluta × portata).
- Calo peso del salame campione (cella da 2 kg, letture a ventole ferme).
- Aspetto della muffa giorno per giorno (foto).

## Da decidere

- **Estrattore**: Airope (assiale, 107 m³/h a bocca libera) oppure un
  elicocentrifugo da condotto Ø100 (per esempio Vortice Lineo 100), che regge
  meglio i ~3 m di tubo, la curva e la valvola. Da decidere prima
  dell'acquisto, eventualmente dopo il test di portata.
- **Durata del preriscaldo**: più lunga di 24 h (decisione 18); quante ore
  esattamente si decide col test delle pareti.
- **Programma**: Morganline o Zanotti, dopo il test delle pareti; a parità di
  risultato quello che consuma meno.
