import sys, json
from xml.sax.saxutils import escape
# Quadro BOXEXPERT Fleet 600x400x200, interno 341x548x189, piastra 330x510 (guide da 270 mm), 3 guide
S=3.0
OX,OY=60,150
cells=[]; n=[1]; RAW=[]
def nid():
    n[0]+=1; return f"c{n[0]}"
def M(y): return y   # 3 guide: coordinate dirette, niente rimappatura
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
# colori dei conduttori dei Cat5e (T568B); "bianco-x" = bianco con tratteggio del colore
CAT={"blu":"#1565C0","arancio":"#EF6C00","verde":"#2E7D32","marrone":"#6D4C41"}
def wire(pts,kind,layer,cond=None):
    i=nid(); p=[P(q[0],q[1]) if len(q)==3 else P(q[0],M(q[1])) for q in pts]
    RAW.append((kind,p,cond))
    mids=''.join(f'<mxPoint x="{x:.1f}" y="{y:.1f}"/>' for x,y in p[1:-1])
    arr=f'<Array as="points">{mids}</Array>' if mids else ''
    cells.append(f'<mxCell id="{i}" value="" style="endArrow=none;html=1;rounded=0;jumpStyle=arc;jumpSize=6;{ST[kind] if not cond else "strokeColor="+CAT[cond.split("-")[-1]]+";strokeWidth=3;"+("dashed=1;dashPattern=3 2;" if cond.startswith("bianco") else "")}" edge="1" parent="{layer}"><mxGeometry relative="1" as="geometry"><mxPoint x="{p[0][0]:.1f}" y="{p[0][1]:.1f}" as="sourcePoint"/><mxPoint x="{p[-1][0]:.1f}" y="{p[-1][1]:.1f}" as="targetPoint"/>{arr}</mxGeometry></mxCell>')
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
PX,PY,PW,PH=35,45,330,510             # piastra: larghezza dalle guide da 270 mm, altezza da misurare
rect(0,0,W,H,"",BOX); rect(IX,IY,IW,IH,"",INNER); rect(PX,PY,PW,PH,"",PLATE)
text(0,-30,400,26,"<b>Quadro camera salumi – disposizione sulla piastra (3 guide)</b><br>BOXEXPERT Fleet 600×400×200 con sportello trasparente · vista frontale, sportello tolto · interno 341×548×189",12)
lab(IX,IY+1,70,"vano interno 341 × 548",7)
D=25
rect(PX,PY,D,PH,"",DUCT); rect(PX+PW-D,PY,D,PH,"",DUCT)
text(PX+1,PY+PH/2-60,23,120,"canalina 230 V",9,"horizontal=0;align=center;verticalAlign=middle;")
text(PX+PW-D+1,PY+PH/2-70,23,140,"canalina bassa tensione",9,"horizontal=0;align=center;verticalAlign=middle;")
HD=[45,207,368,530]                   # bordo alto delle 4 canaline orizzontali
for y in HD: rect(PX+D,y,PW-2*D,D,"canalina 25×40",DUCT+"align=center;verticalAlign=middle;")
X0p=PX+D+5; XL=PX+PW-D-5              # 65 .. 335 = 270 mm (guide)
r1,r2,r3=138.5,300,461.5
for k,cy in [(1,r1),(2,r2),(3,r3)]:
    rect(X0p,cy-17.5,XL-X0p,35,"",RAIL)
    text(PX+2,cy-6,22,12,f"G{k}",8,"fontColor=#000000;align=center;fontStyle=1;")

# ---------------- G1: alimentatore + Waveshare
cy=r1; x=X0p+1
T1x=x; rect(x,cy-45,52.5,90,"<b>T1</b><br>Mean Well<br>HDR-60-12<br>12 V 4,5 A<br>3 moduli",LV); x+=52.5+3
A1x=x; rect(x,cy-45,145,90,"<b>A1</b> Waveshare ESP32-S3-Relay-6CH<br>con <b>A5</b> RTC innestato<br>relè K1–K6 → bobine KM1–KM6<br>RS485 · alimentazione 12 V<br>145 × 90 × 40 mm",LV); x+=145
rect(x+3,cy-38,XL-x-3,76,"riserva<br>~65 mm",FREE)

