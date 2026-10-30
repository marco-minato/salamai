import sys, json
from xml.sax.saxutils import escape
# Scatola X6 (nodo in camera): schema dei collegamenti. Coordinate in mm.
# Le schede hanno le misure vere; i Wago sono disegnati in fila per leggere i
# collegamenti (nella scatola stanno liberi).
S=3.0; OX,OY=60,150
cells=[]; n=[1]; V=[]; WIRES=[]
def nid():
    n[0]+=1; return f"c{n[0]}"
def rect(x,y,w,h,label,style,fs=9,fc="#222222",align="center",valign="middle",rot=False,text=False):
    i=nid()
    cells.append(f'<mxCell id="{i}" value="{escape(label,{chr(34):"&quot;"})}" style="{style}" vertex="1" parent="1"><mxGeometry x="{OX+x*S:.1f}" y="{OY+y*S:.1f}" width="{w*S:.1f}" height="{h*S:.1f}" as="geometry"/></mxCell>')
    import re
    def g(k):
        m=re.search(k+r'=([^;]+)',style); return m.group(1) if m else None
    plain=re.sub(r'<br\s*/?>','\n',label); plain=re.sub(r'<[^>]+>','',plain)
    V.append(dict(x=x,y=y,w=w,h=h,fill=g('fillColor') or 'none',stroke=g('strokeColor') or 'none',text=text,
        ell='ellipse' in style,dash='dashed=1' in style,rot=rot,fs=fs,fc=fc,align=align,valign=valign,
        hatch=False,sw=float(g('strokeWidth') or 1),label=plain.replace('&amp;','&')))
def text(x,y,w,h,label,fs=9,align="left",valign="top",fc="#222222",bold=False):
    st=f"text;html=1;whiteSpace=wrap;align={align};verticalAlign={valign};fontSize={fs};fontColor={fc};"
    rect(x,y,w,h,label,st,fs=fs,fc=fc,align=align,valign=valign,text=True)
def lab(x,y,w,t,fs=6,fc="#222222",align="center"):
    text(x,y,w,4,t,fs=fs,align=align,valign="middle",fc=fc)

COL={"P12":"#E00000","V0":"#000000","G":"#555555","A":"#FF8C00","B":"#8A2BE2","V33":"#C99700","OW":"#00897B",
     "PWM":"#E0399A","TACH":"#00ACC1","HX":"#7CB342","CELL":"#8D6E63","CAB":"#6c8ebf","PRL":"#424242"}
def wire(pts,kind,a,b,net,dash=False):
    WIRES.append(dict(kind=kind,pts=[(round(x,2),round(y,2)) for x,y in pts],a=a,b=b,net=net))

W,H=345,215
def frame():
    rect(2,2,W-4,H-6,"","rounded=1;arcSize=2;fillColor=#f5f5f5;strokeColor=#666666;strokeWidth=2;dashed=1;")
    cells.insert(0,cells.pop()); V.insert(0,V.pop())
text(4,-24,W,20,"<b>Scatola X6 – nodo in camera</b><br>schema dei collegamenti · schede in scala, Wago in fila (nella scatola stanno liberi) · scatola vera 150×110×70",11)

# ---------------- schede
LV="fillColor=#dae8fc;strokeColor=#6c8ebf;"
# A6: scheda RS485 Seeed con XIAO ESP32C3 innestata (verticale, morsettiere in basso)
AX,AY,AW,AH=26,6,26,44
rect(AX,AY,AW,AH,"",LV)
rect(AX+2.5,AY+1,21,19.8,"","fillColor=#1f2d3d;strokeColor=#111111;")
text(AX+2.5,AY+21.3,21,9,"<b>A6</b> XIAO ESP32C3<br>su scheda RS485",6,align="center")
PIN={}
LCOL=["D0","D1","D2","D3","D4","D5","D6"]; RCOL=["5V","GND","3V3","D10","D9","D8","D7"]
for k,nm in enumerate(LCOL):
    x,y=AX+2.2,AY+3.5+2.54*k; PIN["XIAO "+nm]=(x,y)
    rect(x-0.9,y-0.9,1.8,1.8,"","fillColor=#e0b84a;strokeColor=none;"); lab(x+1.2,y-2,6,nm,5,fc="#ffffff",align="left")
