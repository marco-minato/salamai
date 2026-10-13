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
REVISIONE = "A"
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
    "12V": "#ff0000", "5V": "#ff8800", "0V": "#000000", "SEG": "#aa00aa", "A": "#008080", "B": "#6b8e23",
}

# Distinta: sigla -> (componente, note, costruttore, riferimento). Alimenta la nomenclatura del folio 8.
DISTINTA = {
    "-A1": ("Scheda ESP32-S3-Relay-6CH", "6 relè 10 A 250 VAC (COM/NA/NC), RS485 isolato (A/B/Earth), 7–36 V DC, connettori H1/H2, guida DIN", "Waveshare", "Amazon B0CXPG4XGZ"),
    "-A2": ("Modulo MOSFET dual D4184", "PWM ventole, low-side, ingresso logico 3,3 V", "", "Amazon B0GL1NWZQH"),
    "-A3": ("Misuratore di energia PZEM-016 con TA apribile", "RS485 Modbus 9600 8N1, indirizzo da cambiare in 2", "Peacefair", "Amazon B0D5NDPP4L"),
    "-A4": ("Modulo HX711", "In scatolina IP65 dentro la camera", "", "scatola: Amazon B0F8NW1YZ2"),
    "-A5": ("Modulo RTC DS3231 (opzionale)", "I²C, mantiene l'ora senza rete", "", "Amazon B0FPPTHKBX"),
    "-B1": ("Sonda temperatura/umidità S-TH-01", "RS485 Modbus, indirizzo 1, 9600 baud; 3,6–30 V DC (4 mA @ 24 V), alimentata a 12 V da -T1", "Seeed", "101990881"),
    "-B2": ("Cella di carico", "4 fili E+, E−, A+, A−", "", ""),
    "-B3": ("Termostato di sicurezza PP1461", "Elettromeccanico 5–30 °C, a parete in camera, apre sopra soglia (28–30 °C)", "Poly Pool", "Amazon B00L49ZA6K"),
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
    "-T1": ("Alimentatore HDR-30-12", "230 VAC → 12 V DC 2 A, guida DIN 2 moduli", "Mean Well", "Amazon B071KXJPYB"),
    "-T2": ("Convertitore DC-DC 12 → 5 V 3 A resinato", "Alimenta le ventole", "", "Amazon B09B818N5F"),
    "-X0:L": ("Morsetti ingresso linea L / N / PE", "Linea da quadro generale, protetta 16 A + Id 30 mA", "", ""),
    "-XS1": ("Presa Schuko (scatola -X1)", "Umidificatore 1", "", ""),
    "-XS2": ("Presa Schuko (scatola -X1)", "Umidificatore 2", "", ""),
    "-XS3": ("Presa Schuko (scatola -X1)", "Estrattore", "", ""),
}
CAVI = [
    ("-W1", "Cavo 5G1,5 quadro → stufa", "L1 marrone, L2 nero, L3 grigio, N blu, PE giallo-verde"),
    ("-W2", "Cavo 2×1,5 (o 3G1,5) quadro → termostato -B3", "Andata e ritorno della fase lampade"),
    ("-W3", "Cavo 4 poli quadro → sonda -B1", "+12 V, GND, A, B"),
    ("-W4", "Cavo di rete (doppini) quadro → -A4", "3,3 V, GND, DOUT, SCK (DOUT e SCK accoppiati a GND)"),
    ("-X1", "Scatola da esterno con 3 prese Schuko", "XS1, XS2, XS3 — accanto al quadro"),
    ("-X2…", "Morsetti Wago 221 / morsettiere", "Distribuzione N, PE e bassa tensione (nodi dello schema)"),
    ("—", "Filo silicone 18 AWG (B07TT68455)", "Collegamenti interni alla stufa, in guaina di vetro"),
    ("—", "Quadro IP65 24 moduli 2 file (B0DPXCLZPR)", "Clip DIN per PCB (B0FCM3N3P9), pressacavi M20 (B0GYRDCC9Z)"),
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
    ("7", "Fronte / disposizione quadro"), ("8", "Distinta componenti"),
    ("9", "Cablaggio del quadro (vista d'insieme)"),
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


def folio(titolo, rows=10):
    d = p.diagram(titolo, cols=24, rows=rows)
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
d2 = folio("Alimentazione 230 V")
d3 = folio("Stufa (3 lampade IR)")
d4 = folio("Prese di servizio")
d5 = folio("Bassa tensione 12 V / 5 V")
d6 = folio("Bus RS485 e sensori", rows=12)
d7 = folio("Fronte / disposizione quadro", rows=11)
d8 = folio("Distinta componenti", rows=13)
d9 = folio("Cablaggio del quadro (vista d'insieme)", rows=13)

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
     ("Tratteggiato", "opzionale / non collegato")]), 60, 520, size=9)
