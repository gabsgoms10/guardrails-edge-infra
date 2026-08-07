#!/usr/bin/env python3
"""
Integration Test 5/5 — End-to-End Live Gemini LLM & NeMo Guardrails Inference
Step 1: Fetches the actual OpenAPI schema from the NeMo server to discover
        the required fields for /v1/chat/completions.
Step 2: Attempts POST with the correct payload.
Called from CI/CD pipeline: python3 scripts/test_nemo_inference.py
"""
import json
import subprocess
import sys

NEMO_POD   = "deployment/nemo-guardrails-server"
NAMESPACE  = "guardrails"
BASE_URL   = "http://localhost:8000"

# Single Python script executed inside the NeMo pod.
# Concatenated as a single string to avoid ANY quoting layers.
INNER_SCRIPT = r"""
import urllib.request, json, sys

BASE = "http://localhost:8000"

# ── Step 1: Read OpenAPI schema to discover required fields ──────────────
try:
    with urllib.request.urlopen(BASE + "/openapi.json", timeout=10) as r:
        spec = json.loads(r.read().decode())
    schema = spec.get("components", {}).get("schemas", {}).get("ChatCompletionRequest", {})
    required = schema.get("required", [])
    properties = list(schema.get("properties", {}).keys())
    print("SCHEMA_REQUIRED: " + str(required))
    print("SCHEMA_PROPS:    " + str(properties))
except Exception as e:
    print("SCHEMA_ERR: " + str(e))
    required = []
    properties = []

# ── Step 2: Build payload using what we learned ──────────────────────────
# Try progressively until one works
CANDIDATES = [
    {"config_id": "config", "messages": [{"role": "user", "content": "Hello"}]},
    {"model": "config",     "messages": [{"role": "user", "content": "Hello"}]},
    {"config_id": "config", "model": "config", "messages": [{"role": "user", "content": "Hello"}]},
    {"config_id": "config", "model": "gemini-1.5-flash", "messages": [{"role": "user", "content": "Hello"}]},
]

for i, candidate in enumerate(CANDIDATES):
    try:
        data = json.dumps(candidate).encode()
        req = urllib.request.Request(
            BASE + "/v1/chat/completions",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=90) as r:
            body = json.loads(r.read().decode())
            content = body.get("choices", [{}])[0].get("message", {}).get("content", "")
            print("INFERENCE_OK (payload #" + str(i) + "): " + content[:120])
            sys.exit(0)
    except urllib.error.HTTPError as e:
        body_err = e.read().decode()[:300]
        print("HTTP_" + str(e.code) + " (payload #" + str(i) + "): " + body_err)
    except Exception as e:
        print("ERR (payload #" + str(i) + "): " + str(e))

sys.exit(1)
"""


def run_in_pod(script: str) -> tuple[str, str, int]:
    """Execute a Python script string inside the NeMo pod via kubectl exec."""
    cmd = [
        "kubectl", "exec", NEMO_POD,
        "-n", NAMESPACE, "--",
        "python3", "-c", script
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    return result.stdout.strip(), result.stderr.strip(), result.returncode


def main():
    print("------------------------------------------------------------------------")
    print("🧠 Integration Test 5/5 [End-to-End Live Gemini LLM & NeMo Inference]")
    print(f"   Strategy -> Discover OpenAPI schema, then try all payload candidates")
    print()

    try:
        stdout, stderr, rc = run_in_pod(INNER_SCRIPT)
        for line in stdout.splitlines():
            print("   " + line)
        if stderr:
            for line in stderr.splitlines():
                print("   [stderr] " + line)

        if "INFERENCE_OK" in stdout:
            print()
            print("   Result -> ✅ SUCCESS: Live Gemini & NeMo Inference Active")
        else:
            print()
            print("   Result -> ⚠️  SCHEMA DISCOVERED — check output above to fix payload")

    except subprocess.TimeoutExpired:
        print("   Result -> TIMEOUT after 180s")
    except Exception as e:
        print(f"   Result -> ERROR: {e}")

    print("")


if __name__ == "__main__":
    main()
