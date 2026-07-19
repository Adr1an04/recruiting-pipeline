# Security policy

## Reporting a vulnerability

Please do not open a public issue for a suspected vulnerability and do not include credentials,
résumés, application data, email content, or other personal information in a report.

Use GitHub's private vulnerability reporting for
[`Adr1an04/erga-mcp`](https://github.com/Adr1an04/erga-mcp/security/advisories/new). Include:

- the affected version or commit;
- the relevant component and configuration;
- reproducible steps using synthetic data;
- the impact you observed; and
- a suggested mitigation, if you have one.

The maintainer will acknowledge a complete report as soon as practical, validate the issue, and
coordinate remediation and disclosure. Please allow time for a fix before publishing details.

## Supported versions

Erga is pre-alpha. Security fixes are applied to the latest code on the default branch; older
commits and unreleased snapshots are not maintained as separate supported lines.

## Security model

Erga's detailed trust boundaries, credential handling, content-safety rules, network-fetch
controls, and MCP capability classes are documented in [`docs/security.md`](docs/security.md).
