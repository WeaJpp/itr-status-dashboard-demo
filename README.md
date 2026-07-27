Exit code: 0
Wall time: 2.6 seconds
Output:
# ITR Status Dashboard — Public Demo

A privacy-safe static demonstration of a railway QA/QC Inspection & Test Report (ITR) status dashboard.

## Live demo

After GitHub Pages is enabled, the demo is available from the repository's Pages URL.

## Features

- Status KPI cards for CODE-1, CODE-2, CODE-4, CODE-5, UR, and DRAFT
- Per-site status distribution
- Search and filters for site and status
- Filtered CSV export
- Responsive layout and light/dark theme
- No build step and no backend

## Run locally

Open `index.html` directly, or serve this folder with any static file server:

```bash
python -m http.server 8000
```

Then open <http://localhost:8000>.

## Privacy and security

This repository contains synthetic sample data only:

- Site names use the `Demo` prefix.
- Record IDs use the `DEMO-GQC-IR-xxxxx` format.
- Dates, quantities, chainages, processes, and statuses are fictional.
- There are no passwords, cookies, API keys, service-account files, customer names, internal URLs, Google Sheet IDs, or live integrations.

Do not copy production data into this public repository. For real deployments, keep secrets server-side and provide public pages only with approved, sanitized data.

## Project structure

```text
.
├── index.html
├── styles.css
├── app.js
├── SECURITY.md
├── LICENSE
└── .github/workflows/pages.yml
```

## License

MIT

