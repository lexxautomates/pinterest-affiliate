"""Monthly seed product pool for each niche.

Replace ASINs with YOUR real Amazon products (Associates Central).
The orchestrator/planner cycles through these so pins aren't 5 products
repeated 48x. Each niche has a small pool; the planner picks round-robin.

Format: {niche: [(asin, name), ...]}
"""
SEED_PRODUCTS = {
    "home_organization": [
        ("REPLACE_ASIN_1", "closet organizer"),
        ("REPLACE_ASIN_6", "drawer divider set"),
        ("REPLACE_ASIN_7", "under-bed storage bin"),
    ],
    "kitchen_gadgets": [
        ("REPLACE_ASIN_2", "space-saving gadget"),
        ("REPLACE_ASIN_8", "electric can opener"),
        ("REPLACE_ASIN_9", "measuring cup set"),
    ],
    "home_decor": [
        ("REPLACE_ASIN_10", "peel-and-stick wallpaper"),
        ("REPLACE_ASIN_11", "LED strip lights"),
        ("REPLACE_ASIN_12", "boho area rug"),
    ],
    "beauty_skincare_tools": [
        ("REPLACE_ASIN_13", "LED face mask"),
        ("REPLACE_ASIN_14", "jade roller set"),
        ("REPLACE_ASIN_15", "hair dryer brush"),
    ],
    "fitness_homegym": [
        ("REPLACE_ASIN_16", "resistance band set"),
        ("REPLACE_ASIN_17", "adjustable dumbbells"),
        ("REPLACE_ASIN_18", "yoga mat"),
    ],
    "pet_supplies": [
        ("REPLACE_ASIN_19", "orthopedic pet bed"),
        ("REPLACE_ASIN_20", "auto pet feeder"),
        ("REPLACE_ASIN_21", "cat scratching post"),
    ],
    "outdoor_grilling": [
        ("REPLACE_ASIN_22", "grill brush"),
        ("REPLACE_ASIN_23", "bbq tool set"),
        ("REPLACE_ASIN_24", "patio string lights"),
    ],
    "tech_desk_accessories": [
        ("REPLACE_ASIN_3", "cable management tray"),
        ("REPLACE_ASIN_25", "laptop stand"),
        ("REPLACE_ASIN_26", "wireless charger"),
    ],
    "baby_parenting": [
        ("REPLACE_ASIN_27", "baby monitor"),
        ("REPLACE_ASIN_28", "diaper caddy"),
        ("REPLACE_ASIN_29", "white noise machine"),
    ],
    "cleaning_tools": [
        ("REPLACE_ASIN_4", "robot vacuum"),
        ("REPLACE_ASIN_30", "steam mop"),
        ("REPLACE_ASIN_31", "cordless handheld vac"),
    ],
    "travel_accessories": [
        ("REPLACE_ASIN_32", "packing cubes"),
        ("REPLACE_ASIN_33", "carry-on luggage"),
        ("REPLACE_ASIN_34", "travel pillow"),
    ],
    "gardening_planters": [
        ("REPLACE_ASIN_35", "self-watering planter"),
        ("REPLACE_ASIN_36", "raised garden bed"),
        ("REPLACE_ASIN_37", "indoor grow light"),
    ],
}

# Flat list for the simple orchestrator path
SEED_PRODUCTS_FLAT = [
    {"niche": n, "asin": a, "name": nm} for n, items in SEED_PRODUCTS.items() for a, nm in items
]
