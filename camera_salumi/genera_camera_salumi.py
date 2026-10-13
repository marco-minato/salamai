#!/usr/bin/env python3
"""Genera camera_salumi.qet: schema elettrico della camera di stagionatura salumi (ESP32-S3, 6 relè).

Uso:  python3 genera_camera_salumi.py [uscita.qet] [--first N]
      --first N porta il folio N in testa (serve solo per i render di controllo).
"""
import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "qet-tools"))
from qetlib import ORIENT, Project, make_box  # noqa: E402

# ----------------------------------------------------------------------------- dati di progetto
PROGETTO = "Camera salumi — controllo ESP32"
REVISIONE = "B"
AUTORE = ""  # da compilare
OGGI = datetime.date.today()

A = "10_electric/10_allpole/"
SYM = {
    "sorgente": A + "110_network_supplies/src_1p_pe_n.elmt",
    "morsetto": A + "130_terminals_terminal_strips/90_terminal_strips_diagram/90-10-0111.elmt",
    "morsetto_pe": A + "130_terminals_terminal_strips/90_terminal_strips_diagram/90-10-0121.elmt",
    "termostato": A + "390_sensors_instruments/15_sensors_temperature/thermostat_nc.elmt",
    "ta": A + "340_converters_inverters/20_current_tansformers/transformateur_courant1.elmt.elmt",
    "contatto_na": A + "310_relays_contactors_contacts/02_contacts_cross_referencing/01_auxiliary_contacts/con_simple.elmt",
    "interruttore": A + "380_signaling_operating/21_selector_switches/010_switch_1pos.elmt",
    "lampada": A + "380_signaling_operating/11_optical_signaling/lampe2.elmt",
    "finecorsa_na": A + "390_sensors_instruments/41_limit_switches/fin_de_course_no.elmt",
    "massa": A + "110_network_supplies/masse.elmt",
    "motore_ac": A + "391_consumers_actuators/10_engines/moteur_mono.elmt",
    "motore_dc": A + "391_consumers_actuators/10_engines/moteur_dc.elmt",
    "presa": A + "140_connectors_plugs/20_socket_outlets/pc16pnt.elmt",
}

# Colori dei conduttori (convenzione del disegno, riportata in legenda sul folio 1)
C = {
    "L": "#8b4513", "L2": "#000000", "L3": "#808080", "N": "#0000ff", "PE": "#00aa00", "PE2": "#ffff00",
    "12V": "#ff0000", "5V": "#ff8800", "0V": "#000000", "SEG": "#aa00aa", "A": "#008080", "B": "#6b8e23", "CMD": "#ff66cc",
}

# Distinta: sigla -> (componente, note, costruttore, riferimento). Alimenta la nomenclatura del folio 8.
DISTINTA = {
    "-A1": ("Scheda ESP32-S3-Relay-6CH", "6 relè HLS8L 10 A 250 VAC (rev. B: commutano solo le bobine 12 V), RS485 isolato (A+/B−/G), 7–36 V DC, H1/H2, guida DIN", "Waveshare", "Amazon B0CXPG4XGZ"),
    "-A2": ("Modulo MOSFET dual D4184", "PWM ventole, low-side, ingresso logico 3,3 V", "", "Amazon B0GL1NWZQH"),
    "-A3": ("Misuratore di energia PZEM-016 con TA apribile", "RS485 Modbus 9600 8N1 (optoisolata secondo il manuale, +5V in uscita), indirizzo da cambiare in 2", "Peacefair", "Amazon B0D5NDPP4L"),
    "-A4": ("Modulo HX711", "In scatolina IP65 dentro la camera", "", "scatola: Amazon B0F8NW1YZ2"),
    "-A5": ("Modulo RTC DS3231 (opzionale)", "I²C, mantiene l'ora senza rete", "", "Amazon B0FPPTHKBX"),
    "-B1": ("Sonda temperatura/umidità S-TH-01", "RS485 Modbus, indirizzo 1 o 42, 9600 baud; 3,6–30 V DC, IP54; fili rosso V+, nero GND, giallo A, bianco B", "Seeed", "101990881"),
    "-B2": ("Cella di carico", "4 fili E+, E−, A+, A−", "", ""),
    "-B3": ("Termostato di sicurezza PP1461", "Elettromeccanico 5–30 °C, contatti 10(2,5) A 250 V; a parete in camera, apre sopra soglia (28–30 °C)", "Poly Pool", "Amazon B00L49ZA6K"),
    "-E1": ("Stufa a 3 lampade IR, 1200 W", "Cavallotto S1–S4 rimosso; rotazione non usata", "", ""),
    "-E1.1": ("Lampada IR 1", "~400 W, 230 V", "", ""),
    "-E1.2": ("Lampada IR 2", "~400 W, 230 V", "", ""),
    "-E1.3": ("Lampada IR 3", "~400 W, 230 V", "", ""),
    "-M1": ("Motorino rotazione stufa", "Scollegato", "", ""),
    "-M2": ("Umidificatore a ultrasuoni 1", "A spina, su presa XS1", "", ""),
    "-M3": ("Umidificatore a ultrasuoni 2", "A spina, su presa XS2", "", ""),
    "-M4": ("Estrattore", "A spina, su presa XS3", "", ""),
    "-M5": ("Ventola USB 5 V doppia 120 mm", "Selettore su «alta»; adattatore USB-A femmina a morsetti (B09MH69W3N)", "ELUTENG", "Amazon B0B38KFVZX"),
    "-M6": ("Ventola USB 5 V doppia 120 mm", "Selettore su «alta»; adattatore USB-A femmina a morsetti (B09MH69W3N)", "ELUTENG", "Amazon B0B38KFVZX"),
    "-S1": ("Interruttore lampada 1 (rosso, luminoso)", "Interno stufa, lasciato su acceso", "", ""),
    "-S2": ("Interruttore lampada 2", "Interno stufa, lasciato su acceso", "", ""),
    "-S3": ("Interruttore lampada 3", "Interno stufa, lasciato su acceso", "", ""),
    "-S4": ("Interruttore rotazione", "Non usato, non alimentato", "", ""),
    "-S5": ("Antiribaltamento a pulsante", "Sotto la base della stufa, in serie al neutro comune", "", ""),
    "-T1": ("Alimentatore HDR-30-12 (rev. B: HDR-60-12)", "230 VAC → 12 V DC 2 A, classe II senza PE, guida DIN 2 moduli", "Mean Well", "Amazon B071KXJPYB"),
    "-T2": ("Convertitore DC-DC 12 → 5 V 3 A resinato", "Alimenta le ventole", "", "Amazon B09B818N5F"),
    "-X0:L": ("Morsetti ingresso linea L / N / PE", "Linea da quadro generale, protetta 16 A + Id 30 mA", "", ""),
    "-XS1": ("Presa Schuko (scatola -X1)", "Umidificatore 1", "", ""),
    "-XS2": ("Presa Schuko (scatola -X1)", "Umidificatore 2", "", ""),
    "-XS3": ("Presa Schuko (scatola -X1)", "Estrattore", "", ""),
}
CAVI = [
    ("-W1", "Cavo 5G1,5 quadro → stufa", "L1 marrone, L2 nero, L3 grigio, N blu, PE giallo-verde"),
    ("-W2", "Cavo 2×1,5 (o 3G1,5) quadro → termostato -B3", "Rev. A: fase lampade. Rev. B: 12 V della bobina di -Q7 (cavo 2×0,75)"),
    ("-W3", "Cavo 4 poli quadro → sonda -B1", "+12 V, GND, A, B (A e B sullo stesso doppino)"),
    ("-W4", "Cavo di rete (doppini) quadro → -A4", "3,3 V, GND, DOUT, SCK (DOUT e SCK accoppiati a GND)"),
    ("-X1", "Scatola da esterno con 3 prese Schuko", "XS1, XS2, XS3 — accanto al quadro"),
    ("-X2…", "Morsetti Wago 221 / morsettiere", "Distribuzione N, PE e bassa tensione (nodi dello schema)"),
    ("—", "Filo silicone 18 AWG (B07TT68455)", "Collegamenti interni alla stufa, in guaina di vetro"),
    ("—", "Quadro IP65 24 moduli 2 file (B0DPXCLZPR)", "Clip DIN per PCB (B0FCM3N3P9), pressacavi M20 (B0GYRDCC9Z)"),
]
MODIFICHE = [
    ("+", "-Q0", "Sezionatore modulare 2P, 25 A o più", "Sezionamento locale: l'interruttore a monte è nel quadro generale"),
    ("+", "-F1", "Interruttore magnetotermico 1P+N C10", "Ramo stufa (5,2 A); protegge anche il cavo -W1"),
    ("+", "-F2", "Interruttore magnetotermico 1P+N C6", "Ramo prese: umidificatori ed estrattore"),
    ("+", "-F3", "Interruttore magnetotermico 1P+N C6", "Ausiliari: -T1 e misura di tensione di -A3"),
    ("+", "-Q1…-Q7", "7 contattori modulari 2 NA 25 A, bobina 12 V AC/DC, contatti AgSnO2 (es. Finder 22.32.0.012.4340)",
     "Isolamento rinforzato bobina/contatti, 2000 W di lampade alogene; -Q7 senza forzatura manuale"),
    ("↔", "-T1", "Mean Well HDR-60-12 (54 W, 3 moduli) al posto di HDR-30-12 (24 W)", "7 bobine da 2,2 W + scheda + ventole ≈ 25 W"),
    ("↔", "—", "Cassetta IP65 ~400 × 600 × 200 con piastra di fondo al posto del centralino da 24 moduli", "4 guide DIN, canalina asolata 25 × 40 (~2,5 m)"),
    ("↔", "-X0, -X2, -XPE, -X3", "Morsetti su guida (3 + 10 + terra da 2,5 mm²; 14 piccoli), fermi, setto separatore, ponticelli",
     "Al posto dei Wago 221 usati come nodi"),
    ("↔", "-W2", "Cavo 2 × 0,75 al posto di 2 × 1,5", "Il termostato lavora a 12 V sulla bobina di -Q7"),
    ("+", "—", "Filo H07V-K 1,5 mm² (230 V) e H05V-K 0,75 mm² (comandi), puntalini, pressacavi M20 e M12", "Colori: fase marrone/nero/grigio, neutro blu, terra giallo-verde"),
    ("?", "—", "Isolatore RS485 per -A3", "Solo se la prova di isolamento del PZEM non è soddisfacente"),
]
# Connettori a 20 pin della scheda -A1 (dallo schema Waveshare) e pin impegnati dal progetto
H1 = ["5V", "VSYS", "GND", "3V3", "3V3", "GPIO10", "GPIO9", "GND", "GPIO8", "GPIO7", "3V3", "GPIO6", "GND",
      "GPIO5", "GPIO4", "GPIO40", "GPIO39", "GND", "GPIO3 (strapping, evitare)", "GPIO21 (buzzer, occupato)"]
