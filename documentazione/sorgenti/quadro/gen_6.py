import sys, json
from xml.sax.saxutils import escape
# Quadro BOXEXPERT Fleet 600x400x200, interno 341x548x189, piastra stimata 300x510, 4 guide
S=3.0
OX,OY=60,150
cells=[]; n=[1]; RAW=[]
def nid():
    n[0]+=1; return f"c{n[0]}"
# Righe ridistribuite (v4.7): il disegno resta scritto nelle coordinate "vecchie" e
# M() le sposta. G1 e G4 con ~9 mm di stacco dalle canaline, G2 (display) attaccata,
# fascia libera in basso eliminata (la canalina inferiore va sul bordo della piastra).
def M(y):
    if y<70: return y
    if y<=160: return y+9         # G1
    if y<185: return y+18         # canalina H2
    if y<=275: return y+13        # G2
    if y<415: return y+8          # H3, G3, H4 (415 = bordo alto del contatore -> G4)
    if y<=505: return y+16        # G4
    if y<=530: return y+24        # canalina H5
    if y>555: return y            # sotto la piastra
    raise ValueError(f"y {y} nella vecchia fascia libera")
def rect(x,y,w,h,label,style,parent="1",raw=False):
    if not raw and x<=W and h<200:
        mid=y+h/2
        if 45<mid<555: y+=M(mid)-mid
    x,y,w,h=OX+x*S,OY+y*S,w*S,h*S
    i=nid()
    cells.append(f'<mxCell id="{i}" value="{escape(label,{chr(34):"&quot;"})}" style="{style}" vertex="1" parent="{parent}"><mxGeometry x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" as="geometry"/></mxCell>')
    return i
def text(x,y,w,h,label,size=11,extra=""):
    return rect(x,y,w,h,label,f"text;html=1;whiteSpace=wrap;align=left;verticalAlign=top;fontSize={size};{extra}")
def lab(x,y,w,t,size=7):
    rect(x,y,w,5,t,f"text;html=1;align=center;verticalAlign=middle;fontSize={size};spacing=0;")
def P(x,y): return OX+x*S, OY+y*S
ST={
 "L":"strokeColor=#8B4513;strokeWidth=2.4;","N":"strokeColor=#1E56C8;strokeWidth=2.4;",
 "PE":"strokeColor=#2E9B2E;strokeWidth=2.4;dashed=1;dashPattern=5 2;",
 "C230":"strokeColor=#777777;strokeWidth=10;opacity=55;",
 "P12":"strokeColor=#E00000;strokeWidth=2;","V0":"strokeColor=#000000;strokeWidth=2;",
 "A":"strokeColor=#FF8C00;strokeWidth=2;","B":"strokeColor=#8A2BE2;strokeWidth=2;",
 "COIL":"strokeColor=#E0399A;strokeWidth=2;",
 "PEb":"strokeColor=#2E9B2E;strokeWidth=2;dashed=1;dashPattern=5 2;",
 "CBT":"strokeColor=#6c8ebf;strokeWidth=9;opacity=55;",
}
def wire(pts,kind,layer):
    i=nid(); p=[P(q[0],q[1]) if len(q)==3 else P(q[0],M(q[1])) for q in pts]
    RAW.append((kind,p))
    mids=''.join(f'<mxPoint x="{x:.1f}" y="{y:.1f}"/>' for x,y in p[1:-1])
    arr=f'<Array as="points">{mids}</Array>' if mids else ''
    cells.append(f'<mxCell id="{i}" value="" style="endArrow=none;html=1;rounded=0;jumpStyle=arc;jumpSize=6;{ST[kind]}" edge="1" parent="{layer}"><mxGeometry relative="1" as="geometry"><mxPoint x="{p[0][0]:.1f}" y="{p[0][1]:.1f}" as="sourcePoint"/><mxPoint x="{p[-1][0]:.1f}" y="{p[-1][1]:.1f}" as="targetPoint"/>{arr}</mxGeometry></mxCell>')
H2="L230"; BT="LBT"