for k,nm in enumerate(RCOL):
    x,y=AX+AW-2.2,AY+3.5+2.54*k; PIN["XIAO "+nm]=(x,y)
    rect(x-0.9,y-0.9,1.8,1.8,"","fillColor=#e0b84a;strokeColor=none;"); lab(x-7.2,y-2,6,nm,5,fc="#ffffff",align="right")
# gusci Dupont 1×6 e guscio da 1 su D6 (tratteggio), tappo da 1 vuoto (grigio) sul 5V
GS="fillColor=none;strokeColor=#ff9800;strokeWidth=1.5;dashed=1;"
TP="fillColor=#9e9e9e;strokeColor=#424242;"
x,y=PIN["XIAO D0"]; rect(x-1.4,y-1.4,2.8,5*2.54+2.8,"",GS)
x,y=PIN["XIAO D6"]; rect(x-1.4,y-1.4,2.8,2.8,"",GS)
x,y=PIN["XIAO GND"]; rect(x-1.4,y-1.4,2.8,5*2.54+2.8,"",GS)
x,y=PIN["XIAO 5V"]; rect(x-1.2,y-1.2,2.4,2.4,"",TP)
# morsettiere (ordine dei poli da verificare sulla serigrafia)
rect(AX,AY+33,6,13,"","fillColor=#7fc97f;strokeColor=#2e7d32;")
rect(AX+AW-6,AY+33,6,13,"","fillColor=#7fc97f;strokeColor=#2e7d32;")
for k,nm in enumerate(["INT","5V","12V"]):
    y=AY+35+4.3*k; PIN["RS485 alim. "+nm]=(AX,y); lab(AX+0.5,y-2,5,nm,4.5,align="left")
for k,nm in enumerate(["A","B","GND"]):
    y=AY+35+4.3*k; PIN["RS485 bus "+nm]=(AX+AW,y); lab(AX+AW-5.5,y-2,5,nm,4.5,align="right")
text(AX-2,AY+AH+0.5,AW+4,8,"interruttori: 120R su ON · 5V su OUT",5,align="center")

# A4: HX711 (verticale, pin in basso, piazzole cella in alto)
HX,HY,HW,HH=86,10,21,34
rect(HX,HY,HW,HH,"",LV+"")
text(HX,HY+12,HW,10,"<b>A4</b> HX711",7,align="center")
for k,nm in enumerate(["GND","DT","SCK","VCC"]):
    x=HX+HW/2+(k-1.5)*2.54; PIN["HX711 "+nm]=(x,HY+HH)
    lab(x-2,HY+HH-5,4,nm,4.2)
for k,nm in enumerate(["E+","E−","A−","A+","B−","B+"]):
    x=HX+2.5+k*3.2; PIN["HX711 "+nm]=(x,HY)
    lab(x-2,HY+1,4,nm,4.2)

# A2: modulo MOSFET (posizione morsetti indicativa)
MX,MY,MW,MH=128,10,40,22
rect(MX,MY,MW,MH,"",LV)
text(MX,MY+6,MW,10,"<b>A2</b> modulo MOSFET<br>(morsetti indicativi)",6,align="center")
PIN["MOSFET PWM"]=(MX,MY+6); PIN["MOSFET GND segnale"]=(MX,MY+14)
lab(MX+0.5,MY+4,8,"PWM",4.5,align="left"); lab(MX+0.5,MY+12,8,"GND",4.5,align="left")
for nm,dx in [("DC+",7),("DC−",14),("OUT+",25),("OUT−",32)]:
    PIN["MOSFET "+nm]=(MX+dx,MY+MH); lab(MX+dx-3,MY+MH-5,6,nm,4.5)

# ---------------- Wago e canali dei cavi
YW=112; WD=18.6
def wago_w(n): return {2:13.1,3:18.9,5:29.9}[n]
SEQ=[("cab","W3",6),("w","A",3),("w","B",3),("cab","B1",4),("w","12a",5),("w","12b",3),("w","0a",5),("w","0b",5),
     ("cab","B3",3),("w","GND",5),("w","3V3",5),("w","1W",5),("cab","B4",3),("cab","W5",6),("w","T5",2),("w","T6",2),("w","T7",2),("cab","B2",4)]
