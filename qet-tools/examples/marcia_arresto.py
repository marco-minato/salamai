#!/usr/bin/env python3
"""Esempio: comando marcia/arresto con autoritenuta e lampada spia."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from qetlib import Project

A = "10_electric/10_allpole/"
p = Project("Marcia / arresto con autoritenuta", author="Claude")
d = p.diagram("Circuito di comando", cols=12, rows=7)

src = d.add(A + "110_network_supplies/src_1pn.elmt", 80, 100)
s0 = d.add(A + "380_signaling_operating/20_push_buttons/poussoir_nf.elmt", 300, 160, "S0")
s1 = d.add(A + "380_signaling_operating/20_push_buttons/poussoir.elmt", 300, 280, "S1")
k1c = d.add(A + "310_relays_contactors_contacts/02_contacts_cross_referencing/01_auxiliary_contacts/con_simple.elmt", 420, 280, "K1")
k1 = d.add(A + "310_relays_contactors_contacts/01_coils/bobine3.elmt", 300, 420, "K1")
h1 = d.add(A + "380_signaling_operating/11_optical_signaling/lampe2.elmt", 520, 420, "H1")

L, N = src.t[0], src.t[1]
d.wire(L, s0.t[0])
d.wire(s0.t[1], s1.t[0])
d.wire(s0.t[1], k1c.t[0])
d.wire(s1.t[1], k1.t[0])
d.wire(k1c.t[1], k1.t[0])
d.wire(k1.t[0], h1.t[0])
d.wire(k1.t[1], N)
d.wire(h1.t[1], k1.t[1])
d.text("S0 = arresto, S1 = marcia", 420, 120)

print(p.save(sys.argv[1] if len(sys.argv) > 1 else "marcia_arresto.qet"))
