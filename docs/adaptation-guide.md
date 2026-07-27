# Website adaptation guide

Use either method below only for a website you are authorized to access. Keep phase one read-only: no ledger writes, form submissions, or unauthorized attachment downloads.

## Method A: inspect the API or HTML yourself

Start with 1–3 non-sensitive test identities. In browser DevTools, clear the Network panel, filter to Fetch/XHR, and perform one manual search. Identify the request method, query/body fields, pagination, and response fields for identity, final status, lifecycle, and timestamp.

For an authorized download, inspect whether the file comes from a normal link, a signed URL, or a download API. Record the contract—not authorization headers, cookies, passwords, or real response data. Check that every downloaded file remains exactly traceable to its requested identity.

When there is no stable API, use Playwright and stable accessible names, IDs, or `data-*` attributes for:

- the search input and submit action;
- the unique result card and identity field;
- submission history and final status;
- attachment links.

Implement `PortalAdapter` so that one query returns only the public contract:

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

The pipeline then verifies exact identity, removes cancelled lifecycle entries, applies the status allowlist and revision rules, and fails closed on uncertainty. Keep secrets in environment variables and run tests plus a read-only preflight before scheduling.

## Method B: use the AI prompt

```text
Help me connect “ITR-status · Inspection Checker” to a website I am authorized to access.

Goal: read inspection identities from my ledger, query the final active status, and generate dashboard.json. Phase one must be read-only.

1. Run the existing tests and inspect config.example.json, PortalAdapter, and status rules.
2. Observe one manual test query with browser DevTools.
3. Prefer Network Fetch/XHR for query, pagination, and download endpoints; use Playwright HTML selectors only when no stable API exists.
4. Never print or commit passwords, cookies, tokens, private URLs, or production records. Read secrets only from environment variables.
5. Require an exact match_code, discard Cancelled lifecycle entries, allowlist statuses, and fail closed on uncertainty.
6. Add offline fixtures, focused tests, and a preflight-only mode.
7. List the environment variables and configuration I must provide, then give runnable commands.

Authorized site: [URL]
Ledger: [JSON / CSV / Excel / Google Sheet]
Identity column: [name]
Attachment download allowed: [yes / no]
```

Review the AI's query scope, identity matching, status semantics, and all possible write operations before using it with production data.
