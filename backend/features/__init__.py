"""Feature package root.

Each subpackage is a hexagonal feature exposing ``domain`` and ``application``
plus inbound/outbound adapters. Features never import each other's internals
directly; they cooperate through the shared ports in :mod:`backend.shared`.
"""
