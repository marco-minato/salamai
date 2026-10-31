import sys, json, re, html as H
import xml.etree.ElementTree as ET
sys.argv=['gen_3.py','q6.drawio']
g={}
exec(open('gen_3.py').read(),g)
S,OX,OY=g['S'],g['OX'],g['OY']
mm=lambda X,Y:((X-OX)/S,(Y-OY)/S)
W,Hh=g['W'],g['H']

# ---------- vertices from the drawio file
root=ET.parse('q6.drawio').getroot()
def sty(s,k):
    m=re.search(k+r'=([^;]+)',s); return m.group(1) if m else None
V=[]
for c in root.iter('mxCell'):
    if c.get('vertex')!='1': continue
    st=c.get('style') or ''; gm=c.find('mxGeometry')
    x,y=mm(float(gm.get('x')),float(gm.get('y'))); w,h=float(gm.get('width'))/S,float(gm.get('height'))/S
    if x>W+65: continue                     # legenda: va nella pagina (le quote restano)
    val=c.get('value') or ''
    val=re.sub(r'<br\s*/?>','\n',val); val=H.unescape(re.sub(r'<[^>]+>','',val)).strip()
    V.append(dict(x=round(x,2),y=round(y,2),w=round(w,2),h=round(h,2),
      fill=sty(st,'fillColor') or 'none',stroke=sty(st,'strokeColor') or 'none',
      text=st.startswith('text'),ell='ellipse' in st,dash='dashed=1' in st,
      rot=('horizontal=0' in st),fs=float(sty(st,'fontSize') or 11),
      fc=sty(st,'fontColor') or '#222222',
      align=sty(st,'align') or ('left' if st.startswith('text') else 'center'),
      valign=sty(st,'verticalAlign') or ('top' if st.startswith('text') else 'middle'),
      hatch='fillStyle=hatch' in st, sw=float(sty(st,'strokeWidth') or 1),
      label=val))

# ---------- named pins (mm)
TP=g['TP']; P={}
def pin(n,x,y,raw=False): P[n]=(x,y if raw else g["M"](y))
rails=g['RAILS']
for k,x in TP.items():
    grp,num=k.split('_'); r=rails[grp]
    pin(f"{grp}:{num} sopra",x,r-21); pin(f"{grp}:{num} sotto",x,r+21)
for n,x,y in [("T1 L",g['T1L'],g['T1bot']),("T1 N",g['T1N'],g['T1bot']),("T1 +V",g['T1P'],g['T1top']),("T1 −V",g['T1M'],g['T1top']),
              ("Waveshare 12V",g['A1P'],g['A1top']),("Waveshare GND",g['A1G'],g['A1top']),("Waveshare A",g['A1A'],g['A1top']),("Waveshare B",g['A1B'],g['A1top']),("Waveshare terra",g['A1E'],g['A1top']),
              ("Q1 L ingresso",g['Q1L'],g['Q1top']),("Q1 N ingresso",g['Q1N'],g['Q1top']),("Q1 L uscita",g['Q1L'],g['Q1bot']),("Q1 N uscita",g['Q1N'],g['Q1bot']),
              ("Contatore 1 L ingresso",g['A3Lin'],g['A3bot']),("Contatore 3 N",g['A3N'],g['A3top']),("Contatore 2 L uscita",g['A3Lout'],g['A3bot']),("Contatore 4 N",g['A3Nout'],g['A3top']),("Contatore 10 A+",g['A3A'],g['A3top']),("Contatore 9 B−",g['A3B'],g['A3top']),
              ("F1 ingresso",g['FU']['F1'],g['FUin']),("F1 uscita",g['FU']['F1'],g['FUout']),
              ]:
    pin(n,x,y)
pin("Vite di terra piastra",*g['SCREW'])
for k in range(6):
    pin(f"Relè K{k+1} COM",g['COM'][k],g['A1bot']); pin(f"Relè K{k+1} NA",g['NO'][k],g['A1bot'])
    pin(f"KM{k+1} morsetto 1",g['KM1'][k],g['KMtop']); pin(f"KM{k+1} morsetto 2",g['KM1'][k],g['KMbot'])
    pin(f"KM{k+1} bobina +",g['KMP'][k],g['KMtop']); pin(f"KM{k+1} bobina −",g['KMP'][k],g['KMbot'])

# cavi (guaina): punto in cui il cavo si apre nei singoli fili
GLN={"casa":"cavo linea di casa","stufa":"cavo stufa","u1":"cavo presa umidificatore 1","u2":"cavo presa umidificatore 2","estr":"cavo presa estrattore","cam":"Cat5e camera"}
CABLE={}
RAW=g['RAW']
wires=[]
for i,(kind,pts,cond) in enumerate(RAW):
    q=[mm(*p) for p in pts]
    if kind in ('C230','CBT'):
        gx=round(q[0][0]); name=[v for k,v in GLN.items() if g['GL'][k]==gx]
        CABLE[(round(q[-1][0],1),round(q[-1][1],1))]=name[0] if name else 'cavo'
    w=dict(kind=kind,pts=[(round(a,2),round(b,2)) for a,b in q])
    if cond: w['cond']=cond
    wires.append(w)
def name_of(pt):
    best=None;bd=1.2
    for n,(x,y) in P.items():
        d=abs(x-pt[0])+abs(y-pt[1])
        if d<bd: bd=d;best=n
    if best: return best
    k=(round(pt[0],1),round(pt[1],1))
    for (cx,cy),n in CABLE.items():
        if abs(cx-pt[0])+abs(cy-pt[1])<1.2: return n
    return None

