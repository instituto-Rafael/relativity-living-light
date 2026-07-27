#!/usr/bin/env python3
"""Stable entry point for the RLL canonical-region generator."""
from _rll_canonical_generator_impl import RELATIONS, main

# Compatibility correction for the transport-time typo preserved in the
# implementation blob. The canonical manifest key remains INDEX_POINTER.
RELATIONS["INDEX_POINTER"] = RELATIONS.pop("INDEQ_POINTER", 6)

if __name__ == "__main__":
    raise SystemExit(main())
