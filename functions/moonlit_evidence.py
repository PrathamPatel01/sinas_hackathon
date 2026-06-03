"""Sinas function: default/moonlit_evidence

Grounds EU AI Act citations in verbatim Official-Journal text from the live
Moonlit Legal Research API (https://api.moonlit.ai/v1.1). Given a list of citation
references, returns the exact source passage for each plus a clickable Moonlit link.

Runs in a Sinas function container (outbound internet verified). The full AI Act is
fetched once and cached in /tmp for warm-container reuse. The Moonlit subscription
key is supplied via the calling agent's function_parameters (locked from the LLM).

Mirrors scripts/moonlit.py (the demo-runner client) so the live copilot and the demo
produce identical grounding.
"""
import json
import os
import re
import urllib.request

AI_ACT = "32024R1689"
BASE = "https://api.moonlit.ai/v1.1"
DOC_URL = f"https://app.moonlit.ai/document/{AI_ACT}/read"
CACHE = "/tmp/ai-act-full.md"


def _fetch_full_text(key):
    if os.path.exists(CACHE) and os.path.getsize(CACHE) > 100_000:
        return open(CACHE).read()
    req = urllib.request.Request(
        f"{BASE}/document/retrieve_document?DocumentIdentifier={AI_ACT}&markdown=true")
    req.add_header("Ocp-Apim-Subscription-Key", key)
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.loads(r.read().decode())
    res = data.get("result", data)
    md = (res.get("markdown") or res.get("text") or "") if isinstance(res, dict) else str(res)
    try:
        open(CACHE, "w").write(md)
    except Exception:  # noqa: BLE001 — cache is best-effort
        pass
    return md


def _trim(text, limit=700):
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    cut = text[:limit]
    last = max(cut.rfind(". "), cut.rfind("; "))
    return (cut[:last + 1] if last > 200 else cut).strip() + " […]"


def _parse(md):
    arts = {}
    matches = list(re.finditer(r"(?m)^Article\s+(\d+)\b", md))
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(md)
        arts[int(m.group(1))] = md[m.start():end]
    annex = ""
    am = re.search(r"(?m)^ANNEX\s+III\b", md)
    if am:
        nxt = re.search(r"(?m)^ANNEX\s+IV\b", md[am.start():])
        annex = md[am.start(): am.start() + (nxt.start() if nxt else 4000)]
    return arts, annex


def handler(input_data, context):
    # Prefer the Sinas secret (shared-pool functions get it via context['secrets']),
    # then an explicit input key, then an env var — defensive across deploy modes.
    secrets = context.get("secrets") or {} if isinstance(context, dict) else {}
    key = secrets.get("MOONLIT_KEY") or input_data.get("key") or os.environ.get("MOONLIT_KEY", "")
    citations = input_data.get("citations", [])
    if not key:
        return {"evidence": [], "error": "no Moonlit key provided"}
    try:
        md = _fetch_full_text(key)
    except Exception as e:  # noqa: BLE001
        return {"evidence": [], "error": f"moonlit fetch failed: {e!r}"[:200]}
    arts, annex = _parse(md)
    anchors = {"3": "Education", "4": "Employment", "5": "essential private",
               "1": "Biometrics", "2": "Critical infrastructure"}
    out, seen = [], set()
    for c in citations:
        if c in seen:
            continue
        seen.add(c)
        passage = None
        if re.search(r"annex\s+iii", c, re.I):
            tail = c.split("III", 1)[-1]
            pt = re.search(r"([0-9])", tail)
            anchor = anchors.get(pt.group(1) if pt else "", "")
            if anchor:
                seg = re.search(re.escape(anchor) + r".*?(?=\n\s*\|\s*\d+\.|\Z)", annex, re.S | re.I)
                passage = _trim(seg.group(0)) if seg else _trim(annex)
            else:
                passage = _trim(annex)
        else:
            m_art = re.search(r"article\s+(\d+)", c, re.I)
            if m_art and int(m_art.group(1)) in arts:
                passage = _trim(arts[int(m_art.group(1))])
        out.append({"reference": c, "passage": passage, "url": DOC_URL, "in_source": bool(passage)})
    grounded = sum(1 for e in out if e["passage"])
    return {"evidence": out, "grounded": grounded, "total": len(out)}
