"""Sinas function: default/get_inventory

Read back a previously saved company profile + inventory from the
`default/sessions` state store. Lets the orchestrator answer follow-ups
("what changes if I add tool X?") and regenerate the pack incrementally.
"""

import json
import os
import urllib.parse
import urllib.request


def _api_base():
    return os.environ.get("SINAS_API_BASE", "http://host.docker.internal:8000")


def _get_state(token, namespace, key):
    qs = urllib.parse.urlencode({"namespace": namespace, "key": key})
    url = f"{_api_base()}/api/v1/states?{qs}"
    req = urllib.request.Request(url, method="GET")
    req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def handler(input_data, context):
    session_key = input_data["session_key"]
    result = _get_state(
        context["access_token"],
        namespace="default",
        key=f"session:{session_key}",
    )
    # The list endpoint may return a list; normalise to the stored value.
    items = result if isinstance(result, list) else result.get("items", [result])
    if not items:
        return {"found": False, "session_key": session_key}
    value = items[0].get("value", items[0])
    return {
        "found": True,
        "session_key": session_key,
        "company": value.get("company", {}),
        "surfaces": value.get("surfaces", []),
    }