BOX="rounded=1;arcSize=2;fillColor=#f5f5f5;strokeColor=#666666;strokeWidth=2;"
INNER="fillColor=none;strokeColor=#999999;dashed=1;dashPattern=2 2;"
PLATE="fillColor=#e6e6e6;strokeColor=#999999;dashed=1;"
DUCT="fillColor=#d0d0d0;strokeColor=#808080;fillStyle=hatch;fontSize=9;fontColor=#333333;"
RAIL="fillColor=#b3b3b3;strokeColor=#666666;"
LV="fillColor=#dae8fc;strokeColor=#6c8ebf;whiteSpace=wrap;html=1;fontSize=10;"
HV="fillColor=#f8cecc;strokeColor=#b85450;whiteSpace=wrap;html=1;fontSize=10;"
KM="fillColor=#fff2cc;strokeColor=#d6b656;whiteSpace=wrap;html=1;fontSize=10;horizontal=0;"
STOP="fillColor=#4d4d4d;strokeColor=#333333;"
FREE="fillColor=none;dashed=1;strokeColor=#999999;fontColor=#888888;fontSize=9;whiteSpace=wrap;html=1;"
TERM={"grigio":"#cccccc","blu":"#7ea6e0","rosso":"#ea6b66","nero":"#4d4d4d","pe":"#97d077","viola":"#c3a6e8","arancio":"#ffc98a"}
TP={}; CUR=[""]
def term(x,y,lab_,col,h=42):
    TP[CUR[0]+lab_.split()[0]]=x+2.6
    st=f"fillColor={TERM[col]};strokeColor=#333333;fontSize=8;horizontal=0;html=1;verticalAlign=middle;"+("fontColor=#ffffff;" if col=="nero" else "")+("fillStyle=dashed;gradientColor=#ffff88;gradientDirection=east;" if col=="pe" else "")
    rect(x,y,5.2,h,lab_,st); return x+5.2
def stop(x,y,h=35):
    rect(x,y,9.5,h,"",STOP); return x+9.5

# ---------------- cassetta, piastra, canaline
W,H=400,600
IX,IY,IW,IH=29.5,26,341,548           # vano interno (dato venditore 548x341x189)
PX,PY,PW,PH=50,45,300,510             # piastra: STIMA, da misurare
rect(0,0,W,H,"",BOX); rect(IX,IY,IW,IH,"",INNER); rect(PX,PY,PW,PH,"",PLATE)
text(0,-30,400,26,"<b>Quadro camera salumi – disposizione sulla piastra</b><br>BOXEXPERT Fleet 600×400×200 con sportello trasparente · vista frontale, sportello tolto · interno 341×548×189",12)
lab(IX,IY+1,70,"vano interno 341 × 548",7)
D=25
rect(PX,PY,D,PH,"",DUCT); rect(PX+PW-D,PY,D,PH,"",DUCT)
text(PX+1,PY+PH/2-60,23,120,"canalina 230 V",9,"horizontal=0;align=center;verticalAlign=middle;")
text(PX+PW-D+1,PY+PH/2-70,23,140,"canalina bassa tensione",9,"horizontal=0;align=center;verticalAlign=middle;")
for dy in [0,115,230,345,460]: rect(PX+D,PY+dy,PW-2*D,D,"canalina 25×40",DUCT+"align=center;verticalAlign=middle;")
X0p=PX+D+5; XL=PX+PW-D-5           # 80 .. 320 = 240 mm utili
r1,r2,r3,r4=115,230,345,460
for k,cy in [(1,r1),(2,r2),(3,r3),(4,r4)]:
    rect(X0p-3,cy-17.5,XL-X0p+6,35,"",RAIL)
    text(PX+2,cy-6,22,12,f"G{k}",8,"fontColor=#000000;align=center;fontStyle=1;")

# ---------------- G1: alimentatore + Waveshare
cy=r1; x=X0p
T1x=x; rect(x,cy-45,52.5,90,"<b>T1</b><br>Mean Well<br>HDR-60-12<br>12 V 4,5 A<br>3 moduli",LV); x+=52.5+3
A1x=x; rect(x,cy-45,145,90,"<b>A1</b> Waveshare ESP32-S3-Relay-6CH<br>con <b>A5</b> RTC innestato<br>relè K1–K6 → bobine KM1–KM6<br>RS485 · alimentazione 12 V<br>145 × 90 × 40 mm",LV); x+=145
rect(x+3,cy-38,XL-x-3,76,"riserva<br>~35 mm",FREE)

