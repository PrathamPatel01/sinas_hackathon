#!/usr/bin/env python3
"""AI Act Co-Pilot — demo runner.

Drives the Sinas specialist agents and renders a complete, full-length compliance
pack to a Markdown file. Designed for a live demo / pitch:

  - Calls the real Sinas agents (classifier, evidence, policy-drafter, training-architect).
  - Runs the three independent specialists TRULY in parallel (separate top-level
    requests run concurrently on the worker pool — far faster than the in-agent
    orchestrator, which Sinas executes serially).
  - Each agent is a clean single-turn invoke: fast, untruncated, and free of the
    in-pipeline skill-as-tool compaction issue.
  - Renders the pack with the SAME logic as the Sinas generate_pack function
    (functions/generate_pack.py) — single source of truth.

Usage:
  python3 scripts/demo.py                      # built-in Amsterdam-recruiter demo
  python3 scripts/demo.py "We are a 40-person fintech using a credit-scoring model and a support chatbot."
"""
import json
import os
import re
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "functions"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from generate_pack import _render_pack  # noqa: E402  (reuse the real renderer)
import moonlit  # noqa: E402  (live Moonlit Legal Research grounding)

DEMO = ("We are a 60-person Amsterdam recruitment agency. We use ChatGPT Team for internal "
        "drafting, a CV-screening tool called HireScan that ranks job applicants, a website "
        "chatbot for customer questions, and HubSpot AI for marketing emails.")


def load_dotenv():
    p = os.path.join(ROOT, ".env")
    if os.path.exists(p):
        for line in open(p):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def invoke(agent, message):
    base = os.environ["SINAS_URL"].rstrip("/")
    token = os.environ["SINAS_TOKEN"]
    body = json.dumps({"message": message}).encode()
    req = urllib.request.Request(f"{base}/agents/default/{agent}/invoke", data=body, method="POST")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.loads(r.read().decode()).get("reply", "")


def parse_json(reply):
    """Pull a JSON object out of an agent reply (handles ```json fences / prose)."""
    if not reply:
        return {}
    m = re.search(r"```(?:json)?\s*(\{.*\})\s*```", reply, re.S)
    blob = m.group(1) if m else reply
    if not m:
        i, j = blob.find("{"), blob.rfind("}")
        if i != -1 and j != -1:
            blob = blob[i:j + 1]
    try:
        return json.loads(blob)
    except Exception:
        return {}


def extract_field(reply, field):
    """Robustly pull a markdown string field out of an agent reply, even when the
    surrounding JSON is malformed (e.g. literal newlines inside the value, which
    breaks json.loads). Falls back to the cleaned reply if the field isn't found."""
    if not reply:
        return ""
    obj = parse_json(reply)
    if isinstance(obj, dict) and obj.get(field):
        return obj[field]
    # Tolerant regex: capture from the opening quote to the last quote before the final }.
    m = re.search(r'"' + re.escape(field) + r'"\s*:\s*"', reply)
    if m:
        rest = reply[m.end():]
        end = rest.rfind('"')
        if end > 0:
            val = rest[:end]
            for a, b in (("\\n", "\n"), ("\\t", "\t"), ('\\"', '"'), ("\\\\", "\\"), ("\\/", "/")):
                val = val.replace(a, b)
            return val
    # Last resort: strip code fences and return the reply as-is.
    return re.sub(r"^```(?:json|markdown)?\s*|\s*```$", "", reply.strip())


def main():
    load_dotenv()
    message = sys.argv[1] if len(sys.argv) > 1 else DEMO
    t0 = time.time()

    print("⚙  1/3  classifier — inventorying & classifying AI surfaces …")
    cls = parse_json(invoke("classifier", f"Surfaces from this company description — classify each:\n{message}"))
    surfaces = cls.get("surfaces", [])
    if not surfaces:
        sys.exit("classifier returned no surfaces; reply was not parseable.")
    citations = sorted({c for s in surfaces for c in s.get("citations", [])})
    # Derive a readable company label from the description.
    m_size = re.search(r"(\d+)[\s-]*(?:person|employee|staff|people)", message, re.I)
    m_name = re.search(r"[Ww]e(?:'re| are)\s+an?\s+([^.,;]+)", message)
    company = {
        "name": (m_name.group(1).strip().title() if m_name else "the company"),
        "size": (f"{m_size.group(1)} staff" if m_size else ""),
        "sector": "",
    }
    print(f"     → {len(surfaces)} surfaces, {sum(1 for s in surfaces if s.get('risk_tier')=='high')} high-risk")

    surfaces_json = json.dumps(surfaces)
    key = moonlit._key()
    print("⚙  2/3  legal grounding — Moonlit evidence (EU) + Dutch law (AP/ACM) in PARALLEL …")
    with ThreadPoolExecutor(max_workers=2) as ex:
        f_ev = ex.submit(moonlit.evidence_for, citations, key)        # verbatim EU AI Act text
        f_nat = ex.submit(moonlit.national_context, surfaces, key)    # Dutch AP/ACM guidance
        evidence = f_ev.result()
        national = f_nat.result()
    grounded = sum(1 for e in evidence if e.get("passage"))
    print(f"     → {grounded}/{len(evidence)} EU citations grounded; {len(national)} Dutch (AP/ACM) sources")

    nat_lines = "\n".join(f"  [{d['tag']}] {d['authority']} ({d.get('year')}): {d['title']}" for d in national) or "  (none found)"
    nat_note = ("\n\nApplicable Dutch national guidance (Netherlands). Where one of these is relevant to a "
                "specific control or obligation, cite it INLINE using its EXACT bracketed tag — e.g. "
                "'…meaningful human intervention is required [NL-1]'. Use the tags verbatim. Sources:\n" + nat_lines)
    print("⚙  3/4  policy-drafter + training-architect — using the classification AND Dutch guidance …")
    with ThreadPoolExecutor(max_workers=2) as ex:
        f_pol = ex.submit(invoke, "policy-drafter", f"Company: {message}\nClassified surfaces: {surfaces_json}{nat_note}")
        f_tr = ex.submit(invoke, "training-architect", f"Company: {message}\nClassified surfaces: {surfaces_json}{nat_note}")
        policy_md = extract_field(f_pol.result(), "policy_markdown")
        training_md = extract_field(f_tr.result(), "training_markdown")

    print("⚙  4/4  rendering compliance pack …")
    pack = _render_pack(company, surfaces, policy_md, training_md, evidence, national)
    out = os.path.join(ROOT, "demo_pack.md")
    open(out, "w").write(pack)

    counts = {t: sum(1 for s in surfaces if s.get("risk_tier") == t) for t in ("prohibited", "high", "limited", "minimal")}
    print(f"\n✅ Done in {time.time()-t0:.0f}s — {len(pack):,} char pack → {out}")
    print(f"   Tiers: {counts['prohibited']} prohibited · {counts['high']} high · "
          f"{counts['limited']} limited · {counts['minimal']} minimal")
    print(f"   Evidence passages: {sum(1 for e in evidence if e.get('passage'))}/{len(evidence)} citations grounded")


if __name__ == "__main__":
    main()
