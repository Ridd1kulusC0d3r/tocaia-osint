# Security policy

## Reporting

Please report vulnerabilities privately through GitHub's security reporting features when available. Do not include live credentials, personal data or sensitive target information in public issues.

## Scope

Security issues include, among other things:

- path traversal or unsafe file handling;
- unintended network egress from analysis components;
- provenance or integrity bypasses;
- unsafe deserialization;
- collection behavior that violates the repository's passive posture.

The public reference implementation is intentionally small so these properties can be audited before the project grows into a dependency hydra.