# ---------------- G2: display + morsettiera bassa tensione
cy=r2
DW,DH=116.3,79
D1x=X0p
rect(D1x,cy-DH/2,DW,DH,"<b>D1</b> display 4,3\" touch<br>Waveshare ESP32-S3-Touch-LCD-4.3B<br>(versione con case)<br><br>agganciato alla guida con<br>clip DIN avvitata dietro<br>morsetti sul retro","fillColor=#1f2d3d;strokeColor=#6c8ebf;strokeWidth=2;fontColor=#ffffff;whiteSpace=wrap;html=1;fontSize=10;")
X3W=9.5*2+15*5.2
rect(D1x+DW+3,cy-38,XL-X3W-(D1x+DW)-6,76,"riserva",FREE)
x=XL-X3W
x=stop(x,cy-17.5)
CUR[0]="X3_"
for lab_,col in [("PE1","pe"),("PE2","pe"),("PE3","pe"),("1 B","viola"),("2 B","viola"),("3 B","viola"),("4 A","arancio"),("5 A","arancio"),("6 A","arancio"),
                 ("7 0V","nero"),("8 0V","nero"),("9 0V","nero"),("10 +12V","rosso"),("11 +12V","rosso"),("12 +12V","rosso")]:
    x=term(x,cy-21,lab_,col)
x=stop(x,cy-17.5)
text(XL-X3W,cy-37,X3W,14,"<b>X3</b> bassa tensione",9,"align=center;")

# ---------------- G3: contattori
cy=r3; x=X0p
KMx=[]
for i,l in enumerate(["lampada 1","lampada 2","lampada 3","umidif. 1","umidif. 2","estrattore"],1):
    KMx.append(x); rect(x,cy-42.5,18,85,f"<b>KM{i}</b> {l}",KM); x+=18
X5W=9.5*2+8.2*2+6*5.2
rect(x+5,cy-38,XL-X5W-x-10,76,"contattori HCH8s-25Z, bobina 12 V<br>con diodo interno (+ sopra, − sotto)<br>fase in catena sul morsetto 1<br>con puntalini doppi<br><br><i>libero: ~3 contattori</i>",FREE)
# X5: fusibili F1 (camera) e F2 (cantina) e morsetti 12 V protetti, lontano dai contattori
x=XL-X5W
x=stop(x,cy-17.5)
FUH=72.5; FU={}
for nm,t in [("F1","F1 camera · 1 A? (da conf.)"),("F2","F2 cantina · 0,25 A T? (da conf.)")]:
    FU[nm]=x+4.1
    rect(x,cy-FUH/2,8.2,FUH,t,"fillColor=#e1d5e7;strokeColor=#9673a6;fontSize=8;horizontal=0;html=1;verticalAlign=middle;whiteSpace=wrap;")
    x+=8.2
CUR[0]="X5_"
for lab_,col in [("1 +12V F2","rosso"),("2 +12V F1","rosso"),("3 +12V F1","rosso"),("4 0V","nero"),("5 0V","nero"),("6 0V","nero")]:
    x=term(x,cy-21,lab_,col)
x=stop(x,cy-17.5)
text(XL-X5W,cy-50,X5W,12,"<b>X5</b> 12 V protetti",9,"align=center;")
FUtop,FUbot=cy-FUH/2,cy+FUH/2

# ---------------- G4: 230 V
cy=r4; x=X0p
rect(x,cy-42.5,17.5,85,"<b>Q1</b> magnetot. C10 Gewiss",HV+"horizontal=0;fontSize=9;"); x+=17.5+3
x=stop(x,cy-17.5); xs=x
CUR[0]="X0_"
for lab_,col in [("1 L","grigio"),("2 L","grigio"),("3 N","blu"),("4 N","blu"),("PE","pe")]:
    x=term(x,cy-21,lab_,col)
x=stop(x,cy-17.5)
text(xs-12,cy-37,50,14,"<b>X0</b> ingresso",9)
x+=3; A3x=x
rect(x,cy-45,18,90,"<b>A3</b> SDM120 contatore",HV+"horizontal=0;fontSize=9;"); x+=18+3
x=stop(x,cy-17.5); xs=x
CUR[0]="X2_"
for lab_,col in [("1 L1","grigio"),("2 L2","grigio"),("3 L3","grigio"),("4 L4","grigio"),("5 L5","grigio"),("6 L6","grigio"),("7 N","blu"),("8 N","blu"),("9 N","blu"),("10 N","blu"),("PE1","pe"),("PE2","pe"),("PE3","pe"),("PE4","pe")]:
    x=term(x,cy-21,lab_,col)
