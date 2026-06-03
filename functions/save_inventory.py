"""Sinas function: default/save_inventory

Persist the company profile + classified AI-surface inventory into the
`default/sessions` state store, keyed by session_key, so the pack can be
regenerated or updated when the company adds a tool later.

Handler signature follows the Sinas contract: handler(input_data, context).
context provides `access_token` (short-lived JWT) to call back into the API.
"""

import json
import os
import urllib.request


def _api_base():
    # Functions run in containers on the Sinas host; the management API is
    # reachable on the internal address. Override with SINAS_API_BASE if needed.
    return os.environ.get("SINAS_API_BASE", "http://host.docker.internal:8000")


def _put_state(token, namespace, key, value):
    url = f"{_api_base()}/api/v1/states"
    body = json.dumps(
        {"namespace": namespace, "key": key, "value": value}
    ).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def handler(input_data, context):
    session_key = input_data["session_key"]
    record = {
        "session_key": session_key,
        "company": input_data.get("company", {}),
        "surfaces": input_data.get("surfaces", []),
    }
    saved = _put_state(
        context["access_token"],
        namespace="default",
        key=f"session:{session_key}",
        value=record,
    )
    return {
        "status": "saved",
        "session_key": session_key,
        "surface_count": len(record["surfaces"]),
        "state_id": saved.get("id"),
    }
