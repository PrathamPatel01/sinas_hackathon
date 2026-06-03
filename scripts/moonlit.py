#!/usr/bin/env python3
"""Moonlit Legal Research REST client — grounds AI Act citations in verbatim source text.

Fetches the full EU AI Act (CELEX 32024R1689) from the live Moonlit corpus
(https://api.moonlit.ai/v1.1) once, caches it, and extracts the precise verbatim
Official-Journal text for each cited provision (article or Annex III point), plus a
clickable Moonlit document link.

Deterministic article/annex extraction beats semantic search for "give me the exact
text of Article 26". Used by scripts/demo.py.
"""
import json
import os
import re
import urllib.request

AI_ACT = "32024R1689"
BASE = "https://api.moonlit.ai/v1.1"
DOC_URL = f"https://app.moonlit.ai/document/{AI_ACT}/read"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, ".cache", "ai-act-full.md")


def _fetch_full_text(key):
    if os.path.exists(CACHE) and os.path.getsize(CACHE) > 100_000:
        return open(CACHE).read()
    req = urllib.request.Request(
        f"{BASE}/document/retrieve_document?DocumentIdentifier={AI_ACT}&markdown=true")
    req.add_header("Ocp-Apim-Subscription-Key", key)
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.loads(r.read().decode())
    res = data.get("result", data)
    md = res.get("markdown") or res.get("text") if isinstance(res, dict) else str(res)
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    open(CACHE, "w").write(md)
    return md


def _trim(text, limit=600):
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    cut = text[:limit]
    last = max(cut.rfind(". "), cut.rfind("; "))
    return (cut[:last + 1] if last > 200 else cut).strip() + " […]"


def _parse(md):
    """Return ({article_no: text}, annexIII_text)."""
    arts = {}
    matches = list(re.finditer(r"(?m)^Article\s+(\d+)\b", md))
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(md)
        arts[int(m.group(1))] = md[m.start():end]
    # Annex III block
    annex = ""
    am = re.search(r"(?m)^ANNEX\s+III\b", md)
    if am:
        nxt = re.search(r"(?m)^ANNEX\s+IV\b", md[am.start():])
        annex = md[am.start(): am.start() + (nxt.start() if nxt else 4000)]
    return arts, annex


def evidence_for(citations, key):
    """Return [{reference, passage, url, in_source}] grounded in live Moonlit AI Act text."""
    md = _fetch_full_text(key)
    arts, annex = _parse(md)
    out, seen = [], set()
    for c in citations:
        if c in seen:
            continue
        seen.add(c)
        passage = None
        m_art = re.search(r"article\s+(\d+)", c, re.I)
        m_annex = re.search(r"annex\s+iii", c, re.I)
        if m_annex:
            # For an Annex III citation, extract the specific point if numbered (e.g. §4
            # employment, §5 essential services), else the Annex III intro.
            pt = re.search(r"(?:§|point)?\s*([0-9])\b", c.split("Annex III", 1)[-1] if "Annex III" in c else c)
            anchor = {"3": "Education", "4": "Employment", "5": "essential private",
                      "1": "Biometrics", "2": "Critical infrastructure"}.get(pt.group(1) if pt else "", "")
            if anchor:
                seg = re.search(re.escape(anchor) + r".*?(?=\n\s*\|\s*\d+\.|\Z)", annex, re.S | re.I)
                passage = _trim(seg.group(0), 700) if seg else _trim(annex, 700)
            else:
                passage = _trim(annex, 700)
        elif m_art:
            n = int(m_art.group(1))
            if n in arts:
                passage = _trim(arts[n], 700)
        out.append({"reference": c, "passage": passage, "url": DOC_URL, "in_source": bool(passage)})
    return out


# ── National (Netherlands) context: AP / ACM / human-rights guidance ──
NL_PORTALS = ["1|autoriteitpersoonsgegevens.nl", "1|acm.nl", "1|oordelen.mensenrechten.nl"]
PORTAL_AUTHORITY = {
    "autoriteitpersoonsgegevens.nl": "Autoriteit Persoonsgegevens (Dutch DPA)",
    "acm.nl": "ACM (Netherlands — national AI Act authority)",
    "oordelen.mensenrechten.nl": "Netherlands Institute for Human Rights",
}
# Dutch-language queries by risk theme (national searches must use the national language).
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


