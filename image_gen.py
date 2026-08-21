"""Image generator for pins (Designer agent).

Generates one distinct 2:3 hero image per (niche x format) combo via Hermes
image_generate (FLUX). Saves to assets/<niche>_<format>.png. Reuses per combo
across the month — compliant because each pin still gets unique copy and the
image varies by niche+angle (not the "identical product+creative" spam case).

In this environment, image_generate is invoked by the calling agent; this
module provides the PROMPT builder + filesystem bookkeeping so the pipeline is
deterministic and re-runnable.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")

NICHE_PROMPT = {
    "home_organization": "clean minimalist home organization flat-lay, woven baskets, labeled bins, calm neutral palette, bright natural light",
    "kitchen_gadgets": "modern kitchen gadget flat-lay on marble counter, stainless steel tools, fresh ingredients, bright studio light",
    "home_decor": "cozy aesthetic home decor scene, soft textiles, warm lamp glow, pastel walls, lifestyle interior",
    "beauty_skincare_tools": "clean beauty flat-lay, skincare tools, jade roller, serum bottles, soft pink background, spa aesthetic",
    "fitness_homegym": "home gym setup flat-lay, resistance bands, mat, dumbbells, energetic bright background",
    "pet_supplies": "cute pet supplies flat-lay, cozy pet bed, toys, soft pastel background, warm light",
    "outdoor_grilling": "outdoor grilling flat-lay, bbq tools, string lights, patio setting, golden hour",
    "tech_desk_accessories": "modern desk setup flat-lay, cable organizer, laptop stand, minimalist tech, clean white background",
    "baby_parenting": "soft baby gear flat-lay, monitor, caddy, plush tones, gentle natural light",
    "cleaning_tools": "cleaning tools flat-lay, robot vacuum, steam mop, fresh bright scene, before/after vibe",
    "travel_accessories": "travel flat-lay, packing cubes, luggage, passport, wanderlust aesthetic, bright",
    "gardening_planters": "garden flat-lay, planters, grow light, greenery, fresh outdoor light",
}
FORMAT_SUFFIX = {
    "listicle": "with small numbered tags overlay feel, arranged in a grid",
    "problem_solution": "messy side transitioning to tidy side, satisfying transformation",
    "gift_guide": "gift-wrapped accents, festive but clean, multiple items grouped",
    "tiktok_made_me_buy_it": "trendy vibrant flat-lay, pop of color, social-media aesthetic",
    "before_after": "split composition, cluttered left, organized right, transformation",
    "price_roundup": "budget-friendly arrangement, price-tag feel, approachable",
}


def slug_for(niche, fmt):
    return f"{niche}_{fmt}"


def build_prompt(niche, fmt):
    base = NICHE_PROMPT.get(niche, "lifestyle product flat-lay, bright clean")
    suf = FORMAT_SUFFIX.get(fmt, "")
    return (f"A Pinterest-style vertical product flat-lay: {base} {suf}. "
            f"2:3 composition, lots of negative space, high production quality, no text, no logo.")


def image_path(niche, fmt):
    return os.path.join(ASSETS, f"{slug_for(niche, fmt)}.png")


if __name__ == "__main__":
    from niches import EVERGREEN_NICHES, CONTENT_FORMATS
    fmts = [c["format"] for c in CONTENT_FORMATS]
    combos = [(n, f) for n in EVERGREEN_NICHES for f in fmts]
    for n, f in combos:
        print(f"{slug_for(n, f)}  ->  {image_path(n, f)}")
    print(f"\nTotal unique images to generate: {len(combos)}")
