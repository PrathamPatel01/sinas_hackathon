"""Sinas function: default/generate_pack

Assemble the final compliance pack from the orchestrator's collected pieces:
  - company profile
  - classified AI-surface inventory (from default/classifier)
  - human-oversight & logging policy (from default/policy-drafter)
  - Article 4 training plan (from default/training-architect)

Renders a single Markdown document (plus a machine-readable summary), uploads it
to the `default/packs` collection, and returns a reference the agent can hand back.

Markdown is built with plain string composition — no template-engine dependency
needed inside the container.
"""

import datetime
import io
import json
import os
import urllib.request

DEADLINE = datetime.date(2026, 8, 2)  # Annex III high-risk + Art. 50 transparency
LITERACY_IN_FORCE = datetime.date(2025, 2, 2)  # Article 4 + Article 5

TIER_LABEL = {
    "prohibited": "🛑 PROHIBITED — must stop using",
    "high": "🔴 HIGH RISK (Annex III)",
    "limited": "🟡 LIMITED RISK (transparency)",
    "minimal": "🟢 MINIMAL RISK",
}
TIER_ORDER = {"prohibited": 0, "high": 1, "limited": 2, "minimal": 3}


def _api_base():
    return os.environ.get("SINAS_API_BASE", "http://host.docker.internal:8000")


def _days_to_deadline():
    return (DEADLINE - datetime.date.today()).days


def _render_inventory_table(surfaces):
    rows = ["| # | AI surface | Use | Tier | Annex III | Citations |",
            "|---|-----------|-----|------|-----------|-----------|"]
    for i, s in enumerate(sorted(surfaces, key=lambda x: TIER_ORDER.get(x.get("risk_tier"), 9)), 1):
        cites = "; ".join(s.get("citations", [])) or "—"
        rows.append(
            f"| {i} | {s.get('name','?')} | {s.get('use','')} | "
            f"{TIER_LABEL.get(s.get('risk_tier'), s.get('risk_tier','?'))} | "
            f"{s.get('annex_iii_category') or '—'} | {cites} |"
        )
    return "\n".join(rows)


def _evidence_map(evidence):
    """Map a citation reference -> (verbatim source passage, source url)."""
    out = {}
    for e in evidence or []:
        ref = (e.get("reference") or "").strip()
        passage = e.get("passage")
        if ref and passage and e.get("in_source", True):
            out[ref] = (passage, e.get("url"))
    return out


def _match_passage(citation, evmap):
    """Find a (passage, url) for a citation by exact or substring match."""
    if citation in evmap:
        return evmap[citation]
    for ref, val in evmap.items():
        if ref in citation or citation in ref:
            return val
    return (None, None)


def _render_classification_detail(surfaces, evmap):
    blocks = []
    for s in sorted(surfaces, key=lambda x: TIER_ORDER.get(x.get("risk_tier"), 9)):
        ob = "\n".join(f"  - {o}" for o in s.get("obligations", [])) or "  - (none)"
        exemption = s.get("article_6_3_exemption")
        ex_line = f"\n- **Article 6(3) exemption claimed:** {exemption}" if exemption else ""
        cites = s.get("citations", [])
        # Verbatim source passages backing each cited provision.
        ev_lines = []
        for c in cites:
            p, url = _match_passage(c, evmap)
            if p:
                src = f"[{c}]({url})" if url else c
                ev_lines.append(f"  > *\"{p}\"* — {src}")
        ev_block = ("\n- **Verbatim source passages (EU AI Act, via Moonlit):**\n" + "\n".join(ev_lines)) if ev_lines else ""
        blocks.append(
            f"### {s.get('name','?')} — {TIER_LABEL.get(s.get('risk_tier'), '?')}\n"
            f"- **Use:** {s.get('use','')}\n"
            f"- **Annex III category:** {s.get('annex_iii_category') or '—'}{ex_line}\n"
            f"- **Why:** {s.get('justification','')}\n"
            f"- **Citations:** {'; '.join(cites) or '—'}{ev_block}\n"
            f"- **Obligations for this company:**\n{ob}\n"
        )
    return "\n".join(blocks)


def _render_action_checklist(surfaces):
    items = []
    if any(s.get("risk_tier") == "prohibited" for s in surfaces):
        items.append("- [ ] **Decommission prohibited systems immediately** (already banned since 2 Feb 2025).")
    items.append("- [ ] Adopt the Human Oversight & Logging Policy below; assign a named AI accountable owner.")
    if any(s.get("risk_tier") == "high" for s in surfaces):
        items.append("- [ ] For each high-risk surface: name a human overseer, enable logging, set review cadence.")
        items.append("- [ ] Inform workers/representatives before any high-risk system is used at work.")
        items.append("- [ ] Confirm vendor provides instructions for use + technical documentation for high-risk tools.")
    if any(s.get("risk_tier") == "limited" for s in surfaces):
        items.append("- [ ] Add AI-disclosure to chatbots; label AI-generated/synthetic content.")
    items.append("- [ ] Roll out the Article 4 AI-literacy training (overdue since 2 Feb 2025).")
    items.append("- [ ] Maintain the AI system inventory; re-run this assessment when a tool is added.")
    return "\n".join(items)


