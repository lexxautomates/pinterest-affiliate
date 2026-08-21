"""Amazon Associates affiliate link builder.

The only programmatic part of the Amazon side: take any Amazon product URL
(or bare ASIN) and append the associate tag. PA-API/Creators API product
lookup is gated (needs >=10 sales/30d), so product sourcing is a curated list.
"""
import re
import urllib.parse as up

DEFAULT_TAG = "lexxdigital03-20"


def build_affiliate_link(url_or_asin, tag=DEFAULT_TAG):
    """Return an Amazon URL with the associate `tag` set (overwriting any existing)."""
    tag = (tag or "").strip()
    if not tag:
        raise ValueError("associate tag required")
    s = (url_or_asin or "").strip()
    if not s:
        raise ValueError("url_or_asin required")

    is_asin = bool(re.fullmatch(r"[A-Z0-9]{10}", s, re.I))
    if is_asin:
        asin = s.upper()
        scheme, netloc, path, query = "https", "www.amazon.com", f"/dp/{asin}", ""
    else:
        p = up.urlparse(s)
        scheme = p.scheme or "https"
        netloc = p.netloc or "www.amazon.com"
        path = p.path or "/"
        query = p.query

    q = up.parse_qs(query, keep_blank_values=True)
    q["tag"] = [tag]  # overwrite any prior tag to avoid double-tagging
    new_query = up.urlencode(q, doseq=True)
    return up.urlunparse((scheme, netloc, path, "", new_query, ""))


if __name__ == "__main__":
    tests = [
        "B0EXAMPLE12",
        "https://www.amazon.com/dp/B0EXAMPLE12",
        "https://www.amazon.com/dp/B0EXAMPLE12/?ref=foo",
        "https://www.amazon.com/Example-Product/dp/B0EXAMPLE12/",
        "https://www.amazon.com/dp/B0EXAMPLE12?tag=OLDID-20",
    ]
    for t in tests:
        print(f"{t}\n  -> {build_affiliate_link(t)}\n")