def _nl_passage(x):
    """Top verbatim Dutch chunk from a search hit, markup stripped."""
    for ch in (x.get("semanticHighlights") or x.get("highlights") or []):
        txt = (ch.get("chunkText") or "").strip()
        if txt:
            return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", txt)).strip()[:600]
    return None


def _nl_anchors(title):
    """Matchable phrases from a Dutch doc title (for inline citation chips)."""
    sub = title
    m = re.search(r"\(([^)]{10,})\)", title)          # text inside parentheses
    if m:
        sub = m.group(1)
    else:
        m = re.search(r"\b(?:19|20)\d{2}\b\s*[,:.\-]?\s*(.+)$", title)  # text after a year
        if m and len(m.group(1).strip()) >= 10:
            sub = m.group(1)
    sub = sub.strip(" ,:.-")
    anchors = {sub}
    words = sub.split()
    if len(words) >= 2:
        anchors.add(" ".join(words[:2]))             # distinctive 2-word lead
    return [a for a in anchors if len(a) >= 12]


def national_context(surfaces, key, jurisdiction="NL"):
    """Surface relevant Dutch (AP/ACM/human-rights) guidance for the classified profile,
    each with a verbatim passage + matchable title anchors so the UI can make them
    clickable like the EU citations."""
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
            title = x.get("title", "")
            out.append({
                "title": title,
                "authority": PORTAL_AUTHORITY.get(portal, portal),
                "year": x.get("year"),
                "url": x.get("sourceUrl") or DOC_URL.replace(AI_ACT, ident),
                "theme": theme,
                "passage": _nl_passage(x),
                "anchors": _nl_anchors(title),
            })
    final = out[:5]
    def _abbr(a):
        return "AP" if "Persoonsgegevens" in a else "ACM" if "ACM" in a else "NIHR" if "Human Rights" in a else a.split()[0]
    for i, d in enumerate(final, 1):
        d["tag"] = f"NL-{i}"
        lead = " ".join((d["anchors"][0] if d.get("anchors") else d["title"]).split()[:2])
        d["short"] = f"{_abbr(d['authority'])} {lead}{(' ' + str(d['year'])) if d.get('year') else ''}"
    return final


EU_PORTALS = ["0|eur-lex.europa.eu", "0|edpb.europa.eu"]


def qa_search(question, key, n=6):
    """Free-text search for the Q&A chat: returns top passages with source + link.
    Restricted to AUTHORITATIVE portals (EU eur-lex/EDPB + Dutch AP/ACM/human-rights) so the
    chat never cites random municipal regs or case law. Dutch-leaning if the question mentions NL."""
    nl_first = bool(re.search(r"\b(dutch|netherlands|nederland|\bAP\b|ACM|autoriteit|werknemer|sollicit)\b", question, re.I))
    body = {"query": question, "num_results": n,
            "portals": (NL_PORTALS + EU_PORTALS) if nl_first else (EU_PORTALS + NL_PORTALS)}
    try:
        req = urllib.request.Request(f"{BASE}/search/hybrid_search_reranked",
                                     data=json.dumps(body).encode(), method="POST")
        req.add_header("Ocp-Apim-Subscription-Key", key)
        req.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(req, timeout=25) as r:
            results = json.loads(r.read().decode()).get("result", {}).get("results", [])
    except Exception:
        return []
    out = []
    for x in results:
        passage = _nl_passage(x)
        if not passage:
            continue
        ident = x.get("identifier", "")
        portal = x.get("portal", "")
        src = "EU AI Act (Reg. 2024/1689)" if ident == AI_ACT else PORTAL_AUTHORITY.get(portal, portal or "source")
        url = x.get("sourceUrl") or (DOC_URL if ident == AI_ACT else f"https://app.moonlit.ai/document/{ident}/read")
        out.append({"title": x.get("title", ""), "url": url, "passage": passage, "source": src})
        if len(out) >= 3:
            break
    return out


def _key():
    k = os.environ.get("MOONLIT_KEY")
    if not k and os.path.exists(os.path.join(ROOT, ".env")):
        for line in open(os.path.join(ROOT, ".env")):
            if line.startswith("MOONLIT_KEY="):
                k = line.strip().split("=", 1)[1]
    return k


if __name__ == "__main__":
    cites = ["Annex III §4(a)", "Article 6(2)", "Article 26", "Article 50(1)", "Article 4", "Article 9"]
    for e in evidence_for(cites, _key()):
        print(f"{'✓' if e['in_source'] else '✗'} {e['reference']}: {(e['passage'] or '(none)')[:170]}")