H2 = ["TXD0 (GPIO43)", "RXD0 (GPIO44)", "GND", "GPIO13", "GPIO14", "GPIO15", "GPIO16", "GND", "GPIO47", "GPIO48",
      "GPIO17 (RS485 TX, occupato)", "GPIO18 (RS485 RX, occupato)", "GND", "GPIO35 (evitare, PSRAM)",
      "GPIO36 (evitare, PSRAM)", "GPIO37 (evitare, PSRAM)", "GPIO38 (LED RGB, occupato)", "GND", "GPIO11", "GPIO12"]
USO_H1 = {3: "GND HX711", 4: "3,3 V HX711", 5: "3,3 V RTC", 7: "RTC SCL (opz.)", 8: "GND RTC", 9: "RTC SDA (opz.)",
          12: "HX711 SCK", 13: "GND MOSFET", 14: "HX711 DOUT", 15: "PWM ventole"}
FOLII = [
    ("1", "Copertina e legenda"), ("2", "Alimentazione 230 V"), ("3", "Stufa (3 lampade IR)"),
    ("4", "Prese di servizio"), ("5", "Bassa tensione 12 V / 5 V"), ("6", "Bus RS485 e sensori"),
    ("7", "Disposizione su piastra — rev B"), ("8", "Distinta componenti"),
    ("9", "Cablaggio del quadro (vista d'insieme) — rev B"),
]

# ----------------------------------------------------------------------------- utilità
p = Project(PROGETTO, author=AUTORE, date=OGGI.strftime("%Y%m%d"), indexrev=REVISIONE, filename="camera_salumi")
SYM["contatto"] = p.variant("contatto_na_rele", SYM["contatto_na"], link_type="simple")
rimandi = {}  # nome potenziale -> [freccia uscente, freccia entrante]


def campo(riga, col, valore, etichetta=None, align="left", **extra):
    attr = {"row": str(riga), "col": str(col), "name": f"c{riga}{col}", "valign": "center", "hadjust": "true",
            "align": align, "displaylabel": "true" if etichetta else "false", **extra}
    a = " ".join(f'{k}="{v}"' for k, v in attr.items())
    lab = f'<label><translation lang="en">{etichetta}</translation></label>' if etichetta else "<label/>"
    return f'<field {a}><value><translation lang="en">{valore}</translation></value>{lab}</field>'


CARTIGLIO = p.titleblock(
    '<titleblocktemplate name="camera_salumi"><information>Cartiglio del progetto camera salumi</information>'
    '<logos/><grid cols="t20%;r100%;t12%;t20%;" rows="25;25;">'
    + campo(0, 0, "%author", "Autore") + campo(1, 0, "%{data}", "Data")
    + campo(0, 1, "%{progetto}", align="center", fontsize="11") + campo(1, 1, "%title", align="center")
    + campo(0, 2, "%{revisione}", "Rev.") + campo(1, 2, "%{folio-id}/%{folio-total}", "Folio")
    + campo(0, 3, "%filename", "File") + campo(1, 3, "IEC 60617 / IEC 81346", "Simboli")
    + "</grid></titleblocktemplate>")


def folio(titolo, rows=10, cols=24):
    d = p.diagram(titolo, cols=cols, rows=rows)
    d.template = CARTIGLIO
    d.properties = {"progetto": PROGETTO, "revisione": REVISIONE, "data": OGGI.strftime("%d/%m/%Y")}
    return d


def side(el, s):
    """Morsetto dell'elemento rivolto verso n/e/s/w (tiene conto della rotazione)."""
    return next(t for t in el.t if t.facing == ORIENT[s])


def info(sigla):
    comp, note, costr, rif = DISTINTA[sigla]
    return {"description": comp, "comment": note, "manufacturer": costr, "designation": rif}


def html(righe, size=None):
    return "<br>".join(righe)


def tabella(intest, righe):
    out = ['<table border="1" cellspacing="0" cellpadding="3"><tr>']
    out += [f"<th>{h}</th>" for h in intest] + ["</tr>"]
    for r in righe:
        out += ["<tr>"] + [f"<td>{c}</td>" for c in r] + ["</tr>"]
    return "".join(out) + "</table>"


def pe(d, a, b, **kw):
    d.wire(a, b, color=C["PE"], color2=C["PE2"], **kw)


def esce(d, nome, x, y, testo):
    """Rimando verso un folio successivo: restituisce il morsetto (a sinistra della freccia)."""
    r = d.report_out(x + 13, y)
    rimandi.setdefault(nome, []).append(r)
    d.text(testo, x + 26, y - 26, size=7)
    return r.t[0]


def entra(d, nome, x, y, testo):
    """Rimando da un folio precedente: restituisce il morsetto (a destra della freccia)."""
    r = d.report_in(x - 13, y)
    rimandi.setdefault(nome, []).append(r)
    d.text(testo, x - 30, y - 30, size=7)
    return r.t[0]


def box(nome, w, h, pins, lines=(), **kw):
    return p.define(nome, make_box(nome, w, h, pins, lines, **kw))


d1 = folio("Copertina e legenda", rows=12)
d2 = folio("Alimentazione 230 V", rows=11)
d3 = folio("Stufa (3 lampade IR)", rows=11)
d4 = folio("Prese di servizio", rows=11)
d5 = folio("Bassa tensione 12 V / 5 V", rows=11)
d6 = folio("Bus RS485 e sensori", rows=12)
d7 = folio("Disposizione su piastra — rev B", rows=17, cols=26)
d8 = folio("Distinta componenti", rows=18)
d9 = folio("Cablaggio del quadro (vista d'insieme) — rev B", rows=18, cols=32)

AVVISO = ('<span style="color:#c00000"><b>Rev. B — folio non ancora aggiornato:</b> mancano sezionatore -Q0, interruttori -F1…-F3 e contattori '
          '-Q1…-Q7; il termostato -B3 passa sulla bobina di -Q7. Fa fede il folio 9.</span>')
for dd in (d2, d3, d4, d5):
    dd.text(AVVISO, 60, 820, size=8)

# ----------------------------------------------------------------------------- folio 1: copertina
d = d1
d.text(f'<span style="font-size:26pt"><b>{PROGETTO}</b></span>', 60, 30)
d.text(html([
    "Camera di asciugatura e stagionatura salumi: ciclo di circa 15 giorni a temperatura e umidità",
    "controllate (da 20 °C / 72 % UR a 12 °C / 80 % UR). Quadro di comando in cantina, fuori dalla camera;",
    "in camera: stufa a 3 lampade IR, 2 umidificatori, ventole, estrattore, sonda, bilancia, termostato di sicurezza.",
    "Controllo: scheda Waveshare ESP32-S3-Relay-6CH con firmware ESPHome, integrata in Home Assistant.",
    f"<b>Revisione {REVISIONE}</b> — {OGGI.strftime('%d/%m/%Y')} — autore: (da compilare)",
]), 60, 90, size=10)
d.text("<b>Elenco folii</b>" + tabella(["Folio", "Contenuto"], FOLII), 60, 230, size=9)
d.text("<b>Colori dei conduttori (convenzione del disegno)</b>" + tabella(
    ["Conduttore", "Colore"],
    [("L — fase 230 V (anche L-lampade, L1 di W1)", '<span style="color:#8b4513">■</span> marrone'),
     ("L2 di W1 (lampada 2)", '<span style="color:#000000">■</span> nero'),
     ("L3 di W1 (lampada 3)", '<span style="color:#808080">■</span> grigio'),
     ("N — neutro", '<span style="color:#0000ff">■</span> blu'),
     ("PE — protezione", '<span style="color:#00aa00">■</span><span style="color:#d8d800">■</span> giallo-verde'),
     ("+12 V DC", '<span style="color:#ff0000">■</span> rosso'),
     ("+5 V DC", '<span style="color:#ff8800">■</span> arancione'),
     ("0 V / GND", '<span style="color:#000000">■</span> nero'),
     ("Segnali logici (PWM, HX711, I²C)", '<span style="color:#aa00aa">■</span> viola'),
     ("RS485 A", '<span style="color:#008080">■</span> verde acqua'),
     ("RS485 B", '<span style="color:#6b8e23">■</span> verde oliva'),
     ("Comando bobine 12 V (folio 9)", '<span style="color:#ff66cc">■</span> rosa'),
     ("Tratteggiato", "opzionale / non collegato")]), 60, 520, size=9)