WAGO={}; CHAN={}
x=30
prev=None
for t,nm,k in SEQ:
    if t=="w":
        gap=1.5 if (prev and prev[0]=="w" and prev[1][:-1]==nm[:-1] and nm[-1]=="b") else (3 if prev and prev[0]=="w" else 2)
        x+=gap; w=wago_w(k)
        WAGO[nm]=dict(x=x,w=w,n=k,slots=[x+w/2+(i-(k-1)/2)*5.8 for i in range(k)])
        x+=w
    else:
        x+=3; CHAN[nm]=[x+1.4*i for i in range(k)]; x+=1.4*(k-1)+3
    prev=(t,nm)
W=round(x+8); frame()
WTITLE={"A":"RS485 A","B":"RS485 B","12a":"+12 V","12b":"+12 V","0a":"0 V","0b":"0 V","GND":"GND sensori","3V3":"3,3 V","1W":"1-Wire","T5":"giri M5","T6":"giri M6","T7":"giri M7"}
WFILL={"A":"#ffd8a8","B":"#e0ccf5","12a":"#f8b4b4","12b":"#f8b4b4","0a":"#cfcfcf","0b":"#cfcfcf","GND":"#e3e3e3","3V3":"#fbe7a1","1W":"#b2dfdb","T5":"#b2ebf2","T6":"#b2ebf2","T7":"#b2ebf2"}
for nm,d in WAGO.items():
    rect(d["x"],YW,d["w"],WD,"",f"fillColor={WFILL[nm]};strokeColor=#555555;")
    for i,sx in enumerate(d["slots"]):
        rect(sx-2.2,YW+0.6,4.4,3,"","fillColor=#ffffff;strokeColor=#888888;")
        rect(sx-1.6,YW+8,3.2,8,"","fillColor=#ff9800;strokeColor=#b26a00;")
    text(d["x"],YW+WD+1,d["w"],8,f"Wago {d['n']}<br>{WTITLE[nm]}",5,align="center")
def slot(nm,i): return (WAGO[nm]["slots"][i],YW)
def sname(nm,i): return f"Wago {WTITLE[nm]}{' (2°)' if nm in ('12b','0b') else ''} foro {i+1}"

# ---------------- pressacavi e cavi
YS=168; YG=H-4
GLAB={"W3":"W3 Cat5e dal quadro","B1":"B1 sonda S-TH-01","B3":"B3 sonda parete","B4":"B4 sonda pavimento","W5":"W5 Cat5e verso X4 ventole","B2":"B2 cella di carico"}
SPLIT={}
for nm,xs in CHAN.items():
    cx=sum(xs)/len(xs); SPLIT[nm]=cx
    wire([(cx,YG),(cx,YS)],"CAB",None,None,None)
    rect(cx-6,YG-1,12,6,"","ellipse;fillColor=#dae8fc;strokeColor=#333333;")
    text(cx-14,YG-12,28,8,GLAB[nm],5.5,align="center")
rect(250,YG-1,10,5,"","ellipse;fillColor=#ffffff;strokeColor=#333333;dashed=1;")
text(242,YG-12,26,8,"valvola anticondensa",5.5,align="center")

# ---------------- percorso dei fili
LANE=[106.5]
def lane():
    y=LANE[0]; LANE[0]-=1.25; return y
def cab_start(c,i):  # filo che esce dalla guaina
    return [(SPLIT[c],YS),(CHAN[c][i],YS-4)]
def route(pa,pb,kind,a,b,net):
    """pa, pb: liste di punti dal capo fino al punto da cui il filo scende/sale verticale verso la corsia."""
    y=lane()
    pts=pa+[(pa[-1][0],y),(pb[-1][0],y)]+pb[::-1]
    wire(pts,kind,a,b,net)
# capi
STUBL={"D0":12,"D1":13.4,"D3":14.8,"D6":16.2}            # uscite a sinistra della XIAO
STUBR={"D7":58,"D8":59.4,"D10":60.8,"3V3":62.2,"GND":63.6}  # uscite a destra della XIAO
def xiao(nm):
    x,y=PIN["XIAO "+nm]
    if nm in STUBL: return [(x,y),(STUBL[nm],y)]
    return [(x,y),(STUBR[nm],y)]
def pin(nm): return [PIN[nm]]
def sl(g,i): return [slot(g,i)]
def cab(c,i): return cab_start(c,i)

