# Changelog

## 0.1.1 - 2026-07-01

- Hardened GitHub Actions permissions and Docker runtime user defaults.
- Added trusted-root validation for CLI manifest verification to prevent
  untrusted manifests from reading outside the intended shard directory.

## 0.1.0 - 2026-06-22

- Added manifest persistence, validation, row-count inference, and media-type
  metadata.
- Added deterministic worker plan serialization.
- Added checkpoint progress summaries and atomic checkpoint writes.
- Added manifest verification, manifest diffing, and resume-aware worker plans.
- Added CLI version output, manifest inspection, schema output, Markdown reports,
  all-worker plans, diagnostics, Makefile helpers, and community templates.
- Added CLI commands for indexing, planning, and checkpoint status.
- Added GitHub Actions, contribution guidance, security policy, packaging
  metadata, Dockerfile, release-artifact workflow, and sample shard data.
