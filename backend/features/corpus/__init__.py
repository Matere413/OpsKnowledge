"""Corpus feature: manifest-controlled synthetic knowledge boundary.

Exposes the immutable fragment domain model, the loading policy, and the
manifest adapter. The loader consumes the development-only synthetic corpus
from ``evaluation-dataset/`` and fails closed on any non-development,
non-synthetic, unapproved, invalid-parent, mixed-language, or unlisted path.
"""