CN={"W3":["blu (A)","bianco-blu (B)","arancio (+12 V)","bianco-arancio (0 V)","verde (+12 V)","bianco-verde (0 V)"],
    "B1":["+ (alimentazione)","− (alimentazione)","A","B"],
    "B3":["rosso (VDD)","nero (GND)","giallo (DATA)"],"B4":["rosso (VDD)","nero (GND)","giallo (DATA)"],
    "W5":["blu (+12 V)","bianco-blu (0 V)","verde (PWM)","marrone (giri M5)","bianco-marrone (giri M6)","arancio (giri M7)"],
    "B2":["rosso (E+)","nero (E−)","bianco (A−)","verde (A+)"]}
def cname(c,i): return f"{GLAB[c].split(' ')[0]} {CN[c][i]}"

# RS485
route(cab("W3",0),sl("A",0),"A",cname("W3",0),sname("A",0),"RS485 A")
route(cab("W3",1),sl("B",0),"B",cname("W3",1),sname("B",0),"RS485 B")
route([PIN["RS485 bus A"],(56.3,PIN["RS485 bus A"][1])],sl("A",1),"A","Scheda RS485 morsetto A",sname("A",1),"RS485 A")
route([PIN["RS485 bus B"],(54.9,PIN["RS485 bus B"][1])],sl("B",1),"B","Scheda RS485 morsetto B",sname("B",1),"RS485 B")
route(cab("B1",2),sl("A",2),"A",cname("B1",2),sname("A",2),"RS485 A")
route(cab("B1",3),sl("B",2),"B",cname("B1",3),sname("B",2),"RS485 B")
# +12 V (Wago da 5 + Wago da 3 uniti)
route(cab("W3",2),sl("12a",0),"P12",cname("W3",2),sname("12a",0),"+12 V")
route(cab("W3",4),sl("12a",1),"P12",cname("W3",4),sname("12a",1),"+12 V")
route([PIN["RS485 alim. 12V"],(20,PIN["RS485 alim. 12V"][1])],sl("12a",2),"P12","Scheda RS485 morsetto 12V",sname("12a",2),"+12 V")
route(cab("B1",0),sl("12a",3),"P12",cname("B1",0),sname("12a",3),"+12 V")
route(sl("12a",4),sl("12b",0),"P12",sname("12a",4),sname("12b",0),"+12 V")
route(pin("MOSFET DC+"),sl("12b",1),"P12","Modulo MOSFET DC+",sname("12b",1),"+12 V")
route(cab("W5",0),sl("12b",2),"P12",cname("W5",0),sname("12b",2),"+12 V")
# 0 V
route(cab("W3",3),sl("0a",0),"V0",cname("W3",3),sname("0a",0),"0 V")
route(cab("W3",5),sl("0a",1),"V0",cname("W3",5),sname("0a",1),"0 V")
route([PIN["RS485 bus GND"],(53.5,PIN["RS485 bus GND"][1])],sl("0a",2),"V0","Scheda RS485 morsetto GND",sname("0a",2),"0 V")
route(cab("B1",1),sl("0a",3),"V0",cname("B1",1),sname("0a",3),"0 V")
route(sl("0a",4),sl("0b",0),"V0",sname("0a",4),sname("0b",0),"0 V")
route(pin("MOSFET DC−"),sl("0b",1),"V0","Modulo MOSFET DC−",sname("0b",1),"0 V")
route(cab("W5",1),sl("0b",2),"V0",cname("W5",1),sname("0b",2),"0 V")
route([PIN["MOSFET GND segnale"],(122.6,PIN["MOSFET GND segnale"][1])],sl("0b",3),"V0","Modulo MOSFET GND segnale",sname("0b",3),"0 V")
# GND sensori, 3,3 V, 1-Wire
route(cab("B3",1),sl("GND",2),"G",cname("B3",1),sname("GND",2),"GND sensori")
route(cab("B4",1),sl("GND",3),"G",cname("B4",1),sname("GND",3),"GND sensori")
route(cab("B3",0),sl("3V3",2),"V33",cname("B3",0),sname("3V3",2),"3,3 V")
route(cab("B4",0),sl("3V3",3),"V33",cname("B4",0),sname("3V3",3),"3,3 V")
route(cab("B3",2),sl("1W",1),"OW",cname("B3",2),sname("1W",1),"1-Wire sonde")
route(cab("B4",2),sl("1W",2),"OW",cname("B4",2),sname("1W",2),"1-Wire sonde")
# R3 4,7 kΩ tra 3,3 V (foro 5) e 1-Wire (foro 4): corpo nello spazio tra i due Wago
s1=slot("3V3",4); s2=slot("1W",3)
RX=(s1[0]+s2[0])/2; RY=YW-4.5
rect(RX-3.5,RY-1.3,7,2.6,"","fillColor=#f3d9b1;strokeColor=#7a5a2a;")
text(RX-8,RY-6.5,16,4,"R3 4,7 kΩ",5,align="center")
wire([(RX-3.5,RY),(s1[0],RY),(s1[0],YW)],"V33","R3 (4,7 kΩ) piedino 1",sname("3V3",4),"3,3 V")
wire([(RX+3.5,RY),(s2[0],RY),(s2[0],YW)],"OW","R3 (4,7 kΩ) piedino 2",sname("1W",3),"1-Wire sonde")
# giri ventole (pull-up interni della XIAO)
route(cab("W5",3),sl("T5",1),"TACH",cname("W5",3),sname("T5",1),"Giri ventola M5")
route(cab("W5",4),sl("T6",1),"TACH",cname("W5",4),sname("T6",1),"Giri ventola M6")
route(cab("W5",5),sl("T7",1),"TACH",cname("W5",5),sname("T7",1),"Giri ventola M7")
# HX711 DT/SCK: cavetto C1 (prolunga ventola) dall'HX711 alla XIAO
# PWM: D7 → ingresso del MOSFET (sopra le schede); OUT− → W5 verde
route(cab("W5",2),pin("MOSFET OUT−"),"PWM",cname("W5",2),"Modulo MOSFET OUT−","PWM ventole (uscita)")
# cella di carico → HX711 (sale a destra, entra dall'alto)
for i,(pad) in enumerate(["E+","E−","A−","A+"]):
    cx=CHAN["B2"][i]; px,py=PIN["HX711 "+pad]; yy=4.2+0.9*i
    wire(cab_start("B2",i)+[(cx,yy),(px,yy),(px,py)],"CELL",cname("B2",i),"HX711 "+pad,"Cella di carico "+pad)

