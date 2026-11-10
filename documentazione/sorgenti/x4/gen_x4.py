import sys, json, re
from xml.sax.saxutils import escape
# Scatola X4 (derivazione ventole): schema dei collegamenti. Coordinate in mm.
# Modulo MOSFET con morsetti in posizione indicativa; i Wago sono disegnati in fila
# per leggere i collegamenti (nella scatola stanno liberi).
S=3.0; OX,OY=60,150
cells=[]; n=[1]; V=[]; WIRES=[]
def nid():
    n[0]+=1; return f"c{n[0]}"
def rect(x,y,w,h,label,style,fs=9,fc="#222222",align="center",valign="middle",rot=False,text=False):
    i=nid()
    cells.append(f'<mxCell id="{i}" value="{escape(label,{chr(34):"&quot;"})}" style="{style}" vertex="1" parent="1"><mxGeometry x="{OX+x*S:.1f}" y="{OY+y*S:.1f}" width="{w*S:.1f}" height="{h*S:.1f}" as="geometry"/></mxCell>')
    def g(k):
        m=re.search(k+r'=([^;]+)',style); return m.group(1) if m else None
    plain=re.sub(r'<br\s*/?>','\n',label); plain=re.sub(r'<[^>]+>','',plain)
    V.append(dict(x=x,y=y,w=w,h=h,fill=g('fillColor') or 'none',stroke=g('strokeColor') or 'none',text=text,
        ell='ellipse' in style,dash='dashed=1' in style,rot=rot,fs=fs,fc=fc,align=align,valign=valign,
        hatch=False,sw=float(g('strokeWidth') or 1),label=plain.replace('&amp;','&')))
def text(x,y,w,h,label,fs=9,align="left",valign="top",fc="#222222"):
    st=f"text;html=1;whiteSpace=wrap;align={align};verticalAlign={valign};fontSize={fs};fontColor={fc};"
    rect(x,y,w,h,label,st,fs=fs,fc=fc,align=align,valign=valign,text=True)
def lab(x,y,w,t,fs=6,fc="#222222",align="center"):
    text(x,y,w,4,t,fs=fs,align=align,valign="middle",fc=fc)

COL={"P12":"#E00000","V0":"#000000","PWM":"#E0399A","TACH":"#00ACC1","CAB":"#6c8ebf"}
def wire(pts,kind,a,b,net):
    WIRES.append(dict(kind=kind,pts=[(round(x,2),round(y,2)) for x,y in pts],a=a,b=b,net=net))

H=160
text(4,-24,260,20,"<b>Scatola X4 – derivazione ventole</b><br>schema dei collegamenti · Wago in fila (nella scatola stanno liberi) · scatola vera 150×110×70",11)

# ---------------- A2: modulo MOSFET (morsetti indicativi: verificare la serigrafia)
LV="fillColor=#dae8fc;strokeColor=#6c8ebf;"
MX,MY,MW,MH=64,10,48,28
rect(MX,MY,MW,MH,"",LV)
text(MX+8,MY+5,MW-10,12,"<b>A2</b> modulo MOSFET<br>morsetti indicativi:<br>nomi sulla serigrafia",5.5,align="center")
PIN={}
rect(MX,MY+5,7,15,"","fillColor=#7fc97f;strokeColor=#2e7d32;")
for k,nm in enumerate(["PWM","GND"]):
    y=MY+9+7*k; PIN["A2 "+nm]=(MX,y); lab(MX+0.6,y-2,6,nm,4.3,align="left")
rect(MX+4,MY+MH-7,MW-8,7,"","fillColor=#7fc97f;strokeColor=#2e7d32;")
for k,nm in enumerate(["DC+","DC−","OUT+","OUT−"]):
    x=MX+9+k*10; PIN["A2 "+nm]=(x,MY+MH); lab(x-4,MY+MH-6,8,nm,4.3)
text(MX+16,MY+MH+0.5,30,5,"OUT+ libero",4.5,align="center",fc="#666666")

# ---------------- Wago e canali dei cavi
YW=84; WD=18.6
def wago_w(n): return {2:13.1,3:18.9,5:29.9}[n]
SEQ=[("cab","W5",7),("w","12",5),("w","0",5),("w","PW",5),("cab","M5",4),("w","T5",2),("cab","M6",4),("w","T6",2),("cab","M7",4),("w","T7",2)]
WAGO={}; CHAN={}
x=12; prev=None
for t,nm,k in SEQ:
    if t=="w":
        x+=3 if prev and prev[0]=="w" else 2; w=wago_w(k)
        WAGO[nm]=dict(x=x,w=w,n=k,slots=[x+w/2+(i-(k-1)/2)*5.8 for i in range(k)])
        x+=w
    else:
        x+=3; CHAN[nm]=[x+1.4*i for i in range(k)]; x+=1.4*(k-1)+3
    prev=(t,nm)
