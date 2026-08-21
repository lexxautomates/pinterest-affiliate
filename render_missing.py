"""Render missing pin images from manifest.json.

Generates FLUX images ONLY for (niche,format) combos not yet in manifest.json.
Call this whenever image budget is available (e.g. after a billing reset, or
via a cron that runs a few per day). Each generated URL is appended to manifest.

Usage:  python render_missing.py [--limit N]
(Requires the agent's image_generate tool; this script prints the prompts to
run, OR is driven by the agent which calls image_generate and records URLs.)
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MANIFEST = os.path.join(HERE, "manifest.json")
import image_gen
from niches import EVERGREEN_NICHES, CONTENT_FORMATS

fmts = [c["format"] for c in CONTENT_FORMATS]
combos = [(n, f) for n in EVERGREEN_NICHES for f in fmts]


def missing():
    m = json.load(open(MANIFEST)) if os.path.exists(MANIFEST) else {}
    return [(n, f) for n, f in combos if image_gen.slug_for(n, f) not in m]


if __name__ == "__main__":
    lim = int(sys.argv[1]) if len(sys.argv) > 1 else 999
    miss = missing()
    print(f"Missing {len(miss)} of {len(combos)} combos.")
    for n, f in miss[:lim]:
        print(f"GEN {image_gen.slug_for(n,f)} :: {image_gen.build_prompt(n,f)}")
