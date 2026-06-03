#!/usr/bin/env python3
"""Live demo server for the AI Act Co-Pilot.

Serves an interactive UI (web/index.html) and drives the multi-agent pipeline,
streaming each step's start/finish to the browser via Server-Sent Events (SSE) so
the audience watches the agents spin up, work, and complete in real time.

Pipeline (mirrors scripts/demo.py):
  classifier (Sinas agent)
    → [ Moonlit evidence  ‖  policy-drafter  ‖  training-architect ]  (parallel)
    → generate_pack (render)

No third-party deps — Python stdlib only.
  python3 scripts/server.py         # then open http://localhost:8800
"""
import json
import os
import sys
import time
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "functions"))
import demo            # noqa: E402  reuse invoke(), parse_json(), load_dotenv(), DEMO
import moonlit         # noqa: E402
from generate_pack import _render_pack  # noqa: E402

PORT = int(os.environ.get("PORT", "8800"))


def run_pipeline(message, emit):
    t0 = time.time()
    el = lambda: int((time.time() - t0) * 1000)

    # 1) Classifier
    key = moonlit._key()
    # PHASE 1 — classifier  ‖  Moonlit corpus fetch (independent: warms the AI Act cache)
    emit("step", id="classifier", status="running")
    emit("step", id="evidence", status="running", detail="fetching EU AI Act corpus from Moonlit…")
    ev_start = time.time()
    pool = ThreadPoolExecutor(max_workers=3)
    prefetch = pool.submit(moonlit._fetch_full_text, key)  # runs concurrently with the classifier

    s = time.time()
    cls = demo.parse_json(demo.invoke("classifier", f"Surfaces from this company description — classify each:\n{message}"))
    surfaces = cls.get("surfaces", [])
    if not surfaces:
        emit("error", message="Classifier returned no parseable surfaces.")
        return
    citations = sorted({c for x in surfaces for c in x.get("citations", [])})
    counts = {t: sum(1 for x in surfaces if x.get("risk_tier") == t) for t in ("prohibited", "high", "limited", "minimal")}
    emit("step", id="classifier", status="done", ms=int((time.time() - s) * 1000),
         detail=f"{len(surfaces)} surfaces · {counts['high']} high-risk · {counts['limited']} limited")
    emit("output", id="classifier", kind="surfaces", surfaces=surfaces, counts=counts)

    # PHASE 2 — legal grounding (both run after the classifier, in parallel):
    #   Moonlit Evidence (verbatim EU AI Act text)  ‖  Dutch Law (AP/ACM national guidance)
    try:
        prefetch.result(timeout=90)
    except Exception:
        pass
    emit("step", id="dutch", status="running")
    d0 = time.time()
    f_ev = pool.submit(moonlit.evidence_for, citations, key)
    f_nat = pool.submit(moonlit.national_context, surfaces, key)
    evidence = f_ev.result()
    national = f_nat.result()
    emit("step", id="evidence", status="done", ms=int((time.time() - ev_start) * 1000),
         detail=f"{sum(1 for e in evidence if e.get('passage'))}/{len(evidence)} citations grounded in verbatim Moonlit/OJ text")
    emit("output", id="evidence", kind="evidence", evidence=evidence)
    emit("step", id="dutch", status="done", ms=int((time.time() - d0) * 1000),
         detail=f"{len(national)} Dutch sources (AP / ACM) — fed into the policy & training")
    emit("output", id="dutch", kind="national", national=national)

    # Dutch guidance → injected into the drafters so answers USE it. Each source has a fixed tag;
    # the agent cites inline with the exact tag, which the UI turns into a clickable evidence chip.
    nat_lines = "\n".join(f"  [{d['tag']}] {d['authority']} ({d.get('year')}): {d['title']}" for d in national) or "  (none found)"
    nat_note = ("\n\nApplicable Dutch national guidance (Netherlands). Where one of these is relevant to a "
                "specific control or obligation, cite it INLINE using its EXACT bracketed tag — e.g. "
                "'…meaningful human intervention is required [NL-1]'. Use the tags verbatim. Sources:\n" + nat_lines)

    # PHASE 3 — policy-drafter ‖ training-architect, grounded in the classification AND Dutch guidance
    sjson = json.dumps(surfaces)
    tasks = {
        "policy": lambda: demo.invoke("policy-drafter", f"Company: {message}\nClassified surfaces: {sjson}{nat_note}"),
        "training": lambda: demo.invoke("training-architect", f"Company: {message}\nClassified surfaces: {sjson}{nat_note}"),
    }
    for sid in tasks:
        emit("step", id=sid, status="running")
    starts = {sid: time.time() for sid in tasks}
    mds = {}
    fut = {pool.submit(fn): sid for sid, fn in tasks.items()}
    for f in as_completed(fut):
        sid = fut[f]
        field = "policy_markdown" if sid == "policy" else "training_markdown"
        md = demo.extract_field(f.result(), field)
        mds[sid] = md
        emit("step", id=sid, status="done", ms=int((time.time() - starts[sid]) * 1000), detail=f"{len(md):,} chars drafted")
        emit("output", id=sid, kind="markdown", markdown=md)
    pool.shutdown(wait=False)

    policy_md = mds.get("policy", "")
    training_md = mds.get("training", "")

    # 3) Assemble
    emit("step", id="generate_pack", status="running")
    s = time.time()
    company = demo_company(message)
    pack = _render_pack(company, surfaces, policy_md, training_md, evidence, national)
    emit("step", id="generate_pack", status="done", ms=int((time.time() - s) * 1000),
         detail=f"{len(pack):,}-char compliance pack assembled")
    emit("output", id="generate_pack", kind="markdown", markdown=pack)

    emit("summary", company=company.get("name"), counts=counts,
         grounded=sum(1 for e in evidence if e.get("passage")), total_citations=len(evidence))
    emit("done", total_ms=el())