W=round(x+10)
rect(2,2,W-4,H-6,"","rounded=1;arcSize=2;fillColor=#f5f5f5;strokeColor=#666666;strokeWidth=2;dashed=1;")
cells.insert(0,cells.pop()); V.insert(0,V.pop())
WTITLE={"12":"+12 V","0":"0 V","PW":"PWM ventole","T5":"giri M5","T6":"giri M6","T7":"giri M7"}
WFILL={"12":"#f8b4b4","0":"#cfcfcf","PW":"#f7c6e0","T5":"#b2ebf2","T6":"#b2ebf2","T7":"#b2ebf2"}
for nm,d in WAGO.items():
    rect(d["x"],YW,d["w"],WD,"",f"fillColor={WFILL[nm]};strokeColor=#555555;")
    for sx in d["slots"]:
        rect(sx-2.2,YW+0.6,4.4,3,"","fillColor=#ffffff;strokeColor=#888888;")
        rect(sx-1.6,YW+8,3.2,8,"","fillColor=#ff9800;strokeColor=#b26a00;")
    text(d["x"],YW+WD+1,d["w"],8,f"Wago {d['n']}<br>{WTITLE[nm]}",5,align="center")
def sl(nm,i): return [(WAGO[nm]["slots"][i],YW)]
def sname(nm,i): return f"Wago {WTITLE[nm]} foro {i+1}"

# ---------------- pressacavi e cavi
YS=128; YG=H-4
GLAB={"W5":"W5 Cat5e da X6","M5":"M5 ventola","M6":"M6 ventola","M7":"M7 ventola"}
SPLIT={}
for nm,xs in CHAN.items():
    cx=sum(xs)/len(xs); SPLIT[nm]=cx
    wire([(cx,YG),(cx,YS)],"CAB",None,None,None)
    rect(cx-6,YG-1,12,6,"","ellipse;fillColor=#dae8fc;strokeColor=#333333;")
    text(cx-14,YG-12,28,8,GLAB[nm],5.5,align="center")
VX=W-14
rect(VX-5,YG-1,10,5,"","ellipse;fillColor=#ffffff;strokeColor=#333333;dashed=1;")
text(VX-12,YG-12,22,8,"valvola anticondensa",5,align="center")

CN={"W5":["blu (+12 V)","bianco-blu (0 V)","verde (comando PWM)","bianco-verde (0 V comando)","marrone (giri M5)","bianco-marrone (giri M6)","arancio (giri M7)"]}
for m in ("M5","M6","M7"): CN[m]=["filo 1 con la riga (GND)","filo 2 (+12 V)","filo 3 (giri)","filo 4 (PWM)"]
def cname(c,i): return f"{c} {CN[c][i]}"

LANE=[78.5]
def lane():
    y=LANE[0]; LANE[0]-=1.25; return y
def cab(c,i): return [(SPLIT[c],YS),(CHAN[c][i],YS-4)]
ROUTES=[]
def route(pa,pb,kind,a,b,net): ROUTES.append((pa,pb,kind,a,b,net))
def place_routes():
    # corsie: i fili più corti stanno più vicini ai Wago, così si incrociano meno
    order=sorted(range(len(ROUTES)),key=lambda i:abs(ROUTES[i][0][-1][0]-ROUTES[i][1][-1][0]))
    ys={i:lane() for i in order}
    for i,(pa,pb,kind,a,b,net) in enumerate(ROUTES):
        y=ys[i]; wire(pa+[(pa[-1][0],y),(pb[-1][0],y)]+pb[::-1],kind,a,b,net)
def a2side(nm,dx):  # morsetti a sinistra del modulo: il filo arriva da sinistra
    x,y=PIN["A2 "+nm]; return [(x,y),(x-dx,y)]

# comando dal W5 direttamente sui morsetti di A2
route(cab("W5",2),a2side("PWM",6),"PWM",cname("W5",2),"A2 morsetto PWM","PWM ventole (comando)")
route(cab("W5",3),a2side("GND",4),"V0",cname("W5",3),"A2 morsetto GND","0 V comando")
# +12 V
route(cab("W5",0),sl("12",0),"P12",cname("W5",0),sname("12",0),"+12 V")
route([PIN["A2 DC+"]],sl("12",1),"P12","A2 morsetto DC+",sname("12",1),"+12 V")
# 0 V
route(cab("W5",1),sl("0",0),"V0",cname("W5",1),sname("0",0),"0 V")
route([PIN["A2 DC−"]],sl("0",1),"V0","A2 morsetto DC−",sname("0",1),"0 V")
# uscita PWM del modulo
route([PIN["A2 OUT−"]],sl("PW",0),"PWM","A2 morsetto OUT−",sname("PW",0),"PWM ventole (uscita A2)")
# giri dal W5
for i,(m,t) in enumerate([("M5","T5"),("M6","T6"),("M7","T7")]):
    route(cab("W5",4+i),sl(t,0),"TACH",cname("W5",4+i),sname(t,0),f"Giri ventola {m}")
