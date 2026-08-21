"""Pinterest-performing content formats + seed product catalog.

Grounded in research/playbook (pinterest-amazon-playbook.md): evergreen niches
with proven Pinterest search volume + buyer intent, and FTC/Amazon-compliant
title/description templates. Each description ends with the REQUIRED disclosure.

CONTENT_FORMATS = the "what performs well" angle for a product/niche.
SEED_PRODUCTS    = YOUR curated Amazon products (fill ASINs from Associates Central).
"""

DISCLOSURE = "As an Amazon Associate, I earn from qualifying purchases."

# 12 evergreen niches (rotate; never post same niche/product back-to-back)
EVERGREEN_NICHES = [
    "home_organization", "kitchen_gadgets", "home_decor", "beauty_skincare_tools",
    "fitness_homegym", "pet_supplies", "outdoor_grilling", "tech_desk_accessories",
    "baby_parenting", "cleaning_tools", "travel_accessories", "gardening_planters",
]

CONTENT_FORMATS = [
    {"format": "listicle",
     "title_tmpl": "{n} {niche} Finds That Make Life Easier",
     "desc_tmpl": "Save this - {n} genius {niche} products you'll wish you'd bought sooner. Our favorite is the {product}; total game-changer. Tap the link to see them all on Amazon. " + DISCLOSURE,
     "tags": "#{niche} #amazonfinds #musthaves #organization #shoppingfinds"},
    {"format": "problem_solution",
     "title_tmpl": "Tired of {problem}? Try This {product}",
     "desc_tmpl": "If {problem} drives you crazy, the {product} fixes it in minutes - and it's under ${price}. See why reviewers love it via the link. " + DISCLOSURE,
     "tags": "#problem #solution #amazonfinds #gadget #lifehack"},
    {"format": "gift_guide",
     "title_tmpl": "{n} Gift Ideas Under ${price}",
     "desc_tmpl": "Stuck on gifts? These {n} {niche} picks are crowd-pleasers under ${price} and ship fast. Save this list for later. " + DISCLOSURE,
     "tags": "#giftguide #giftideas #amazonfinds #shopping"},
    {"format": "tiktok_made_me_buy_it",
     "title_tmpl": "The {product} Everyone's Talking About",
     "desc_tmpl": "You've seen it all over TikTok - here's the {product} that's actually worth it. Link goes straight to Amazon. " + DISCLOSURE,
     "tags": "#tiktokmademebuyit #amazonfinds #viral #musthave"},
    {"format": "before_after",
     "title_tmpl": "Before & After: How We Fixed {problem} with {product}",
     "desc_tmpl": "Swipe-ready transformation - this {product} turned things around for under ${price}. Save it for your next project. " + DISCLOSURE,
     "tags": "#beforeandafter #transformation #organization #cleaning"},
    {"format": "price_roundup",
     "title_tmpl": "{n} Amazon Finds Under ${price}",
     "desc_tmpl": "Budget-friendly must-haves under ${price}. Tap to shop the full list. " + DISCLOSURE,
     "tags": "#underbudget #amazonfinds #deals #shoppingfinds"},
]

# TODO(user): replace with YOUR real Amazon ASINs / product URLs from Associates Central.
# Recommend 1-3 anchor niches first, expand outward.
SEED_PRODUCTS = [
    {"niche": "home_organization", "asin": "REPLACE_ASIN_1", "name": "closet organizer"},
    {"niche": "kitchen_gadgets",   "asin": "REPLACE_ASIN_2", "name": "space-saving gadget"},
    {"niche": "tech_desk_accessories", "asin": "REPLACE_ASIN_3", "name": "cable management tray"},
    {"niche": "cleaning_tools",     "asin": "REPLACE_ASIN_4", "name": "robot vacuum"},
    {"niche": "pet_supplies",       "asin": "REPLACE_ASIN_5", "name": "pet bed"},
]