x=stop(x,cy-17.5)
text(xs,cy-37,120,14,"<b>X2</b> uscite 230 V",9)
rect(x+3,cy-30,XL-x-3,60,"riserva<br>~55 mm",FREE)

# ---------------- pressacavi sul fondo
gy=H-2
def gland(x,l,col):
    rect(x-7,gy,14,14,"",f"ellipse;fillColor={col};strokeColor=#333333;")
    text(x-5,gy+16,12,70,l,8,"horizontal=0;align=right;verticalAlign=middle;")
GL={"casa":60,"stufa":160,"u1":190,"u2":220,"estr":250,"valv":280,"cam":312,"can":342}
for k,l in [("casa","linea casa"),("stufa","stufa 5G1,5"),("u1","presa umidif. 1"),("u2","presa umidif. 2"),("estr","presa estrattore")]:
    gland(GL[k],l,"#f8cecc")
rect(GL["valv"]-6,gy,12,12,"","ellipse;fillColor=#ffffff;strokeColor=#333333;dashed=1;")
text(GL["valv"]-4,gy+16,12,70,"valvola anticondensa",8,"horizontal=0;align=right;verticalAlign=middle;")
gland(GL["cam"],"Cat5e camera","#dae8fc"); gland(GL["can"],"Cat5e cantina","#dae8fc")
text(10,H+92,380,14,"pressacavi M20 sul fondo: 230 V a sinistra, bassa tensione a destra",9,"align=center;")

# ================= punti di collegamento (posizioni indicative)
X=lambda k:TP[k]
T1L,T1N,T1P,T1M=T1x+10,T1x+20,T1x+30,T1x+42
A1P,A1G,A1A,A1B,A1E=A1x+7.5,A1x+15.5,A1x+39.5,A1x+47.5,A1x+55.5
COM=[A1x+65.5+14*k for k in range(6)]; NO=[c+5 for c in COM]
KM1=[x+5 for x in KMx]; KMP=[x+13 for x in KMx]
T1top,T1bot=r1-45,r1+45; A1top,A1bot=r1-45,r1+45
KMtop,KMbot=r3-42.5,r3+42.5
Q1L,Q1N=X0p+4,X0p+13; Q1top,Q1bot=r4-42.5,r4+42.5
A3Lin,A3N,A3Lout,A3A,A3B=A3x+4,A3x+13,A3x+4,A3x+10.5,A3x+15
A3top,A3bot=r4-45,r4+45
Tt2,Tb2=r2-21,r2+21; Tt4,Tb4=r4-21,r4+21
Dbot=r2+DH/2; DT={"P12":D1x+105,"V0":D1x+108,"A":D1x+111,"B":D1x+114}
for k,t in [("P12","+12"),("V0","0V"),("A","A"),("B","B")]: lab(DT[k]-2,Dbot-6,4,t,6)
lab(T1L-5,T1bot-6,10,"L"); lab(T1N-5,T1bot-6,10,"N"); lab(T1P-5,T1top+1,10,"+V"); lab(T1M-5,T1top+1,10,"−V")
for xx,t in [(A1P,"12V"),(A1G,"GND"),(A1A,"A"),(A1B,"B"),(A1E,"⏚")]: lab(xx-4,A1top+1,8,t)
for k in range(6): lab(COM[k]-3,A1bot-6,13,f"K{k+1}",6)
lab(COM[0]-4,A1bot-11,30,"COM · NA",6)
for k in range(6):
    lab(KM1[k]-4,KMtop+1,8,"1"); lab(KMP[k]-4,KMtop+1,8,"+")
    lab(KM1[k]-4,KMbot-6,8,"2"); lab(KMP[k]-4,KMbot-6,8,"−")