d.text("<b>Legenda sigle (IEC 81346)</b>" + tabella(
    ["Sigla", "Significato", "In questo progetto"],
    [("-A", "Assieme / scheda elettronica", "A1 scheda relè, A2 MOSFET, A3 PZEM-016, A4 HX711, A5 RTC"),
     ("-B", "Sensore / trasduttore", "B1 sonda T/UR, B2 cella di carico, B3 termostato di sicurezza"),
     ("-E", "Riscaldamento / illuminazione", "E1 stufa, E1.1–E1.3 lampade IR"),
     ("-K", "Relè (a bordo di -A1)", "K1–K3 lampade, K4–K5 umidificatori, K6 estrattore"),
     ("-M", "Motore / utilizzatore", "M1 rotazione (scollegato), M2–M3 umidificatori, M4 estrattore, M5–M6 ventole"),
     ("-S", "Comando manuale / contatto", "S1–S4 interruttori stufa, S5 antiribaltamento"),
     ("-T", "Alimentatore / convertitore", "T1 230 VAC → 12 V DC, T2 12 → 5 V DC"),
     ("-W", "Cavo", "W1 stufa, W2 termostato, W3 sonda, W4 HX711"),
     ("-X", "Morsetti / prese", "X0 ingresso linea, X1 scatola prese (XS1–XS3), X2… Wago"),
     ]), 520, 230, size=9)
d.text(html([
    "<b>Convenzioni</b>",
    "• I relè K1–K6 sono a bordo della scheda -A1: sui folii 3 e 4 compare il solo contatto COM–NA.",
    "• La scheda -A1 è rappresentata a blocchi funzionali su più folii (relè, alimentazione, RS485, connettore H1).",
    "• Le frecce ai bordi sono rimandi tra folii: accanto è indicato folio e posizione di arrivo/partenza.",
    "• I riquadri tratteggiati indicano dove si trova fisicamente l'apparecchio (in camera, scatola prese…).",
    "• GPIO e pin dei connettori H1 / H2 della scheda -A1: assegnazione e piedinatura completa sul folio 6.",
    "• I nodi (punti neri) di N, PE e bassa tensione sono realizzati con morsetti Wago 221 / morsettiere (-X2…).",
]), 520, 560, size=9)