def _render_national(national):
    if not national:
        return ""
    rows = []
    for d in national:
        title = d.get("title", "")
        url = d.get("url")
        yr = d.get("year") or ""
        auth = d.get("authority", "")
        link = f"[{title}]({url})" if url else title
        rows.append(f"- **{auth}**{f' ({yr})' if yr else ''} — {link}")
    return ("\n---\n\n## National context — Netherlands 🇳🇱\n\n"
            "Beyond the EU AI Act, Dutch supervisory guidance applies (the AP and ACM are the "
            "national authorities). Relevant current sources, retrieved live from Moonlit:\n\n"
            + "\n".join(rows) + "\n")


def _render_pack(company, surfaces, policy_md, training_md, evidence, national=None):
    name = company.get("name", "the company")
    size = company.get("size", "")
    sector = company.get("sector", "")
    today = datetime.date.today().isoformat()
    days = _days_to_deadline()
    counts = {t: sum(1 for s in surfaces if s.get("risk_tier") == t)
              for t in ("prohibited", "high", "limited", "minimal")}
    deadline_line = (
        f"**{days} days** until the 2 August 2026 high-risk deadline."
        if days >= 0 else
        "The 2 August 2026 high-risk deadline has **passed**."
    )

    return f"""# EU AI Act Compliance Pack — {name}

*Generated {today} by the AI Act Co-Pilot (Sinas). Draft for human review — not legal advice.*

**Profile:** {size} · {sector}
**Summary:** {len(surfaces)} AI surfaces — {counts['prohibited']} prohibited, {counts['high']} high-risk, {counts['limited']} limited-risk, {counts['minimal']} minimal-risk.
**Timeline:** Article 4 AI literacy & Article 5 prohibitions in force since 2 Feb 2025. {deadline_line}

---

## 1. AI System Inventory & Risk Classification

{_render_inventory_table(surfaces)}

---

## 2. Classification Detail (with citations & verbatim source passages)

{_render_classification_detail(surfaces, _evidence_map(evidence))}

---

## 3. Priority Action Checklist

{_render_action_checklist(surfaces)}

---

## 4. Human Oversight & Logging Policy (draft)

{policy_md or '_[policy-drafter output goes here]_'}

---

## 5. Article 4 AI-Literacy Plan (draft)

{training_md or '_[training-architect output goes here]_'}
{_render_national(national)}
---

## Disclaimer

This pack is a **draft** produced to accelerate compliance work. Every classification cites its
source and must be confirmed by a competent person against the consolidated text of Regulation
(EU) 2024/1689 and current guidance before adoption. Human sign-off is required.
"""


def _upload(token, namespace, collection, filename, content, metadata):
    """Multipart upload to the Sinas collection files endpoint."""
    boundary = "----defaultpackboundary7MA4YWxkTrZu0gW"
    parts = []
    parts.append(f"--{boundary}\r\n")
    parts.append(f'Content-Disposition: form-data; name="metadata"\r\n\r\n')
    parts.append(json.dumps(metadata) + "\r\n")
    parts.append(f"--{boundary}\r\n")
    parts.append(
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
    )
    parts.append("Content-Type: text/markdown\r\n\r\n")
    body = io.BytesIO()
    body.write("".join(parts).encode("utf-8"))
    body.write(content.encode("utf-8"))
    body.write(f"\r\n--{boundary}--\r\n".encode("utf-8"))
    data = body.getvalue()

    url = f"{_api_base()}/files/{namespace}/{collection}"
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def handler(input_data, context):
    company = input_data.get("company", {})
    surfaces = input_data.get("surfaces", [])
    policy_md = input_data.get("policy_markdown", "")
    training_md = input_data.get("training_markdown", "")
    evidence = input_data.get("evidence", [])
    national = input_data.get("national", [])
    session_key = input_data.get("session_key", "anon")

    pack_md = _render_pack(company, surfaces, policy_md, training_md, evidence, national)
    filename = f"ai-act-pack-{session_key}-{datetime.date.today().isoformat()}.md"

    # Pure render — no network upload. (The collection-upload path hung because the
    # function container cannot reach the files endpoint on this instance. Persistence,
    # if needed, is handled separately; the rendered pack is returned inline.)
    counts = {t: sum(1 for s in surfaces if s.get("risk_tier") == t)
              for t in ("prohibited", "high", "limited", "minimal")}
    return {
        "filename": filename,
        "days_to_deadline": _days_to_deadline(),
        "counts": counts,
        "pack_markdown": pack_md,
    }
