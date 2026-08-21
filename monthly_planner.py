"""Monthly content strategy engine for the Pinterest -> Amazon affiliate pipeline.

Turns the RESEARCH playbook into a concrete 30-day posting plan: which niches,
formats, boards, and dates — weighted by prior performance (the Analyst feed).
The Foreman/Designer turn each plan row into a real pin (image + CSV row).

Run:  python monthly_planner.py [--month 2026-09] [--ppd 8] [--out plan.json]
"""
import argparse
import datetime
import json
import os

NICHE_BOARD = {
    "home_organization": "Home Organization Finds",
    "kitchen_gadgets": "Kitchen Gadgets Under $30",
    "home_decor": "Budget Home Decor",
    "beauty_skincare_tools": "Beauty & Skincare Tools",
    "fitness_homegym": "Home Gym Gear",
    "pet_supplies": "Pet Must-Haves",
    "outdoor_grilling": "Outdoor & Grill",
    "tech_desk_accessories": "Desk Setup Upgrades",
    "baby_parenting": "Baby & Parenting Gear",
    "cleaning_tools": "Cleaning Hacks",
    "travel_accessories": "Travel Gear",
    "gardening_planters": "Garden & Planters",
}
FORMATS = ["listicle", "problem_solution", "gift_guide",
           "tiktok_made_me_buy_it", "before_after", "price_roundup"]


def first_of_next_month():
    today = datetime.date.today()
    return (today.replace(day=1) + datetime.timedelta(days=32)).replace(day=1)


def plan_month(month=None, perf=None, pins_per_day=8):
    month = month or first_of_next_month()
    ndays = (month.replace(month=month.month % 12 + 1, day=1) - month).days
    perf = perf or {}
    # rank niches by prior score; fall back to playbook order
    ranked = sorted(NICHE_BOARD, key=lambda n: -perf.get(n, 0))
    plan = []
    for d in range(ndays):
        date = month + datetime.timedelta(days=d)
        for k in range(pins_per_day):
            niche = ranked[(d * 7 + k) % len(ranked)]
            fmt = FORMATS[(d + k) % len(FORMATS)]
            plan.append({
                "date": date.isoformat(),
                "niche": niche,
                "board": NICHE_BOARD[niche],
                "format": fmt,
                "slug": f"{niche}_{fmt}_{d}_{k}",
            })
    return plan


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--month", help="YYYY-MM (default: next month)")
    ap.add_argument("--ppd", type=int, default=8, help="pins per day")
    ap.add_argument("--out", default="plan.json")
    args = ap.parse_args()
    m = datetime.date.fromisoformat(args.month + "-01") if args.month else None
    plan = plan_month(m, pins_per_day=args.ppd)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), args.out)
    json.dump(plan, open(out, "w"), indent=2)
    print(f"Planned {len(plan)} pins for "
          f"{plan[0]['date'][:7] if plan else '?'}. Ramp from 3-5/day, scale to {args.ppd}.")


if __name__ == "__main__":
    main()
