# Security

This public repository is an offline demonstration. It contains synthetic records and keeps writeback disabled.

Do not report real credentials or project data in a public issue. If you discover a vulnerability, contact the maintainer privately through the profile listed in the repository.

Never commit:

- usernames, passwords, cookies, session storage or tokens;
- private portal URLs, selectors, workbook IDs or production identifiers;
- real engineering records, attachments or exported browser data.

Production adapters should live in a private deployment and use environment-based secrets, least privilege, explicit scope, backups, audit logs and post-write verification.