d.text("<b>Legenda sigle (IEC 81346)</b>" + tabella(
    ["Sigla", "Significato", "In questo progetto"],
    [("-A", "Assieme / scheda elettronica", "A1 scheda relè, A2 MOSFET, A3 PZEM-016, A4 HX711, A5 RTC"),
     ("-B", "Sensore / trasduttore", "B1 sonda T/UR, B2 cella di carico, B3 termostato di sicurezza"),
     ("-E", "Riscaldamento / illuminazione", "E1 stufa, E1.1–E1.3 lampade IR"),
     ("-F", "Protezione", "F1 stufa, F2 prese, F3 ausiliari (rev. B)"),
     ("-K", "Relè (a bordo di -A1)", "K1–K3 lampade, K4–K5 umidificatori, K6 estrattore"),
     ("-Q", "Sezionatore / contattore", "Q0 sezionatore, Q1–Q6 contattori dei carichi, Q7 sicurezza lampade (rev. B)"),
     ("-M", "Motore / utilizzatore", "M1 rotazione (scollegato), M2–M3 umidificatori, M4 estrattore, M5–M6 ventole"),
     ("-S", "Comando manuale / contatto", "S1–S4 interruttori stufa, S5 antiribaltamento"),
     ("-T", "Alimentatore / convertitore", "T1 230 VAC → 12 V DC, T2 12 → 5 V DC"),
     ("-W", "Cavo", "W1 stufa, W2 termostato, W3 sonda, W4 HX711"),
     ("-X", "Morsetti / prese", "X0 ingresso linea, X1 scatola prese (XS1–XS3), X2 uscite 230 V, X3 morsetti SELV, XPE terra"),
     ]), 520, 230, size=9)
d.text(html([
    "<b>Convenzioni</b>",
    "• I relè K1–K6 sono a bordo della scheda -A1: sui folii 3 e 4 compare il solo contatto COM–NA.",
    "• La scheda -A1 è rappresentata a blocchi funzionali su più folii (relè, alimentazione, RS485, connettore H1).",
    "• Le frecce ai bordi sono rimandi tra folii: accanto è indicato folio e posizione di arrivo/partenza.",
    "• I riquadri tratteggiati indicano dove si trova fisicamente l'apparecchio (in camera, scatola prese…).",
    "• GPIO e pin dei connettori H1 / H2 della scheda -A1: assegnazione e piedinatura completa sul folio 6.",
    "• I nodi (punti neri) sono ponticelli sulle morsettiere (-X0, -X2, -XPE, -X3) o derivazioni a pettine.",
    "• <b>Rev. B</b>: i folii 7, 8 e 9 riportano la proposta con sezionatore -Q0, protezioni -F1…-F3 e contattori -Q1…-Q7;",
    "&nbsp;&nbsp;i folii 2–5 sono ancora alla rev. A e portano un avviso in basso.",
]), 520, 560, size=9)

# ----------------------------------------------------------------------------- folio 2: 230 V
d = d2
T1 = box("alimentatore_hdr_30_12", 120, 120,
         [("n", 40, "L"), ("s", 40, "N"), ("e", 40, "+V", "+12 V"), ("e", 80, "-V", "0 V")],
         [(14, 52, "Mean Well"), (14, 62, "HDR-30-12"), (14, 76, "230 V~ / 12 V= 2 A", 5)])
A3_MIS = box("pzem016_misura", 140, 200,
             [("n", 40, "L"), ("s", 40, "N"), ("e", 80, "TA1", "TA"), ("e", 120, "TA2", "TA")],
             [(14, 90, "PZEM-016"), (14, 102, "misura V / I", 5), (14, 112, "(RS485: folio 6)", 5)])

d.text(html(["<b>Da quadro generale</b>", "linea già protetta: 16 A + Id 30 mA"]), 330, 40, size=8)
src = d.add(SYM["sorgente"], 280, 70, orientation=1)  # ruotata: PE, N, L da sinistra a destra
x0pe = d.add(SYM["morsetto_pe"], 200, 200, "-X0:PE")
x0n = d.add(SYM["morsetto"], 280, 200, "-X0:N")
x0l = d.add(SYM["morsetto"], 360, 200, "-X0:L", infos=info("-X0:L"))
d.wire(src.t[2], side(x0l, "n"), color=C["L"])
d.wire(src.t[0], side(x0n, "n"), color=C["N"])
pe(d, src.t[1], side(x0pe, "n"))

t1 = d.add(T1, 480, 380, "-T1", infos=info("-T1"))
a3 = d.add(A3_MIS, 800, 380, "-A3", infos=info("-A3"))
b3 = d.add(SYM["termostato"], 1160, 390, "-B3", infos=info("-B3"))
ta = d.add(SYM["ta"], 1160, 500, "-A3:TA", orientation=2, label_pos=(16, -24))

# fase
l1, l2, l3 = d.node(520, 300), d.node(840, 300), d.node(1160, 300)
d.wire(side(x0l, "s"), l1, color=C["L"], num="L")
d.chain(l1, l2, l3, esce(d, "L-prese", 1230, 300, "L → COM K4, K5, K6"), color=C["L"])
d.wire(l1, t1.pin["L"], color=C["L"])
d.wire(l2, a3.pin["L"], color=C["L"])
d.wire(l3, side(b3, "n"), color=C["L"], num="W2-1")
d.wire(side(b3, "s"), side(ta, "n"), color=C["L"], num="W2-2")
d.wire(side(ta, "s"), esce(d, "L-lampade", 1230, 600, "L-lampade → COM K1, K2, K3"), color=C["L"], num="L-lampade")
d.wire(ta.t[2], a3.pin["TA2"], color=C["SEG"])
d.wire(ta.t[1], a3.pin["TA1"], color=C["SEG"])
# neutro
n1, n2, n3 = d.node(520, 640), d.node(840, 640), d.node(960, 640)
d.wire(side(x0n, "s"), n1, color=C["N"], num="N")
d.chain(n1, n2, n3, esce(d, "N-stufa", 1040, 640, "N → stufa"), color=C["N"])
d.wire(n3, esce(d, "N-prese", 1040, 600, "N → prese"), color=C["N"])
d.wire(t1.pin["N"], n1, color=C["N"])
d.wire(a3.pin["N"], n2, color=C["N"])
# protezione
g1, g0, g2 = d.node(560, 700, dot=False), d.node(700, 700), d.node(960, 700)
pe(d, side(x0pe, "s"), g1, num="PE")
pe(d, g1, g0)
pe(d, g0, g2)
pe(d, g2, esce(d, "PE-stufa", 1040, 700, "PE → stufa"))
pe(d, g2, esce(d, "PE-prese", 1040, 740, "PE → prese"))
pe(d, g0, esce(d, "PE-rs485", 780, 750, "PE → Earth RS485 di -A1"))
# 12 V
d.wire(t1.pin["+V"], esce(d, "12V", 680, 420, "+12 V"), color=C["12V"])
d.wire(t1.pin["-V"], esce(d, "0V", 680, 460, "0 V"), color=C["0V"])

d.rect(1090, 340, 1300, 440, dashed=True)
d.text(html(["<b>In camera</b>", "termostato di sicurezza", "a parete, tarato 28–30 °C", "(cavo -W2)"]), 1200, 345, size=7)
d.text(html(["TA apribile del PZEM attorno", "al conduttore L-lampade"]), 1180, 500, size=7)
d.text(html([
    "<b>Note</b>",
    "• -B3 è in serie alle sole lampade ed è indipendente dal software.",
    "• N e PE sono distribuiti a tutti gli utilizzatori con morsetti (-X2…).",
    "• -A3: impostare l'indirizzo Modbus 2 (la sonda -B1 usa 1 o 42).",
    "• -T1 è in classe II: non ha morsetto di terra.",
]), 640, 50, size=8)

# ----------------------------------------------------------------------------- folio 3: stufa
d = d3
COL3 = [(300, "1", C["L"]), (480, "2", C["L2"]), (660, "3", C["L3"])]
ll = entra(d, "L-lampade", 80, 120, "L-lampade")
na, nb = d.node(300, 120), d.node(480, 120)
d.chain(ll, na, nb, color=C["L"], num="L-lampade")
r2, r3 = d.node(480, 560), d.node(660, 560)
for i, (x, n, col) in enumerate(COL3):
    k = d.add(SYM["contatto"], x, 200, f"-K{n}")
    s = d.add(SYM["interruttore"], x, 380, f"-S{n}", infos=info(f"-S{n}"))
    e = d.add(SYM["lampada"], x, 480, f"-E1.{n}", infos=info(f"-E1.{n}"))
    d.wire([na, nb, nb][i], side(k, "n"), color=C["L"])
    d.wire(side(k, "s"), side(s, "n"), color=col, num=f"W1-L{n}")
    d.wire(side(s, "s"), side(e, "n"), color=col)
    d.wire(side(e, "s"), [r2, r2, r3][i], color=C["N"])
d.wire(r2, r3, color=C["N"])
s5 = d.add(SYM["finecorsa_na"], 840, 620, "-S5", infos=info("-S5"))
d.wire(r3, side(s5, "n"), color=C["N"])
cn = d.node(840, 680, dot=False)
d.wire(entra(d, "N-stufa", 80, 680, "N"), cn, color=C["N"], num="W1-N")
d.wire(side(s5, "s"), cn, color=C["N"])
massa = d.add(SYM["massa"], 960, 741, "-E1", infos=info("-E1"))
pe(d, entra(d, "PE-stufa", 80, 720, "PE"), massa.t[0], num="W1-PE")
s4 = d.add(SYM["interruttore"], 1020, 380, "-S4", infos=info("-S4"))
m1 = d.add(SYM["motore_ac"], 1015, 500, "-M1", infos=info("-M1"))
d.wire(side(s4, "s"), m1.t[0], dashed=True)

