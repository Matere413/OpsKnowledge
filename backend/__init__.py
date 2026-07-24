"""OpsKnowledge backend runtime.

Feature-organized modular monolith with hexagonal boundaries. Each feature
exposes ``domain``, ``application``, and inbound/outbound adapters. Frameworks,
providers, and infrastructure stay outside ``domain`` and ``application``.

This package is introduced by the ``build-minimal-grounded-opsknowledge-core``
SDD change. Work Unit 1 (PR 1) lands the corpus boundary and shared ports;
query, provider, and CLI arrive in later slices.
"""
