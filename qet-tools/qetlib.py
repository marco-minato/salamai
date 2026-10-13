#!/usr/bin/env python3
"""Generate QElectroTech 0.9 (.qet) projects from Python, using symbols of the official collection.

CLI:
    qetlib.py find <words...>        search the symbol collection (all words must match name or path)
    qetlib.py info <path.elmt>       show size and terminals of a symbol

API:
    p = Project("Titolo", author="...")
    d = p.diagram("Folio 1", cols=17, rows=8)
    s1 = d.add("10_electric/.../x.elmt", x=200, y=200, label="S1")
    n = d.node(200, 300)                     # junction dot with n/e/s/w terminals
    d.wire(s1.t[1], n, color="#0000ff")      # QElectroTech routes the conductor itself
    d.text("nota", x=100, y=50)
    p.save("out.qet")
"""
import copy
import sys
import uuid
import xml.etree.ElementTree as ET
from pathlib import Path

COLLECTION = Path("/usr/share/qelectrotech/elements")
ORIENT = {"n": 0, "e": 1, "s": 2, "w": 3}
# A saved terminal is stored 4px inside the symbol relative to its definition (QET's terminal length).
DOCK_SHIFT = {0: (0, 4), 1: (-4, 0), 2: (0, -4), 3: (4, 0)}
CONDUCTOR = {
    "type": "multi", "num": "", "formula": "", "displaytext": "1", "numsize": "7", "condsize": "1",
    "text_color": "#000000", "conductor_color": "", "color2": "#000000", "bicolor": "false",
    "dash-size": "1", "cable": "", "bus": "", "function": "", "tension_protocol": "",
    "conductor_section": "", "onetextperfolio": "0", "horizrotatetext": "0", "vertirotatetext": "270",
    "horizontal-alignment": "AlignBottom", "vertical-alignment": "AlignRight",
}
LINE = "line-style:normal;line-weight:normal;filling:none;color:black"
FONT = "Sans Serif,%s,-1,5,50,0,0,0,0,0"


def _uuid():
    return "{%s}" % uuid.uuid4()


def _names(root):
    return {n.get("lang"): (n.text or "").strip() for n in root.findall("names/name")}


def load_definition(rel):
    path = COLLECTION / rel
    if not path.is_file():
        raise FileNotFoundError(f"symbol not found: {rel} (use 'qetlib.py find')")
    return ET.parse(path).getroot()


def terminals_of(definition):
    return [
        (float(t.get("x")), float(t.get("y")), ORIENT[t.get("orientation")], t.get("name", "_"))
        for t in definition.findall("description/terminal")
    ]


def _definition(name, width, height, hot_x, hot_y, link_type="simple"):
    d = ET.Element("definition", {
        "type": "element", "link_type": link_type, "version": "0.80", "width": str(width),
        "height": str(height), "hotspot_x": str(hot_x), "hotspot_y": str(hot_y),
    })
    ET.SubElement(d, "uuid", {"uuid": _uuid()})
    ET.SubElement(ET.SubElement(d, "names"), "name", {"lang": "it"}).text = name
    ET.SubElement(d, "informations").text = "Elemento personalizzato generato da qetlib"
    return d, ET.SubElement(d, "description")