def demo_company(message):
    import re
    m_size = re.search(r"(\d+)[\s-]*(?:person|employee|staff|people)", message, re.I)
    m_name = re.search(r"[Ww]e(?:'re| are)\s+an?\s+([^.,;]+)", message)
    return {"name": (m_name.group(1).strip().title() if m_name else "the company"),
            "size": (f"{m_size.group(1)} staff" if m_size else ""), "sector": ""}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _emit(self, event, **data):
        try:
            self.wfile.write(f"event: {event}\ndata: {json.dumps(data)}\n\n".encode())
            self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            raise

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/":
            html = open(os.path.join(ROOT, "web", "index.html"), "rb").read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html)))
            self.end_headers()
            self.wfile.write(html)
        elif parsed.path == "/ask":
            qs = urllib.parse.parse_qs(parsed.query)
            q = (qs.get("q", [""])[0]).strip()
            ctx = (qs.get("ctx", [""])[0]).strip() or "(no assessment has been run yet)"
            try:
                # The aiact_qa agent searches Moonlit itself via the default/moonlit connector.
                prompt = f"CONTEXT — the company's classified AI inventory:\n{ctx}\n\nQUESTION: {q}"
                answer = demo.invoke("aiact_qa", prompt)
                payload = json.dumps({"answer": answer, "sources": []}).encode()
            except Exception as e:  # noqa: BLE001
                payload = json.dumps({"answer": f"Sorry — I hit an error: {e!r}"[:200], "sources": []}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
        elif parsed.path == "/run":
            qs = urllib.parse.parse_qs(parsed.query)
            message = (qs.get("message", [demo.DEMO])[0]).strip() or demo.DEMO
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.end_headers()
            try:
                run_pipeline(message, self._emit)
            except Exception as e:  # noqa: BLE001
                try:
                    self._emit("error", message=repr(e)[:300])
                except Exception:
                    pass
        else:
            self.send_response(404)
            self.end_headers()


if __name__ == "__main__":
    demo.load_dotenv()
    print(f"\n  AI Act Co-Pilot demo UI →  http://localhost:{PORT}\n  (Ctrl-C to stop)\n")
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
