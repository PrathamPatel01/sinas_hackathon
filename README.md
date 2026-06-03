# AI Act Co-Pilot

A multi-agent compliance assistant for Dutch SMEs, built on the [Sinas](https://sinas.co) platform.

It inventories every AI tool a company uses, classifies each one against the **EU AI Act** (Annex III risk tiers), and generates a ready-to-adopt **compliance pack** — AI system inventory, risk classification with citations, an Article 4 staff-literacy plan, and a human-oversight & logging policy — in about 75 seconds.

Every legal claim is **grounded in verbatim source text** — the EU AI Act *and* Dutch national guidance (AP / ACM) — fetched live from the [Moonlit Legal Research](https://moonlit.ai) API, with clickable citation popups. A built-in **Q&A chat** answers follow-up questions, searching Moonlit on demand.

> Built for the **2 August 2026** deadline that most Dutch SMEs are currently unprepared for. Turns a €25k consulting scope into a free, instant, citeable artifact.

---

## The problem

- **Article 4** (AI literacy obligation for all staff) has been in force since **2 February 2025**.
- **Annex III high-risk obligations** become enforceable on **2 August 2026** — weeks after this hackathon.
- A typical 20–200-person Dutch SME runs 10–15 AI features across its stack (ChatGPT seats, Copilot, Notion AI, a CV-screening tool, a website chatbot, HubSpot AI…) and has **no inventory, no risk classification, no policy, and no training plan.**

The demo moment: the agent flags the company's **CV-screening tool as high-risk under Annex III §4 (employment)**, cites the article, and immediately drafts the human-oversight policy for that exact tool.

---

## Architecture (on Sinas)

Everything is deployed in the `default` namespace. The pipeline runs in three phases:
**classify → ground in law (EU + NL) → draft → assemble.**

```
 company description
        │
        ▼
 ① default/classifier ─────────────► AI surfaces + risk tiers + Annex III citations
        │
        ▼                          (run in parallel — legal grounding)
 ② default/moonlit_evidence (fn) ─► verbatim EU AI Act passages          ┐ live, via the
    default/moonlit_national (fn) ─► Dutch AP / ACM / human-rights guidance ┘ Moonlit REST API
        │
        ▼                          (run in parallel — drafting, using the Dutch guidance)
 ③ default/policy-drafter ────────► Human Oversight & Logging Policy  (cites EU + NL law)
    default/training-architect ───► Article 4 AI-literacy plan
        │
        ▼
 ④ default/generate_pack (fn) ────► assembled compliance pack (rendered markdown)

 Q&A chat (no pipeline re-run):
    default/aiact_qa ──(default/moonlit connector → search)──► live Moonlit legal search
```

| Resource | Role |
|----------|------|
| `default/copilot` | In-Sinas orchestrator — runs the full pipeline end-to-end (used for the agent-orchestration story; the UI/CLI drive the same agents client-side for speed). |
| `default/classifier` | Classifies each AI surface → risk tier + Annex III category + obligations + citations. |
| `default/moonlit_evidence` (function) | Grounds each citation in **verbatim EU AI Act text** from the live Moonlit API. Shared-pool; reads the `MOONLIT_KEY` secret. |
| `default/moonlit_national` (function) | Fetches relevant **Dutch national guidance** (AP / ACM) from Moonlit, fed into the drafters. |
| `default/policy-drafter` | Drafts the human-oversight & logging policy, citing the applicable EU + NL provisions. |
| `default/training-architect` | Generates the Article 4 literacy plan: roles × scenarios × briefs. |
| `default/generate_pack` (function) | Assembles the final pack (inventory, classification w/ verbatim passages, checklist, policy, training, NL context). |
| `default/aiact_qa` | **Q&A chat assistant** — answers follow-up questions; searches Moonlit itself via the connector. No pipeline re-run. |
| `default/moonlit` (connector) | First-class Sinas HTTP connector to the Moonlit Legal Research API (`search`); auth via the `MOONLIT_KEY` secret. |
| `default/packs` (collection) | Generated compliance packs. |
| `MOONLIT_KEY` (secret) | Moonlit REST subscription key, encrypted at rest. |

**Skills** (`skills/`) are the curated EU AI Act decision knowledge, preloaded into the agents.
**Legal grounding is live** — verbatim EU AI Act text and Dutch AP/ACM guidance are fetched from
[Moonlit](https://moonlit.ai) at runtime (via functions in the pipeline, and via the connector in chat),
not from static text.

---

## Repo layout

```
.
├── config/                  # Declarative Sinas resources (YAML), deployed via per-resource API
│   ├── 00-stores.yaml       # packs collection
│   ├── 05-secrets.yaml      # MOONLIT_KEY secret (value from .env)
│   ├── 10-skills.yaml       # curated decision knowledge (preloaded into agents)
│   ├── 15-connectors.yaml   # default/moonlit connector (Moonlit REST API, auth via secret)
│   ├── 20-functions.yaml    # function defs (code injected from functions/)
│   ├── 30-agents.yaml       # classifier, policy/training drafters, copilot, aiact_qa (chat)
│   └── 40-evidence.yaml     # original-source corpus skills
├── functions/               # Python handler(input_data, context) source
│   ├── moonlit_evidence.py  # verbatim EU AI Act passages per citation (shared-pool, reads secret)
│   ├── moonlit_national.py  # Dutch AP/ACM national guidance (shared-pool, reads secret)
│   ├── generate_pack.py     # assembles the final compliance pack (pure render)
│   └── save_inventory.py / get_inventory.py
├── skills/                  # Decision knowledge (risk tiers, Annex III, Article 4, …)
├── corpus/                  # Source-text excerpts (legacy/fallback)
├── scripts/
│   ├── build_config.py      # assembles config/*.yaml + injects code + interpolates .env → dist/config.yaml
│   ├── deploy_resources.py  # upserts every resource to Sinas (secrets, skills, connectors, functions, agents)
│   ├── moonlit.py           # Moonlit REST client — verbatim EU passages, Dutch context, Q&A search
│   ├── demo.py              # fast CLI runner → writes demo_pack.md (~75s)
│   └── server.py            # live demo UI server (SSE pipeline visualizer + /ask chat endpoint)
├── web/index.html           # interactive UI: live agents, per-agent inspection, inline citation popups, Q&A chat
├── .env.example
└── README.md
```

---

## Run it

**Prerequisites:** Python 3 (stdlib only — no pip installs). Internet access to your Sinas
instance, `api.moonlit.ai`, and the `marked` CDN (for the UI).

**1. Configure** — copy the env template and fill in your credentials:
```bash
cp .env.example .env
#   SINAS_URL    = https://your-team.sinas.wearebrain.com
#   SINAS_TOKEN  = API key from the Sinas console (needs full permissions to deploy)
#   MOONLIT_KEY  = Moonlit Legal Research REST subscription key
```

**2. Deploy** all resources to your Sinas instance (idempotent — safe to re-run):
```bash
python3 scripts/build_config.py        # assemble config/*.yaml → dist/config.yaml
python3 scripts/deploy_resources.py    # upsert secrets, skills, connectors, functions, agents
```

**3a. Launch the interactive demo UI** (recommended for the pitch):
```bash
python3 scripts/server.py              # → http://localhost:8800
```
- Type a company (or pick an example) → **Run pipeline** → watch the agents work across the three
  phases, click any node/tab to inspect its output.
- **Hover/click any citation** for the verbatim source text — **EU AI Act** (blue) and **Dutch AP/ACM
  guidance** (amber 🇳🇱), straight from Moonlit.
- **Follow-up** box to re-assess when the company adds a tool (new surfaces get a `✦ NEW` badge).
- **💬 Ask about this pack** chat (bottom-right): the `aiact_qa` agent answers follow-up questions,
  searching Moonlit live via the `default/moonlit` connector — no full pipeline re-run.
- Export the pack via **⬇ Markdown** / **🖨 PDF**.

**3b. Or the fast CLI runner** (writes `demo_pack.md`, ~70s):
```bash
python3 scripts/demo.py "We are a 40-person Dutch fintech using an AI credit-scoring model, a support chatbot, and Copilot."
```

**3c. Or invoke the live Sinas copilot directly** (full agent orchestration, ~4 min):
```bash
curl -X POST "$SINAS_URL/agents/default/copilot/invoke" \
  -H "Authorization: Bearer $SINAS_TOKEN" -H "Content-Type: application/json" \
  -d '{"message": "We are a 60-person Amsterdam recruitment agency using HireScan to screen applicants, a website chatbot, and ChatGPT Team."}'
```

> The UI and CLI runner drive the Sinas specialist agents client-side (running the independent
> ones in parallel) for speed; the `copilot` agent is the same pipeline orchestrated end-to-end
> inside Sinas. All paths ground citations in **verbatim EU AI Act text and Dutch AP/ACM guidance
> via Moonlit** — in the pipeline through the `moonlit_evidence` / `moonlit_national` functions,
> and in the chat through the `default/moonlit` connector.

---

## ⚠️ Disclaimer

This tool produces **draft** compliance artifacts to accelerate review, not legal advice. Every classification cites its source and is flagged for human sign-off. Verify against the consolidated EU AI Act text (Regulation (EU) 2024/1689) and current guidance before adoption. Human-in-the-loop is a feature, not a gap.