def make_box(name, w, h, pins=(), lines=(), dashed=False, font=6, label_at=(0, -19)):
    """Custom symbol: a w x h rectangle (origin at its top-left corner) with named pins on its edges.

    pins:  (side, offset, pin_name[, shown_text]) with side in "nesw"; offset runs along that edge.
    lines: (x, y, text[, size]) static texts inside the box.
    """
    d, desc = _definition(name, w + 20, h + 20, 10, 10)
    style = "line-style:dashed;line-weight:normal;filling:none;color:black" if dashed else LINE
    ET.SubElement(desc, "rect", {"x": "0", "y": "0", "width": str(w), "height": str(h), "rx": "0", "ry": "0",
                                 "style": style, "antialias": "false"})
    for ln in lines:
        x, y, text = ln[:3]
        size = ln[3] if len(ln) > 3 else font
        ET.SubElement(desc, "text", {"x": str(x), "y": str(y), "size": str(size), "text": text})
    ET.SubElement(desc, "dynamic_text", {
        "x": str(label_at[0]), "y": str(label_at[1]), "z": "2", "rotation": "0", "uuid": _uuid(),
        "font": FONT % 9, "frame": "false", "text_width": "-1", "text_from": "ElementInfo",
        "Halignment": "AlignLeft", "Valignment": "AlignTop",
    })
    dt = desc[-1]
    ET.SubElement(dt, "text")
    ET.SubElement(dt, "info_name").text = "label"
    for pin in pins:
        side, off, pname = pin[:3]
        shown = pin[3] if len(pin) > 3 else pname
        tw = len(shown) * font * 0.62
        x, y = {"n": (off, 0), "s": (off, h), "w": (0, off), "e": (w, off)}[side]
        tx, ty = {"n": (x - tw / 2, 4 + font), "s": (x - tw / 2, h - 5),
                  "w": (4, y + font / 2 - 1), "e": (w - 4 - tw, y + font / 2 - 1)}[side]
        if shown:
            ET.SubElement(desc, "text", {"x": f"{tx:g}", "y": f"{ty:g}", "size": str(font), "text": shown})
        ET.SubElement(desc, "terminal", {"x": str(x), "y": str(y), "orientation": side, "name": pname})
    return d


NODE_OFFSET = {"n": (0, -4), "e": (4, 0), "s": (0, 4), "w": (-4, 0)}
# Colours an element drawing may use, to tint a junction like the conductors that reach it.
NAMED = {"black": (0, 0, 0), "gray": (128, 128, 128), "brown": (139, 69, 19), "blue": (0, 0, 255),
         "green": (0, 170, 0), "red": (255, 0, 0), "orange": (255, 136, 0), "purple": (150, 0, 150),
         "cyan": (0, 150, 150)}


def named_color(hexcolor):
    if not hexcolor:
        return "black"
    rgb = tuple(int(hexcolor[i:i + 2], 16) for i in (1, 3, 5))
    return min(NAMED, key=lambda n: sum((a - b) ** 2 for a, b in zip(NAMED[n], rgb)))


def make_node(dot=True, sides="nesw", color="black"):
    """Junction or bend. Each terminal sits 4px out of the centre so that its stub (a terminal is always
    drawn 4px long, towards the symbol) lies on the conductor instead of sticking out of the bend."""
    d, desc = _definition("Nodo" if dot else "Angolo", 10, 10, 5, 5)
    for side in sides:
        x, y = NODE_OFFSET[side]
        ET.SubElement(desc, "line", {
            "x1": "0", "y1": "0", "x2": str(x), "y2": str(y), "antialias": "false", "end1": "none",
            "end2": "none", "length1": "1.5", "length2": "1.5",
            "style": f"line-style:normal;line-weight:normal;filling:none;color:{color}"})
    if dot:
        ET.SubElement(desc, "circle", {"x": "-2", "y": "-2", "diameter": "4", "antialias": "true",
                                       "style": f"line-style:normal;line-weight:normal;filling:{color};color:{color}"})
    for side in sides:
        x, y = NODE_OFFSET[side]
        ET.SubElement(desc, "terminal", {"x": str(x), "y": str(y), "orientation": side, "name": side})
    return d


class Terminal:
    def __init__(self, element, tid, lx, ly, orient, name):
        self.element, self.id, self.lx, self.ly, self.orient, self.name = element, tid, lx, ly, orient, name

    @property
    def pos(self):
        """Absolute folio coordinates, accounting for the element rotation."""
        x, y = self.lx, self.ly
        for _ in range(self.element.orientation % 4):
            x, y = -y, x
        return (self.element.x + x, self.element.y + y)

    @property
    def facing(self):
        return (self.orient + self.element.orientation) % 4

    def __repr__(self):
        return f"<T{self.id} {self.name} @{self.pos}>"