# ---------------- G2: generale, contatore, contattori (solo potenza)
cy=r2; x=X0p+1
Q1x=x; rect(x,cy-42.5,17.5,85,"<b>Q1</b> magnetot. C10 Gewiss",HV+"horizontal=0;fontSize=9;"); x+=17.5+8   # spazio per il neutro verso il contatore
A3x=x; rect(x,cy-45,18,90,"<b>A3</b> SDM120 contatore",HV+"horizontal=0;fontSize=9;"); x+=18+9   # spazio per la fase verso KM1
KMx=[]
for i,l in enumerate(["lampada 1","lampada 2","lampada 3","umidif. 1","umidif. 2","estrattore"],1):
    KMx.append(x); rect(x,cy-42.5,18,85,f"<b>KM{i}</b> {l}",KM); x+=18
rect(x+16,cy-38,XL-x-20,76,"libero<br>~105 mm",FREE)

# ---------------- G3: X2 uscite 230 V a sinistra; X3, fusibile F1 e X5 a destra
cy=r3; x=X0p+5
x=stop(x,cy-17.5); xs=x
CUR[0]="X2_"
for lab_,col in [("1 L1","grigio"),("2 L2","grigio"),("3 L3","grigio"),("4 L4","grigio"),("5 L5","grigio"),("6 L6","grigio"),("7 N","blu"),("8 N","blu"),("9 N","blu"),("10 N","blu"),
                 ("PE1","pe"),("PE2","pe"),("PE3","pe"),("PE4","pe"),("PE5","pe")]:
    x=term(x,cy-21,lab_,col)
x=stop(x,cy-17.5); X2end=x
text(xs,cy-37,90,14,"<b>X2</b> uscite 230 V e terra",9)
X3W=9.5*2+15*5.2; X5W=8.2+2*5.2+9.5     # X5: F1, due morsetti, fermo (a sinistra usa il fermo di X3)
x0=XL-X3W-X5W
rect(X2end+4,cy-30,x0-X2end-8,60,"libero<br>~40 mm",FREE)
x=x0
x=stop(x,cy-17.5)
CUR[0]="X3_"
for lab_,col in [("PE1","pe"),("PE2","pe"),("PE3","pe"),("1 B","viola"),("2 B","viola"),("3 B","viola"),("4 A","arancio"),("5 A","arancio"),("6 A","arancio"),
                 ("7 0V","nero"),("8 0V","nero"),("9 0V","nero"),("10 +12V","rosso"),("11 +12V","rosso"),("12 +12V","rosso")]:
    x=term(x,cy-21,lab_,col)
x=stop(x,cy-17.5)
text(x0,cy-37,X3W,14,"<b>X3</b> bassa tensione",9,"align=center;")
FUH=72.5; FU={}; x5=x
for nm,t in [("F1","F1 camera · 1 A T")]:
    FU[nm]=x+4.1
    rect(x,cy-FUH/2,8.2,FUH,t,"fillColor=#e1d5e7;strokeColor=#9673a6;fontSize=8;horizontal=0;html=1;verticalAlign=middle;whiteSpace=wrap;")
    x+=8.2
CUR[0]="X5_"
for lab_,col in [("1 +12V F1","rosso"),("2 +12V F1","rosso")]:
    x=term(x,cy-21,lab_,col)
x=stop(x,cy-17.5)
text(x5,cy-50,XL-x5,12,"<b>F1 · X5</b>",9,"align=center;")
FUtop,FUbot=cy-FUH/2,cy+FUH/2
FUin,FUout=FUbot,FUtop     # portafusibile montato con l'ingresso in basso

