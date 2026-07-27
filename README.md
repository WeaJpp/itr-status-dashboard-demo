# ITR-status · Inspection Checker

[简体中文](README.zh-CN.md) · [Live demo](https://weajpp.github.io/itr-status-dashboard-demo/) · [Adaptation guide](docs/adaptation-guide.md)

A privacy-safe, runnable reference implementation for daily **engineering Inspection Request / Inspection & Test Report status checks**. It can also be adapted to other websites that require routine status queries.

This is a complete workflow, not a standalone static page:

```text
Ledger → preflight → identity validation → sequential website queries
       → exact result matching → status/revision rules
       → guarded proposals → bilingual dashboard
```

All records are synthetic. The public demo contains no production URL, password, cookie, token, Sheet ID, or real project identity, and it forcibly disables writeback.

## Two ways to connect a real website

### Method A: inspect HTML or API yourself

Observe one authorized manual query in Network → Fetch/XHR. Prefer a stable query, pagination, and authorized-download API. If none exists, use Playwright to locate the search input, unique result, final status, and download link. Implement `PortalAdapter`, then run fixtures, tests, and read-only preflight.

### Method B: use the AI prompt

The live page includes a copy-ready prompt for a browser-and-code capable AI. Fill in the authorized URL, ledger format, and identity column. The AI is instructed to remain read-only, keep secrets external, require exact identity matching, and add fixtures plus tests.

See the [complete adaptation guide](docs/adaptation-guide.md) for API extraction, download analysis, HTML selectors, environment variables, and the full prompt.

## Implemented safety logic

- JSON and CSV ledger adapters;
- offline portal fixture and optional HTTP JSON adapter;
- reject malformed identities such as `pending` before querying;
- verify exact `match_code` after every query;
- discard cancelled submissions and allowlist final statuses;
- exact `Issued For Inspection → UR` mapping;
- exact `Ready for Sign Off/Out → READY` mapping;
- ledger-authoritative `REV-00...REV-NN` targeting;
- preserve an explicit special `-20` identity;
- fail closed per row and emit no proposal when uncertain;
- generate proposal artifacts without modifying the source ledger.

## Run locally

Python 3.10+ is sufficient:

```bash
python -m unittest discover -s tests -v
python scripts/run_pipeline.py --config config.example.json
python -m http.server 8000 --directory public
```

Open `http://localhost:8000`. First visit defaults to Chinese; use the header toggle for English, or test directly with `?lang=zh` / `?lang=en`.

Generated files:

- `public/data/dashboard.json`
- `artifacts/run_summary.json`
- `artifacts/proposed_writeback.json`
- `artifacts/errors.json`

## Contributors

- [WeaJpp](https://github.com/WeaJpp) — creator and domain workflow
- [OpenAI Codex](https://github.com/codex) — implementation collaborator

MIT licensed.