for k in FU: lab(FU[k]-4,FUtop+1,8,"in",6); lab(FU[k]-4,FUbot-6,8,"out",6)
for xx,t in [(Q1L,"L"),(Q1N,"N")]: lab(xx-4,Q1top+1,8,t); lab(xx-4,Q1bot-6,8,t)
lab(A3Lout-3,A3top+1,6,"L↑"); lab(A3A-2.5,A3top+1,5,"A"); lab(A3B-2.5,A3top+1,5,"B")
lab(A3Lin-3,A3bot-6,6,"L"); lab(A3N-3,A3bot-6,6,"N")

# ponticelli
BR=[(r2,["X3_1","X3_2","X3_3"]),(r2,["X3_4","X3_5","X3_6"]),(r2,["X3_7","X3_8","X3_9"]),(r2,["X3_10","X3_11","X3_12"]),
    (r3,["X5_2","X5_3"]),(r3,["X5_4","X5_5","X5_6"]),(r4,["X0_1","X0_2"]),(r4,["X0_3","X0_4"]),(r4,["X2_7","X2_8","X2_9","X2_10"])]
for cyb,ks in BR:
    xa,xb=X(ks[0]),X(ks[-1]); yb=cyb+13
    rect(xa-1.2,yb,xb-xa+2.4,2.6,"","fillColor=#FF6A00;strokeColor=#7a3300;strokeWidth=1;")
    for k in ks: rect(X(k)-1.3,yb-0.05,2.6,2.6,"","ellipse;fillColor=#ffffff;strokeColor=#7a3300;")

# ================= 230 V
gc=GL["casa"]
wire([(gc,H),(gc,553,"r")],"C230",H2)
wire([(gc,553,"r"),(57,550,"r"),(57,414),(Q1L,414),(Q1L,Q1top)],"L",H2)
wire([(gc,553,"r"),(54,550,"r"),(54,412.5),(Q1N,412.5),(Q1N,Q1top)],"N",H2)
wire([(gc,553,"r"),(72,550,"r"),(72,408.3),(X("X0_PE"),408.3),(X("X0_PE"),Tt4)],"PE",H2)
wire([(Q1L,Q1bot),(Q1L,510),(X("X0_1"),510),(X("X0_1"),Tb4)],"L",H2)
wire([(Q1N,Q1bot),(Q1N,508),(X("X0_3"),508),(X("X0_3"),Tb4)],"N",H2)
wire([(X("X0_2"),Tb4),(X("X0_2"),513),(A3Lin,513),(A3Lin,A3bot)],"L",H2)
wire([(X("X0_4"),Tb4),(X("X0_4"),515.5),(A3N,515.5),(A3N,A3bot)],"N",H2)
wire([(X("X0_PE"),Tb4),(X("X0_PE"),522.5,"r")],"PE",H2)
rect(X("X0_PE")-2.5,522.5,5,5,"","ellipse;fillColor=#97d077;strokeColor=#333333;",raw=True)
rect(X("X0_PE")+4,520,40,10,"vite di terra sulla piastra","text;html=1;align=left;verticalAlign=middle;fontSize=7;",raw=True)
# ingresso -> alimentatore (sale nella canalina sinistra fino alla guida 1)
wire([(X("X0_1"),Tt4),(X("X0_1"),411),(60,411),(60,162.5),(T1L,162.5),(T1L,T1bot)],"L",H2)
wire([(X("X0_3"),Tt4),(X("X0_3"),409.5),(63,409.5),(63,163.6),(T1N,163.6),(T1N,T1bot)],"N",H2)
wire([(X("X0_4"),Tt4),(X("X0_4"),406),(X("X2_7"),406),(X("X2_7"),Tt4)],"N",H2)
# contatore -> fase dei contattori in catena (puntalini doppi sul morsetto 1)
wire([(A3Lout,A3top),(A3Lout,407),(66,407),(66,297),(KM1[0]-0.8,297),(KM1[0]-0.8,KMtop)],"L",H2)
for k in range(5):
    wire([(KM1[k]+0.8,KMtop),(KM1[k]+0.8,299.5),(KM1[k+1]-0.8,299.5),(KM1[k+1]-0.8,KMtop)],"L",H2)
for k in range(6):
    y=404.5-1.5*k
    wire([(KM1[k],KMbot),(KM1[k],y),(X(f"X2_{k+1}"),y),(X(f"X2_{k+1}"),Tt4)],"L",H2)
