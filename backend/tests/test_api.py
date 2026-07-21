"""Offline API tests — no Vertex calls (those are exercised manually).

Covers routing, config shape, validation, and the local-only compress tool.
"""
import json

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
MC = {"model_name": "gemini-3.6-flash", "temperature": 1.0, "top_p": 0.8, "max_tokens": 4096}


def test_health():
    assert client.get("/api/health").json() == {"status": "ok"}


def test_config_lists_all_tools():
    cfg = client.get("/api/config").json()
    ids = {t["id"] for t in cfg["tools"]}
    # 12 generic + 2 special (dare, images)
    assert len(cfg["tools"]) == 14
    assert {"fine_tune", "json_prompt", "compress", "dare", "images"} <= ids
    assert cfg["default_model"] in cfg["models"]


def test_unknown_tool_404():
    r = client.post("/api/tools/nope", json={"input": "x", "modelConfig": MC})
    assert r.status_code == 404


def test_empty_input_400():
    r = client.post("/api/tools/system_prompt", json={"input": "  ", "modelConfig": MC})
    assert r.status_code == 400
    assert r.json()["code"] == "validation_error"


def test_model_config_accepts_alias_and_name():
    # alias "modelConfig"
    r1 = client.post("/api/tools/compress", json={"input": "the quick brown fox", "modelConfig": MC})
    # python field name "cfg"
    r2 = client.post("/api/tools/compress", json={"input": "the quick brown fox", "cfg": MC})
    assert r1.status_code == 200 and r2.status_code == 200


def test_compress_returns_stats():
    r = client.post(
        "/api/tools/compress",
        json={"input": "the quick brown fox jumps over the lazy dog", "modelConfig": MC},
    )
    assert r.status_code == 200
    meta = r.json()["meta"]
    assert {"original_len", "compressed_len", "reduction_pct"} <= meta.keys()
    assert meta["compressed_len"] <= meta["original_len"]


def test_fine_tune_stream_emits_four_blocks(monkeypatch):
    # Stub the (async) Vertex call so the four jobs return without a network hop.
    async def fake(*a, **k):
        return "FAKE OUTPUT"

    monkeypatch.setattr("app.api.routes_tools.generate_text_async", fake)
    with client.stream(
        "POST",
        "/api/tools/fine_tune/stream",
        json={"input": "tweet about Israel", "modelConfig": MC},
    ) as r:
        assert r.status_code == 200
        assert r.headers["content-type"].startswith("application/x-ndjson")
        msgs = [json.loads(line) for line in r.iter_lines() if line.strip()]

    blocks = [m for m in msgs if "content" in m]
    assert len(blocks) == 4
    assert {b["index"] for b in blocks} == {0, 1, 2, 3}
    assert all(b["content"] == "FAKE OUTPUT" for b in blocks)
    # Terminator arrives last.
    assert msgs[-1] == {"done": True}


def test_fine_tune_stream_per_block_error_isolated(monkeypatch):
    # One job raises; the other three must still stream through plus a done event.
    async def flaky(*a, **k):
        from app.core.errors import SafetyBlockedError

        flaky.calls = getattr(flaky, "calls", 0) + 1
        if flaky.calls == 1:
            raise SafetyBlockedError("blocked")
        return "OK"

    monkeypatch.setattr("app.api.routes_tools.generate_text_async", flaky)
    with client.stream(
        "POST",
        "/api/tools/fine_tune/stream",
        json={"input": "x", "modelConfig": MC},
    ) as r:
        assert r.status_code == 200
        msgs = [json.loads(line) for line in r.iter_lines() if line.strip()]

    errors = [m for m in msgs if "error" in m]
    contents = [m for m in msgs if "content" in m]
    assert len(errors) == 1 and errors[0]["code"] == "safety_blocked"
    assert len(contents) == 3
    assert msgs[-1] == {"done": True}


def test_stream_empty_input_400():
    r = client.post("/api/tools/fine_tune/stream", json={"input": "  ", "modelConfig": MC})
    assert r.status_code == 400
    assert r.json()["code"] == "validation_error"


def test_stream_unknown_tool_404():
    r = client.post("/api/tools/nope/stream", json={"input": "x", "modelConfig": MC})
    assert r.status_code == 404
