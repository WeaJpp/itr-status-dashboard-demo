from __future__ import annotations

import re
from typing import Any

from .models import LedgerRecord

ALLOWED_STATUSES = {
    "CODE-1", "CODE-2", "CODE-3", "CODE-4", "CODE-5",
    "READY", "UR", "DRAFT", "REJECTED", "NO", "N/A",
}
PROTECTED_NO_OP = {"", "NO", "N/A"}
CANCELLED_LABELS = {"CANCELLED", "X. CANCELLED"}
EXACT_STATUS_MAP = {
    "ISSUED FOR INSPECTION": "UR",
    "READY FOR SIGN OFF": "READY",
    "READY FOR SIGN OUT": "READY",
}
IDENTITY_RE = re.compile(
    r"^(?P<base>DEMO-GQC-IR-\d{5})(?:-(?P<revision>\d{2}))?$",
    re.IGNORECASE,
)
REVISION_RE = re.compile(r"^REV-(\d{2})$")


def normalize_status(value: str) -> str:
    text = " ".join(str(value or "").strip().upper().split())
    text = EXACT_STATUS_MAP.get(text, text)
    if text == "NA":
        return "N/A"
    if text.startswith("CODE "):
        text = text.replace("CODE ", "CODE-", 1)
    return text


def _identity_regex(pattern: str | None = None) -> re.Pattern[str]:
    compiled = re.compile(pattern, re.IGNORECASE) if pattern else IDENTITY_RE
    if "base" not in compiled.groupindex:
        raise ValueError("identity pattern must contain a named 'base' group")
    return compiled


def validate_identity(
    record: LedgerRecord, pattern: str | None = None
) -> tuple[bool, str]:
    value = record.itr_id.strip()
    if value.lower() == "pending":
        return False, "literal pending is not a searchable inspection identity"
    if not _identity_regex(pattern).fullmatch(value):
        return False, "identity does not match the configured inspection-number pattern"
    return True, ""


def should_scan(current_status: str, skip_statuses: set[str]) -> bool:
    return normalize_status(current_status) not in skip_statuses


def resolve_final_submission(payload: dict[str, Any]) -> tuple[str, str]:
    active = [
        submission
        for submission in payload.get("submissions", [])
        if normalize_status(submission.get("lifecycle", "")) not in CANCELLED_LABELS
    ]
    if not active:
        raise ValueError("no non-cancelled submission is available")
    final = active[-1]
    labels = final.get("labels", [final.get("label", "")])
    normalized = {normalize_status(label) for label in labels} - {""}
    unsupported = normalized - ALLOWED_STATUSES
    if unsupported:
        raise ValueError(f"unsupported final submission status: {sorted(unsupported)}")
    if len(normalized) != 1:
        raise ValueError("final submission status is missing or conflicting")
    return next(iter(normalized)), str(final.get("updated_at", ""))


def ordered_revision_headers(record: LedgerRecord) -> list[str]:
    numbered: list[tuple[int, str]] = []
    for header in record.revision_history:
        match = REVISION_RE.fullmatch(header)
        if not match:
            raise ValueError(f"invalid revision header: {header}")
        numbered.append((int(match.group(1)), header))
    numbered.sort()
    if not numbered:
        raise ValueError("revision history has no REV-xx headers")
    actual = [number for number, _ in numbered]
    if actual != list(range(len(numbered))):
        raise ValueError("revision headers must be contiguous from REV-00")
    return [header for _, header in numbered]


def compute_revision_target(record: LedgerRecord, observed_status: str) -> str:
    headers = ordered_revision_headers(record)
    latest_index = 0
    latest_value = ""
    for index, header in enumerate(headers):
        value = normalize_status(record.revision_history.get(header, ""))
        if value:
            latest_index = index
            latest_value = value
    if not latest_value or latest_value in {"UR", "READY"}:
        return headers[latest_index]
    if latest_value == observed_status:
        return headers[latest_index]
    next_index = latest_index + 1
    if next_index >= len(headers):
        raise ValueError("next revision header is missing; writeback is blocked")
    return headers[next_index]


def identity_for_target(
    record: LedgerRecord, target_revision: str, pattern: str | None = None
) -> str:
    match = _identity_regex(pattern).fullmatch(record.itr_id)
    if not match:
        raise ValueError("cannot build a revision identity from an invalid ITR ID")
    revision_match = match.groupdict().get("revision")
    if revision_match == "20":
        return record.itr_id
    revision = target_revision.removeprefix("REV-")
    return f"{match.group('base')}-{revision}"