# ---------------- pressacavi sul fondo
gy=H-2
def gland(x,l,col):
    rect(x-7,gy,14,14,"",f"ellipse;fillColor={col};strokeColor=#333333;")
    text(x-5,gy+16,12,70,l,8,"horizontal=0;align=right;verticalAlign=middle;")
GL={"casa":50,"stufa":92,"u1":118,"u2":144,"estr":170,"valv":210,"cam":330}
for k,l in [("casa","linea casa"),("stufa","stufa 5G1,5"),("u1","presa umidif. 1"),("u2","presa umidif. 2"),("estr","presa estrattore")]:
    gland(GL[k],l,"#f8cecc")
rect(GL["valv"]-6,gy,12,12,"","ellipse;fillColor=#ffffff;strokeColor=#333333;dashed=1;")
text(GL["valv"]-4,gy+16,12,70,"valvola anticondensa",8,"horizontal=0;align=right;verticalAlign=middle;")
gland(GL["cam"],"Cat5e camera","#dae8fc")
text(10,H+92,380,14,"pressacavi M20 sul fondo: 230 V a sinistra, bassa tensione a destra",9,"align=center;")

# ================= punti di collegamento (posizioni indicative)
X=lambda k:TP[k]
T1L,T1N,T1P,T1M=T1x+10,T1x+20,T1x+30,T1x+42
A1P,A1G,A1A,A1B,A1E=A1x+7.5,A1x+15.5,A1x+39.5,A1x+47.5,A1x+55.5
COM=[A1x+65.5+14*k for k in range(6)]; NO=[c+5 for c in COM]
KM1=[x+5 for x in KMx]; KMP=[x+13 for x in KMx]
T1top,T1bot=r1-45,r1+45; A1top,A1bot=r1-45,r1+45
KMtop,KMbot=r2-42.5,r2+42.5
Q1L,Q1N=Q1x+4,Q1x+13; Q1top,Q1bot=r2-42.5,r2+42.5
# SDM120-M: in basso 1 (L ingresso) e 2 (L uscita); in alto 3 e 4 (N, uniti dentro), 9 (B−) e 10 (A+)
A3Lin,A3Lout,A3N,A3Nout,A3B,A3A=A3x+4,A3x+13,A3x+3.5,A3x+7.5,A3x+11.5,A3x+15
A3top,A3bot=r2-45,r2+45
Tt3,Tb3=r3-21,r3+21
SCREW=(X("X2_PE5")+6.5,412)
RAILS={'X5':r3,'X2':r3,'X3':r3}
BRIDGES=[["X3_1","X3_2","X3_3"],["X3_4","X3_5","X3_6"],["X3_7","X3_8","X3_9"],["X3_10","X3_11","X3_12"],["X5_1","X5_2"],["X2_7","X2_8","X2_9","X2_10"]]
lab(T1L-5,T1bot-6,10,"L"); lab(T1N-5,T1bot-6,10,"N"); lab(T1P-5,T1top+1,10,"+V"); lab(T1M-5,T1top+1,10,"−V")
for xx,t in [(A1P,"12V"),(A1G,"GND"),(A1A,"A"),(A1B,"B"),(A1E,"⏚")]: lab(xx-4,A1top+1,8,t)
for k in range(6): lab(COM[k]-3,A1bot-6,13,f"K{k+1}",6)
lab(COM[0]-4,A1bot-11,30,"COM · NA",6)
for k in range(6):
    lab(KM1[k]-4,KMtop+1,8,"1"); lab(KMP[k]-4,KMtop+1,8,"+")
    lab(KM1[k]-4,KMbot-6,8,"2"); lab(KMP[k]-4,KMbot-6,8,"−")
for k in FU: lab(FU[k]-4,FUtop+1,8,"out",6); lab(FU[k]-4,FUbot-6,8,"in",6)
for xx,t in [(Q1L,"L"),(Q1N,"N")]: lab(xx-4,Q1top+1,8,t); lab(xx-4,Q1bot-6,8,t)
lab(A3N-2.5,A3top+1,5,"3",6); lab(A3Nout-2.5,A3top+1,5,"4",6); lab(A3B-2.5,A3top+1,5,"9",6); lab(A3A-2.5,A3top+1,5,"10",6)
lab(A3x,A3top+5.5,18,"N · B− A+",5)
lab(A3Lin-3,A3bot-6,6,"1"); lab(A3Lout-3,A3bot-6,6,"2"); lab(A3x,A3bot-11,18,"L↑ · L↓",5)