for g,ts in [("stufa",["X2_1","X2_2","X2_3","X2_7","X2_PE1"]),("u1",["X2_4","X2_8","X2_PE2"]),("u2",["X2_5","X2_9","X2_PE3"]),("estr",["X2_6","X2_10","X2_PE4"])]:
    gx=GL[g]; wire([(gx,H),(gx,527)],"C230",H2)
    for t in ts:
        kind="PE" if "PE" in t else ("N" if int(t[3:])>=7 else "L")
        wire([(gx,527),(X(t),Tb4)],kind,H2)

# ================= bassa tensione
# relè: COM in catena; NA -> + bobina (scendono nella canalina sinistra fino ai contattori)
for k in range(5):
    wire([(COM[k]+0.6,A1bot),(COM[k]+0.6,161.5),(COM[k+1]-0.6,161.5),(COM[k+1]-0.6,A1bot)],"P12",BT)
for k in range(6):
    y=165+1.0*k; xr=67.5+1.5*k; z=290-1.5*k
    wire([(NO[k],A1bot),(NO[k],y),(xr,y),(xr,z),(KMP[k],z),(KMP[k],KMtop)],"COIL",BT)
# morsettiera X3 -> alimentatore e Waveshare (canalina H1 -> canalina destra -> canalina in alto)
UP=[("X3_PE1",A1E,"PEb"),("X3_1",A1B,"B"),("X3_4",A1A,"A"),("X3_7",A1G,"V0"),("X3_8",T1M,"V0"),("X3_10",A1P,"P12"),("X3_11",T1P,"P12")]
nu=len(UP)
for j,(t,dst,kd) in enumerate(UP):
    xd=326+1.4*j; y0=50+2*(nu-1-j); y1=175+1.4*j
    wire([(X(t),Tt2),(X(t),y1),(xd,y1),(xd,y0),(dst,y0),(dst,A1top)],kd,BT)
# 12 V ai COM dei relè: da X3:12 sopra (foro libero del gruppo 10-12) al COM di K6 (puntalino doppio con la catena)
wire([(X("X3_12"),Tt2),(X("X3_12"),170.8),(COM[5]+1.0,170.8),(COM[5]+1.0,A1bot)],"P12",BT)
# display: dai morsetti X3 (sotto) ai morsetti sul retro del display
for i,(t,kd) in enumerate([("X3_3","B"),("X3_6","A"),("X3_9","V0"),("X3_12","P12")]):
    yd=283+1.5*i
    wire([(X(t),Tb2),(X(t),yd),(DT[kd],yd),(DT[kd],Dbot)],kd,BT)
# RS485 al contatore e terra verso le uscite 230 V: canalina destra fino a H3
for t,kd,yh,xd,y3,dst,ybot in [("X3_PE3","PEb",276,331.5,396.5,X("X2_PE4"),Tt4)]:
    wire([(X(t),Tb2),(X(t),yh),(xd,yh),(xd,y3),(dst,y3),(dst,ybot)],kd,BT)
# RS485 al contatore: dai fori liberi sopra X3:3 e X3:6, canalina in alto -> canalina destra -> H3
for t,kd,yl,xd,y3,dst in [("X3_3","B",171.6,338.8,395,A3B),("X3_6","A",172.6,337.4,393.5,A3A)]:
    wire([(X(t),Tt2),(X(t),yl),(xd,yl),(xd,y3),(dst,y3),(dst,A3top)],kd,BT)
# ritorno 0 V bobine (− in catena) -> canalina destra -> X3:9 sopra (foro libero del gruppo 7-9)
wire([(KMP[0]-0.8,KMbot),(KMP[0]-0.8,391.5),(336,391.5),(336,173.6),(X("X3_9"),173.6),(X("X3_9"),Tt2)],"V0",BT)
for k in range(5):   # − bobine in catena da contattore a contattore (puntalini doppi)
    wire([(KMP[k]+0.8,KMbot),(KMP[k]+0.8,389.5),(KMP[k+1]-0.8,389.5),(KMP[k+1]-0.8,KMbot)],"V0",BT)
