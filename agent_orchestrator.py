"""
Pinterest -> Amazon affiliate pin pipeline.

FOREMAN coordinates 5 child agents. Each is a focused unit:
  Researcher  - picks the content angle/format that performs on Pinterest
  Matcher     - pairs the angle with a curated Amazon product + builds the affiliate link
  Designer    - produces the 2:3 pin image (Hermes supplies image_generate; headless fallback = PIL)
  Publisher   - posts to Pinterest (MCP / REST) once the app is approved; else stages to queue
  Analyst     - pulls pin analytics later to see which niches "cell", feeds Researcher

Run:  python agent_orchestrator.py
This builds the campaign (links + staged payloads) end-to-end. Posting is
gated on the approved Pinterest app + token; until then pins land in queue/.
"""
import os
import json
import base64
import datetime
import random

import amazon_link
import niches
import products
import pin_spec
import image_gen

QUEUE_DIR = os.path.join(os.path.dirname(__file__), "queue")
QUEUE_FILE = os.path.join(QUEUE_DIR, "staged_pins.json")


# ---------- child agents (each a pure function / class) ----------
class Researcher:
    """Selects a content format for a product/niche."""
    @staticmethod
    def pick(product):
        # Simple deterministic mapping; a delegate_task LLM child can replace this.
        fmt = niches.CONTENT_FORMATS[hash(product["niche"]) % len(niches.CONTENT_FORMATS)]
        return fmt


class Matcher:
    """Builds the affiliate link for a product."""
    @staticmethod
    def link(product):
        return amazon_link.build_affiliate_link(product["asin"])


class Designer:
    """Produces the pin image. Hermes sets `make_image` to image_generate (FLUX).
    Headless fallback returns a marker so the pipeline still stages."""
    make_image = None  # callable(niche, title) -> local image path

    @classmethod
    def design(cls, product, title):
        if cls.make_image:
            return cls.make_image(product["niche"], title)
        return "PENDING_DESIGN"


class Publisher:
    """Posts to Pinterest if a token + board exist; otherwise stages."""
    @staticmethod
    def publish(payload, board_id=None):
        if board_id:
            from pinterest_client import PinterestClient
            c = PinterestClient()
            img = payload.pop("image_path", None)
            if img and os.path.exists(img):
                with open(img, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode()
                return c.create_pin(board_id, payload["title"], payload["description"],
                                    payload["link"], b64)
            return {"error": "no image to post yet"}
        # stage
        os.makedirs(QUEUE_DIR, exist_ok=True)
        staged = []
        if os.path.exists(QUEUE_FILE):
            staged = json.load(open(QUEUE_FILE))
        staged.append({**payload, "staged_at": datetime.datetime.utcnow().isoformat() + "Z"})
        json.dump(staged, open(QUEUE_FILE, "w"), indent=2)
        return {"staged": True, "queue": QUEUE_FILE}


class Analyst:
    """Later: pull analytics for a pin id to measure 'cells'."""
    @staticmethod
    def measure(pin_id):
        from pinterest_client import PinterestClient
        return PinterestClient().get_pin_analytics(pin_id)


# ---------- foreman ----------
HERE = os.path.dirname(os.path.abspath(__file__))

class Foreman:
    def __init__(self, board_id=None):
        self.board_id = board_id

    def build_campaign(self, plan, perf=None):
        """plan: list of {date,niche,board,format,slug} from monthly_planner.
        Returns Sheet-ready pin dicts using the expanded product pool + per-combo image."""
        perf = perf or {}
        pins = []
        pool_idx = {}
        for row in plan:
            niche, fmt, slug = row["niche"], row["format"], row["slug"]
            pool = products.SEED_PRODUCTS.get(niche, [])
            if not pool:
                continue
            i = pool_idx.get(niche, 0) % len(pool)
            pool_idx[niche] = i + 1
            asin, name = pool[i]
            tmpl = next(c for c in niches.CONTENT_FORMATS if c["format"] == fmt)
            link = amazon_link.build_affiliate_link(asin)
            ctx = dict(n=5, price=25, problem="clutter", season="Holiday",
                       seasonlower="holiday", product=name, niche=niche.replace("_", " "))
            title = tmpl["title_tmpl"].format(**ctx)
            description = tmpl["desc_tmpl"].format(**ctx)
            img = image_gen.image_path(niche, fmt)
            slug = image_gen.slug_for(niche, fmt)
            # Use rendered URL if present in manifest, else the demo placeholder host.
            m = json.load(open(os.path.join(HERE, "manifest.json"))) if os.path.exists(
                os.path.join(HERE, "manifest.json")) else {}
            media = m.get(slug) or ("https://lexxautomates.github.io/pinterest-pins/images/demo_pin.png")
            pins.append({
                "title": title, "description": description, "link": link,
                "board": row["board"], "keywords": f"{niche},amazonfinds,musthaves,shopping",
                "media_url": media, "slug": slug, "niche": niche, "format": fmt,
                "publish_date": row["date"],
            })
        return pins

    def run(self, plan=None, perf=None, board_id=None):
        board_id = board_id or self.board_id
        if plan is None:
            plan = json.load(open(os.path.join(os.path.dirname(__file__), "plan.json")))
        pins = self.build_campaign(plan, perf)
        results = []
        for p in pins:
            body = pin_spec.build_pin_body(p["title"], p["description"], p["link"])
            payload = {**body, "image_path": image_gen.image_path(p["niche"], p["format"]),
                       "niche": p["niche"], "format": p["format"],
                       "affiliate_tag": "lexxdigital03-20"}
            status = Publisher.publish(payload, board_id)
            results.append({"title": p["title"], "link": p["link"], "status": status})
        return results


if __name__ == "__main__":
    import sys
    plan = json.load(open(os.path.join(os.path.dirname(__file__), "plan.json")))
    perf = json.load(open(sys.argv[1])).get("perf") if len(sys.argv) > 1 and os.path.exists(sys.argv[1]) else None
    out = Foreman(board_id=None).run(plan, perf)
    for r in out:
        print("TITLE :", r["title"])
        print("LINK  :", r["link"])
        print("STATUS:", r["status"])
        print("-" * 60)
    print("Staged queue ->", QUEUE_FILE)
