import sys,re,zlib,struct,xml.etree.ElementTree as ET
SC=float(sys.argv[3]) if len(sys.argv)>3 else 1.0
r=ET.parse(sys.argv[1]).getroot()
CX,CY,CW,CH=[float(v) for v in (sys.argv[4:8] if len(sys.argv)>7 else (0,0,1400,1300))]
Wd,Hd=int(CW*SC),int(CH*SC)
img=bytearray(b'\xff'*(Wd*Hd*3))
def hexc(s,d):
    m=re.search(s+r'=(#[0-9a-fA-F]{6})',d)
    return tuple(int(m.group(1)[i:i+2],16) for i in (1,3,5)) if m else None
def px(x,y,c):
    x-=CX*SC; y-=CY*SC
    x=int(x);y=int(y)
    if 0<=x<Wd and 0<=y<Hd: img[(y*Wd+x)*3:(y*Wd+x)*3+3]=bytes(c)
def fill(x,y,w,h,c):
    for yy in range(int(y),int(y+h)):
        for xx in range(int(x),int(x+w)): px(xx,yy,c)
def line(a,b,c,w):
    (x0,y0),(x1,y1)=a,b; n=int(max(abs(x1-x0),abs(y1-y0)))+1
    for i in range(n+1):
        t=i/n; x=x0+(x1-x0)*t; y=y0+(y1-y0)*t
        for dx in range(-int(w//2),int(w//2)+1):
            for dy in range(-int(w//2),int(w//2)+1): px(x+dx,y+dy,c)
edges=[]
for c in r.iter('mxCell'):
    st=c.get('style') or ''; g=c.find('mxGeometry')
    if g is None: continue
    if c.get('vertex'):
        if st.startswith('text'): continue
        x,y,w,h=[float(g.get(k))*SC for k in('x','y','width','height')]
        f=hexc('fillColor',st); s=hexc('strokeColor',st) or (0,0,0)
        if f: fill(x,y,w,h,f)
        line((x,y),(x+w,y),s,1);line((x,y+h),(x+w,y+h),s,1);line((x,y),(x,y+h),s,1);line((x+w,y),(x+w,y+h),s,1)
    else:
        pts=[g.find("mxPoint[@as='sourcePoint']")]+list(g.iter('Array') and [p for a in g.iter('Array') for p in a])+[g.find("mxPoint[@as='targetPoint']")]
        pts=[(float(p.get('x'))*SC,float(p.get('y'))*SC) for p in pts]
        sw=float(re.search(r'strokeWidth=([\d.]+)',st).group(1))*SC
        edges.append((pts,hexc('strokeColor',st),max(1,round(sw))))
for pts,c,w in edges:
    for a,b in zip(pts,pts[1:]): line(a,b,c,w)
raw=b''.join(b'\x00'+bytes(img[y*Wd*3:(y+1)*Wd*3]) for y in range(Hd))
def chunk(t,d): return struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
open(sys.argv[2],'wb').write(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',Wd,Hd,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(raw,6))+chunk(b'IEND',b''))
