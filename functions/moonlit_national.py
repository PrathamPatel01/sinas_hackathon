"""Sinas function: default/moonlit_national

Surfaces relevant Dutch national guidance (AP / ACM / human-rights) for the classified
AI profile, from the live Moonlit Legal Research API. Gives the in-Sinas copilot the same
national-law grounding as the demo runner (scripts/moonlit.py national_context).

Shared-pool function: reads the Moonlit key from context['secrets']['MOONLIT_KEY'].
National searches use Dutch (the corpus is Dutch-language).
"""
import json
import os
import urllib.request

BASE = "https://api.moonlit.ai/v1.1"
NL_PORTALS = ["1|autoriteitpersoonsgegevens.nl", "1|acm.nl", "1|oordelen.mensenrechten.nl"]
PORTAL_AUTHORITY = {
    "autoriteitpersoonsgegevens.nl": "Autoriteit Persoonsgegevens (Dutch DPA)",
    "acm.nl": "ACM (Netherlands — national AI Act authority)",
    "oordelen.mensenrechten.nl": "Netherlands Institute for Human Rights",
}
NL_QUERIES = {
    "employment": "kunstmatige intelligentie werving en selectie van sollicitanten geautomatiseerde besluitvorming betekenisvolle menselijke tussenkomst",
    "essential": "geautomatiseerde besluitvorming kredietwaardigheid verzekering algoritme persoonsgegevens",
    "education": "kunstmatige intelligentie in het onderwijs proctoring toezicht studenten algoritme",
    "transparency": "chatbot transparantie geautomatiseerde verwerking persoonsgegevens informeren",
    "general": "AI en algoritmes betekenisvolle menselijke tussenkomst toezicht persoonsgegevens",
}


def _themes(surfaces):
    themes = set()
    for s in surfaces:
        cat = (s.get("annex_iii_category") or "").lower()
        tier = s.get("risk_tier")
        if "employ" in cat or "§4" in cat or "point 4" in cat:
            themes.add("employment")
        elif "essential" in cat or "§5" in cat or "point 5" in cat:
            themes.add("essential")
        elif "educat" in cat or "§3" in cat or "point 3" in cat:
            themes.add("education")
        elif tier == "limited":
            themes.add("transparency")
    return themes or {"general"}


def handler(input_data, context):
    secrets = context.get("secrets") or {} if isinstance(context, dict) else {}
    key = secrets.get("MOONLIT_KEY") or input_data.get("key") or os.environ.get("MOONLIT_KEY", "")
    surfaces = input_data.get("surfaces", [])
    if not key:
        return {"national": [], "error": "no Moonlit key"}
    seen, out = set(), []
    for theme in _themes(surfaces):
        try:
            req = urllib.request.Request(
                f"{BASE}/search/hybrid_search_reranked",
                data=json.dumps({"query": NL_QUERIES[theme], "portals": NL_PORTALS, "num_results": 3}).encode(),
                method="POST")
            req.add_header("Ocp-Apim-Subscription-Key", key)
            req.add_header("Content-Type", "application/json")
            with urllib.request.urlopen(req, timeout=25) as r:
                results = json.loads(r.read().decode()).get("result", {}).get("results", [])
        except Exception:
            results = []
        for x in results:
            ident = x.get("identifier")
            if not ident or ident in seen:
                continue
            seen.add(ident)
            portal = x.get("portal", "")
            out.append({
                "title": x.get("title", ""),
                "authority": PORTAL_AUTHORITY.get(portal, portal),
                "year": x.get("year"),
                "url": x.get("sourceUrl") or f"https://app.moonlit.ai/document/{ident}/read",
                "theme": theme,
            })
    return {"national": out[:5]}
