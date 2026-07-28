from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class LedgerRecord:
    task_id: str
    site: str
    site_zh: str
    process: str
    process_zh: str
    itr_id: str
    status: str
    track: str
    chainage: str
    submitted_date: str
    revision_history: dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "LedgerRecord":
        return cls(
            task_id=str(value["task_id"]).strip(),
            site=str(value["site"]).strip(),
            site_zh=str(value.get("site_zh", value["site"])).strip(),
            process=str(value["process"]).strip(),
            process_zh=str(value.get("process_zh", value["process"])).strip(),
            itr_id=str(value["itr_id"]).strip(),
            status=str(value.get("status", "")).strip(),
            track=str(value.get("track", "N/A")).strip(),
            chainage=str(value.get("chainage", "")).strip(),
            submitted_date=str(value.get("submitted_date", "")).strip(),
            revision_history={
                str(key).strip(): str(item or "").strip()
                for key, item in dict(value.get("revision_history", {})).items()
            },
        )

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class RowError:
    task_id: str
    itr_id: str
    code: str
    message_en: str
    message_zh: str

    def as_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(slots=True)
class ChangeProposal:
    task_id: str
    itr_id: str
    current_status: str
    observed_status: str
    target_revision: str
    identity_after_write: str
    reason: str

    def as_dict(self) -> dict[str, str]:
        return asdict(self)
