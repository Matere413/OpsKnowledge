# Approved Source Inventory Specification

## Purpose

Define a provider-independent, development-only boundary for a complete current snapshot of approved source metadata. It does not ingest, interpret, persist, publish, or synchronize content.

## Requirements

### Requirement: Immutable provider-neutral source contract

The system MUST expose immutable metadata for repository-relative path, collection, entry, language, revision, approval, classification, and hash. A repository port MUST return a complete snapshot or rejection; domain and application contracts MUST NOT depend on a provider.

#### Scenario: Metadata-only result

- GIVEN a valid development artifact
- WHEN inventory scans it
- THEN the port returns immutable metadata and no interpreted content

### Requirement: Manifest authority

The controlled manifest MUST authorize approval, classification, collection, path, and expected hash. A filename MUST NOT prove approval; a hash mismatch or manifest disagreement MUST reject the snapshot.

#### Scenario: Filename cannot override policy

- GIVEN a validly named artifact with an unapproved, non-synthetic, or mismatched manifest record
- WHEN it is scanned
- THEN the complete snapshot is rejected

### Requirement: Filename identity and independent revisions

Filenames MUST match `<entry-id>_ESP_REV_<revision>.pdf` or `<entry-id>_EN_REV_<revision>.pdf`. Tokens MUST be non-empty, contain no separators, controls, or whitespace, and remain unnormalized. Identity MUST include collection, entry, language, and revision; Spanish and English revisions are independent.

#### Scenario: Bilingual revisions remain distinct

- GIVEN `runbook-1_ESP_REV_2.pdf` and `runbook-1_EN_REV_7.pdf` with valid manifest records
- WHEN both are scanned
- THEN both identities are accepted without comparing revisions across languages

### Requirement: Safe paths and deterministic output

Accepted paths MUST be normalized repository-relative paths within the configured root; absolute paths, traversal, and external links MUST be rejected. Entries and diagnostics MUST be stably ordered. Diagnostics MUST omit absolute paths, bytes, document text, secrets, credentials, and provider payloads.

#### Scenario: Unsafe paths fail consistently

- GIVEN an escaping path or changed enumeration order
- WHEN inventory runs
- THEN the unsafe artifact is rejected and valid output ordering remains byte-stable

### Requirement: Explicit complete-scan semantics

A scan MUST be complete only after enumeration, manifest coverage, reads, and validation finish without omission or uncertainty. A completed zero-artifact scan MUST return a valid immutable empty snapshot; an incomplete scan MUST NOT appear empty.

#### Scenario: Empty success differs from partial failure

- GIVEN either a completed empty fixture or a scan that stops before coverage/read completion
- WHEN inventory is requested
- THEN it returns an empty complete snapshot in the first case and no snapshot with an incomplete-scan rejection in the second

### Requirement: Whole-snapshot fail-closed validation

Invalid names, duplicate identities, missing records, unreadable artifacts, unsafe paths, hash mismatches, invalid manifest records, and incomplete scans MUST reject the entire snapshot. Partial valid entries MUST NOT be returned as current inventory.

#### Scenario: One bad artifact rejects all

- GIVEN valid artifacts plus one unreadable or invalid artifact
- WHEN scanning encounters the failure
- THEN no current snapshot or partial subset is returned

### Requirement: Development synthetic fixture isolation

The local adapter MUST run only in the development profile against a manifest-controlled synthetic fixture outside `evaluation-dataset/`. It MUST NOT reuse or modify the evaluation loader and MUST deny non-development initialization.

#### Scenario: Evaluation corpus stays separate

- GIVEN `evaluation-dataset/` or a non-development profile
- WHEN source inventory is initialized
- THEN initialization is denied before any source artifact is scanned

### Requirement: Corporate boundary and exclusions

This change MUST NOT access SharePoint/Graph, Entra, corporate documents, managed identity, private endpoints, or a corporate adapter. Phase 8 identity, authorization, privacy/sensitive-screening, controlled-provider, and TI gates remain prerequisites. PDF/OCR extraction, interpretation, embeddings, PostgreSQL/index persistence, publication, rollback, cleanup, scheduling, administration, diff/synchronization, and provider egress are excluded.

#### Scenario: Corporate access is denied

- GIVEN corporate configuration or a corporate-source request
- WHEN inventory initializes
- THEN it fails closed before source access with a safe boundary diagnostic
