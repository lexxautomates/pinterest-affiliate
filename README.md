# pinterest-affiliate — Pinterest → Amazon Associates pin pipeline

Automates: **niche/content research → Amazon affiliate link → pin creative → post → measure ("cells")**.

## Architecture (Foreman + child agents)
| Agent | Job |
|-------|-----|
| **Foreman** (`agent_orchestrator.Foreman`) | schedules & coordinates the run |
| **Researcher** | picks the Pinterest-performing content format/angle for a niche |
| **Matcher** | pairs product → Amazon URL + `?tag=lexxdigital03-20` affiliate link |
| **Designer** | makes the 2:3 pin image (Hermes `image_generate`/FLUX; headless PIL fallback) |
| **Publisher** | posts via Pinterest MCP/REST when approved; else stages to `queue/` |
| **Analyst** | pulls pin analytics later to see which niches "cell", feeds Researcher |

## Run it
```bash
cd D:/repos/pinterest-affiliate
python agent_orchestrator.py          # builds links + stages payloads (no post until approved)
```

## Gates (honest)
1. **Amazon product lookup** — PA-API deprecated → Creators API needs ≥10 sales/30d. So fill `niches.SEED_PRODUCTS` with YOUR ASINs. The affiliate link itself is 100% programmatic.
2. **Pinterest posting** — app under review (sandbox). After approval: `node D:/repos/pinterest-mcp/auth.js` (one-time OAuth → `~/.pinterest-mcp/token.json`), set `board_id`, re-run. Fully hands-off via cron after that.
3. **Canva** — waitlist-gated; replaced by `image_generate` (FLUX) for the creative. No human step.

## Files
- `amazon_link.py` — affiliate link builder (verified)
- `niches.py` — content formats + seed products
- `pin_spec.py` — compliant Pin body builder
- `pinterest_client.py` — REST client (create pin + analytics)
- `agent_orchestrator.py` — Foreman + 5 child agents
