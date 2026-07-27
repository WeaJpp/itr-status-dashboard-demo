from __future__ import annotations

import csv
import json
import os
import urllib.parse
import urllib.request
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from .models import LedgerRecord


class SourceAdapter(ABC):
    @abstractmethod
    def load(self) -> list[LedgerRecord]:
        """Read the authoritative ledger without modifying it."""


class JsonLedgerAdapter(SourceAdapter):
    def __init__(self, path: Path):
        self.path = path

    def load(self) -> list[LedgerRecord]:
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        rows = payload["records"] if isinstance(payload, dict) else payload
        return [LedgerRecord.from_dict(row) for row in rows]


class CsvLedgerAdapter(SourceAdapter):
    def __init__(self, path: Path):
        self.path = path

    def load(self) -> list[LedgerRecord]:
        with self.path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = []
            for row in csv.DictReader(handle):
                row["revision_history"] = json.loads(row.get("revision_history") or "{}")
                rows.append(LedgerRecord.from_dict(row))
            return rows


class PortalAdapter(ABC):
    @abstractmethod
    def preflight(self) -> None:
        """Validate configuration before any query."""

    @abstractmethod
    def query(self, record: LedgerRecord) -> dict[str, Any]:
        """Return match_code and submission history for one record."""


class FixturePortalAdapter(PortalAdapter):
    def __init__(self, path: Path):
        self.path = path
        self._rows: dict[str, dict[str, Any]] = {}

    def preflight(self) -> None:
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        if isinstance(payload, dict) and "results" not in payload:
            self._rows = {str(key): value for key, value in payload.items()}
        else:
            rows = payload["results"] if isinstance(payload, dict) else payload
            self._rows = {str(row["task_id"]): row for row in rows}

    def query(self, record: LedgerRecord) -> dict[str, Any]:
        if record.task_id not in self._rows:
            raise LookupError(f"portal fixture has no result for task_id={record.task_id}")
        return self._rows[record.task_id]


class HttpJsonPortalAdapter(PortalAdapter):
    """Optional adapter for a private, sanitized JSON gateway.

    A browser automation adapter can implement the same contract. Keep target
    URLs, selectors, cookies, credentials and tokens out of this repository.
    """

    def __init__(self, base_url: str, token_env: str = ""):
        self.base_url = base_url
        self.token_env = token_env

    def preflight(self) -> None:
        parsed = urllib.parse.urlparse(self.base_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("crawler.base_url must be an absolute HTTP(S) URL")
        if self.token_env and not os.getenv(self.token_env):
            raise ValueError(f"required environment variable is missing: {self.token_env}")

    def query(self, record: LedgerRecord) -> dict[str, Any]:
        url = f"{self.base_url}?{urllib.parse.urlencode({'itr_id': record.itr_id})}"
        headers = {"Accept": "application/json"}
        if self.token_env:
            headers["Authorization"] = f"Bearer {os.environ[self.token_env]}"
        request = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))


def build_source_adapter(root: Path, config: dict[str, Any]) -> SourceAdapter:
    path = root / config["path"]
    if config["adapter"] == "json-ledger":
        return JsonLedgerAdapter(path)
    if config["adapter"] == "csv-ledger":
        return CsvLedgerAdapter(path)
    raise ValueError(f"unsupported source adapter: {config['adapter']}")


def build_portal_adapter(root: Path, config: dict[str, Any]) -> PortalAdapter:
    if config["adapter"] == "fixture":
        return FixturePortalAdapter(root / config["path"])
    if config["adapter"] == "http-json":
        return HttpJsonPortalAdapter(str(config["base_url"]), str(config.get("token_env", "")))
    raise ValueError(f"unsupported crawler adapter: {config['adapter']}")