class Element:
    def __init__(self, diagram, rel, x, y, label, orientation, infos, z=10, label_pos=None):
        self.rel, self.x, self.y, self.label, self.orientation, self.z = rel, x, y, label, orientation, z
        self.label_pos = label_pos
        self.infos = dict(infos or {})
        self.uuid, self.links, self.is_node = _uuid(), [], False
        self.definition = diagram.project._embed(rel)
        self.t, self.pin = [], {}
        for lx, ly, o, name in terminals_of(self.definition):
            t = Terminal(self, diagram._next_tid(), lx, ly, o, name)
            self.t.append(t)
            self.pin[name] = t

    def to_xml(self):
        e = ET.Element("element", {
            "x": str(self.x), "y": str(self.y), "z": str(self.z), "orientation": str(self.orientation),
            "type": "embed://import/" + self.rel, "uuid": self.uuid, "prefix": "", "freezeLabel": "false",
        })
        ts = ET.SubElement(e, "terminals")
        for t in self.t:
            dx, dy = DOCK_SHIFT[t.orient]
            ET.SubElement(ts, "terminal", {
                "x": f"{t.lx + dx:g}", "y": f"{t.ly + dy:g}", "orientation": str(t.orient), "id": str(t.id),
                "name": t.name, "number": "_", "nameHidden": "0",
            })
        ET.SubElement(e, "inputs")
        if self.links:
            lk = ET.SubElement(e, "links_uuids")
            for other in self.links:
                ET.SubElement(lk, "link_uuid", {"uuid": other.uuid})
        infos = ET.SubElement(e, "elementInformations")
        allinfos = dict(self.infos)
        if self.label is not None:
            allinfos["label"] = self.label
        for k, v in allinfos.items():
            ET.SubElement(infos, "elementInformation", {"name": k, "show": "1"}).text = str(v)
        dyn = ET.SubElement(e, "dynamic_texts")
        d = self.definition
        # Folio reports keep an empty label text: QET fills it with the linked folio position.
        is_report = d.get("link_type") in ("next_report", "previous_report")
        if self.label is not None or is_report:
            dt = None
            for cand in d.findall("description/dynamic_text"):
                if (cand.findtext("info_name") or "").strip() == "label":
                    dt = cand
            if dt is not None:
                x, y, uid, rot = dt.get("x"), dt.get("y"), dt.get("uuid"), dt.get("rotation", "0")
                font = dt.get("font") or FONT % dt.get("font_size", "9")
            else:
                x, y = f"{float(d.get('width')) - float(d.get('hotspot_x')) + 2:g}", "-12"
                uid, rot, font = _uuid(), "0", FONT % 9
            if self.label_pos:
                # label_pos is the wanted on-screen offset: undo the element rotation and keep it upright
                lx, ly = self.label_pos
                for _ in range(self.orientation % 4):
                    lx, ly = ly, -lx
                x, y, rot = f"{lx:g}", f"{ly:g}", str((360 - 90 * self.orientation) % 360)
            t = ET.SubElement(dyn, "dynamic_elmt_text", {
                "x": x, "y": y, "rotation": rot, "uuid": uid, "frame": "false", "text_width": "-1",
                "Halignment": "AlignLeft", "Valignment": "AlignTop", "keep_visual_rotation": "true",
                "text_from": "ElementInfo", "font": font,
            })
            ET.SubElement(t, "text").text = "" if self.label is None else str(self.label)
            ET.SubElement(t, "info_name").text = "label"
        ET.SubElement(e, "texts_groups")
        return e


