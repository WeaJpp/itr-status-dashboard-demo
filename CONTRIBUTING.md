# Contributing

Use synthetic data only. Never commit credentials, cookies, tokens, private URLs, selectors, production IDs, workbooks or exported portal content.

Before opening a pull request:

```bash
python -m unittest discover -s tests -v
python scripts/run_pipeline.py --config config.example.json
node --check public/app.js
```

Changes to identity, status, revision or writeback rules require focused tests. A new adapter must preserve preflight, exact result matching and row-level fail-closed behavior.
