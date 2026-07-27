from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .adapters import build_portal_adapter, build_source_adapter
from .models import ChangeProposal, LedgerRecord, RowError
from .rules import (
    ALLOWED_STATUSES,
    PROTECTED_NO_OP,
    compute_revision_target,
    identity_for_target,
    normalize_status,
    resolve_final_submission,
    should_scan,
    validate_identity,
)


class Pipeline:
    def __init__(self, root: Path, config_path: Path):
        self.root = root
        self.config_path = config_path
        self.config = json.loads(config_path.read_text(encoding="utf-8"))
        self.phases: list[dict[str, Any]] = []
        self.errors: list[RowError] = []
        self.proposals: list[ChangeProposal] = []
        self.portal_queries: list[str] = []

    def _phase(self, key: str, status: str, detail_en: str, detail_zh: str) -> None:
        self.phases.append(
            {"key": key, "status": status, "detail_en": detail_en, "detail_zh": detail_zh}
        )

    def _error(
        self,
        record: LedgerRecord,
        code: str,
        message_en: str,
        message_zh: str,
    ) -> None:
        self.errors.append(
            RowError(
                task_id=record.task_id,
                itr_id=record.itr_id,
                code=code,
                message_en=message_en,
                message_zh=message_zh,
            )
        )

    def _preflight(self) -> tuple[Any, Any]:
        required = {"project", "source", "crawler", "rules", "report", "writeback"}
        missing = required - set(self.config)
        if missing:
            raise ValueError(f"config is missing sections: {sorted(missing)}")
        if self.config["writeback"].get("enabled") is not False:
            raise ValueError("the public demo requires writeback.enabled=false")
        source = build_source_adapter(self.root, self.config["source"])
        portal = build_portal_adapter(self.root, self.config["crawler"])
        portal.preflight()
        self._phase(
            "preflight",
            "ok",
            "Configuration, source, and crawler adapter are readable.",
            "配置、源台账和爬虫适配器均可读取。",
        )
        return source, portal

    def run(self) -> dict[str, Any]:
        source, portal = self._preflight()
        records = source.load()
        self._phase(
            "source",
            "ok",
            f"Loaded {len(records)} rows from the authoritative sample ledger.",
            f"已从权威样例台账读取 {len(records)} 行。",
        )

        seen_task_ids: set[str] = set()
        validated: list[LedgerRecord] = []
        for record in records:
            if record.task_id in seen_task_ids:
                self._error(
                    record,
                    "DUPLICATE_TASK_ID",
                    "Duplicate task_id; the row was not queried or written.",
                    "task_id 重复；该行未查询、未写回。",
                )
                continue
            seen_task_ids.add(record.task_id)
            valid, reason = validate_identity(record)
            if not valid:
                self._error(
                    record,
                    "INVALID_IDENTITY",
                    f"{reason}; the row was rejected before portal search.",
                    f"{reason}；该行在门户查询前已被拒绝。",
                )
                continue
            validated.append(record)

        self._phase(
            "identity",
            "warn" if self.errors else "ok",
            f"Validated {len(validated)} unique searchable identities.",
            f"已验证 {len(validated)} 个唯一且可查询的报验编号。",
        )

        skip_statuses = {
            normalize_status(item) for item in self.config["rules"]["skip_current_statuses"]
        }
        display_rows: list[dict[str, Any]] = []
        scanned = 0
        unchanged = 0
        skipped = 0

        for record in records:
            row = record.as_dict()
            row["current_status"] = normalize_status(record.status)
            row["observed_status"] = ""
            row["display_status"] = row["current_status"]
            row["query_state"] = "not_scanned"
            row["updated_at"] = record.submitted_date
            display_rows.append(row)

        rows_by_task = {row["task_id"]: row for row in display_rows}
        valid_task_ids = {record.task_id for record in validated}

        for record in validated:
            row = rows_by_task[record.task_id]
            if not should_scan(record.status, skip_statuses):
                skipped += 1
                row["query_state"] = "skipped_by_policy"
                continue

            scanned += 1
            self.portal_queries.append(record.task_id)
            try:
                payload = portal.query(record)
                if str(payload.get("match_code", "")).strip() != record.itr_id:
                    raise ValueError("portal match_code does not match the requested identity")
                observed, updated_at = resolve_final_submission(payload)
                if observed not in ALLOWED_STATUSES:
                    raise ValueError(f"status is not allowlisted: {observed}")
                row["observed_status"] = observed
                row["updated_at"] = updated_at or row["updated_at"]
                row["query_state"] = "resolved"

                if observed in PROTECTED_NO_OP:
                    unchanged += 1
                    continue
                row["display_status"] = observed
                current = normalize_status(record.status)
                if current == observed:
                    unchanged += 1
                    continue

                target = compute_revision_target(record, observed)
                identity_after = identity_for_target(record, target)
                self.proposals.append(
                    ChangeProposal(
                        task_id=record.task_id,
                        itr_id=record.itr_id,
                        current_status=current,
                        observed_status=observed,
                        target_revision=target,
                        identity_after_write=identity_after,
                        reason="validated portal status differs from ledger cache",
                    )
                )
            except Exception as exc:  # row-level fail-closed boundary
                row["query_state"] = "error"
                self._error(
                    record,
                    "QUERY_OR_RULE_ERROR",
                    f"{exc}; no writeback was proposed.",
                    f"{exc}；未生成写回建议。",
                )

        for row in display_rows:
            if row["task_id"] not in valid_task_ids and row["query_state"] == "not_scanned":
                row["query_state"] = "rejected_before_query"

        self._phase(
            "crawl",
            "warn" if self.errors else "ok",
            f"Queried {scanned} rows sequentially; skipped {skipped} approved terminal rows.",
            f"已顺序查询 {scanned} 行；按规则跳过 {skipped} 行终态记录。",
        )
        self._phase(
            "rules",
            "warn" if self.errors else "ok",
            f"Produced {len(self.proposals)} guarded writeback proposals.",
            f"已生成 {len(self.proposals)} 条受保护的写回建议。",
        )
        self._phase(
            "writeback",
            "disabled",
            "Public demo writeback is disabled; proposals were saved as an artifact only.",
            "公开样例已禁用写回；建议仅保存为产物。",
        )

        scope_complete = not self.errors
        confirmed_ur = sum(
            1
            for row in display_rows
            if row["query_state"] == "resolved" and row["display_status"] == "UR"
        )
        counts = Counter(
            row["display_status"]
            for row in display_rows
            if row["display_status"] not in {"", "NO", "N/A"}
        )
        result = {
            "schema_version": 2,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "project": self.config["project"],
            "summary": {
                "status": "completed_with_errors" if self.errors else "success",
                "source_rows": len(records),
                "validated_rows": len(validated),
                "scanned": scanned,
                "skipped": skipped,
                "unchanged": unchanged,
                "changes": len(self.proposals),
                "unresolved": len(self.errors),
                "scope_complete": scope_complete,
                "confirmed_still_ur": confirmed_ur,
                "status_counts": dict(sorted(counts.items())),
            },
            "phases": self.phases,
            "records": display_rows,
            "changes": [proposal.as_dict() for proposal in self.proposals],
            "errors": [error.as_dict() for error in self.errors],
            "safety": {
                "writeback_enabled": False,
                "credentials_in_repository": False,
                "portal_queries": self.portal_queries,
            },
        }
        self._write_outputs(result)
        self._phase(
            "publish",
            "ok",
            "Generated the dashboard JSON and run artifacts.",
            "已生成仪表盘 JSON 和运行产物。",
        )
        result["phases"] = self.phases
        self._write_outputs(result)
        return result

    def _write_outputs(self, result: dict[str, Any]) -> None:
        report_path = self.root / self.config["report"]["output"]
        artifact_dir = self.root / self.config["report"]["artifact_dir"]
        report_path.parent.mkdir(parents=True, exist_ok=True)
        artifact_dir.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (artifact_dir / "run_summary.json").write_text(
            json.dumps(result["summary"], ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (artifact_dir / "proposed_writeback.json").write_text(
            json.dumps(result["changes"], ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (artifact_dir / "errors.json").write_text(
            json.dumps(result["errors"], ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
