# Prompt per Claude Code — seconda revisione della checklist PRE-ACCENSIONE Salamai

Voglio che tu agisca da **secondo revisore tecnico indipendente** della checklist che ChatGPT ha redatto per il quadro elettrico Salamai.

**PRIMA DI TUTTO**: verifica `git status`, l'ultimo commit e le modifiche non committate. Lavora sulla situazione **reale della tua directory di lavoro**, evitando di sovrascrivere modifiche locali. **Non fare commit e non fare push. Non modificare ancora gli schemi elettrici.**

## Input

La bozza condivisa è già pubblicata in questo repository in `documentazione/checklist_pre_accensione.md`: aprila e usala come unico documento canonico. Non creare una seconda checklist con nome diverso.

Controlla almeno questi file nella versione effettivamente disponibile:

- `documentazione/schema-quadro.html` (analizza anche le reti JavaScript `const D` / `nets` / `wires`);
- `documentazione/scatola-x6.html`;
- `documentazione/distinta_base.md`;
- `documentazione/prompt_schema_qelectrotech.md`;
- `documentazione/specifiche_firmware.md`;
- `esphome/salumi-nodo.yaml` e `esphome/salumi-camera.yaml`;
- la tua precedente `revisione-alimentazione-12V.md`, se disponibile.

## Obiettivo

Produrre una checklist **verificabile punto per punto, prima di applicare la tensione 230 V al quadro**, con identificativi univoci, possibilità di segnare OK/NO/NA, valori misurati e distinzione:

- **BLOCCANTE**: se fallito o non verificato non si alimenta;
- **TECNICO**: controllo riservato a personale qualificato, soprattutto sui circuiti di rete;
- **CONSIGLIATO**: non sostitutivo dei controlli bloccanti.

Voglio una lista pratica, non una trattazione generica. Deve essere specifica per Salamai e per i componenti/morsetti realmente previsti.

## Punti critici da verificare in modo indipendente

1. Rete 230 V: Q1 Gewiss C10 1P+N, X0, Eastron SDM120, KM1–KM6, X2, carichi e differenziale a monte.
2. Protezione PE: continuità effettivamente verificata su piastra, tutte le guide DIN, morsetti di terra e carcassa stufa. Non basta presumere continuità meccanica.
3. Stufa: W1 diretto a 5 conduttori, tre fasi comandate provenienti dalla stessa alimentazione monofase, N e PE; nessuna CEE. **S5 antiribaltamento attualmente sul neutro comune**: valuta e segnala il rischio di lasciare parti interne in tensione. Non trattarlo come risolto senza una valutazione elettrica competente. Tratta separatamente l'assenza di protezione termica indipendente contro contattori incollati.
4. Alimentazione 12 V: T1 Mean Well HDR-60-12; Waveshare, display, relè K1–K6 e sei bobine con polarità e soppressione interna.
5. F1/F2: portafusibili acquistati su Amazon, 4 UK5-HESI generici (ASIN B0FGD7CXSN), due da installare sui positivi W3 e W6; valori **non ancora definitivi**. Verifica DC rating, fusibili, curve, sezioni 24 AWG, guasti e assenza di ponticelli che escludano la protezione.
6. X3: gruppi B 1–3, A 4–6, 0 V 7–9, +12 V 10–12; separazione dei rami protetti e corretta terminazione di **due fili per polo** del W3 senza assumere che i morsetti ne accettino due per foro.
7. Cablaggio reale: ora previsto Cat5e UTP 4 coppie 24 AWG, apparentemente rame pieno ma non ancora certificato; W3 due coppie in parallelo per il 12 V, W5 alimentazione ventole, W6 sonda cantina; eliminare dal controllo i riferimenti a schermature FTP che non esistono.
8. X6/X4: Wago 221 e compatibilità conduttori, Seeed XIAO ESP32-C3, HX711/DS18B20, modulino MOSFET PWM, due ventole con TACH separati; nessun 12 V sui GPIO.
9. RS485: due terminazioni, polarità, indirizzi previsti 1/2/3/4; verifica ruolo del display D1 per evitare due master Modbus concorrenti. Distingui verifiche possibili **a quadro spento** da collaudi successivi con alimentazione.
10. Misure a quadro completamente disalimentato: continuità PE, collegamenti errati L/N/PE, cablaggio X3, continuità percorsi F1/F2, isolamento **solo con metodo compatibile con l'elettronica**, chiusure/pressacavi.
11. Procedura di STOP/GO finale che non autorizzi l'accensione con questioni di sicurezza aperte; non proporre prove con parti attive esposte all'operatore non qualificato.

## Compito

- Esamina la checklist iniziale **riga per riga** e confrontala con schemi e componenti reali.
- Identifica eventuali omissioni, controlli inutili, errori di sigle, criteri troppo vaghi e controlli che richiedono dati ancora sconosciuti.
- **Revisiona il file `documentazione/checklist_pre_accensione.md`**. Per prima cosa restituisci commenti puntuali e proposte di modifica; puoi aggiornare il file solo dopo esplicita autorizzazione dell'utente. Non modificare altri file e non effettuare commit/push.
- Se trovi problemi progettuali non risolvibili con una checklist, mettili in un paragrafo **«Blocchi progettuali prima dell'alimentazione»** anziché assumere che siano risolti.
- Produci un riepilogo finale molto concreto: controlli aggiunti, corretti, rimossi, e domande ancora aperte; separa i bloccanti dalle scelte opzionali.
- Non compilare «OK» per controlli che nessuno ha effettuato fisicamente. Lascia le caselle non marcate.

**Nota:** la revisione deve essere rigorosa ma pragmatica. Niente acquisti aggiuntivi se non motivati, niente modifiche al firmware in questa attività, niente testo che faccia sembrare un quadro non collaudato già approvato.