d.rect(240, 150, 960, 250, dashed=True)
d.text(html(["<b>-A1</b> Waveshare ESP32-S3-Relay-6CH", "relè CH1, CH2, CH3", "morsetti COM – NA (NC non usato)"]), 740, 170, size=7)
d.rect(220, 320, 1110, 780, dashed=True)
d.text("<b>-E1 Stufa a 3 lampade IR, 1200 W</b> (in camera)", 700, 322, size=8)
d.text(html(["<b>-W1</b> cavo 5G1,5 quadro → stufa", "(L1, L2, L3, N, PE)"]), 700, 262, size=7)
d.text(html(["S4 e M1 (rotazione):", "<b>non collegati</b>"]), 1034, 425, size=7)
d.text(html(["carcassa", "(giallo-verde interno)"]), 990, 690, size=7)
d.text(html(["antiribaltamento:", "chiuso a stufa in piedi"]), 900, 625, size=7)
d.text(html(["ritorni lampade uniti", "(filo blu interno)"]), 330, 565, size=7)
d.text(html([
    "<b>Note</b>",
    "• Cavallotto originale tra S1–S2–S3–S4 <b>rimosso</b>:",
    "&nbsp;&nbsp;le tre lampade sono indipendenti.",
    "• S1, S2, S3 restano su «acceso»: servono solo",
    "&nbsp;&nbsp;come esclusione manuale.",
    "• Antiribaltamento -S5: se in origine era sulla fase,",
    "&nbsp;&nbsp;viene <b>spostato sul neutro comune</b> delle lampade.",
    "• Giunzione -W1 ↔ fili interni nella parte bassa",
    "&nbsp;&nbsp;della stufa; da lì agli interruttori filo silicone",
    "&nbsp;&nbsp;18 AWG in guaina di vetro (zona calda).",
    "• Logica (ESPHome): lampade comandate una per",
    "&nbsp;&nbsp;una; la lampada «di base» ruota.",
    "• -B3 (folio 2) toglie la fase a tutte le lampade.",
]), 1125, 120, size=8)

# ----------------------------------------------------------------------------- folio 4: prese
d = d4
CARICO = box("utilizzatore_a_spina", 120, 40, [], [(8, 16, "utilizzatore a spina", 5), (8, 30, "230 V~", 5)])
COL4 = [(300, "4", "1", "-M2"), (560, "5", "2", "-M3"), (820, "6", "3", "-M4")]
lp = entra(d, "L-prese", 80, 120, "L")
la, lb = d.node(300, 120), d.node(560, 120)
d.chain(lp, la, lb, color=C["L"], num="L")
nn = entra(d, "N-prese", 80, 300, "N")
na, nb = d.node(320, 300), d.node(580, 300)
d.chain(nn, na, nb, color=C["N"], num="N")
pp = entra(d, "PE-prese", 80, 520, "PE")
pa, pb = d.node(310, 520), d.node(570, 520)
pe(d, pp, pa, num="PE")
pe(d, pa, pb)
for i, (x, k, xs, m) in enumerate(COL4):
    kk = d.add(SYM["contatto"], x, 200, f"-K{k}")
    pr = d.add(SYM["presa"], x + 10, 420, f"-XS{xs}", infos=info(f"-XS{xs}"))
    d.wire([la, lb, lb][i], side(kk, "n"), color=C["L"])
    d.wire(side(kk, "s"), pr.t[2], color=C["L"])
    d.wire([na, nb, nb][i], pr.t[1], color=C["N"])
    pe(d, pr.t[0], [pa, pb, pb][i])
    d.add(CARICO, x - 20, 580, m, infos=info(m))
    d.text(DISTINTA[m][0], x - 20, 624, size=7)
    d.line(x + 60, 430, x + 60, 580, dashed=True)
    d.line(x + 32, 430, x + 60, 430, dashed=True)
d.rect(240, 150, 1120, 250, dashed=True)
d.text(html(["<b>-A1</b> Waveshare ESP32-S3-Relay-6CH", "relè CH4, CH5, CH6", "morsetti COM – NA (NC non usato)"]), 900, 170, size=7)
d.rect(250, 370, 1010, 475, dashed=True)
d.text(html(["<b>-X1</b> scatola da esterno", "3 prese Schuko", "(accanto al quadro)"]), 895, 425, size=7)
d.text(html([
    "<b>Note</b>",
    "• K5 e K6 sono su GPIO di strapping (45 / 46):",
    "&nbsp;&nbsp;possibile breve scatto all'accensione, per questo",
    "&nbsp;&nbsp;vi sono collegati carichi non critici.",
    "• N e PE comuni alle tre prese.",
    "• Umidificatori ridondanti (K4, K5); estrattore (K6)",
    "&nbsp;&nbsp;sul lato opposto alle ventole.",
]), 1040, 280, size=8)

# ----------------------------------------------------------------------------- folio 5: 12 V / 5 V
d = d5
A1_ALIM = box("waveshare_alimentazione", 160, 340,
              [("n", 60, "VIN+", "VIN 7–36 V"), ("s", 60, "GND"), ("e", 260, "GPIO", "GPIO4 (H1-15)"),
               ("e", 300, "GNDs", "GND (H1-13)")],
              [(14, 150, "Waveshare"), (14, 162, "ESP32-S3-Relay-6CH"), (14, 176, "morsettiera alim. 2 poli", 5),
               (14, 185, "e connettore H1", 5), (14, 250, "PWM ventole", 5)])
T2 = box("dcdc_12_5", 140, 100,
         [("n", 60, "IN+"), ("s", 60, "IN-", "IN−"), ("e", 30, "OUT+", "+5 V"), ("e", 70, "OUT-", "0 V")],
         [(14, 46, "DC-DC"), (14, 58, "12 → 5 V 3 A", 5)])
A2 = box("mosfet_d4184", 140, 120,
         [("n", 60, "OUT-", "OUT−"), ("s", 60, "VIN-", "VIN− / GND"), ("w", 40, "PWM"), ("w", 80, "GND"),
          ("e", 40, "VIN+"), ("e", 80, "OUT+")],
         [(46, 56, "MOSFET"), (46, 68, "D4184", 5)])
a1 = d.add(A1_ALIM, 200, 300, "-A1", infos=info("-A1"))
t2 = d.add(T2, 440, 300, "-T2", infos=info("-T2"))
a2 = d.add(A2, 840, 520, "-A2", infos=info("-A2"))
m5 = d.add(SYM["motore_dc"], 820, 400, "-M5", infos=info("-M5"))
m6 = d.add(SYM["motore_dc"], 980, 400, "-M6", infos=info("-M6"))
v1, v2 = d.node(260, 120), d.node(500, 120)
d.chain(entra(d, "12V", 80, 120, "+12 V"), v1, v2, esce(d, "12V-sonda", 1260, 120, "+12 V → sonda -B1"),
        color=C["12V"], num="+12 V")
d.wire(v1, a1.pin["VIN+"], color=C["12V"])
d.wire(v2, t2.pin["IN+"], color=C["12V"])
z1, z2, z3, z4 = d.node(260, 700), d.node(500, 700), d.node(640, 700), d.node(900, 700)
d.chain(entra(d, "0V", 80, 700, "0 V"), z1, z2, z3, z4, esce(d, "0V-sonda", 1260, 700, "0 V → sonda -B1"),
        color=C["0V"], num="0 V")
d.wire(a1.pin["GND"], z1, color=C["0V"])
d.wire(t2.pin["IN-"], z2, color=C["0V"])
d.wire(t2.pin["OUT-"], z3, color=C["0V"])
d.wire(a2.pin["VIN-"], z4, color=C["0V"])
f5 = d.node(820, 330)
d.wire(t2.pin["OUT+"], f5, color=C["5V"], num="+5 V")
d.wire(f5, side(m5, "n"), color=C["5V"])
d.wire(f5, side(m6, "n"), color=C["5V"])
fm = d.node(900, 480)
d.wire(side(m5, "s"), fm, color=C["0V"])
d.wire(side(m6, "s"), fm, color=C["0V"])
d.wire(fm, a2.pin["OUT-"], color=C["0V"])
d.wire(a1.pin["GPIO"], a2.pin["PWM"], color=C["SEG"], num="PWM")
d.wire(a1.pin["GNDs"], a2.pin["GND"], color=C["0V"])
d.text(html(["ventole in parallelo (+ da -T2,", "− verso OUT− del MOSFET)", "tramite adattatori USB-A", "femmina a morsetti"]), 1050, 360, size=7)
d.text(html(["VIN+ e OUT+ di -A2:", "non collegati (il + delle ventole", "arriva direttamente da -T2)"]), 1000, 545, size=7)
d.text(html([
    "<b>Note</b>",
    "• Masse 0 V di -T1, -T2, -A1 e -A2 in comune.",
    "• PWM ventole: GPIO4, pin 15 del connettore H1;",
    "&nbsp;&nbsp;massa del segnale su H1-13.",
    "• -A2: comando low-side, ingresso logico 3,3 V.",
    "• Selettore sul cavo delle ventole fisso su «alta»:",
    "&nbsp;&nbsp;la velocità è regolata dal PWM.",
]), 1040, 180, size=8)

# ----------------------------------------------------------------------------- folio 6: RS485 e sensori
d = d6
A1_485 = box("waveshare_rs485", 140, 100, [("e", 30, "A"), ("e", 70, "B"), ("w", 50, "Earth")],
             [(40, 40, "Waveshare"), (40, 52, "RS485 isolato", 5), (40, 61, "GPIO17 / 18", 5), (40, 70, "120 Ω: H3 ON", 5)])
A3_485 = box("pzem016_rs485", 140, 140, [("w", 30, "A"), ("w", 70, "B"), ("e", 30, "5V", "5 V"), ("e", 70, "GND")],
             [(40, 100, "PZEM-016"), (40, 112, "RS485, ind. 2", 5)])
B1 = box("sonda_s_th_01", 200, 80, [("n", 60, "V+"), ("n", 100, "GND"), ("n", 140, "A"), ("n", 180, "B")],
         [(14, 48, "Seeed S-TH-01"), (14, 60, "T / UR — Modbus ind. 1, 9600 — 3,6–30 V DC", 5)])
A1_HDR = box("waveshare_h1", 160, 240,
             [("e", 20, "3V3", "3V3 (H1-4, 5)"), ("e", 60, "GND", "GND (H1-3, 8)"), ("e", 100, "DOUT", "GPIO5 (H1-14)"),
              ("e", 140, "SCK", "GPIO6 (H1-12)"), ("e", 180, "SDA", "GPIO8 (H1-9)"), ("e", 220, "SCL", "GPIO9 (H1-7)")],
             [(8, 100, "Waveshare"), (8, 112, "connettore", 5), (8, 121, "H1 (20 pin)", 5)])
A4 = box("hx711", 140, 160,
         [("w", 20, "VCC"), ("w", 60, "GND"), ("w", 100, "DOUT"), ("w", 140, "SCK"),
          ("e", 20, "E+"), ("e", 60, "E-", "E−"), ("e", 100, "A+"), ("e", 140, "A-", "A−")],
         [(52, 84, "HX711")])