# cavetti dalle prolunghe ventola (C1, C2, C3): corsie vicine e fascia grigia sotto
def lanes_of(k): return len(WIRES)
def band(pts,label,lx,ly,lw=22,bw=3.6):
    WIRES.insert(0,dict(kind="PRL",bw=bw,pts=[(round(x,2),round(y,2)) for x,y in pts],a=None,b=None,net=None))
    if label: lab(lx,ly,lw,label,4.5,fc="#424242",align="left")
# C3 ventole: D7, D8, D0 (corsie più basse del gruppo)
y_d7=LANE[0]; route(xiao("D7"),[PIN["MOSFET PWM"],(124,PIN["MOSFET PWM"][1])],"PWM","XIAO D7 (pin)","Modulo MOSFET PWM","PWM ventole (comando)")
y_d8=LANE[0]; route(xiao("D8"),sl("T6",0),"TACH","XIAO D8 (pin)",sname("T6",0),"Giri ventola M6")
y_d0=LANE[0]; route(xiao("D0"),sl("T5",0),"TACH","XIAO D0 (pin)",sname("T5",0),"Giri ventola M5")
route(xiao("D6"),sl("T7",0),"TACH","XIAO D6 (pin)",sname("T7",0),"Giri ventola M7")
# C2 sensori: D10, 3V3, GND
y_10=LANE[0]; route(xiao("D10"),sl("1W",0),"OW","XIAO D10 (pin)",sname("1W",0),"1-Wire sonde")
route(xiao("3V3"),sl("3V3",0),"V33","XIAO 3V3 (pin)",sname("3V3",0),"3,3 V")
y_gn=LANE[0]; route(xiao("GND"),sl("GND",0),"G","XIAO GND (pin)",sname("GND",0),"GND sensori")
# C1 HX711: GND, VCC verso i Wago; DT, SCK verso la XIAO
y_hg=LANE[0]; route(pin("HX711 GND"),sl("GND",1),"G","HX711 GND",sname("GND",1),"GND sensori")
route(pin("HX711 VCC"),sl("3V3",1),"V33","HX711 VCC",sname("3V3",1),"3,3 V")
route([PIN["HX711 DT"]],xiao("D1"),"HX","HX711 DT","XIAO D1 (pin)","HX711 DT")
y_sc=LANE[0]; route([PIN["HX711 SCK"]],xiao("D3"),"HX","HX711 SCK","XIAO D3 (pin)","HX711 SCK")
# Ogni cavetto ha un tratto unico e due aperture. I singoli fili vengono
# mostrati solo fuori dalla guaina; i capi elettrici restano quelli originali.
HARNESS = [
    ("C1", (76, 54), (110, 54), ["HX711 GND", "HX711 VCC", "HX711 DT", "HX711 SCK"]),
    ("C2", (68, 59), (204, 59), ["XIAO D10 (pin)", "XIAO 3V3 (pin)", "XIAO GND (pin)"]),
    ("C3", (71, 66), (176, 66), ["XIAO D7 (pin)", "XIAO D8 (pin)", "XIAO D0 (pin)", "XIAO D6 (pin)"]),
]
OPENINGS=[]
for cable, start, end, members in HARNESS:
    bundle=[]
    for w in WIRES:
        if w["a"] not in members: continue
        # C1 parte dall'HX711; C2 e C3 dalla XIAO.
        pa=w["pts"][0]; pb=w["pts"][-1]
        j=len(bundle); offset=(j-(len(members)-1)/2)*1.25
        sa=(start[0],start[1]+offset); sb=(end[0],end[1]+offset)
        if cable=="C1":
            lead=[pa,(pa[0],48+j*1.25),sa]
        else:
            stub=xiao(w["a"].split()[1]); lead=stub+[(stub[-1][0],start[1]+offset),sa]
        # Apertura lato destinazioni: corsie distinte sotto i cavetti.
        yy=68.6+j*2+(0 if cable=="C1" else 9 if cable=="C2" else 17)
        if pb[1]<30 and pb[0]<65:  # DT e SCK al guscio sinistro
            stub=xiao(w["b"].split()[1]); tail=[sb,(end[0]+j*1.3,yy),(stub[-1][0],yy)]+stub[::-1]
        elif w["b"]=="Modulo MOSFET PWM":
            tail=[sb,(end[0]+j*1.3,yy),(118,yy),(118,pb[1]),pb]
        else:
            tail=[sb,(end[0]+j*1.3,yy),(pb[0],yy),pb]
        w["segments"]=[lead,tail]
        w["pts"]=lead+[start,end]+tail
        w["cable"]=cable
        bundle.append(w)
    trunk=dict(kind="PRL",bw=2.4,pts=[start,end],a=None,b=None,net=None,cable=cable)
    WIRES.insert(0,trunk)
    OPENINGS.extend([start,end])
    lab((start[0]+end[0])/2-12,start[1]-4,24,cable+" · 4 fili",6,fc="#333333")