# ponticelli
for ks in BRIDGES:
    cyb=RAILS[ks[0].split('_')[0]]
    xa,xb=X(ks[0]),X(ks[-1]); yb=cyb+13
    rect(xa-1.2,yb,xb-xa+2.4,2.6,"","fillColor=#FF6A00;strokeColor=#7a3300;strokeWidth=1;")
    for k in ks: rect(X(k)-1.3,yb-0.05,2.6,2.6,"","ellipse;fillColor=#ffffff;strokeColor=#7a3300;")

# ================= 230 V
gc=GL["casa"]; cs=(gc,543)
wire([(gc,H),cs],"C230",H2)
wire([cs,(39,540),(39,219),(Q1L,219),(Q1L,Q1top)],"L",H2)
wire([cs,(42,541.5),(42,221.5),(Q1N,221.5),(Q1N,Q1top)],"N",H2)
wire([cs,(56,548.5),(X("X2_PE5"),548.5),(X("X2_PE5"),Tb3)],"PE",H2)
# terra: X2 PE5 sopra → vite della piastra
wire([(X("X2_PE5"),Tt3),(X("X2_PE5"),SCREW[1]),SCREW],"PE",H2)
rect(SCREW[0]-2.5,SCREW[1]-2.5,5,5,"","ellipse;fillColor=#97d077;strokeColor=#333333;")
text(SCREW[0]+3.5,SCREW[1]-5,34,10,"vite di terra<br>sulla piastra",7,"verticalAlign=middle;")
# uscite di Q1 con puntalini doppi: alimentatore (canalina sinistra fino a G1) e contatore
wire([(Q1L-0.8,Q1bot),(Q1L-0.8,374),(45,374),(45,212),(T1L,212),(T1L,T1bot)],"L",H2)
wire([(Q1N-0.8,Q1bot),(Q1N-0.8,376),(48,376),(48,214),(T1N,214),(T1N,T1bot)],"N",H2)
wire([(Q1L+0.8,Q1bot),(Q1L+0.8,369.5),(A3Lin,369.5),(A3Lin,A3bot)],"L",H2)
xg1=Q1x+17.5+4   # spazio tra Q1 e contatore
wire([(Q1N+0.8,Q1bot),(Q1N+0.8,349),(xg1,349),(xg1,250),(A3N,250),(A3N,A3top)],"N",H2)
# contatore → fase dei contattori in catena (puntalini doppi sul morsetto 1)
xg2=A3x+18+4.5   # spazio tra contatore e KM1
wire([(A3Lout,A3bot),(A3Lout,351),(xg2,351),(xg2,250),(KM1[0]-0.8,250),(KM1[0]-0.8,KMtop)],"L",H2)
for k in range(5):
    wire([(KM1[k]+0.8,KMtop),(KM1[k]+0.8,229),(KM1[k+1]-0.8,229),(KM1[k+1]-0.8,KMtop)],"L",H2)
# neutro dal contatore a X2 7 (passa nello spazio libero a destra dei contattori)
xn=KMx[5]+18+6
wire([(A3Nout,A3top),(A3Nout,210.3),(xn,210.3),(xn,386),(X("X2_7"),386),(X("X2_7"),Tt3)],"N",H2)
# morsetto 2 dei contattori → X2 L1…L6
for k in range(6):
    y=373+1.4*k
    wire([(KM1[k],KMbot),(KM1[k],y),(X(f"X2_{k+1}"),y),(X(f"X2_{k+1}"),Tt3)],"L",H2)
