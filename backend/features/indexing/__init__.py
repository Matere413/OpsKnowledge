"""Indexing feature: provider-neutral approved source inventory.

Feature-organized module exposing the domain value objects, application
use case, and outbound repository port for a complete current snapshot of
approved source metadata. The feature does not ingest, interpret, persist,
publish, or synchronize content; it returns immutable metadata only.

Introduced by the ``integrate-approved-source-repository`` SDD change.
Work Unit 1 (PR 1) lands the provider-neutral contracts and application gate;
the local development adapter and fixture arrive in a later slice.
"""