# Riepilogo in uno spazio libero sopra le corsie; nessuna fascia sotto i fili.
x0=PIN["HX711 GND"][0]; x1=PIN["HX711 VCC"][0]; yb=PIN["HX711 GND"][1]
rect(x0-1.6,yb-2.2,x1-x0+3.2,4.4,"","fillColor=none;strokeColor=#ff9800;strokeWidth=1.5;")

# Riquadro di lettura dei cavetti, lontano dai percorsi.
rect(180,10,W-210,37,"","fillColor=#ffffff;strokeColor=#999999;")
text(182,11,W-214,35,"<b>Cavetti · apertura ai due estremi del tratto spesso</b><br>C1: femmina sui 4 pin HX711. GND → Wago GND f.2; VCC → 3,3 V f.2; DT → D1; SCK → D3.<br>C2: 1 GND → GND f.1; 2 3V3 → 3,3 V f.1; 3 D10 → 1-Wire f.1.<br>C3: 1 D0 → giri M5 f.1; 2 D8 → giri M6 f.1; 3 D7 → MOSFET PWM; 4 D6 → giri M7 f.1.<br>C2: filo 4 isolato a entrambi i capi. Tutti neri; n.1 con riga.<br>Guscio sinistro D0–D5: C3·1 / C1·DT / vuoto / C1·SCK / vuoto / vuoto.<br>Guscio destro GND–D7: C2·1 / C2·2 / C2·3 / vuoto / C3·2 / C3·3.<br>D6: guscio da 1, C3·4. Ordine dal lato USB. Tappo vuoto: 5V. Colori = funzione del filo.",6)