# cavi verso i carichi: dal fondo ai fori sotto di X2
for g,ts in [("stufa",["X2_1","X2_2","X2_3","X2_7","X2_PE1"]),("u1",["X2_4","X2_8","X2_PE2"]),("u2",["X2_5","X2_9","X2_PE3"]),("estr",["X2_6","X2_10","X2_PE4"])]:
    gx=GL[g]; wire([(gx,H),(gx,537)],"C230",H2)
    for t in ts:
        kind="PE" if "PE" in t else ("N" if int(t[3:])>=7 else "L")
        wire([(gx,537),(X(t),Tb3)],kind,H2)

# ================= bassa tensione
# relè: COM in catena; NA → + bobina (canalina H2)
for k in range(5):
    wire([(COM[k]+0.6,A1bot),(COM[k]+0.6,188),(COM[k+1]-0.6,188),(COM[k+1]-0.6,A1bot)],"P12",BT)
for k in range(6):
    y=211.5+1.2*k
    wire([(NO[k],A1bot),(NO[k],y),(KMP[k],y),(KMP[k],KMtop)],"COIL",BT)
# − delle bobine in catena; ritorno 0 V → X3 9 sotto (giù nello spazio libero di G3, poi canalina H4)
for k in range(5):
    wire([(KMP[k]+0.8,KMbot),(KMP[k]+0.8,347),(KMP[k+1]-0.8,347),(KMP[k+1]-0.8,KMbot)],"V0",BT)
xr=KMP[5]+0.8; xd3=X2end+23     # scende nello spazio libero di G3
wire([(xr,KMbot),(xr,360),(xd3,360),(xd3,533.5),(X("X3_9"),533.5),(X("X3_9"),Tb3)],"V0",BT)
# 12 V ai COM dei relè: X3 12 sopra → COM di K6 (puntalino doppio con la catena)
wire([(X("X3_12"),Tt3),(X("X3_12"),384),(340.5,384),(340.5,190),(COM[5]+1.0,190),(COM[5]+1.0,A1bot)],"P12",BT)
# X3 sopra → Waveshare, alimentatore, contatore (canalina H3 → canalina destra → H1 o H2)
UP=[("X3_PE1",A1E,"PEb","H1"),("X3_1",A1B,"B","H1"),("X3_3",A3B,"B","H2"),("X3_4",A1A,"A","H1"),("X3_6",A3A,"A","H2"),
    ("X3_7",A1G,"V0","H1"),("X3_8",T1M,"V0","H1"),("X3_10",A1P,"P12","H1"),("X3_11",T1P,"P12","H1")]
h1=[u for u in UP if u[3]=="H1"]
for i,(t,dst,kd,dd) in enumerate(UP):
    y=384.9+0.85*i; xd=341.6+1.15*i
    if dd=="H1":
        r=len(h1)-1-h1.index((t,dst,kd,dd)); y0=48+1.8*r
        wire([(X(t),Tt3),(X(t),y),(xd,y),(xd,y0),(dst,y0),(dst,A1top)],kd,BT)
    else:
        y0=207.9 if t=="X3_6" else 208.9
        wire([(X(t),Tt3),(X(t),y),(xd,y),(xd,y0),(dst,y0),(dst,A3top)],kd,BT)