# cavi di rete dal fondo: salgono nella canalina destra e si aprono sotto X3
# A e B su X3 (sotto); alimentazione su X5 (sopra), un conduttore per morsetto
Tt3=r3-21; Tb3=r3+21
for g,xd,ye,ts in [("cam",343,292,[("X3_1","B",Tb2),("X3_4","A",Tb2),("X5_2","P12",Tt3),("X5_3","P12",Tt3),("X5_4","V0",Tt3),("X5_5","V0",Tt3)]),
                   ("can",347.5,296,[("X3_2","B",Tb2),("X3_5","A",Tb2),("X5_1","P12",Tt3),("X5_6","V0",Tt3)])]:
    gx=GL[g]; yb=565 if g=="cam" else 570
    wire([(gx,H),(gx,yb),(xd,yb),(xd,ye)],"CBT",BT)
    for t,kd,yt in ts: wire([(xd,ye),(X(t),yt)],kd,BT)
# X3 +12 V non protetto -> ingressi dei fusibili (fori sotto di X3 10 e 11, canalina H3)
wire([(X("X3_10"),Tb2),(X("X3_10"),279.5),(FU["F1"],279.5),(FU["F1"],FUtop)],"P12",BT)
wire([(X("X3_11"),Tb2),(X("X3_11"),281),(FU["F2"],281),(FU["F2"],FUtop)],"P12",BT)
# uscite dei fusibili -> X5 sotto (canalina H4, a destra dei fili 230 V)
wire([(FU["F2"],FUbot),(FU["F2"],399),(X("X5_1"),399),(X("X5_1"),Tb3)],"P12",BT)
wire([(FU["F1"],FUbot),(FU["F1"],401),(X("X5_2"),401),(X("X5_2"),Tb3)],"P12",BT)
# 0 V comune: X3 7 sotto -> X5 4 sotto (H3, canalina destra, H4)
wire([(X("X3_7"),Tb2),(X("X3_7"),289),(340,289),(340,402.5),(X("X5_4"),402.5),(X("X5_4"),Tb3)],"V0",BT)

# ================= legenda e note
# ================= quote (dal bordo alto e dal bordo sinistro della piastra)
QC="fillColor=#555555;strokeColor=none;"
QX=412
LEV=[(0,"0",0),(25,"25",0),(133,"133",0),(158,"158",0),(238,"238",0),(263,"263",0),(353,"353",0),(378,"378",0),(484,"484",0),(509,"509",0),(510,"",0),
     (79,"asse guida 1: 79",1),(198,"asse guida 2: 198",1),(308,"asse guida 3: 308",1),(431,"asse guida 4: 431",1)]
rect(QX,PY,0.3,PH,"",QC,raw=True)
for yp,t,ax in LEV:
    ya=PY+yp
    rect(PX+PW,ya-0.12,QX+3-(PX+PW),0.25,"","fillColor=#c00000;strokeColor=none;" if ax else "fillColor=#999999;strokeColor=none;",raw=True)
    if t: rect(QX+4,ya-2.5,60,5,t,"text;html=1;align=left;verticalAlign=middle;fontSize=8;spacing=0;"+("fontColor=#c00000;fontStyle=1;" if ax else "fontColor=#333333;"),raw=True)
text(QX-2,PY-16,64,14,"<b>Quote in mm</b><br>dal bordo alto piastra",7)
text(QX-2,PY+PH+3,64,60,"canaline 25 mm<br>guide: centrare sull'asse rosso<br><br><b>In larghezza</b> (dal bordo sinistro):<br>canalina sx 0–25<br>canalina dx 275–300<br>orizzontali lunghe 250<br>guide da 27 a 273 (246)",7)

