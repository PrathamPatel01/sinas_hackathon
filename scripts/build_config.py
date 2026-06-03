#!/usr/bin/env python3
"""Assemble the Sinas config from config/*.yaml.

- Merges the top-level resource lists across all config/*.yaml files.
- Inlines `content_file:` -> `content:` (skills) and `code_file:` -> `code:` (functions).
- Interpolates ${ENV_VAR} from the environment.
- Writes dist/config.yaml.
- With --dry-run / --apply, POSTs to {SINAS_MGMT_URL}/api/v1/config/apply.

Usage:
  python scripts/build_config.py                 # build dist/config.yaml only
  python scripts/build_config.py --dry-run       # build + preview apply (no writes)
  python scripts/build_config.py --apply         # build + apply for real
"""
import glob
import json
import os
import re
import sys
import urllib.request

try:
    import yaml
except ImportError:
    sys.exit("PyYAML required: pip install pyyaml")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(ROOT, "config")
DIST = os.path.join(ROOT, "dist", "config.yaml")

ENV_RE = re.compile(r"\$\{([A-Z0-9_]+)\}")


def load_dotenv():
    path = os.path.join(ROOT, ".env")
    if not os.path.exists(path):
        return
    for line in open(path):
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())


def interpolate(obj):
    if isinstance(obj, str):
        return ENV_RE.sub(lambda m: os.environ.get(m.group(1), ""), obj)
    if isinstance(obj, list):
        return [interpolate(x) for x in obj]
    if isinstance(obj, dict):
        # Drop keys that interpolate to "" so unset env vars become "omitted"
        # (e.g. llm_provider_id="" -> use the instance default) rather than null.
        out = {k: interpolate(v) for k, v in obj.items()}
        return {k: v for k, v in out.items() if v != ""}
    return obj


def inline_files(resource):
    """Replace *_file references with the file's contents."""
    for ref, target in (("content_file", "content"), ("code_file", "code")):
        if ref in resource:
            with open(os.path.join(ROOT, resource.pop(ref))) as f:
                resource[target] = f.read()
    return resource


def build():
    merged = {}
    for path in sorted(glob.glob(os.path.join(CONFIG_DIR, "*.yaml"))):
        doc = yaml.safe_load(open(path)) or {}
        for key, items in doc.items():
            if not isinstance(items, list):
                merged.setdefault(key, items)
                continue
            merged.setdefault(key, [])
            merged[key].extend(inline_files(it) if isinstance(it, dict) else it for it in items)
    merged = interpolate(merged)
    os.makedirs(os.path.dirname(DIST), exist_ok=True)
    with open(DIST, "w") as f:
        yaml.safe_dump(merged, f, sort_keys=False, allow_unicode=True, width=100)
    counts = {k: len(v) if isinstance(v, list) else 1 for k, v in merged.items()}
    print(f"Built {DIST}: " + ", ".join(f"{n}×{k}" for k, n in counts.items()))
    return merged


def apply(config, dry_run):
    mgmt = os.environ.get("SINAS_MGMT_URL") or os.environ.get("SINAS_URL")
    token = os.environ.get("SINAS_TOKEN")
    if not mgmt or not token:
        sys.exit("Set SINAS_URL (or SINAS_MGMT_URL) and SINAS_TOKEN in .env")
    url = mgmt.rstrip("/") + "/api/v1/config/apply"
    payload = json.dumps({
        "config": yaml.safe_dump(config, sort_keys=False, allow_unicode=True),
        "dryRun": dry_run,
    }).encode("utf-8")
    req = urllib.request.Request(url, data=payload, method="POST")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    print(f"{'DRY-RUN' if dry_run else 'APPLY'} → {url}")
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            print(json.dumps(json.loads(resp.read().decode()), indent=2))
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code}: {e.read().decode()}")


if __name__ == "__main__":
    load_dotenv()
    cfg = build()
    if "--dry-run" in sys.argv:
        apply(cfg, dry_run=True)
    elif "--apply" in sys.argv:
        apply(cfg, dry_run=False)