B2 = box("cella_di_carico", 120, 160, [("w", 20, "E+"), ("w", 60, "E-", "E−"), ("w", 100, "A+"), ("w", 140, "A-", "A−")],
         [(40, 78, "cella di"), (40, 90, "carico")])
A5 = box("rtc_ds3231", 140, 100, [("n", 40, "VCC"), ("n", 80, "GND"), ("w", 20, "SDA"), ("w", 60, "SCL")],
         [(50, 60, "RTC DS3231"), (50, 72, "(opzionale)", 5)], dashed=True)
a1r = d.add(A1_485, 200, 220, "-A1")
a3r = d.add(A3_485, 1000, 220, "-A3")
b1 = d.add(B1, 540, 360, "-B1", infos=info("-B1"))
ba, bb = d.node(680, 250), d.node(720, 290)
d.chain(a1r.pin["A"], ba, a3r.pin["A"], color=C["A"], num="A")
d.chain(a1r.pin["B"], bb, a3r.pin["B"], color=C["B"], num="B")
d.wire(ba, b1.pin["A"], color=C["A"], num="W3-A")
d.wire(bb, b1.pin["B"], color=C["B"], num="W3-B")
d.wire(entra(d, "12V-sonda", 80, 100, "+12 V"), b1.pin["V+"], color=C["12V"], num="W3 +12 V")
d.wire(entra(d, "0V-sonda", 80, 140, "0 V"), b1.pin["GND"], color=C["0V"], num="W3 GND")
pe(d, entra(d, "PE-rs485", 80, 270, "PE"), a1r.pin["Earth"])
a1h = d.add(A1_HDR, 200, 480, "-A1")
a4 = d.add(A4, 900, 480, "-A4", infos=info("-A4"))
b2 = d.add(B2, 1200, 480, "-B2", infos=info("-B2"))
a5 = d.add(A5, 480, 640, "-A5", infos=info("-A5"))
h3, hg = d.node(520, 500), d.node(560, 540)
d.chain(a1h.pin["3V3"], h3, a4.pin["VCC"], color=C["12V"], num="3,3 V")
d.chain(a1h.pin["GND"], hg, a4.pin["GND"], color=C["0V"], num="GND")
d.wire(a1h.pin["DOUT"], a4.pin["DOUT"], color=C["SEG"], num="DOUT")
d.wire(a1h.pin["SCK"], a4.pin["SCK"], color=C["SEG"], num="SCK")
for pin in ("E+", "E-", "A+", "A-"):
    d.wire(a4.pin[pin], b2.pin[pin], color=C["SEG"])
d.wire(h3, a5.pin["VCC"], color=C["12V"], dashed=True)
d.wire(hg, a5.pin["GND"], color=C["0V"], dashed=True)
d.wire(a1h.pin["SDA"], a5.pin["SDA"], color=C["SEG"], dashed=True, num="SDA")
d.wire(a1h.pin["SCL"], a5.pin["SCL"], color=C["SEG"], dashed=True, num="SCL")
d.rect(500, 330, 840, 450, dashed=True)
d.text(html(["<b>In camera</b>", "cavo -W3", "(4 poli)"]), 750, 380, size=7)
d.rect(860, 440, 1350, 660, dashed=True)
d.text("<b>In camera</b> — -A4 in scatolina IP65 vicino alla cella; cavo di rete -W4", 870, 442, size=7)
d.text(html(["-W4: DOUT accoppiato", "a GND, SCK accoppiato", "a GND (doppini)"]), 740, 630, size=7)
d.text(html(["+5V di -A3 è un'uscita:", "<b>non collegare</b>.", "GND: vedi note"]), 1160, 240, size=7)
d.text(html([
    "<b>Note</b>",
    "• Bus RS485: -A1 → -B1 e -A3 in parallelo (A con A, B con B).",
    "• RS485 di -A1 isolato; il terzo morsetto (G) è il ritorno degli scaricatori, non la massa del bus: G → PE.",
    "• Terminazione 120 Ω: ponticello H3 sulla scheda -A1 abilitato.",
    "• Indirizzi Modbus: -B1 = 1 (o 42: leggerlo), -A3 = 2 (da cambiare sul PZEM, da solo sul bus).",
    "• -B1: 3,6–30 V DC, qui a 12 V da -T1; fili rosso V+, nero GND, giallo A, bianco B.",
    "• -A5 RTC opzionale (tratteggiato): I²C, VCC 3,3 V, GND.",
    "• PZEM-016: RS485 alimentata dall'interno e optoisolata secondo il manuale, che però non dichiara",
    "&nbsp;&nbsp;la tensione di isolamento: provarla prima di collegare. GND → 0 V solo a prova superata (folio 9).",
]), 700, 30, size=8)


def cella_pin(nome, uso=None):
    return f"<b>{nome} → {uso}</b>" if uso else nome


meta = lambda a, b: [(str(i), cella_pin(H1[i - 1], USO_H1.get(i)), H2[i - 1]) for i in range(a, b)]
d.text("<b>-A1 — piedinatura connettori H1 / H2</b> (in grassetto i pin usati; riserva libera: GPIO7, 10, 39, 40, 11–16, 47, 48)",
       60, 772, size=8)
d.text(tabella(["Pin", "H1", "H2"], meta(1, 8)), 60, 795, size=7)
d.text(tabella(["Pin", "H1", "H2"], meta(8, 15)), 500, 795, size=7)
d.text(tabella(["Pin", "H1", "H2"], meta(15, 21)), 960, 795, size=7)

# ----------------------------------------------------------------------------- folio 7: piastra
# Disposizione fisica preliminare (rev. B): piastra di fondo con 4 guide DIN e canaline, in scala 2 px = 1 mm.
# Ipotesi: cassetta ~400 × 600 × 200 mm con piastra utile 350 × 550 mm (da confermare all'acquisto).
d = d7
MM, PX0, PY0 = 2, 150, 120
Z230, ZSELV, C230, CSELV, PONTE, APP = "#ffece8", "#e6efff", "#ffb9a8", "#a9c7ff", "#fff2b0", "#f2f2f2"


def mm(x, y):
    return PX0 + x * MM, PY0 + y * MM


def area(x1, y1, x2, y2, fill, **kw):
    d.rect(*mm(x1, y1), *mm(x2, y2), fill=fill, **kw)


def canalina(x1, y1, x2, y2, fill, nome, vert=False):
    area(x1, y1, x2, y2, fill)
    px, py = mm(x1, y1)
    if vert:
        d.text(nome, px + 2, py + (y2 - y1) * MM / 2 + 150, size=6, rotation=270)
    else:
        d.text(nome, px + 6, py + 12, size=6)


def app(x, y, w, h, righe, fill=APP, vert=False):
    area(x, y, x + w, y + h, fill)
    px, py = mm(x, y)
    if vert:
        d.text(" ".join(righe), px + 2, py + h * MM - 6, size=6, rotation=270)
    else:
        d.text(html(righe), px + 3, py + 4, size=6)


d.text("<b>Disposizione su piastra — proposta preliminare rev. B</b> (vista frontale, scala 2 px = 1 mm; quote in mm)", 60, 30, size=9)
d.rect(*mm(-25, -25), *mm(375, 590), width=2)
d.text("cassetta ~400 × 600 × 200 mm (ipotesi)", *mm(-22, -24), size=6)
area(0, 0, 350, 550, Z230)
d.text("piastra di fondo 350 × 550", PX0 + 240, PY0 + 2, size=6)
# zone SELV: colonna destra, guida C, canalina C3 e parte destra della guida D
area(320, 0, 350, 550, ZSELV, color=ZSELV)
area(160, 303, 350, 407, ZSELV, color=ZSELV)
area(145, 407, 350, 550, ZSELV, color=ZSELV)
# guide DIN
for yc, nome in ((85, "A"), (220, "B"), (355, "C"), (485, "D")):
    area(30, yc - 4, 320, yc + 4, "#c8c8c8", color="#909090")
    d.text(f"<b>{nome}</b>", PX0 - 22, PY0 + yc * MM - 12, size=9)
# canaline
canalina(0, 10, 25, 435, C230, "CV1 — 230 V", vert=True)
canalina(325, 10, 350, 540, CSELV, "CV2 — SELV (12 / 5 / 3,3 V e segnali)", vert=True)
canalina(25, 10, 215, 35, C230, "C0 — 230 V")
canalina(25, 140, 318, 165, C230, "C1 — 230 V")
canalina(25, 275, 318, 300, C230, "C2 — 230 V + comandi bobine 12 V (filo isolato 450/750 V)")
canalina(25, 410, 135, 435, C230, "C3a — 230 V")
canalina(150, 410, 325, 435, CSELV, "C3b — SELV")
for x, y in ((318, 140), (318, 275)):  # tappi: C1 e C2 non comunicano con CV2
    d.line(*mm(x, y), *mm(x, y + 25), width=3)
d.line(*mm(142, 405), *mm(142, 540), width=3)  # setto separatore tra morsettiere 230 V e SELV
# guida A
app(35, 40, 35, 90, ["<b>-Q0</b>", "sez.", "2P"])
for i, (n, t) in enumerate((("-F1", "C10"), ("-F2", "C6"), ("-F3", "C6"))):
    app(72 + i * 18, 40, 17.5, 90, [f"<b>{n}</b> {t}"], vert=True)
area(130, 40, 262, 130, None, dashed=True, color="#909090")
d.text("riserva", *mm(180, 78), size=6)
app(265, 40, 52.5, 90, ["<b>-T1</b>", "HDR-60-12", "uscita 12 V", "↑ in alto", "", "", "", "", "", "ingresso", "230 V ↓"], fill=PONTE)
# guida B
app(35, 175, 17.5, 90, ["<b>-Q7</b> sicurezza"], vert=True)
for i in range(6):
    app(57 + i * 18, 175, 17.5, 90, [f"<b>-Q{i + 1}</b>"], vert=True)