lx=W+70
text(lx,0,240,330,
"<b>Legenda</b><br>"
"<span style='background:#f8cecc'>&nbsp;&nbsp;&nbsp;&nbsp;</span> 230 V · <span style='background:#dae8fc'>&nbsp;&nbsp;&nbsp;&nbsp;</span> bassa tensione 12 V · <span style='background:#fff2cc'>&nbsp;&nbsp;&nbsp;&nbsp;</span> contattori<br>"
"<span style='background:#97d077'>&nbsp;&nbsp;&nbsp;&nbsp;</span> morsetti di terra (si serrano sulla guida) · <span style='background:#7ea6e0'>&nbsp;&nbsp;&nbsp;&nbsp;</span> neutro<br>"
"X3: <span style='background:#c3a6e8'>&nbsp;&nbsp;&nbsp;&nbsp;</span> RS485 B · <span style='background:#ffc98a'>&nbsp;&nbsp;&nbsp;&nbsp;</span> RS485 A · <span style='background:#4d4d4d'>&nbsp;&nbsp;&nbsp;&nbsp;</span> 0 V · <span style='background:#ea6b66'>&nbsp;&nbsp;&nbsp;&nbsp;</span> +12 V (colori indicativi: i morsetti del kit sono grigi, usa i marcafili)<br><br>"
"<b>Note</b><br>"
"• Scala: 1 mm = 3 px. Misure in mm.<br>"
"• Vano interno 341×548×189 (dato venditore). <b>Piastra 300×510 stimata</b>: misurala all'arrivo, poi si spostano i blocchi.<br>"
"• 4 guide DIN da ~246 mm, 240 utili tra le canaline laterali.<br>"
"• G1: T1 + Waveshare ≈ 206 mm · G2: display + X3 ≈ 216 mm · G3: 6 contattori ≈ 108 mm + X5 con F1, F2 ≈ 67 mm · G4: Q1, X0, contatore, X2 ≈ 181 mm.<br>"
"• Display D1 in alto: si legge attraverso lo sportello trasparente e si tocca aprendolo.<br>"
"• Profondità interna 189 mm: verificare che display su clip e Waveshare con RTC non tocchino lo sportello.<br>"
"• Fase ai contattori in catena sul morsetto 1 con puntalini doppi.<br>"
"• Morsetti UK2.5B larghi 5,2 mm; 1 modulo = 17,5 mm.<br>"
"• Ponticelli: X0 1-2, 3-4 · X2 7-10 · X3 1-3, 4-6, 7-9, 10-12 · X5 2-3, 4-6 (X5 1 da solo).<br>"
"• Fusibili 5×20 su portafusibili UK5-HESI: F1 → W3 camera (X5 2-3), F2 → W6 cantina (X5 1). Valori da confermare.",10)
text(lx,340,240,200,
"<b>Fili</b> (livelli «Fili 230 V» e «Fili bassa tensione»)<br>"
"<span style='color:#8B4513'>━━</span> fase L · <span style='color:#1E56C8'>━━</span> neutro N · <span style='color:#2E9B2E'>╍╍</span> terra<br>"
"<span style='color:#E00000'>━━</span> +12 V · <span style='color:#000000'>━━</span> 0 V · <span style='color:#E0399A'>━━</span> relè → + bobina contattore<br>"
"<span style='color:#FF8C00'>━━</span> RS485 A · <span style='color:#8A2BE2'>━━</span> RS485 B<br>"
"<span style='color:#FF6A00'>━●━●</span> ponticello tra morsetti · <span style='color:#999999'>███</span> cavi con guaina<br><br>"
"• X3 sopra: Waveshare, alimentatore, COM relè, contatore, ritorno bobine. X3 sotto: A e B dei Cat5e, display, ingressi di F1 e F2, 0 V verso X5.<br>"
"• X5 sopra: alimentazione dei Cat5e. X5 sotto: uscite di F1 e F2, 0 V da X3.<br>"
"• Un solo filo per foro su X3. Puntalini doppi solo sui COM dei relè e sui contattori (catene).<br>"
"• I fili relè → bobine (12 V, H05V-K) scendono nella canalina sinistra insieme ai 230 V: isolamento 300/500 V.<br>"
"• Posizione dei morsetti su alimentatore, Waveshare, display e contatore indicativa.",9)

xml=('<mxfile host="app.diagrams.net"><diagram id="quadro" name="Disposizione quadro">'
 '<mxGraphModel dx="1600" dy="2000" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="2100" pageHeight="2500" math="0" shadow="0">'
 '<root><mxCell id="0"/><mxCell id="1" value="Componenti" parent="0"/>'
 '<mxCell id="L230" value="Fili 230 V" parent="0"/><mxCell id="LBT" value="Fili bassa tensione" parent="0"/>'
 +''.join(c for c in cells if 'edge="1"' not in c)+''.join(c for c in cells if 'edge="1"' in c)+'</root></mxGraphModel></diagram></mxfile>')
open(sys.argv[1],'w').write(xml)
print("ok",len(cells))