# ---------- nets (union-find)
par={}
def f(a):
    par.setdefault(a,a)
    while par[a]!=a: par[a]=par[par[a]]; a=par[a]
    return a
def u(a,b): par[f(a)]=f(b)
for k in TP:
    grp,num=k.split('_'); u(f"{grp}:{num} sopra",f"{grp}:{num} sotto")
for ks in g['BRIDGES']:
    for a,b in zip(ks,ks[1:]): u(a.replace('_',':')+" sopra",b.replace('_',':')+" sopra")
pes=[f"{k.replace('_',':')} sopra" for k in TP if 'PE' in k]+["Vite di terra piastra"]
for a in pes[1:]: u(pes[0],a)
u("Contatore 3 N","Contatore 4 N")   # nel contatore il neutro passa dentro
cable_wire_end={}
for i,w in enumerate(wires):
    if w['kind'] in ('C230','CBT'): w['net']=None; w['a']=w['b']=None; continue
    a,b=name_of(w['pts'][0]),name_of(w['pts'][-1])
    w['a'],w['b']=a,b
    ka=a if a and not a.startswith(('cavo','Cat5e')) else f"_w{i}a"
    kb=b if b and not b.startswith(('cavo','Cat5e')) else f"_w{i}b"
    f(ka);f(kb)
    if w['kind'] not in ('PE','PEb') or True: u(ka,kb)
DOTS=[]
# giunzioni a T: estremo senza nome che cade sul percorso di un altro filo
def onseg(pt,a,b):
    (x,y),(x1,y1),(x2,y2)=pt,a,b
    if abs(x1-x2)<0.01: return abs(x-x1)<0.3 and min(y1,y2)-0.3<=y<=max(y1,y2)+0.3
    if abs(y1-y2)<0.01: return abs(y-y1)<0.3 and min(x1,x2)-0.3<=x<=max(x1,x2)+0.3
    return False
for i,w in enumerate(wires):
    if w['kind'] in ('C230','CBT'): continue
    for end,key in ((w['pts'][0],'a'),(w['pts'][-1],'b')):
        if w[key] is not None: continue
        for j,v in enumerate(wires):
            if j==i or v['kind']!=w['kind']: continue
            if any(onseg(end,s,e) for s,e in zip(v['pts'],v['pts'][1:])):
                kv=v['a'] if v['a'] and not v['a'].startswith(('cavo','Cat5e')) else f"_w{j}a"
                u(f"_w{i}{key}",kv); DOTS.append([round(end[0],2),round(end[1],2)]); break
# nomi delle reti
groups={}
for i,w in enumerate(wires):
    if w['kind'] in ('C230','CBT'): continue
    ka=w['a'] if w['a'] and not w['a'].startswith(('cavo','Cat5e')) else f"_w{i}a"
    r=f(ka); groups.setdefault(r,[]).append(i)
KN={"L":"Fase","N":"Neutro","PE":"Terra","PEb":"Terra","P12":"+12 V","V0":"0 V","A":"RS485 A","B":"RS485 B","COIL":"Comando bobina"}
nets=[]
for n,(r,ids) in enumerate(groups.items()):
    kinds=[wires[i]['kind'] for i in ids]
    kind=max(set(kinds),key=kinds.count)
    ends=set()
    for i in ids:
        for e in (wires[i]['a'],wires[i]['b']):
            if e: ends.add(e.replace(' sopra','').replace(' sotto','') if e.startswith(('X0','X2','X3','X5')) else e)
    nm=KN[kind]
    if kind=='COIL':
        k=[e for e in ends if e.startswith('Relè')]; nm+=" "+(k[0].split()[1] if k else '')
    if kind=='L':
        km=[e for e in ends if 'morsetto 2' in e]
        if km: nm="Fase al carico da "+km[0].split()[0]
        elif any('Contatore 2 L uscita' in e for e in ends): nm="Fase ai contattori (dopo il contatore)"
        elif any('Q1 L ingresso' in e for e in ends): nm="Fase dalla linea di casa"
        else: nm="Fase dopo il magnetotermico"
    if kind=='P12':
        if 'F1 uscita' in ends: nm="+12 V camera (dopo F1)"
        elif 'F2 uscita' in ends: nm="+12 V cantina (dopo F2)"
    if kind=='N':
        nm="Neutro dalla linea di casa" if any('Q1 N ingresso' in e for e in ends) else "Neutro dopo il magnetotermico"
    for i in ids: wires[i]['net']=n
    nets.append(dict(id=n,name=nm,kind=kind,ends=sorted(ends),wires=ids))
order={"L":0,"N":1,"PE":2,"PEb":2,"P12":3,"V0":4,"A":5,"B":6,"COIL":7}
nets.sort(key=lambda d:(order[d['kind']],d['name']))
out=dict(W=W+78,H=Hh,V=V,wires=wires,nets=nets,dots=DOTS,splits=[[k[0],k[1]] for k in CABLE])
json.dump(out,open('schema.json','w'),ensure_ascii=False)
print(len(V),'vertici',len(wires),'fili',len(nets),'reti')
for d in nets: print(d['id'],d['name'],'|',', '.join(d['ends'])[:160])
nulls=[(i,w['a'],w['b']) for i,w in enumerate(wires) if w['kind'] not in ('C230','CBT') and (w['a'] is None or w['b'] is None)]
print('estremi senza nome:',nulls[:20])