area(167, 175, 222, 265, None, dashed=True, color="#909090")
d.text("riserva", *mm(180, 213), size=6)
app(225, 190, 90, 60, ["<b>-A3</b> PZEM-016", "", "← L N TA"], fill=PONTE)
d.text("RS485 →", *mm(288, 232), size=6)
# guida C
area(35, 310, 162, 400, None, dashed=True, color="#909090")
d.text("riserva", *mm(85, 348), size=6)
app(170, 310, 145, 90, ["↑ morsettiera relè: solo comandi bobine 12 V", "", "<b>-A1</b> Waveshare ESP32-S3-Relay-6CH", "145 × 90 × 40", "", "", "", "↓ alimentazione 12 V, RS485, H1"])
# guida D
app(35, 450, 100, 70, ["<b>-X0</b> linea L N PE", "<b>-X2</b> uscite stufa, prese", "<b>-XPE</b> terra"])
app(160, 450, 35, 70, ["<b>-T2</b>", "DC-DC"])
app(197, 450, 35, 70, ["<b>-A2</b>", "MOSFET"])
app(238, 450, 80, 70, ["<b>-X3</b> SELV", "sonda, HX711,", "ventole,", "termostato"])
# pressacavi sul fondo della cassetta
for x, nome in ((35, "linea"), (75, "-W1"), (115, "prese"), (170, "-W3"), (205, "-W4"), (240, "M5"), (275, "M6"), (310, "-W2")):
    px, py = mm(x, 568)
    d.ellipse(px - 16, py - 16, px + 16, py + 16, fill="#ffffff")
    d.text(nome, px - 14, py + 48, size=6)
d.text("pressacavi 230 V", *mm(30, 606), size=7)
d.text("pressacavi SELV", *mm(200, 606), size=7)
d.rect(*mm(0, 0), *mm(350, 550))

d.text("<b>Zone e canaline</b>" + tabella(["", "Zona", "Contenuto"], [
    (f'<span style="color:{C230}">■■</span>', "230 V", "linea, protezioni, contatti dei contattori, uscite verso stufa e prese"),
    (f'<span style="color:{CSELV}">■■</span>', "SELV", "12 V, 5 V, 3,3 V, RS485, HX711, PWM, termostato -B3"),
    (f'<span style="color:#e0c000">■■</span>', "a cavallo", "-T1 e -A3: isolamento interno tra i due lati (vedi criticità)"),
    ("▌", "barriera", "tappi di C1 e C2 verso CV2; setto tra -X2 e -T2 sulla guida D"),
]), 960, 100, size=7)
d.text(html([
    "<b>Percorsi</b>",
    "• <b>230 V</b>: linea e cavi di stufa e prese entrano in basso a sinistra, si attestano su -X0 / -X2 e salgono in CV1.",
    "&nbsp;&nbsp;C0 alimenta -Q0 e -F1…-F3 dall'alto; C1 porta le uscite degli interruttori ai contattori, a -A3 e a -T1;",
    "&nbsp;&nbsp;C2 raccoglie le uscite dei contattori e le riporta a -X2 passando da CV1.",
    "• <b>Comandi bobine</b> (12 V): dalla morsettiera relè di -A1 (bordo alto) salgono in C2 fino ad A1/A2 dei contattori.",
    "&nbsp;&nbsp;Stanno nella canalina di potenza, quindi vanno fatti con filo isolato per 230 V (H05V-K / H07V-K).",
    "• <b>SELV</b>: dal bordo basso di -A1 (alimentazione, RS485, H1) in C3b e CV2; i cavi dei sensori entrano in basso a destra",
    "&nbsp;&nbsp;e si attestano su -X3. L'uscita 12 V di -T1 e il lato RS485 di -A3 entrano direttamente in CV2.",
    "• Nessun conduttore SELV in CV1, C0, C1; nessun conduttore 230 V in CV2, C3b. C1 e C2 sono tappate verso CV2.",
    "",
    "<b>Separazione per sicurezza</b> (obbligatoria)",
    "• Circuiti SELV e 230 V nella stessa canalina solo se <i>ogni</i> conduttore è isolato per la tensione più alta",
    "&nbsp;&nbsp;(regola CEI 64-8 art. 528.1): vale per i comandi bobine, non per i cavetti di sensori e RS485.",
    "• Sulla scheda -A1 non arriva più il 230 V: i contatti dei relè di bordo commutano solo i 12 V delle bobine.",
    "• Morsetti 230 V e SELV sulla guida D separati da fermi, setto e almeno 30 mm.",
    "",
    "<b>Separazione per i disturbi</b> (consigliata)",
    "• RS485 e cavo HX711 su doppini intrecciati, lontani da C2 e dai contattori; incroci a 90°.",
    "• Andata e ritorno delle ventole (corrente PWM) intrecciati tra loro e non affiancati a DOUT / SCK dell'HX711.",
    "• In CV2 tenere su un lato le alimentazioni e sull'altro i segnali; fili di segnale non più lunghi del necessario.",
    "",
    "<b>Ipotesi da confermare</b>",
    "• Dimensioni di cassetta e piastra; il centralino da 24 moduli (37 × 28 × 11,5 cm) non contiene questa disposizione.",
    "• -T1: montaggio verticale con ingresso in basso e uscita in alto, 40 mm liberi sopra e 20 sotto (manuale Mean Well).",
    "• -A3 non ha attacco DIN dichiarato: su clip o a vite sulla piastra, lato rete a sinistra.",
    "• Connettore H1 di -A1 interno al contenitore: verificare da dove far uscire i fili (PWM, HX711).",
    "• Piastra metallica: va collegata a -XPE. Pressacavi adatti al diametro di ogni cavo (M20 per i 230 V, M12 per i sensori).",
]), 960, 230, size=7)

# ----------------------------------------------------------------------------- folio 8: distinta
d = d8
d.text("<b>Distinta componenti</b> — generata da QElectroTech dalle informazioni degli elementi", 50, 20, size=9)
d.table(50, 90, 1330, 620,
        "SELECT label, description, comment, manufacturer, designation, diagram_position "
        "FROM element_nomenclature_view WHERE description <> '' ORDER BY label",
        ["Sigla", "Componente", "Note", "Costruttore", "Riferimento", "Folio"], rows=len(DISTINTA) + 1, font=7)
d.text("<b>Cavi, morsetti e meccanica</b> (non rappresentati come elementi)" + tabella(["Sigla", "Descrizione", "Note"], CAVI), 50, 800, size=7)
d.text("<b>Modifiche ai materiali — rev. B</b> (proposta, vedi folii 7 e 9)" + tabella(["", "Sigla", "Materiale", "Motivo / note"], MODIFICHE), 50, 1040, size=7)

# ----------------------------------------------------------------------------- folio 9: cablaggio
# Vista d'insieme rev. B: apparecchi sulle quattro guide della piastra (folio 7) e ogni filo tracciato da
# morsetto a morsetto. I percorsi sono espliciti: ogni filo ha la sua "pista" orizzontale e la sua "corsia".
d = d9


def qbox(nome, w, h, pins, lines=()):
    return p.define("q_" + nome, make_box(nome, w, h, pins, lines, font=5, label_at=(6, h / 2 - 18)))


def xy(t):
    return (t.x, t.y) if hasattr(t, "is_node") else t.pos


def posa(a, punti, b, **kw):
    """Filo da a a b passando per gli angoli indicati (tratti solo orizzontali o verticali)."""
    tappe = [a] + [d.node(x, y, dot=False) for x, y in punti] + [b]
    for u, v in zip(tappe, tappe[1:]):
        pu, pv = xy(u), xy(v)
        assert abs(pu[0] - pv[0]) < 0.5 or abs(pu[1] - pv[1]) < 0.5, f"tratto obliquo {pu} -> {pv}"
        d.wire(u, v, **kw)
        kw = dict(kw, num="")


def barra(y, prese, da=None, via=(), **kw):
    """Pista orizzontale a quota y con una derivazione verticale per ogni morsetto di `prese`.

    `da` è il morsetto (o nodo) che alimenta la pista passando per gli angoli `via`: arriva su un'estremità.
    """
    num = kw.pop("num", "")
    per_x = {}
    for t in prese:
        per_x.setdefault(round(t.pos[0]), []).append(t)
    xs = sorted(per_x)
    capo = None
    if da is not None:
        fx = via[-1][0] if via else xy(da)[0]
        capo = xs[0] if fx < xs[0] else xs[-1]
        assert fx < xs[0] or fx > xs[-1], f"alimentazione della pista y={y} non a un'estremità"
    nodi = {}
    for i, x in enumerate(xs):
        rami = len(per_x[x]) + (i > 0) + (i < len(xs) - 1) + (x == capo)
        nodi[x] = d.node(x, y, dot=rami >= 3)
        for t in per_x[x]:
            d.wire(t, nodi[x], **kw)
    for u, v in zip(xs, xs[1:]):
        d.wire(nodi[u], nodi[v], **kw)
    if da is not None:
        posa(da, list(via), nodi[capo], num=num, **kw)
    return nodi


def pins(side, items):
    return [(side, off, name, shown) for off, name, shown in items]


def serie(side, nomi, passo, primo, pref=""):
    """Morsetti equidistanti: nome interno con prefisso, testo mostrato senza."""
    return [(side, primo + i * passo, pref + n, "" if pref.endswith("^") else n.split("/")[-1])
            for i, n in enumerate(nomi)]


X1_M = ["W1/L1", "W1/L2", "W1/L3", "W1/N", "W1/PE", "P/XS1", "P/XS2", "P/XS3", "P/N", "P/PE"]
X3_M = ["W3/+12", "W3/0V", "W3/A", "W3/B", "W4/3V3", "W4/GND", "W4/DT", "W4/SCK", "M5/+", "M5/−", "M6/+", "M6/−",
        "W2/1", "W2/2"]
rele = []
for i in range(6):
    rele += [(25 + i * 70, f"NA{i + 1}", "NA"), (45 + i * 70, f"COM{i + 1}", "C")]