# ----------------------------------------------------------------------------- folio 2: 230 V
d = d2
T1 = box("alimentatore_hdr_30_12", 120, 120,
         [("n", 40, "L"), ("s", 40, "N"), ("s", 80, "PE"), ("e", 40, "+V", "+12 V"), ("e", 80, "-V", "0 V")],
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
g1, g0, g2 = d.node(560, 700), d.node(700, 700), d.node(960, 700)
pe(d, side(x0pe, "s"), g1, num="PE")
pe(d, t1.pin["PE"], g1)
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
    "• -A3: impostare l'indirizzo Modbus 2 (la sonda -B1 usa 1).",
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
d.text(html(["5 V / GND dell'interfaccia", "RS485 di -A3: <b>da verificare</b>", "(vedi note)"]), 1160, 240, size=7)
d.text(html([
    "<b>Note</b>",
    "• Bus RS485: -A1 → -B1 e -A3 in parallelo (A con A, B con B).",
    "• RS485 di -A1 isolato galvanicamente (morsettiera A / B / Earth): Earth → PE, scarica le protezioni.",
    "• Terminazione 120 Ω: ponticello H3 sulla scheda -A1 abilitato.",
    "• Indirizzi Modbus: -B1 = 1, -A3 = 2 (da cambiare sul PZEM).",
    "• -B1: alimentazione 3,6–30 V DC (4 mA @ 24 V), qui a 12 V da -T1.",
    "• -A5 RTC opzionale (tratteggiato): I²C, VCC 3,3 V, GND.",
    "• PZEM-016: l'interfaccia RS485 è normalmente passiva e richiede 5 V esterni",
    "&nbsp;&nbsp;sui morsetti 5V/GND; non è nella netlist: verificare sul modulo.",
]), 700, 30, size=8)


def cella_pin(nome, uso=None):
    return f"<b>{nome} → {uso}</b>" if uso else nome


meta = lambda a, b: [(str(i), cella_pin(H1[i - 1], USO_H1.get(i)), H2[i - 1]) for i in range(a, b)]
d.text("<b>-A1 — piedinatura connettori H1 / H2</b> (in grassetto i pin usati; riserva libera: GPIO7, 10, 39, 40, 11–16, 47, 48)",
       60, 772, size=8)
d.text(tabella(["Pin", "H1", "H2"], meta(1, 8)), 60, 795, size=7)
d.text(tabella(["Pin", "H1", "H2"], meta(8, 15)), 500, 795, size=7)
d.text(tabella(["Pin", "H1", "H2"], meta(15, 21)), 960, 795, size=7)

# ----------------------------------------------------------------------------- folio 7: quadro
d = d7
MOD = 60  # px per modulo DIN (17,5 mm)
X0, Y1, Y2, HR = 140, 110, 440, 270
d.text("<b>Quadro IP65 — 24 moduli su 2 file</b> (1 modulo = 17,5 mm; vista frontale, non in scala esatta)", 100, 30, size=9)
d.rect(100, 70, 900, 760, width=2)
for y, nome in ((Y1, "Fila superiore — 230 V"), (Y2, "Fila inferiore — bassa tensione")):
    d.rect(X0, y, X0 + 12 * MOD, y + HR, dashed=True, color="#808080")
    d.text(nome, X0, y - 28, size=8)
    for m in range(13):
        d.line(X0 + m * MOD, y + HR, X0 + m * MOD, y + HR + 8, color="#808080")


def ingombro(x_mod, larg_mod, y, righe, fill="#f2f2f2", dashed=False):
    x1, x2 = X0 + x_mod * MOD, X0 + (x_mod + larg_mod) * MOD
    d.rect(round(x1), y + 10, round(x2), y + HR - 10, fill=None if dashed else fill, dashed=dashed)
    d.text(html(righe), round(x1) + 4, y + 90, size=7)


ingombro(0, 1, Y1, ["<b>-X0</b>", "L N PE"])
ingombro(1, 2, Y1, ["<b>-T1</b>", "Mean Well", "HDR-30-12", "2 mod"])
ingombro(3, 4, Y1, ["<b>-A3</b> PZEM-016", "su clip DIN", "~4 mod"])
ingombro(7, 2, Y1, ["<b>-X2…</b>", "morsetti", "N / PE"])
ingombro(9, 3, Y1, ["spazio libero", "3 mod"], dashed=True)
A1_MOD = 145 / 17.5
ingombro(0, A1_MOD, Y2, ["<b>-A1</b> Waveshare ESP32-S3-Relay-6CH", "145 × 90 mm (~9 mod)", "frontale alto 90 mm: mostrina rimossa"])
ingombro(A1_MOD, 3, Y2, ["<b>-A2</b> MOSFET", "<b>-T2</b> DC-DC", "su clip DIN", "~3 mod"])
ingombro(A1_MOD + 3, 12 - A1_MOD - 3, Y2, ["<b>X</b>"], fill="#ffe0e0")
d.text(html([
    "<b>Morsetti bassa tensione</b> (12 V / 5 V / RS485 / cavo HX711):",
    "con -A1 (~9 mod) e clip -A2/-T2 (~3 mod) la fila è piena: restano ~12 mm (riquadro X).",
    "Da verificare: morsetti BT su un secondo livello o nello spazio libero della fila superiore, separati dal 230 V.",
]), 140, 716, size=7)
for i, (x, nome) in enumerate([(180, "linea"), (250, "-W1"), (320, "-W2"), (390, "-X1 prese"), (620, "-W3"), (690, "-W4"), (760, "ventole")]):
    d.ellipse(x - 14, 772, x + 14, 800)
    d.text(nome, x - 20, 800, size=7)
d.text("pressacavi 230 V", 240, 826, size=7)
d.text("pressacavi bassa tensione", 630, 826, size=7)
d.rect(960, 110, 1390, 190)
d.text(html(["<b>Accanto al quadro</b>", "-X1 scatola da esterno, 3 prese Schuko: XS1 umidificatore 1, XS2 umidificatore 2, XS3 estrattore"]), 968, 116, size=7)
d.rect(960, 240, 1390, 700, dashed=True)
d.text("<b>Dentro la camera</b>", 968, 244, size=8)
for i, (sig, desc) in enumerate([
        ("-E1", "stufa a 3 lampade IR (cavo -W1)"), ("-B3", "termostato di sicurezza a parete (cavo -W2)"),
        ("-B1", "sonda T/UR S-TH-01 (cavo -W3)"), ("-A4 / -B2", "HX711 in scatolina IP65 + cella di carico (cavo -W4)"),
        ("-M2, -M3", "umidificatori a ultrasuoni (prese XS1, XS2)"), ("-M4", "estrattore, lato opposto alle ventole (presa XS3)"),
        ("-M5, -M6", "ventole USB 5 V, lungo il muro")]):
    d.rect(980, 290 + i * 56, 1370, 290 + i * 56 + 44, fill="#f2f2f2")
    d.text(f"<b>{sig}</b> — {desc}", 988, 298 + i * 56, size=7)

# ----------------------------------------------------------------------------- folio 8: distinta
d = d8
d.text("<b>Distinta componenti</b> — generata da QElectroTech dalle informazioni degli elementi", 50, 20, size=9)
d.table(50, 90, 1330, 620,
        "SELECT label, description, comment, manufacturer, designation, diagram_position "
        "FROM element_nomenclature_view WHERE description <> '' ORDER BY label",
        ["Sigla", "Componente", "Note", "Costruttore", "Riferimento", "Folio"], rows=len(DISTINTA) + 1, font=7)
d.text("<b>Cavi, morsetti e meccanica</b> (non rappresentati come elementi)" + tabella(["Sigla", "Descrizione", "Note"], CAVI), 50, 800, size=7)

# ----------------------------------------------------------------------------- folio 9: cablaggio
# Vista d'insieme: apparecchi nella posizione fisica (come nel folio 7) e ogni filo tracciato da morsetto
# a morsetto. I percorsi sono espliciti: ogni filo ha la sua "pista" orizzontale e la sua "corsia" verticale.
d = d9


def qbox(nome, w, h, pins, lines=()):
    return p.define("q_" + nome, make_box(nome, w, h, pins, lines, font=5, label_at=(6, h / 2 - 18)))


def posa(a, punti, b, **kw):
    """Filo da a a b passando per gli angoli indicati (tratti solo orizzontali o verticali)."""
    tappe = [a] + [d.node(x, y, dot=False) for x, y in punti] + [b]
    for u, v in zip(tappe, tappe[1:]):
        pu, pv = ((t.x, t.y) if hasattr(t, "is_node") else t.pos for t in (u, v))
        assert abs(pu[0] - pv[0]) < 0.5 or abs(pu[1] - pv[1]) < 0.5, f"tratto obliquo {pu} -> {pv}"
        d.wire(u, v, **kw)
        kw = dict(kw, num="")


def pins(side, items):
    return [(side, off, name, shown) for off, name, shown in items]


rele = []
for i in range(6):
    rele += [(40 + i * 50 + 5, f"COM{i + 1}", "C"), (60 + i * 50 + 5, f"NA{i + 1}", "NA")]
Q = {
    "linea": qbox("linea_230v", 100, 40, pins("s", [(20, "L", "L"), (50, "N", "N"), (80, "PE", "PE")]),
                  [(6, 12, "da quadro generale", 5), (6, 21, "16 A + Id 30 mA", 5)]),
    "x0": qbox("morsetti_x0", 100, 100, pins("n", [(20, "Li", ""), (50, "Ni", ""), (80, "PEi", "")])
               + pins("s", [(20, "L", "L"), (50, "N", "N"), (80, "PE", "PE")]), [(30, 62, "ingresso linea", 5)]),
    "t1": qbox("hdr_30_12", 140, 100, pins("s", [(20, "L", "L"), (40, "N", "N"), (60, "PE", "PE"),
                                                 (100, "+V", "+12"), (120, "-V", "0V")]),
               [(34, 46, "Mean Well HDR-30-12", 5)]),
    "a3": qbox("pzem016", 140, 100, pins("s", [(20, "L", "L"), (40, "N", "N"), (70, "TA1", "TA"), (90, "TA2", "TA"),
                                               (110, "A", "A"), (130, "B", "B")]),
               [(34, 46, "PZEM-016 (Modbus ind. 2)", 5)]),
    "xn": qbox("morsettiera_n", 100, 100, pins("s", [(10 + 20 * i, f"N{i + 1}", "N") for i in range(5)]),
               [(40, 46, "neutro (Wago)", 5)]),
    "xpe": qbox("morsettiera_pe", 100, 100, pins("s", [(10 + 20 * i, f"PE{i + 1}", "PE") for i in range(5)]),
                [(40, 46, "terra (Wago)", 5)]),
    "a1": qbox("waveshare_6ch", 480, 140,
               pins("n", rele + [(355, "VIN+", "VIN"), (375, "GND", "GND"), (410, "A", "A"), (430, "B", "B"),
                                 (465, "Earth", "Earth")])
               + pins("s", [(40, "3V3", "3V3"), (70, "GNDh", "GND"), (100, "GPIO5", "IO5"), (130, "GPIO6", "IO6"),
                            (440, "GNDp", "GND"), (460, "GPIO4", "IO4")]),
               [(40, 68, "Waveshare ESP32-S3-Relay-6CH", 7)]
               + [(46 + i * 50, 22, f"K{i + 1}", 5) for i in range(6)]
               + [(346, 22, "7–36 V", 5), (406, 22, "RS485", 5), (36, 124, "connettore H1 (HX711)", 5),
                  (396, 124, "H1 (PWM)", 5)]),
    "t2": qbox("dcdc_5v", 100, 100, pins("n", [(20, "IN+", "IN+"), (40, "IN-", "IN−"), (65, "+5V", "+5"), (85, "0V", "0V")]),
               [(34, 60, "DC-DC 12 → 5 V", 5)]),
    "a2": qbox("mosfet", 100, 100, pins("n", [(20, "VIN-", "VIN−"), (60, "OUT-", "OUT−")])
               + pins("s", [(30, "GND", "GND"), (70, "PWM", "PWM")]), [(34, 60, "MOSFET D4184", 5)]),
    "ta": qbox("ta_apribile", 40, 20, pins("w", [(10, "P1", "")]) + pins("e", [(10, "P2", "")])
               + pins("n", [(10, "S1", ""), (30, "S2", "")]), [(13, 14, "TA", 5)]),
    "e1": qbox("stufa", 120, 100, pins("n", [(20, "L3", "L3"), (40, "L2", "L2"), (60, "L1", "L1"), (80, "N", "N"),
                                             (100, "PE", "PE")]), [(34, 60, "stufa 3 lampade IR", 5)]),
    "b3": qbox("termostato", 60, 100, pins("n", [(15, "1", "1"), (45, "2", "2")]), [(6, 76, "termostato", 5)]),
    "a4": qbox("hx711_q", 130, 100, pins("n", [(20, "3V3", "VCC"), (50, "GND", "GND"), (80, "DOUT", "DT"), (110, "SCK", "SCK")])
               + pins("e", [(15, "E+", "E+"), (40, "E-", "E−"), (65, "A+", "A+"), (90, "A-", "A−")]),
               [(34, 60, "HX711", 5)]),
    "b2": qbox("cella_q", 100, 100, pins("w", [(15, "E+", "E+"), (40, "E-", "E−"), (65, "A+", "A+"), (90, "A-", "A−")]),
               [(40, 60, "cella di carico", 5)]),
    "x1": qbox("scatola_prese", 120, 100, pins("n", [(20, "XS3", "XS3"), (40, "XS2", "XS2"), (60, "XS1", "XS1"),
                                                     (80, "N", "N"), (100, "PE", "PE")]),
               [(34, 56, "3 prese Schuko:", 5), (34, 66, "umidif. 1, 2, estrattore", 5)]),
    "b1": qbox("sonda_q", 100, 100, pins("n", [(20, "V+", "V+"), (40, "GND", "GND"), (60, "A", "A"), (80, "B", "B")]),
               [(34, 60, "sonda S-TH-01", 5)]),
    "fan": qbox("ventola_usb", 120, 80, pins("w", [(20, "+", "+ 5 V"), (60, "-", "−")]), [(50, 44, "ventola USB", 5)]),
}
ql = d.add(Q["linea"], 310, 20)
x0 = d.add(Q["x0"], 310, 110, "-X0")
t1 = d.add(Q["t1"], 430, 110, "-T1")
a3 = d.add(Q["a3"], 600, 110, "-A3")
xn = d.add(Q["xn"], 770, 110, "-X2:N")
xp = d.add(Q["xpe"], 920, 110, "-X2:PE")
a1 = d.add(Q["a1"], 300, 510, "-A1")
t2 = d.add(Q["t2"], 900, 510, "-T2")
a2 = d.add(Q["a2"], 1020, 510, "-A2")
ta = d.add(Q["ta"], 280, 250, "-A3:TA", label_pos=(-52, 14))
e1 = d.add(Q["e1"], 100, 850, "-E1")
b3 = d.add(Q["b3"], 225, 850, "-B3")
a4 = d.add(Q["a4"], 320, 850, "-A4")
b2 = d.add(Q["b2"], 520, 850, "-B2")
x1 = d.add(Q["x1"], 780, 850, "-X1")
b1 = d.add(Q["b1"], 1120, 850, "-B1")
m5 = d.add(Q["fan"], 1290, 400, "-M5")
m6 = d.add(Q["fan"], 1290, 520, "-M6")

L, N = dict(color=C["L"]), dict(color=C["N"])
PE = dict(color=C["PE"], color2=C["PE2"])
# linea in ingresso
posa(ql.pin["L"], [], x0.pin["Li"], **L)
posa(ql.pin["N"], [], x0.pin["Ni"], **N)
posa(ql.pin["PE"], [], x0.pin["PEi"], **PE)
# fase: pista y=240 (da -X0 a -T1, -A3, COM K4–K6 e al termostato con -W2)
f = {x: d.node(x, 240) for x in (330, 450, 495, 545, 595)}
posa(x0.pin["L"], [], f[330], **L)
posa(b3.pin["1"], [(240, 240)], f[330], num="W2-1", **L)
for u, v in zip((330, 450, 495, 545), (450, 495, 545, 595)):
    d.wire(f[u], f[v], **L)
posa(f[595], [(620, 240)], a3.pin["L"], **L)
d.wire(f[450], t1.pin["L"], **L)
for x, k in ((495, 4), (545, 5), (595, 6)):
    d.wire(f[x], a1.pin[f"COM{k}"], **L)
# L-lampade: pista y=260 (ritorno dal termostato, attraverso il TA, ai COM K1–K3)
g = {x: d.node(x, 260) for x in (345, 395)}
posa(b3.pin["2"], [(270, 260)], ta.pin["P1"], num="W2-2", **L)
d.wire(ta.pin["P2"], g[345], **L)
d.wire(g[345], g[395], **L)
posa(g[395], [(445, 260)], a1.pin["COM3"], **L)
d.wire(g[345], a1.pin["COM1"], **L)
d.wire(g[395], a1.pin["COM2"], **L)
posa(a3.pin["TA1"], [(670, 220), (290, 220)], ta.pin["S1"], color=C["SEG"])
posa(a3.pin["TA2"], [(690, 230), (310, 230)], ta.pin["S2"], color=C["SEG"])
# neutro: piste y=270…300
posa(x0.pin["N"], [(360, 270), (780, 270)], xn.pin["N1"], **N)
posa(t1.pin["N"], [(470, 280), (800, 280)], xn.pin["N2"], **N)
posa(a3.pin["N"], [(640, 290), (820, 290)], xn.pin["N3"], **N)
posa(xn.pin["N4"], [(840, 300), (180, 300)], e1.pin["N"], num="W1-N", **N)
posa(xn.pin["N5"], [], x1.pin["N"], **N)
# protezione: piste y=310…350
posa(x0.pin["PE"], [(390, 310), (930, 310)], xp.pin["PE1"], **PE)
posa(t1.pin["PE"], [(490, 320), (950, 320)], xp.pin["PE2"], **PE)
posa(xp.pin["PE3"], [(970, 330), (200, 330)], e1.pin["PE"], num="W1-PE", **PE)
posa(xp.pin["PE4"], [(990, 340), (765, 340)], a1.pin["Earth"], **PE)
posa(xp.pin["PE5"], [(1010, 350), (880, 350)], x1.pin["PE"], **PE)
# uscite relè: verso stufa (-W1) e prese (-X1)
for k, y, corsia, col in ((1, 480, 160, C["L"]), (2, 470, 140, C["L2"]), (3, 460, 120, C["L3"])):
    px = a1.pin[f"NA{k}"].pos[0]
    posa(a1.pin[f"NA{k}"], [(px, y), (corsia, y)], e1.pin[f"L{k}"], num=f"W1-L{k}", color=col)
for k, y, corsia in ((6, 480, 800), (5, 470, 820), (4, 460, 840)):
    px = a1.pin[f"NA{k}"].pos[0]
    posa(a1.pin[f"NA{k}"], [(px, y), (corsia, y)], x1.pin[f"XS{k - 3}"], **L)
# 12 V: pista y=370; 0 V: pista y=380
v = {x: d.node(x, 370) for x in (655, 920)}
posa(t1.pin["+V"], [(530, 370)], v[655], color=C["12V"])
d.wire(v[655], v[920], color=C["12V"])
posa(v[920], [(1140, 370)], b1.pin["V+"], num="W3 +12 V", color=C["12V"])
d.wire(v[655], a1.pin["VIN+"], color=C["12V"])
d.wire(v[920], t2.pin["IN+"], color=C["12V"])
z = {x: d.node(x, 380) for x in (675, 940, 985, 1040)}
posa(t1.pin["-V"], [(550, 380)], z[675], color=C["0V"])
for u, w in zip((675, 940, 985), (940, 985, 1040)):
    d.wire(z[u], z[w], color=C["0V"])
posa(z[1040], [(1160, 380)], b1.pin["GND"], num="W3 GND", color=C["0V"])
for x, t in ((675, a1.pin["GND"]), (940, t2.pin["IN-"]), (985, t2.pin["0V"]), (1040, a2.pin["VIN-"])):
    d.wire(z[x], t, color=C["0V"])
# RS485: A e B scendono dritti da -A3 a -A1, con derivazione verso la sonda (-W3)
ra, rb = d.node(710, 400), d.node(730, 410)
d.wire(a3.pin["A"], ra, color=C["A"])
d.wire(ra, a1.pin["A"], color=C["A"])
posa(ra, [(1180, 400)], b1.pin["A"], num="W3-A", color=C["A"])
d.wire(a3.pin["B"], rb, color=C["B"])
d.wire(rb, a1.pin["B"], color=C["B"])
posa(rb, [(1200, 410)], b1.pin["B"], num="W3-B", color=C["B"])
# 5 V e ventole
p5, pm = d.node(1250, 420), d.node(1270, 460)
posa(t2.pin["+5V"], [(965, 420)], p5, color=C["5V"])
d.wire(p5, m5.pin["+"], color=C["5V"])
posa(p5, [(1250, 540)], m6.pin["+"], color=C["5V"])
posa(a2.pin["OUT-"], [(1080, 460)], pm, color=C["0V"])
d.wire(pm, m5.pin["-"], color=C["0V"])
posa(m6.pin["-"], [(1270, 580)], pm, color=C["0V"])
# connettore H1: PWM verso -A2, HX711 con -W4
posa(a1.pin["GNDp"], [(740, 680), (1050, 680)], a2.pin["GND"], color=C["0V"])
posa(a1.pin["GPIO4"], [(760, 700), (1090, 700)], a2.pin["PWM"], num="PWM", color=C["SEG"])
posa(a1.pin["3V3"], [], a4.pin["3V3"], num="W4 3,3 V", color=C["12V"])
posa(a1.pin["GNDh"], [], a4.pin["GND"], color=C["0V"])
posa(a1.pin["GPIO5"], [], a4.pin["DOUT"], color=C["SEG"])
posa(a1.pin["GPIO6"], [], a4.pin["SCK"], color=C["SEG"])
for pin in ("E+", "E-", "A+", "A-"):
    d.wire(a4.pin[pin], b2.pin[pin], color=C["SEG"])

d.rect(90, 80, 1230, 790, width=2)
d.text("<b>Quadro IP65</b> (in cantina)", 100, 86, size=8)
d.text(html(["fila superiore:", "230 V"]), 100, 130, size=7)
d.text("fila inferiore: bassa tensione", 900, 618, size=7)
for x1_, x2_, nome in ((110, 210, "-W1"), (230, 280, "-W2"), (330, 440, "-W4"), (790, 890, "prese"), (1130, 1210, "-W3")):
    d.ellipse(x1_, 782, x2_, 798, color="#808080")
    d.text(nome, x2_ + 2, 795, size=7)
d.ellipse(320, 72, 400, 88, color="#808080")
d.ellipse(1222, 410, 1238, 590, color="#808080")
d.rect(90, 830, 1230, 960, dashed=True, color="#808080")
d.text("<b>Fuori dal quadro</b> — in camera: -E1, -B3, -A4/-B2, -B1, ventole; accanto al quadro: -X1", 640, 962, size=7)
d.text(html([
    "<b>Vista d'insieme del cablaggio</b>: apparecchi disposti come nel quadro (folio 7), ogni filo tracciato da morsetto a morsetto con i colori della legenda (folio 1).",
    "La posizione dei morsetti sui singoli apparecchi è indicativa. Non rappresentati: -A5 RTC opzionale (folio 6), 5 V / GND dell'interfaccia RS485 di -A3 (da verificare),",
    "interruttori e lampade interni alla stufa (folio 3). NC dei relè non usato.",
]), 100, 985, size=7)

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