class Diagram:
    def __init__(self, project, title, cols, rows, colsize, rowsize):
        self.project, self.title = project, title
        self.cols, self.rows, self.colsize, self.rowsize = cols, rows, colsize, rowsize
        self.elements, self.conductors, self.texts, self.shapes, self.tables = [], [], [], [], []
        self.properties, self.template, self._tid = {}, None, 0

    def _next_tid(self):
        self._tid += 1
        return self._tid - 1

    def add(self, rel, x, y, label=None, orientation=0, infos=None, z=10, label_pos=None):
        """Place a symbol; x/y is its hotspot. Keep coordinates on the 10px grid."""
        el = Element(self, rel, x, y, label, orientation, infos, z, label_pos)
        self.elements.append(el)
        return el

    def node(self, x, y, dot=True):
        self.project.define("nodo" if dot else "angolo", None, factory=lambda: make_node(dot))
        el = self.add("custom/%s.elmt" % ("nodo" if dot else "angolo"), x, y)
        el.is_node, el.dot = True, dot
        return el

    def _trim_nodes(self):
        """Give every junction only the terminals it uses, drawn in the colour of its conductors."""
        used = {}
        for a, b, attrs in self.conductors:
            for t in (a, b):
                used.setdefault(t.element, []).append((t, attrs.get("color")))
        for el in self.elements:
            if not el.is_node or el not in used:
                continue
            keep = [t for t in el.t if any(t is u for u, _ in used[el])]
            sides = "".join("nesw"[t.orient] for t in keep)
            color = named_color(used[el][0][1]).replace("brown", "black")  # QET draws "brown" fills hollow
            name = f"{'nodo' if el.dot else 'angolo'}_{sides}_{color}"
            el.rel = self.project.define(name, None, factory=lambda: make_node(el.dot, sides, color))
            el.definition, el.t = self.project._embedded[el.rel], keep

    @staticmethod
    def _node_side(node, other_pos, other_vertical):
        dx, dy = other_pos[0] - node.x, other_pos[1] - node.y
        if abs(dx) < 0.5:
            return node.t[2] if dy > 0 else node.t[0]
        if abs(dy) < 0.5:
            return node.t[1] if dx > 0 else node.t[3]
        if other_vertical:
            return node.t[1] if dx > 0 else node.t[3]
        return node.t[2] if dy > 0 else node.t[0]

    def wire(self, a, b, num="", color=None, color2=None, dashed=False, **attrs):
        """Connect two terminals (or nodes: the side is chosen from the geometry)."""
        a_node, b_node = isinstance(a, Element), isinstance(b, Element)
        if a_node:
            other_vertical = True if b_node else b.facing in (0, 2)
            ta = self._node_side(a, (b.x, b.y) if b_node else b.pos, other_vertical)
        else:
            ta = a
        if b_node:
            tb = self._node_side(b, ta.pos, ta.facing in (0, 2))
        else:
            tb = b
        if ta is tb:
            raise ValueError("cannot wire a terminal to itself")
        if color:
            attrs["color"] = color
        if color2:
            attrs.update(bicolor="true", color2=color2)
            attrs["dash-size"] = "6"
        if dashed:
            attrs["style"] = "line-style: dashed;"
        self.conductors.append((ta, tb, dict(attrs, num=num)))

    def chain(self, *points, **kw):
        """Wire consecutive points; only the first conductor carries the text."""
        for i in range(len(points) - 1):
            self.wire(points[i], points[i + 1], **kw)
            kw = dict(kw, num="")

    def text(self, text, x, y, size=9, rotation=0):
        """Free text; HTML is accepted (QET renders it as rich text)."""
        self.texts.append((text, x, y, size, rotation))

    def rect(self, x1, y1, x2, y2, dashed=False, color="#000000", fill=None, width=1, kind="Rectangle"):
        self.shapes.append((kind, x1, y1, x2, y2, dashed, color, fill, width))

    def line(self, x1, y1, x2, y2, **kw):
        self.rect(x1, y1, x2, y2, kind="Line", **kw)

    def ellipse(self, x1, y1, x2, y2, **kw):
        self.rect(x1, y1, x2, y2, kind="Ellipse", **kw)

    def report_out(self, x, y, orientation=0):
        return self.add("10_electric/10_allpole/100_folio_referencing/02going_arrow.elmt", x, y,
                        orientation=orientation)

    def report_in(self, x, y, orientation=0):
        return self.add("10_electric/10_allpole/100_folio_referencing/01coming_arrow.elmt", x, y,
                        orientation=orientation)

    def table(self, x, y, width, height, query, headers, identifier="nomenclature", rows=30, font=8):
        self.tables.append((x, y, width, height, query, headers, identifier, rows, font))

    def to_xml(self, order):
        p = self.project
        attrs = {
            "title": self.title, "author": p.author, "date": p.date, "filename": p.filename,
            "folio": "%id/%total", "order": str(order), "cols": str(self.cols), "rows": str(self.rows),
            "colsize": str(self.colsize), "rowsize": str(self.rowsize),
            "height": str(self.rows * self.rowsize + 20), "displaycols": "true", "displayrows": "true",
            "displayAt": "bottom", "version": "0.90", "indexrev": p.indexrev, "plant": "", "locmach": "",
            "auto_page_num": "", "freezeNewElement": "false", "freezeNewConductor": "false",
        }
        if self.template:
            attrs.update(titleblocktemplate=self.template, titleblocktemplateCollection="embedded")
        d = ET.Element("diagram", attrs)
        if self.properties:
            props = ET.SubElement(d, "properties")
            for k, v in self.properties.items():
                ET.SubElement(props, "property", {"name": k, "show": "1"}).text = v
        ET.SubElement(d, "defaultconductor", CONDUCTOR)
        self._trim_nodes()
        els = ET.SubElement(d, "elements")
        for el in self.elements:
            els.append(el.to_xml())
        cs = ET.SubElement(d, "conductors")
        for a, b, attrs in self.conductors:
            c = ET.SubElement(cs, "conductor", dict(
                CONDUCTOR, x="0", y="0", terminal1=str(a.id), terminal2=str(b.id), freezeLabel="false"))
            c.attrib.update({k: str(v) for k, v in attrs.items()})
            ET.SubElement(c, "sequentialNumbers")
        ins = ET.SubElement(d, "inputs")
        for text, x, y, size, rotation in self.texts:
            ET.SubElement(ins, "input", {
                "x": str(x), "y": str(y), "rotation": str(rotation), "text": text, "font": FONT % size,
            })
        if self.shapes:
            sh = ET.SubElement(d, "shapes")
            for kind, x1, y1, x2, y2, dashed, color, fill, width in self.shapes:
                a = {"type": kind, "x1": str(x1), "y1": str(y1), "x2": str(x2), "y2": str(y2),
                     "closed": "0", "is_movable": "1", "z": "0"}
                if kind == "Rectangle":
                    a.update(rx="0", ry="0")
                s = ET.SubElement(sh, "shape", a)
                ET.SubElement(s, "pen", {"style": "DashLine" if dashed else "SolidLine",
                                         "widthF": str(width), "color": color})
                ET.SubElement(s, "brush", {"style": "SolidPattern" if fill else "NoBrush",
                                           "color": fill or "#000000"})
        if self.tables:
            tb = ET.SubElement(d, "tables")
            for x, y, width, height, query, headers, identifier, rows, font in self.tables:
                g = ET.SubElement(tb, "graphics_table", {
                    "x": str(x), "y": str(y), "width": str(width), "height": str(height),
                    "display_n_row": str(rows), "name": self.title, "uuid": _uuid()})
                ET.SubElement(ET.SubElement(g, "graphics_header"), "margins").text = "5;5;10;5"
                m = ET.SubElement(ET.SubElement(g, "model"), "project_data_base_model")
                ET.SubElement(m, "identifier").text = identifier
                ET.SubElement(m, "query").text = query
                ET.SubElement(m, "index00", {"alignment": "AlignLeft", "font": FONT % font,
                                             "margins": "5;5;10;5"})
                hd = ET.SubElement(m, "header_data")
                for i, h in enumerate(headers):
                    for role in ("DisplayRole", "EditRole"):
                        ET.SubElement(hd, "data", {"role": role, "orientation": "Horizontal",
                                                   "section": str(i)}).text = h
                ET.SubElement(hd, "data", {"role": "TextAlignmentRole", "orientation": "Horizontal",
                                           "section": "0"}).text = "AlignLeft"
                ET.SubElement(hd, "data", {"role": "FontRole", "orientation": "Horizontal",
                                           "section": "0"}).text = FONT % font
        return d


