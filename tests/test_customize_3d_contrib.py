#!/usr/bin/env python3
"""Regression tests for accurate dynamic GitHub contribution footer counters."""

from __future__ import annotations

import importlib.util
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / "scripts" / "customize-3d-contrib.py"
SPEC = importlib.util.spec_from_file_location("contribution_footer", FILE)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def sample_svg(commits: int = 49, prs: int = 16) -> str:
    return (
        '<svg xmlns="http://www.w3.org/2000/svg">'
        f'<g><text>Commit<title>{commits}</title></text>'
        f'<text>PullReq<title>{prs}</title></text></g>'
        '<g><text x="384" y="830">70</text>'
        '<text x="394" y="830">contributions</text>'
        '<g transform="translate(608, 802), scale(2)"><path d="M8 0"></path></g>'
        '<text x="650" y="830">0<title>0</title></text>'
        '<g transform="translate(736, 802), scale(2)"><path d="M5 0"></path></g>'
        '<text style="font-size: 32px" x="772" y="830" class="fill-fg">0<title>0</title></text>'
        '</g></svg>'
    )


class ContributionFooterTests(unittest.TestCase):
    def test_replaces_both_misleading_social_counters(self):
        source = sample_svg()
        actual = MODULE.update_svg(source)
        self.assertIn('aria-label="49 commits"', actual)
        self.assertIn('aria-label="16 pull requests"', actual)
        self.assertIn('>COMMITS</text>', actual)
        self.assertIn('>PULL REQUESTS</text>', actual)
        self.assertNotIn('translate(608, 802), scale(2)', actual)
        self.assertNotIn('x="772" y="830"', actual)
        self.assertIn('>70</text>', actual)

    def test_metrics_are_taken_from_svg_not_hardcoded(self):
        changed = MODULE.update_svg(sample_svg(commits=73, prs=24))
        self.assertIn('aria-label="73 commits"', changed)
        self.assertIn('aria-label="24 pull requests"', changed)
        self.assertNotIn('aria-label="49 commits"', changed)

    def test_repeated_transform_is_idempotent(self):
        once = MODULE.update_svg(sample_svg(commits=6, prs=4))
        self.assertEqual(MODULE.update_svg(once), once)

    def test_refuses_incomplete_or_changed_upstream_output(self):
        with self.assertRaisesRegex(ValueError, "Upstream SVG footer changed"):
            MODULE.update_svg(
                '<svg><text>Commit<title>12</title></text>'
                '<text>PullReq<title>5</title></text></svg>'
            )
        with self.assertRaisesRegex(ValueError, "Expected exactly one GitHub"):
            MODULE.update_svg('<svg>nothing found</svg>')

    def test_can_transform_live_repository_asset(self):
        path = ROOT / "profile-3d-contrib" / "profile-night-rainbow.svg"
        current = path.read_text(encoding="utf-8")
        updated = MODULE.update_svg(current)
        self.assertIn(MODULE.COMMIT_BADGE_ID, updated)
        self.assertIn(MODULE.PR_BADGE_ID, updated)
        self.assertTrue(updated.startswith("<svg"))
        self.assertTrue(updated.endswith("</svg>"))
        self.assertIn('contributions</text>', updated)
        self.assertEqual(len(re.findall(MODULE.COMMIT_BADGE_ID, updated)), 1)
        self.assertEqual(len(re.findall(MODULE.PR_BADGE_ID, updated)), 1)


if __name__ == "__main__":
    unittest.main()