CONT = pins("n", [(20, "1", "1")]) + pins("s", [(20, "2", "2"), (50, "A1", "A1"), (70, "A2", "A2")])
INT = pins("n", [(20, "Li", "L"), (60, "Ni", "N")]) + pins("s", [(20, "L", "L"), (60, "N", "N")])
Q = {
    "linea": qbox("linea_230v", 80, 50, pins("n", [(15, "L", "L"), (40, "N", "N"), (65, "PE", "PE")]),
                  [(4, 30, "da quadro generale", 5), (4, 40, "16 A + Id 30 mA", 5)]),
    "x0": qbox("morsetti_x0", 80, 80, serie("n", ["L", "N", "PE"], 25, 15, "^") + serie("s", ["L", "N", "PE"], 25, 15),
               [(30, 56, "linea", 5)]),
    "x1": qbox("morsetti_x1", 268, 80, serie("n", X1_M, 26, 20, "^") + serie("s", X1_M, 26, 20),
               [(60, 56, "uscite 230 V: stufa (-W1) e prese", 5)]),
    "q0": qbox("sezionatore", 80, 80, pins("n", [(20, "1", "1"), (60, "3", "3")]) + pins("s", [(20, "2", "2"), (60, "4", "4")]),
               [(30, 48, "sezionatore 2P", 5)]),
    "f1": qbox("int_f1", 80, 80, INT, [(30, 40, "C10 1P+N", 5), (30, 50, "stufa", 5)]),
    "f2": qbox("int_f2", 80, 80, INT, [(30, 40, "C6 1P+N", 5), (30, 50, "prese", 5)]),
    "f3": qbox("int_f3", 80, 80, INT, [(30, 40, "C6 1P+N", 5), (30, 50, "ausiliari", 5)]),
    "t1": qbox("hdr_60_12", 120, 80, pins("s", [(30, "L", "L"), (60, "N", "N")]) + pins("n", [(70, "+V", "+12"), (100, "-V", "0V")]),
               [(34, 40, "Mean Well HDR-60-12", 5), (34, 50, "classe II: senza PE", 5)]),
    "ta": qbox("ta_apribile", 40, 20, pins("w", [(10, "P1", "")]) + pins("e", [(10, "P2", "")])
               + pins("n", [(10, "S1", ""), (30, "S2", "")]), [(13, 14, "TA", 5)]),
    "q7": qbox("contattore_sicurezza", 80, 90, CONT, [(30, 44, "sicurezza", 5), (30, 54, "lampade", 5)]),
    "q": qbox("contattore", 80, 90, CONT, [(30, 50, "25 A", 5)]),
    "a3": qbox("pzem016", 140, 90, pins("w", [(15, "L", "L"), (35, "N", "N"), (55, "TA1", "TA"), (75, "TA2", "TA")])
               + pins("e", [(15, "5V", "+5V"), (35, "B", "B"), (55, "A", "A"), (75, "GND", "GND")]),
               [(44, 54, "PZEM-016", 5), (44, 64, "(Modbus ind. 2)", 5)]),
    "a1": qbox("waveshare_6ch", 500, 120,
               pins("n", rele)
               + pins("s", [(110, "3V3", "3V3"), (130, "GNDh", "GND"), (150, "GPIO5", "IO5"), (170, "GPIO6", "IO6"),
                            (210, "GPIO4", "IO4"), (230, "GNDp", "GND"), (335, "VIN+", "+"), (365, "GND", "−"),
                            (395, "A", "A+"), (425, "B", "B−"), (470, "G", "G")]),
               [(40, 60, "Waveshare ESP32-S3-Relay-6CH", 7)]
               + [(28 + i * 70, 22, f"K{i + 1}", 5) for i in range(6)]
               + [(100, 104, "connettore H1 (interno)", 5), (326, 104, "7–36 V", 5), (392, 104, "RS485", 5)]),
    "t2": qbox("dcdc_5v", 80, 80, pins("n", [(10, "IN+", "IN+"), (30, "IN-", "IN−"), (50, "+5V", "+5"), (70, "0V", "0V")]),
               [(30, 56, "DC-DC 5 V", 5)]),
    "a2": qbox("mosfet", 90, 80, pins("n", [(15, "PWM", "PWM"), (35, "GND", "GND"), (55, "VIN-", "VIN−"), (75, "OUT-", "OUT−")]),
               [(30, 56, "MOSFET D4184", 5)]),
    "x3": qbox("morsetti_x3", 420, 80, serie("n", X3_M, 30, 15, "^") + serie("s", X3_M, 30, 15),
               [(60, 56, "morsetti SELV: sonda (-W3), HX711 (-W4), ventole, termostato (-W2)", 5)]),
    "e1": qbox("stufa", 128, 70, serie("n", ["L1", "L2", "L3", "N", "PE"], 26, 12), [(40, 50, "stufa 3 lampade IR", 5)]),
    "pr": qbox("scatola_prese", 128, 70, serie("n", ["XS1", "XS2", "XS3", "N", "PE"], 26, 12),
               [(34, 44, "3 prese Schuko:", 5), (34, 54, "umidif. 1, 2, estrattore", 5)]),
    "b1": qbox("sonda_q", 114, 70, serie("n", ["V+", "GND", "A", "B"], 30, 12),
               [(34, 44, "sonda S-TH-01", 5), (6, 62, "rosso, nero, giallo, bianco", 5)]),
    "a4": qbox("hx711_q", 114, 70, serie("n", ["VCC", "GND", "DT", "SCK"], 30, 12)
               + serie("s", ["E+", "E−", "A+", "A−"], 30, 12), [(40, 40, "HX711", 5)]),
    "b2": qbox("cella_q", 114, 50, serie("n", ["E+", "E−", "A+", "A−"], 30, 12), [(40, 38, "cella di carico", 5)]),
    "fan": qbox("ventola_usb", 54, 70, serie("n", ["+", "−"], 30, 12), [(6, 56, "ventola USB", 5)]),
    "b3": qbox("termostato", 54, 70, serie("n", ["1", "2"], 30, 12), [(4, 50, "termostato", 5), (4, 59, "di sicurezza", 5)]),
}
YA, YB, YC, YD, YF = 110, 380, 660, 950, 1180  # guide A–D e apparecchi esterni
q0 = d.add(Q["q0"], 150, YA, "-Q0")
f1 = d.add(Q["f1"], 290, YA, "-F1")
f2 = d.add(Q["f2"], 430, YA, "-F2")
f3 = d.add(Q["f3"], 570, YA, "-F3")
t1 = d.add(Q["t1"], 1120, YA, "-T1")
ta = d.add(Q["ta"], 220, 290, "-A3:TA", label_pos=(-10, 22))
q7 = d.add(Q["q7"], 150, YB, "-Q7")
qk = [d.add(Q["q"], 270 + i * 100, YB, f"-Q{i + 1}") for i in range(6)]
a3 = d.add(Q["a3"], 950, YB, "-A3")
a1 = d.add(Q["a1"], 840, YC, "-A1")
x0 = d.add(Q["x0"], 150, YD, "-X0")
x1 = d.add(Q["x1"], 270, YD, "-X2")
t2 = d.add(Q["t2"], 850, YD, "-T2")
a2 = d.add(Q["a2"], 1035, YD, "-A2")
x3 = d.add(Q["x3"], 1160, YD, "-X3")
ql = d.add(Q["linea"], 150, YF)
e1 = d.add(Q["e1"], 278, YF, "-E1")
pr = d.add(Q["pr"], 408, YF, "-X1")
b1 = d.add(Q["b1"], 1163, YF, "-B1")
a4 = d.add(Q["a4"], 1283, YF, "-A4")
b2 = d.add(Q["b2"], 1283, YF + 100, "-B2")
m5 = d.add(Q["fan"], 1403, YF, "-M5")
m6 = d.add(Q["fan"], 1463, YF, "-M6")
b3 = d.add(Q["b3"], 1523, YF, "-B3")

L, N = dict(color=C["L"]), dict(color=C["N"])
PE = dict(color=C["PE"], color2=C["PE2"])
V12, V0, V5, SEG, CMD = (dict(color=C[k]) for k in ("12V", "0V", "5V", "SEG", "CMD"))
# ---- cavi esterni: dritti dai morsetti agli apparecchi
for n in ("L", "N", "PE"):
    posa(x0.pin[n], [], ql.pin[n], **{"L": L, "N": N, "PE": PE}[n])
for n, col in (("L1", L), ("L2", dict(color=C["L2"])), ("L3", dict(color=C["L3"])), ("N", N), ("PE", PE)):
    posa(x1.pin["W1/" + n], [], e1.pin[n], **col)
for n, col in (("XS1", L), ("XS2", L), ("XS3", L), ("N", N), ("PE", PE)):
    posa(x1.pin["P/" + n], [], pr.pin[n], **col)
for (m, n), col in zip((("W3/+12", "V+"), ("W3/0V", "GND"), ("W3/A", "A"), ("W3/B", "B")),
                       (V12, V0, dict(color=C["A"]), dict(color=C["B"]))):
    posa(x3.pin[m], [], b1.pin[n], **col)
for (m, n), col in zip((("W4/3V3", "VCC"), ("W4/GND", "GND"), ("W4/DT", "DT"), ("W4/SCK", "SCK")), (V12, V0, SEG, SEG)):
    posa(x3.pin[m], [], a4.pin[n], **col)
for n in ("E+", "E−", "A+", "A−"):
    posa(a4.pin[n], [], b2.pin[n], **SEG)
for m, el in (("M5", m5), ("M6", m6)):
    posa(x3.pin[m + "/+"], [], el.pin["+"], **V5)
    posa(x3.pin[m + "/−"], [], el.pin["−"], **V0)
