# ITR Status Dashboard

[简体中文](README.zh-CN.md) · [Live demo](https://weajpp.github.io/itr-status-dashboard-demo/)

A privacy-safe, runnable reference implementation for checking **engineering Inspection Request / Inspection & Test Report status** every day. The adapter pattern also makes it useful for other websites that require routine status queries.

This repository is not merely a dashboard. It includes the complete safe path from a source ledger to query evidence:

```text
Ledger → preflight → identity validation → sequential query
       → exact result matching → status/revision rules
       → guarded proposals → bilingual dashboard
```

All names, IDs, locations and results are synthetic. No production URL, account, password, cookie, token, Sheet ID or project identifier is included. Public-demo writeback is forcibly disabled.

## What is implemented

- JSON and CSV source-ledger adapters
- deterministic offline portal fixture for CI and GitHub Pages
- optional HTTP JSON adapter contract for a private sanitized gateway
- reject-before-query validation for malformed identities such as `pending`
- exact `match_code` verification after every query
- cancelled-submission filtering and strict status allowlist
- exact mappings: `Issued For Inspection → UR`, `Ready for Sign Off/Out → READY`
- ledger-authoritative `REV-00`, `REV-01` revision targeting
- special handling that preserves an explicit `-20` identity
- row-level fail-closed errors; one uncertain row never becomes a writeback
- proposal artifacts rather than real public writeback
- full Chinese or full English UI selected from browser language, plus a manual toggle
- unit tests and scheduled GitHub Pages generation

## Run locally

Python 3.10+ is enough; the pipeline has no third-party dependency.

```bash
python -m unittest discover -s tests -v
python scripts/run_pipeline.py --config config.example.json
python -m http.server 8000 --directory public
```

Open `http://localhost:8000`. Use `?lang=zh` or `?lang=en` to force a language while testing.

Generated files:

- `public/data/dashboard.json` — frontend data contract
- `artifacts/run_summary.json` — run-level result
- `artifacts/proposed_writeback.json` — reviewed change proposals
- `artifacts/errors.json` — unresolved rows

## Adapt it to a real system

Implement `SourceAdapter` for the authoritative workbook/database and `PortalAdapter` for your permitted website or internal API. A portal result must follow this minimum contract:

```json
{
  "match_code": "DEMO-GQC-IR-00001",
  "submissions": [
    {
      "label": "Issued For Inspection",
      "lifecycle": "Active",
      "updated_at": "2026-07-27T05:10:00Z"
    }
  ]
}
```

Keep real endpoints, selectors and authentication in a private deployment. The public configuration refuses `writeback.enabled=true`; production writeback should be a separately reviewed adapter with backups, scope checks and audit logs.

See [Architecture](docs/architecture.md), [Contributing](CONTRIBUTING.md), and [Security](SECURITY.md).

## Repository map

```text
src/itr_pipeline/       Pipeline, adapters, rules and data models
scripts/run_pipeline.py Command-line entry point
sample_data/            Synthetic ledger and portal responses
tests/                  Safety and workflow tests
public/                 Language-aware dashboard
.github/workflows/      Test, generate and deploy
```

## Contributors

- [WeaJpp](https://github.com/WeaJpp) — creator and domain workflow
- [OpenAI Codex](https://github.com/codex) — implementation collaborator

MIT licensed.