# terra: X3 PE3 sopra → X2 PE4 sopra
wire([(X("X3_PE3"),Tt3),(X("X3_PE3"),388.5),(X("X2_PE4"),388.5),(X("X2_PE4"),Tt3)],"PEb",BT)
# fusibile: ingresso in basso da X3 12 sotto (filo corto), uscita in alto → X5 1 sopra
wire([(X("X3_12"),Tb3),(X("X3_12"),505),(FU["F1"],505),(FU["F1"],FUin)],"P12",BT)
wire([(FU["F1"],FUout),(FU["F1"],420),(X("X5_1"),420),(X("X5_1"),Tt3)],"P12",BT)
# cavi di rete dal fondo: salgono nella canalina destra; A e B a X3 sotto, alimentazione a X5 sopra
for g,sp,ts in [("cam",(358,545),[("X3_1","B",552.5,"b","bianco-blu"),("X3_4","A",549.9,"b","blu"),("X3_7","V0",547.3,"b","bianco-arancio"),("X3_8","V0",544.7,"b","bianco-verde"),("X5_1","P12",542.1,"b","arancio"),("X5_2","P12",539.5,"b","verde")])]:
    gx=GL[g]
    wire([(gx,H),(gx,568 if g=="cam" else 571),(sp[0],568 if g=="cam" else 571),sp],"CBT",BT)
    for j,(t,kd,yl,side,cond) in enumerate(ts):
        if side=="b":
            xe=sp[0]-3-0.9*j
            wire([sp,(xe,yl),(X(t),yl),(X(t),Tb3)],kd,BT,cond)
        else:
            xe=sp[0]-1.6-0.9*(j-4)
            wire([sp,(xe,sp[1]-6),(xe,yl),(X(t),yl),(X(t),Tt3)],kd,BT,cond)

# ================= quote (dal bordo alto e dal bordo sinistro della piastra)
QC="fillColor=#555555;strokeColor=none;"
QX=PX+PW+12
LEV=[(y-PY,str(round(y-PY)),0) for y in HD]+[(y-PY+D,str(round(y-PY+D)),0) for y in HD]+[(PH,"",0),
     (r1-PY,f"asse guida 1: {round(r1-PY,1):g}",1),(r2-PY,f"asse guida 2: {round(r2-PY,1):g}",1),(r3-PY,f"asse guida 3: {round(r3-PY,1):g}",1)]
rect(QX,PY,0.3,PH,"",QC,raw=True)
for yp,t,ax in LEV:
    ya=PY+yp
    rect(PX+PW,ya-0.12,QX+3-(PX+PW),0.25,"","fillColor=#c00000;strokeColor=none;" if ax else "fillColor=#999999;strokeColor=none;",raw=True)
    if t: rect(QX+4,ya-2.5,60,5,t,"text;html=1;align=left;verticalAlign=middle;fontSize=8;spacing=0;"+("fontColor=#c00000;fontStyle=1;" if ax else "fontColor=#333333;"),raw=True)
text(QX-2,PY-16,64,14,"<b>Quote in mm</b><br>dal bordo alto piastra",7)
text(QX-2,PY+PH+3,64,60,"canaline 25 mm<br>guide: centrare sull'asse rosso<br><br><b>In larghezza</b> (dal bordo sinistro):<br>canalina sx 0–25<br>canalina dx 305–330<br>orizzontali lunghe 280<br>guide da 30 a 300 (270)",7)