class Project:
    def __init__(self, title, author="", date="null", indexrev="", filename=""):
        self.title, self.author, self.date, self.indexrev, self.filename = title, author, date, indexrev, filename
        self.diagrams, self._embedded, self._titleblocks = [], {}, []

    def titleblock(self, xml_text):
        """Embed a title block template (<titleblocktemplate name=...>); returns its name for Diagram.template."""
        tb = ET.fromstring(xml_text)
        self._titleblocks.append(tb)
        return tb.get("name")

    def diagram(self, title, cols=17, rows=8, colsize=60, rowsize=80):
        d = Diagram(self, title, cols, rows, colsize, rowsize)
        self.diagrams.append(d)
        return d

    def define(self, name, definition, factory=None):
        """Register a custom symbol; returns the path to pass to Diagram.add()."""
        rel = f"custom/{name}.elmt"
        if rel not in self._embedded:
            self._embedded[rel] = definition if definition is not None else factory()
        return rel

    def variant(self, name, rel, **attrs):
        """Embed a copy of a collection symbol with changed definition attributes (e.g. link_type)."""
        d = copy.deepcopy(load_definition(rel))
        d.attrib.update(attrs)
        return self.define(name, d)

    @staticmethod
    def link(a, b):
        """Cross-reference two folio reports (or a master and a slave)."""
        a.links.append(b)
        b.links.append(a)

    def _embed(self, rel):
        if rel not in self._embedded:
            self._embedded[rel] = load_definition(rel)
        return self._embedded[rel]

    def _collection_xml(self):
        col = ET.Element("collection")
        root = ET.SubElement(col, "category", {"name": "import"})
        names = ET.SubElement(root, "names")
        ET.SubElement(names, "name", {"lang": "en"}).text = "Imported elements"
        ET.SubElement(names, "name", {"lang": "it"}).text = "Elementi importati"
        cats = {(): root}
        for rel in sorted(self._embedded):
            parts = Path(rel).parts
            for i in range(1, len(parts)):
                key = parts[:i]
                if key not in cats:
                    cat = ET.SubElement(cats[key[:-1]], "category", {"name": key[-1]})
                    qd = COLLECTION.joinpath(*key) / "qet_directory"
                    if qd.is_file():
                        src = ET.parse(qd).getroot().find("names")
                        if src is not None:
                            cat.append(copy.deepcopy(src))
                    else:
                        n = ET.SubElement(cat, "names")
                        ET.SubElement(n, "name", {"lang": "it"}).text = "Elementi personalizzati"
                    cats[key] = cat
            el = ET.SubElement(cats[parts[:-1]], "element", {"name": parts[-1]})
            el.append(copy.deepcopy(self._embedded[rel]))
        return col

    def save(self, path, first=None):
        """Write the project. `first` (1-based) rotates that folio to the front, for render checks."""
        root = ET.Element("project", {"title": self.title, "version": "0.90"})
        if self._titleblocks:
            ET.SubElement(root, "titleblocktemplates").extend(self._titleblocks)
        ET.SubElement(root, "properties")
        diagrams = list(self.diagrams)
        if first:
            diagrams = diagrams[first - 1:] + diagrams[:first - 1]
        for i, d in enumerate(diagrams, 1):
            root.append(d.to_xml(i))
        root.append(self._collection_xml())
        ET.indent(root, space="    ")
        ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=False)
        return path


def _find(words):
    words = [w.lower() for w in words]
    for f in sorted(COLLECTION.rglob("*.elmt")):
        rel = str(f.relative_to(COLLECTION))
        try:
            root = ET.parse(f).getroot()
        except ET.ParseError:
            continue
        names = _names(root)
        hay = (rel + " " + " ".join(names.values())).lower()
        if all(w in hay for w in words):
            label = names.get("it") or names.get("en") or next(iter(names.values()), "")
            print(f"{rel}\t{label}\t{len(terminals_of(root))}T")


def _info(rel):
    root = load_definition(rel)
    print({k: root.get(k) for k in ("width", "height", "hotspot_x", "hotspot_y", "link_type")})
    print({k: v for k, v in _names(root).items() if k in ("it", "en", "fr")})
    for i, (x, y, o, name) in enumerate(terminals_of(root)):
        print(f"  t[{i}] x={x:g} y={y:g} side={'nesw'[o]} name={name}")


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "find":
        _find(sys.argv[2:])
    elif len(sys.argv) == 3 and sys.argv[1] == "info":
        _info(sys.argv[2])
    else:
        sys.exit(__doc__)
