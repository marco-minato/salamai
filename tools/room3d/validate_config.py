#!/usr/bin/env python3
"""Valida la configurazione del modello 3D (stanza + layout del catalogo).

Uso: python3 tools/room3d/validate_config.py [--config model/room3d/room.json] [--layout L001]
Exit code 0 se valida, 1 se ci sono errori (elencati tutti con il percorso JSON).
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import room3d_core as core  # noqa: E402


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--config", default="model/room3d/room.json")
    ap.add_argument("--layout", default=None, help="valida solo questo layout_id")
    args = ap.parse_args(argv)
    try:
        room, catalog, layouts = core.load_model(args.config, args.layout)
        core.validate(room, layouts, catalog)
    except core.ConfigError as e:
        print(f"CONFIGURAZIONE NON VALIDA ({len(e.errors)} errori):", file=sys.stderr)
        for msg in e.errors:
            print(f"  - {msg}", file=sys.stderr)
        return 1
    except (OSError, ValueError, KeyError) as e:
        print(f"ERRORE di lettura: {e}", file=sys.stderr)
        return 1
    door, hatch = core.derive_openings(room)
    sx, sy, sz = core.room_dims(room)
    print(f"OK: {len(layouts)} layout validi ({', '.join(l['layout_id'] for l in layouts)})")
    print(f"  stanza {sx:.3f} × {sy:.3f} × {sz:.3f} m, volume lordo {sx * sy * sz:.4f} m³")
    print(f"  porta X {door['x_min']:.3f}–{door['x_max']:.3f} m, altezza {door['z_max']:.2f} m "
          f"({door['status']['height']})")
    print(f"  botola X {hatch['x_min']:.3f}–{hatch['x_max']:.3f}, Y {hatch['y_min']:.3f}–{hatch['y_max']:.3f} m "
          f"(riferimento '{hatch['offset_reference']}', {hatch['status']['offset_reference']})")
    for lay in layouts:
        print(f"  {lay['layout_id']}: hash {core.config_hash(room, lay)[:12]}, "
              f"{len(lay.get('components', []))} componenti, tipo {lay['kind']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
