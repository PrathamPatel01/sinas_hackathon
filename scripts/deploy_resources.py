#!/usr/bin/env python3
"""Deploy resources to Sinas via per-resource management endpoints.

Upsert semantics: PUT if the resource already exists, else POST. We never
delete+recreate — this instance has a bug where recreating an agent with a
previously-deleted name returns 500, so deletes are avoided entirely.

Order matters: agents reference functions/skills/collections, so create those
first. Stores are intentionally not used (curated knowledge is preloaded via
skills instead).

Usage:
  python3 scripts/build_config.py        # refresh dist/config.yaml first
  python3 scripts/deploy_resources.py    # deploy (idempotent upsert)
"""
import json
import os
import sys
import urllib.error
import urllib.request

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (config_key, endpoint_plural) in forward (create) dependency order.
TYPES = [
    ("skills", "skills"),
    ("collections", "collections"),
    ("connectors", "connectors"),
    ("functions", "functions"),
    ("agents", "agents"),
]


def load_dotenv():
    path = os.path.join(ROOT, ".env")
    if os.path.exists(path):
        for line in open(path):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def cfg():
    base = (os.environ.get("SINAS_MGMT_URL") or os.environ.get("SINAS_URL") or "").rstrip("/")
    token = os.environ.get("SINAS_TOKEN")
    if not base or not token:
        sys.exit("Set SINAS_URL + SINAS_TOKEN in .env")
    return base, token


def call(method, url, token, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    if data:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            txt = r.read().decode()
            return r.status, (json.loads(txt) if txt else None)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:300]


def existing_names(base, token, plural):
    status, data = call("GET", f"{base}/api/v1/{plural}", token)
    if status == 200 and isinstance(data, list):
        return {(r["namespace"], r.get("name")) for r in data}
    return set()


def deploy_secrets(base, token, config):
    """Secrets are name-only (no namespace). Upsert by name; values are write-only."""
    secrets = config.get("secrets") or []
    if not secrets:
        return
    st, data = call("GET", f"{base}/api/v1/secrets", token)
    have = {s.get("name") for s in data} if st == 200 and isinstance(data, list) else set()
    for sec in secrets:
        name = sec.get("name")
        if not sec.get("value"):
            print(f"  ⚠ skip secret {name} (no value — set it in .env)")
            continue
        if name in have:
            s2, d2 = call("PUT", f"{base}/api/v1/secrets/{name}", token, sec)
        else:
            s2, d2 = call("POST", f"{base}/api/v1/secrets", token, sec)
        ok = s2 in (200, 201)
        print(f"  {'✓' if ok else '✗'} secret {name} -> {s2}" + ("" if ok else f"  {d2}"))


def deploy(base, token, config):
    deploy_secrets(base, token, config)
    for key, plural in TYPES:
        have = existing_names(base, token, plural)
        for res in config.get(key, []) or []:
            ns, name = res.get("namespace"), res.get("name")
            if (ns, name) in have:
                st, data = call("PUT", f"{base}/api/v1/{plural}/{ns}/{name}", token, res)
                verb = "updated"
            else:
                st, data = call("POST", f"{base}/api/v1/{plural}", token, res)
                verb = "created"
            ok = st in (200, 201)
            print(f"  {'✓' if ok else '✗'} {verb} {plural} {ns}/{name} -> {st}"
                  + ("" if ok else f"  {data}"))


if __name__ == "__main__":
    load_dotenv()
    base, token = cfg()
    config = yaml.safe_load(open(os.path.join(ROOT, "dist", "config.yaml")))
    deploy(base, token, config)