lx=W+70
text(lx,0,240,330,
"<b>Legenda</b><br>"
"<span style='background:#f8cecc'>&nbsp;&nbsp;&nbsp;&nbsp;</span> 230 V · <span style='background:#dae8fc'>&nbsp;&nbsp;&nbsp;&nbsp;</span> bassa tensione 12 V · <span style='background:#fff2cc'>&nbsp;&nbsp;&nbsp;&nbsp;</span> contattori<br>"
"<span style='background:#97d077'>&nbsp;&nbsp;&nbsp;&nbsp;</span> morsetti di terra (si serrano sulla guida) · <span style='background:#7ea6e0'>&nbsp;&nbsp;&nbsp;&nbsp;</span> neutro<br>"
"X3: <span style='background:#c3a6e8'>&nbsp;&nbsp;&nbsp;&nbsp;</span> RS485 B · <span style='background:#ffc98a'>&nbsp;&nbsp;&nbsp;&nbsp;</span> RS485 A · <span style='background:#4d4d4d'>&nbsp;&nbsp;&nbsp;&nbsp;</span> 0 V · <span style='background:#ea6b66'>&nbsp;&nbsp;&nbsp;&nbsp;</span> +12 V (colori indicativi: i morsetti del kit sono grigi, usa i marcafili)<br><br>"
"<b>Note</b><br>"
"• Scala: 1 mm = 3 px. Misure in mm.<br>"
"• Vano interno 341×548×189 (dato venditore). Piastra 330 di larghezza (guide da 270 mm); <b>altezza 510 stimata</b>: misurala, poi si ricalcolano le quote.<br>"
"• 3 guide DIN da 270 mm tra le canaline laterali; 4 canaline orizzontali, fasce libere di ~137 mm.<br>"
"• G1: T1 + Waveshare ≈ 200 mm · G2: Q1, contatore, 6 contattori ≈ 150 mm · G3: X2 ≈ 97 mm, X3 ≈ 97 mm, F1 e X5 ≈ 28 mm.<br>"
"• <b>G3 in acciaio</b>: i morsetti di terra di X2 e X3 si serrano sulla guida. Su G3 tutti i morsetti: il Cat5e arriva dal basso.<br>"
"• Niente morsettiera X0: le uscite di Q1 vanno ad alimentatore e contatore con puntalini doppi 2×1,5.<br>"
"• Profondità interna 189 mm: verificare che la Waveshare con RTC e la sua antenna non tocchino sportello e coperchio della canalina.<br>"
"• Fase ai contattori in catena sul morsetto 1 con puntalini doppi.<br>"
"• Morsetti UK2.5B larghi 5,2 mm; 1 modulo = 17,5 mm.<br>"
"• Ponticelli: X2 7-10 · X3 1-3, 4-6, 7-9, 10-12 · X5 1-2.<br>"
"• Fusibile 5×20 F1 1 A ritardato (T) su portafusibile UK5-HESI → W3 camera (X5 1-2). La cantina la misura lo Shelly H&T: niente sonda B5, niente cavo W6, niente F2.",10)
text(lx,340,240,200,
"<b>Fili</b> (livelli «Fili 230 V» e «Fili bassa tensione»)<br>"
"<span style='color:#8B4513'>━━</span> fase L · <span style='color:#1E56C8'>━━</span> neutro N · <span style='color:#2E9B2E'>╍╍</span> terra<br>"
"<span style='color:#E00000'>━━</span> +12 V · <span style='color:#000000'>━━</span> 0 V · <span style='color:#E0399A'>━━</span> relè → + bobina contattore<br>"
"<span style='color:#FF8C00'>━━</span> RS485 A · <span style='color:#8A2BE2'>━━</span> RS485 B<br>"
"<span style='color:#FF6A00'>━●━●</span> ponticello tra morsetti · <span style='color:#999999'>███</span> cavi con guaina<br>"
"Cat5e W3: colori veri dei conduttori (T568B); tratteggio = bianco-colore<br><br>"
"• X3 sopra: Waveshare, alimentatore, COM relè, contatore, 0 V verso X5, terra verso X2. X3 sotto: A, B e 0 V del Cat5e, ingresso di F1 (da X3 12), ritorno bobine.<br>"
"• X5 (+12 V dopo F1) sopra: uscita di F1. X5 sotto: arancio e verde del Cat5e camera. Lo 0 V del Cat5e va su X3 7 e 8 sotto.<br>"
"• Un solo filo per foro su X3. Puntalini doppi sulle uscite di Q1, sui COM dei relè e sui contattori (catene).<br>"
"• Posizione dei morsetti su alimentatore, Waveshare e contatore indicativa.",9)

xml=('<mxfile host="app.diagrams.net"><diagram id="quadro" name="Disposizione quadro">'
 '<mxGraphModel dx="1600" dy="2000" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="2100" pageHeight="2500" math="0" shadow="0">'
 '<root><mxCell id="0"/><mxCell id="1" value="Componenti" parent="0"/>'
 '<mxCell id="L230" value="Fili 230 V" parent="0"/><mxCell id="LBT" value="Fili bassa tensione" parent="0"/>'
 +''.join(c for c in cells if 'edge="1"' not in c)+''.join(c for c in cells if 'edge="1"' in c)+'</root></mxGraphModel></diagram></mxfile>')
open(sys.argv[1],'w').write(xml)
print("ok",len(cells))
