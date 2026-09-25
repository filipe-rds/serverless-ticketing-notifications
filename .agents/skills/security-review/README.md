# Security Review

**Version**: 1.0.0
**Type**: skills
**Authors**: aigile

## Overview

Static security code review simulating a Red Team, focused on OWASP Top 10 vulnerabilities and security best practices.

## Usage

Point to the code to inspect. The skill maps the attack surface, analyzes against OWASP categories (injection, auth, access control, data exposure, misconfiguration), produces severity-ranked findings, and applies corrections after approval. Report at `docs/<feature>/security-report-<feature>.md`.

## Dependencies

None
