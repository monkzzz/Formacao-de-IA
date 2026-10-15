"""Minimal client for the local LM Studio server used in the live demonstrations."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any

BASE_URL = os.environ.get("FORMACAO_LMSTUDIO_URL", "http://localhost:1234").rstrip("/")
TEXT_MODEL = "amalia-9b-0626-dpo"
VISION_MODEL = "zai-org/glm-4.6v-flash"
EMBEDDING_MODEL = "text-embedding-bge-m3"
OFFLINE_VARIABLE = "FORMACAO_LMSTUDIO_OFFLINE"

JsonObject = dict[str, Any]


class LmStudioError(RuntimeError):
    """The local server is unreachable or returned an unusable answer."""


def is_offline_forced() -> bool:
    """Return True when the presenter asked to use only recorded answers."""
    return os.environ.get(OFFLINE_VARIABLE) == "1"


def post_json(path: str, payload: JsonObject, timeout: float = 60.0) -> JsonObject:
    """POST a JSON payload to the local server and return the decoded answer."""
    request = urllib.request.Request(
        f"{BASE_URL}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")[:300]
        raise LmStudioError(f"LM Studio respondeu {error.code} em {path}: {detail}") from error
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        raise LmStudioError(f"LM Studio indisponível em {BASE_URL}{path}: {error}") from error
    except json.JSONDecodeError as error:
        raise LmStudioError(f"Resposta não JSON do LM Studio em {path}.") from error


def list_models(timeout: float = 2.0) -> tuple[str, ...]:
    """Return the model identifiers the local server can serve."""
    try:
        with urllib.request.urlopen(f"{BASE_URL}/v1/models", timeout=timeout) as response:
            data = json.load(response)
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as error:
        raise LmStudioError(f"LM Studio indisponível em {BASE_URL}: {error}") from error
    return tuple(str(model.get("id", "")) for model in data.get("data", ()))


def is_model_available(model: str) -> bool:
    """Check quickly whether live calls to a model can be attempted."""
    if is_offline_forced():
        return False
    try:
        return model in list_models()
    except LmStudioError:
        return False


def embed(texts: list[str], model: str = EMBEDDING_MODEL) -> list[list[float]]:
    """Return one embedding vector per text, in the same order."""
    answer = post_json("/v1/embeddings", {"model": model, "input": texts}, timeout=60.0)
    data = sorted(answer.get("data") or (), key=lambda item: item.get("index", 0))
    if len(data) != len(texts):
        raise LmStudioError(f"O modelo {model} devolveu {len(data)} vetores para {len(texts)} textos.")
    return [list(map(float, item["embedding"])) for item in data]


def count_tokens(text: str, model: str = TEXT_MODEL) -> int:
    """Count the tokens of a text in the model, without the fixed chat-format tokens."""
    def prompt_tokens(content: str) -> int:
        choice = request_chat([{"role": "user", "content": content}], model, timeout=30.0, max_tokens=1,
                              temperature=0)
        return int(choice["usage"]["prompt_tokens"])

    # A one-character message measures the chat format; "." itself is one token.
    return prompt_tokens(text) - (prompt_tokens(".") - 1)


def request_chat(messages: list[JsonObject], model: str = TEXT_MODEL, timeout: float = 60.0,
                 **options: Any) -> JsonObject:
    """Run one chat completion and return its first choice."""
    answer = post_json("/v1/chat/completions", {"model": model, "messages": messages, **options}, timeout)
    if "error" in answer:
        raise LmStudioError(f"LM Studio recusou o pedido ao modelo {model}: {answer['error']}")
    choices = answer.get("choices") or ()
    if not choices:
        raise LmStudioError(f"Resposta sem escolhas do modelo {model}.")
    choice = dict(choices[0])
    choice["usage"] = answer.get("usage", {})
    return choice
