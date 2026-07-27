# Architecture and safety boundary

The ledger is authoritative. A run reads it once, validates every identity, skips configured terminal states, and queries eligible rows sequentially. A returned result is accepted only when its `match_code` equals the requested identity. Cancelled lifecycle entries are ignored; the final active submission must resolve to exactly one allowlisted status.

Revision targeting is derived from contiguous ledger headers beginning at `REV-00`. A transition after a completed `CODE-*` value requires the next revision column. If it is missing, the row fails closed. An explicit `-20` suffix is treated as an identity rule, not ordinary revision 20.

```text
SourceAdapter
    │
    ▼
Preflight ── failure ──► stop run
    │
    ▼
Identity validation ── malformed ──► row error, no query
    │
    ▼
PortalAdapter (one row at a time)
    │
    ▼
Exact identity + final active status
    │
    ├── uncertain ──► row error, no proposal
    ▼
Revision rules ── unsafe ──► row error, no proposal
    │
    ▼
Proposal artifacts ──► dashboard JSON ──► GitHub Pages
```

The demo never writes to a ledger. A production writer should be a separate private component with explicit scope, pre-write backup, idempotency, audit logs and post-write verification.