# ---------------- reti (union-find sui nomi dei capi)
par={}
def f(a):
    par.setdefault(a,a)
    while par[a]!=a: par[a]=par[par[a]]; a=par[a]
    return a
def u(a,b): par[f(a)]=f(b)
for nm,d in WAGO.items():
    for i in range(1,d["n"]): u(sname(nm,0),sname(nm,i))
for w in WIRES:
    if w["a"]: u(w["a"],w["b"])
groups={}
for i,w in enumerate(WIRES):
    if not w["a"]: continue
    groups.setdefault(f(w["a"]),[]).append(i)
nets=[]
ORDER=["P12","V0","A","B","G","V33","OW","HX","CELL","PWM","TACH"]
for r,ids in groups.items():
    names={WIRES[i]["net"] for i in ids}
    kinds=[WIRES[i]["kind"] for i in ids]; kind=max(set(kinds),key=kinds.count)
    nm=" / ".join(sorted(names)) if len(names)>1 else names.pop()
    ends=set()
    for i in ids:
        for e in (WIRES[i]["a"],WIRES[i]["b"]):
            if not e.startswith("Wago"): ends.add(e)
    wg=sorted({e.split(" foro")[0] for i in ids for e in (WIRES[i]["a"],WIRES[i]["b"]) if e.startswith("Wago")})
    nets.append(dict(name=nm,kind=kind,ends=sorted(ends)+wg,wires=ids))
nets.sort(key=lambda d:(ORDER.index(d["kind"]),d["name"]))
for k,d in enumerate(nets):
    d["id"]=k
    for i in d["wires"]: WIRES[i]["net"]=k
for w in WIRES:
    if w["a"] is None:
        w["net"]=None
        if w.get("cable"):
            w["nets"]=sorted({v["net"] for v in WIRES if v.get("cable")==w["cable"] and v["a"]})
splits=[[SPLIT[c],YS] for c in CHAN]+OPENINGS
json.dump(dict(W=W,H=H,V=[{**v,"x":round(v["x"],2),"y":round(v["y"],2),"w":round(v["w"],2),"h":round(v["h"],2)} for v in V],
               wires=WIRES,nets=nets,dots=[],splits=splits),open(sys.argv[2],'w'),ensure_ascii=False)

# drawio: fili
ST={k:f"strokeColor={c};strokeWidth={ {'CAB':9,'PRL':12}.get(k,2)};"+("opacity=55;" if k=='CAB' else "opacity=45;" if k=='PRL' else "") for k,c in COL.items()}
for w in WIRES:
  for segment in w.get("segments", [w["pts"]]):
    p=[(OX+x*S,OY+y*S) for x,y in segment]
    mids=''.join(f'<mxPoint x="{x:.1f}" y="{y:.1f}"/>' for x,y in p[1:-1])
    st=ST[w["kind"]] if w["kind"]!="PRL" else f"strokeColor={COL['PRL']};strokeWidth={w['bw']*S:.0f};opacity=100;"
    if w["kind"]=="G": st+="dashed=1;dashPattern=4 2;"
    cells.append(f'<mxCell id="{nid()}" value="" style="endArrow=none;html=1;rounded=0;jumpStyle=arc;jumpSize=4;{st}" edge="1" parent="1"><mxGeometry relative="1" as="geometry"><mxPoint x="{p[0][0]:.1f}" y="{p[0][1]:.1f}" as="sourcePoint"/><mxPoint x="{p[-1][0]:.1f}" y="{p[-1][1]:.1f}" as="targetPoint"/>'+(f'<Array as="points">{mids}</Array>' if mids else '')+'</mxGeometry></mxCell>')
xml=('<mxfile host="app.diagrams.net"><diagram id="x6" name="Scatola X6"><mxGraphModel dx="1400" dy="1000" grid="0" gridSize="10" guides="1" tooltips="1" connect="0" arrows="0" fold="1" page="1" pageScale="1" pageWidth="1300" pageHeight="900" math="0" shadow="0"><root><mxCell id="0"/><mxCell id="1" parent="0"/>'
     +''.join(cells)+'</root></mxGraphModel></diagram></mxfile>')
open(sys.argv[1],'w').write(xml)
print(len(V),"vertici",len(WIRES),"fili",len(nets),"reti; corsie fino a y",round(LANE[0],1))
for d in nets: print(d["id"],d["name"],"|",", ".join(d["ends"]))
