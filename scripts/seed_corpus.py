#!/usr/bin/env python3
"""Seed the aiact/regulation vector store with the curated corpus.

Uploads each corpus/*.md as a context document so the classifier's
`retrieve_context` tool can ground risk decisions and cite sources.

NOTE: the exact store-ingest endpoint varies by Sinas version. This script
targets the documented pattern and is overridable via SINAS_STORE_INGEST_PATH
(use "{ns}" and "{name}" placeholders). Run `python scripts/seed_corpus.py --check`
to print the resolved URL without uploading.
"""
import glob
import json
import os
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_PATH = "/api/v1/stores/{ns}/{name}/context"


def load_dotenv():
    path = os.path.join(ROOT, ".env")
    if not os.path.exists(path):
        return
    for line in open(path):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


def resolved_url():
    base = (os.environ.get("SINAS_MGMT_URL") or os.environ.get("SINAS_URL") or "").rstrip("/")
    path = os.environ.get("SINAS_STORE_INGEST_PATH", DEFAULT_PATH)
    return base + path.format(ns="aiact", name="regulation")


def upload(url, token, title, text):
    body = json.dumps({"key": title, "content": text, "metadata": {"source": title}}).encode()
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.status


if __name__ == "__main__":
    load_dotenv()
    url = resolved_url()
    if "--check" in sys.argv:
        print(f"Would POST corpus to: {url}")
        print("Override with SINAS_STORE_INGEST_PATH if your instance differs.")
        sys.exit(0)

    token = os.environ.get("SINAS_TOKEN")
    if not token or "your-team" in url or not url.startswith("http"):
        sys.exit("Set SINAS_URL + SINAS_TOKEN in .env first.")

    files = sorted(glob.glob(os.path.join(ROOT, "corpus", "*.md")))
    for path in files:
        title = os.path.basename(path)
        text = open(path).read()
        try:
            status = upload(url, token, title, text)
            print(f"  ✓ {title} ({status})")
        except urllib.error.HTTPError as e:
            print(f"  ✗ {title}: HTTP {e.code} {e.read().decode()[:200]}")
    print(f"Seeded {len(files)} documents into aiact/regulation.")
