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

import amazon_link
import niches
import pin_spec

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
class Foreman:
    def __init__(self, board_id=None):
        self.board_id = board_id

    def run(self):
        results = []
        for product in niches.SEED_PRODUCTS:
            fmt = Researcher.pick(product)
            link = Matcher.link(product)
            title = fmt["title_tmpl"].format(
                n=5, price=25, problem="clutter", season="Holiday", seasonlower="holiday",
                product=product["name"], niche=product["niche"])
            description = fmt["desc_tmpl"].format(
                n=5, price=25, problem="clutter", season="Holiday", seasonlower="holiday",
                product=product["name"], niche=product["niche"])
            body = pin_spec.build_pin_body(title, description, link)
            image_path = Designer.design(product, title)
            payload = {**body, "image_path": image_path, "niche": product["niche"],
                       "format": fmt["format"], "affiliate_tag": "lexxdigital03-20"}
            status = Publisher.publish(payload, self.board_id)
            results.append({"title": title, "link": link, "status": status})
        return results


if __name__ == "__main__":
    out = Foreman(board_id=None).run()
    for r in out:
        print("TITLE :", r["title"])
        print("LINK  :", r["link"])
        print("STATUS:", r["status"])
        print("-" * 60)
    print("Staged queue ->", QUEUE_FILE)