posa(x3.pin["W2/1"], [], b3.pin["1"], **V12)
posa(x3.pin["W2/2"], [], b3.pin["2"], **CMD)
# ---- 230 V: linea -> sezionatore -> interruttori
posa(x0.pin["^L"], [(165, 900), (90, 900), (90, 40), (170, 40)], q0.pin["1"], **L)
posa(x0.pin["^N"], [(190, 890), (100, 890), (100, 30), (210, 30)], q0.pin["3"], **N)
barra(70, [f.pin["Li"] for f in (f1, f2, f3)], da=q0.pin["2"], via=[(170, 220), (120, 220), (120, 70)], **L)
barra(60, [f.pin["Ni"] for f in (f1, f2, f3)], da=q0.pin["4"], via=[(210, 230), (130, 230), (130, 60)], **N)
# ---- ramo stufa: -F1 -> TA -> -Q7 (sicurezza) -> -Q1…-Q3 -> -X1
posa(f1.pin["L"], [(310, 300)], ta.pin["P2"], **L)
posa(ta.pin["P1"], [(170, 300)], q7.pin["1"], **L)
barra(330, [q.pin["1"] for q in qk[:3]], da=q7.pin["2"], via=[(170, 500), (250, 500), (250, 330)], **L)
posa(qk[0].pin["2"], [], x1.pin["^W1/L1"], **L)
posa(qk[1].pin["2"], [(390, 800), (316, 800)], x1.pin["^W1/L2"], color=C["L2"])
posa(qk[2].pin["2"], [(490, 810), (342, 810)], x1.pin["^W1/L3"], color=C["L3"])
posa(f1.pin["N"], [(350, 250), (140, 250), (140, 910), (368, 910)], x1.pin["^W1/N"], **N)
posa(ta.pin["S1"], [(230, 220), (900, 220), (900, 435)], a3.pin["TA1"], **SEG)
posa(ta.pin["S2"], [(250, 230), (910, 230), (910, 455)], a3.pin["TA2"], **SEG)
# ---- ramo prese: -F2 -> -Q4…-Q6 -> -X1
barra(350, [q.pin["1"] for q in qk[3:]], da=f2.pin["L"], via=[(450, 350)], **L)
for i, y in ((3, 820), (4, 830), (5, 840)):
    sx, tx = qk[i].pin["2"].pos[0], x1.pin[f"^P/XS{i - 2}"].pos[0]
    posa(qk[i].pin["2"], [(sx, y), (tx, y)], x1.pin[f"^P/XS{i - 2}"], **L)
posa(f2.pin["N"], [(490, 260), (130, 260), (130, 880), (498, 880)], x1.pin["^P/N"], **N)
# ---- ausiliari: -F3 -> -T1 e misura di tensione di -A3
nl, nn = d.node(880, 270), d.node(890, 280)
posa(f3.pin["L"], [(590, 270)], nl, **L)
posa(nl, [(880, 395)], a3.pin["L"], **L)
posa(nl, [(1150, 270)], t1.pin["L"], **L)
posa(f3.pin["N"], [(630, 280)], nn, **N)
posa(nn, [(890, 415)], a3.pin["N"], **N)
posa(nn, [(1180, 280)], t1.pin["N"], **N)
# ---- protezione: -X0:PE -> PE dei cavi e morsetto G (scaricatori RS485) di -A1
gp = barra(870, [x1.pin["^W1/PE"], x1.pin["^P/PE"]], da=x0.pin["^PE"], via=[(215, 870)], **PE)
posa(gp[max(gp)], [(1310, 870)], a1.pin["G"], **PE)
# ---- +12 V: corsia x=1600; 0 V: corsia x=1610
n12 = d.node(1600, 620)
posa(t1.pin["+V"], [(1190, 60), (1600, 60)], n12, num="+12 V", **V12)
barra(620, [a1.pin[f"COM{k}"] for k in range(1, 7)], da=n12, **V12)
barra(810, [a1.pin["VIN+"], x3.pin["^W3/+12"], x3.pin["^W2/1"], t2.pin["IN+"]], da=n12, via=[(1600, 810)], **V12)
n0a, n0b = d.node(1610, 455), d.node(1610, 510)
posa(t1.pin["-V"], [(1220, 50), (1610, 50)], n0a, num="0 V", **V0)
d.wire(n0a, n0b, **V0)
barra(510, [q.pin["A2"] for q in [q7] + qk], da=n0b, **V0)
barra(820, [a1.pin["GND"], x3.pin["^W3/0V"], a2.pin["VIN-"], t2.pin["0V"], t2.pin["IN-"]], da=n0b, via=[(1610, 820)], **V0)
posa(a3.pin["GND"], [], n0a, dashed=True, **V0)
# ---- comandi bobine: NA dei relè di -A1 -> A1 dei contattori; catena di sicurezza del termostato -> -Q7
for k in range(6):
    sx, tx, y = qk[k].pin["A1"].pos[0], a1.pin[f"NA{k + 1}"].pos[0], 600 - 10 * k
    posa(qk[k].pin["A1"], [(sx, y), (tx, y)], a1.pin[f"NA{k + 1}"], **CMD)
posa(x3.pin["^W2/2"], [(1565, 890), (1640, 890), (1640, 530), (200, 530)], q7.pin["A1"], num="W2-2", **CMD)
# ---- 5 V e ventole
barra(850, [x3.pin["^M5/+"], x3.pin["^M6/+"]], da=t2.pin["+5V"], via=[(900, 850)], **V5)
barra(860, [x3.pin["^M5/−"], x3.pin["^M6/−"]], da=a2.pin["OUT-"], via=[(1110, 860)], **V0)
posa(a1.pin["GPIO4"], [], a2.pin["PWM"], num="PWM", **SEG)
posa(a1.pin["GNDp"], [], a2.pin["GND"], **V0)
# ---- HX711 (-W4)
for n, m, y, col in (("3V3", "3V3", 910, V12), ("GNDh", "GND", 900, V0), ("GPIO5", "DT", 890, SEG), ("GPIO6", "SCK", 880, SEG)):
    sx, tx = a1.pin[n].pos[0], x3.pin["^W4/" + m].pos[0]
    posa(a1.pin[n], [(sx, y), (tx, y)], x3.pin["^W4/" + m], **col)
# ---- RS485: -A1 -> -X3 (sonda) con derivazione verso -A3
ra, rb = d.node(1235, 830), d.node(1265, 840)
for n, nodo, corsia, col in (("A", ra, 1620, C["A"]), ("B", rb, 1630, C["B"])):
    d.wire(a1.pin[n], nodo, color=col)
    d.wire(nodo, x3.pin["^W3/" + n], color=col)
    y = a3.pin[n].pos[1]
    posa(a3.pin[n], [(corsia, y), (corsia, xy(nodo)[1])], nodo, color=col)

d.rect(60, 14, 1670, 1090, width=2)
d.text("<b>Cassetta con piastra</b> (in cantina) — disposizione fisica: folio 7", 660, 130, size=8)
for y, nome in ((YA, "A"), (YB, "B"), (YC, "C"), (YD, "D")):
    d.text(f'<span style="font-size:14pt"><b>{nome}</b></span>', 62, y + 20)
for x1_, x2_, nome in ((155, 225, "linea"), (282, 402, "-W1"), (412, 532, "prese"), (1167, 1273, "-W3"), (1287, 1393, "-W4"),
                       (1407, 1513, "ventole"), (1527, 1573, "-W2")):
    d.ellipse(x1_, 1082, x2_, 1098, color="#808080")
    d.text(nome, x1_ + 2, 1100, size=7)
d.text(html(["+5V di -A3: uscita,", "<b>non collegare</b>"]), 1100, 350, size=6)
d.text(html(["GND di -A3 → 0 V: solo dopo", "la prova di isolamento"]), 1100, 464, size=6)
d.text("L-lampade", 298, 334, size=6)
d.text("PE → piastra di fondo (se metallica)", 560, 852, size=6)
d.text(html([
    "<b>Vista d'insieme del cablaggio — rev. B</b>",
    "• Sulla scheda -A1 non arriva il 230 V: i relè di bordo K1…K6 commutano i 12 V delle bobine dei contattori -Q1…-Q6",
    "&nbsp;&nbsp;(isolamento rinforzato bobina/contatti). -Q1…-Q3 lampade, -Q4…-Q5 umidificatori, -Q6 estrattore.",
    "• Termostato di sicurezza -B3 sulla bobina di -Q7, a 12 V: -Q7 toglie la fase a tutte le lampade senza passare",
    "&nbsp;&nbsp;dalla scheda e dal software. In camera non c'è più il 230 V sul termostato.",
    "• Neutri separati per ramo: stufa da -F1, prese da -F2, ausiliari da -F3. Non unire i neutri a valle degli interruttori.",
    "• -T1 è in classe II: nessun morsetto di terra. 0 V e PE non sono collegati tra loro.",
    "• Morsetto G di -A1: ritorno degli scaricatori della RS485, non è la massa del bus.",
    "• I punti neri sono ponticelli sulle morsettiere o derivazioni a pettine. Posizione dei morsetti sugli apparecchi indicativa.",
    "• Non rappresentati: -A5 RTC opzionale (folio 6), interno della stufa (folio 3), NC dei relè, secondo polo dei contattori.",
    "• Guide: A sezionamento, protezioni, alimentatore — B contattori e misura — C scheda di controllo (solo 12 V e segnali) — D morsettiere.",
]), 560, 1160, size=7)

# tutto il folio 40 px più in basso, per lasciare libera l'intestazione delle colonne
DY = 40
for el in d.elements:
    el.y += DY
d.shapes = [(k, xa, ya + DY, xb, yb + DY, *r) for k, xa, ya, xb, yb, *r in d.shapes]
d.texts = [(t, x, y + DY, *r) for t, x, y, *r in d.texts]

# ----------------------------------------------------------------------------- rimandi tra folii
for nome, coppia in rimandi.items():
    assert len(coppia) == 2, f"rimando {nome}: servono un'uscita e un'entrata, trovati {len(coppia)}"
    p.link(*coppia)

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    first = int(sys.argv[sys.argv.index("--first") + 1]) if "--first" in sys.argv else None
    if first:
        args = [a for a in args if a != str(first)] or args
    out = args[0] if args else str(Path(__file__).resolve().parent / "camera_salumi.qet")
    print(p.save(out, first=first))