# ventole
for k,(m,t) in enumerate([("M5","T5"),("M6","T6"),("M7","T7")]):
    route(cab(m,1),sl("12",2+k),"P12",cname(m,1),sname("12",2+k),"+12 V")
    route(cab(m,0),sl("0",2+k),"V0",cname(m,0),sname("0",2+k),"0 V")
    route(cab(m,3),sl("PW",1+k),"PWM",cname(m,3),sname("PW",1+k),"PWM ventole (uscita A2)")
    route(cab(m,2),sl(t,1),"TACH",cname(m,2),sname(t,1),f"Giri ventola {m}")

place_routes()
# riquadro di lettura
BX=MX+MW+8
rect(BX,8,W-BX-6,40,"","fillColor=#ffffff;strokeColor=#999999;")
text(BX+2,9,W-BX-10,38,"<b>Come si legge</b><br>W5 verde → A2 PWM; bianco-verde → A2 GND (morsetti a vite, niente Wago).<br>A2 OUT− → Wago PWM: tira a massa il filo PWM delle 3 ventole.<br>Prolunghe ventole (fili neri, il n. 1 ha la riga): 1 GND → 0 V; 2 → +12 V; 3 giri → Wago giri; 4 → Wago PWM.<br>W5 bianco-arancio: di riserva, isolalo. Wago PWM: foro 5 libero.",5.5)

# ---------------- reti
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
    if w["a"]: groups.setdefault(f(w["a"]),[]).append(i)
nets=[]
ORDER=["P12","V0","PWM","TACH"]
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
    if w["a"] is None: w["net"]=None
# colori veri dei conduttori del Cat5e W5
CAT={"blu":"#1565C0","arancio":"#EF6C00","verde":"#2E7D32","marrone":"#6D4C41"}
for w in WIRES:
    if not w["a"]: continue
    for e in (w["a"],w["b"]):
        if e.startswith("W5 "): w["cond"]=e.split(" ")[1]
CABLES=[]
for c in CHAN:
    rows=[]
    for i,w in enumerate(WIRES):
        if not w["a"]: continue
        for mine,other in ((w["a"],w["b"]),(w["b"],w["a"])):
            if mine.startswith(c+" "):
                rows.append(dict(c=mine[len(c)+1:],to=other,net=w["net"],w=i))
    rows.sort(key=lambda r:CN[c].index(r["c"]))
    CABLES.append(dict(id=c,title=GLAB[c],x=round(SPLIT[c],2),y0=YS,y1=YG+5,rows=rows))
splits=[[SPLIT[c],YS] for c in CHAN]
json.dump(dict(W=W,H=H,V=[{**v,"x":round(v["x"],2),"y":round(v["y"],2),"w":round(v["w"],2),"h":round(v["h"],2)} for v in V],
               wires=WIRES,nets=nets,dots=[],splits=splits,cables=CABLES),open(sys.argv[2],'w'),ensure_ascii=False)

# drawio
ST={k:f"strokeColor={c};strokeWidth={9 if k=='CAB' else 2};"+("opacity=55;" if k=='CAB' else "") for k,c in COL.items()}
for w in WIRES:
    p=[(OX+x*S,OY+y*S) for x,y in w["pts"]]
    mids=''.join(f'<mxPoint x="{x:.1f}" y="{y:.1f}"/>' for x,y in p[1:-1])
    st=ST[w["kind"]]
    if w.get("cond"):
        st=f"strokeColor={CAT[w['cond'].split('-')[-1]]};strokeWidth=3;"+("dashed=1;dashPattern=3 2;" if w["cond"].startswith("bianco") else "")
    cells.append(f'<mxCell id="{nid()}" value="" style="endArrow=none;html=1;rounded=0;jumpStyle=arc;jumpSize=4;{st}" edge="1" parent="1"><mxGeometry relative="1" as="geometry"><mxPoint x="{p[0][0]:.1f}" y="{p[0][1]:.1f}" as="sourcePoint"/><mxPoint x="{p[-1][0]:.1f}" y="{p[-1][1]:.1f}" as="targetPoint"/>'+(f'<Array as="points">{mids}</Array>' if mids else '')+'</mxGeometry></mxCell>')
xml=('<mxfile host="app.diagrams.net"><diagram id="x4" name="Scatola X4"><mxGraphModel dx="1400" dy="1000" grid="0" gridSize="10" guides="1" tooltips="1" connect="0" arrows="0" fold="1" page="1" pageScale="1" pageWidth="1100" pageHeight="800" math="0" shadow="0"><root><mxCell id="0"/><mxCell id="1" parent="0"/>'
     +''.join(cells)+'</root></mxGraphModel></diagram></mxfile>')
open(sys.argv[1],'w').write(xml)
print(len(V),"vertici",len(WIRES),"fili",len(nets),"reti; larghezza",W,"corsie fino a y",round(LANE[0],1))
for d in nets: print(d["id"],d["name"],"|",", ".join(d["ends"]))
