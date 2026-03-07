---
paths:
  - "src/**/*gdpr*"
  - "src/**/*privacy*"
  - "src/**/*retention*"
  - "src/**/*suppression*"
  - "src/**/*export*"
  - "src/**/*import*"
---

# Data Privacy & Retention

## Retention Policy
- Define retention periods per data type in a design doc or config
- Expired data SHALL be pseudonymized or deleted, never left stale
- Pseudonymization: replace PII with a fixed placeholder (e.g., `[REMOVED]`), keep the record for referential integrity
- Aggregate before delete where analytics depend on historical counts

## Suppression / Opt-Out
- Check suppression list before EVERY contact creation or outreach path
- Suppression is org-scoped and case-insensitive on email/identifier
- Opt-out flags are write-once (`true`) — never programmatically reset to `false`

## Data Export
- Export function SHALL be restricted to authorized roles (admin+)
- Exclude internal tokens, confidence scores, and org-internal IDs from export
- Time-bound activity data (e.g., 90-day window) to limit exposure

## Data Import / Dedup
- Deduplicate on stable business identifiers (tax number, registration ID, etc.)
- Run suppression check on contact fields (warn, don't block)
- Header matching SHALL be case-insensitive with auto-detection
