#!/usr/bin/env python3
"""Replace the generated 3D SVG's star/fork footer with real commit/PR counts.

Numbers come from the same generated GitHub activity radar as the visualization.
Run this after yoshi389111/github-profile-3d-contrib. No personal access token or
external dependency is needed. Fail rather than display inaccurate statistics.
"""

from __future__ import annotations

import re
from pathlib import Path

DEFAULT_IMAGE = Path("profile-3d-contrib/profile-night-rainbow.svg")

COMMIT_PATTERN = re.compile(r">Commit<title>(\d+)</title></text>")
PULL_PATTERN = re.compile(r">PullReq<title>(\d+)</title></text>")

# The upstream generator's two footer counters are repository stars and forks.
# Both are replaced together so the branch-shaped fork icon is not confused
# with the Pull Requests contribution metric shown in the radar.
LEGACY_SOCIAL_METRICS = re.compile(
    r'<g transform="translate\(608,\s*802\),\s*scale\(2\)">.*?'
    r'<text\b[^>]*\bx="772"\s+y="830"[^>]*>\d+<title>\d+</title></text>',
    re.DOTALL,
)

COMMIT_BADGE_ID = 'id="contribution-summary-commits"'
PR_BADGE_ID = 'id="contribution-summary-pull-requests"'


def unique_count(pattern: re.Pattern[str], svg: str, name: str) -> int:
    matches = pattern.findall(svg)
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one GitHub {name} metric, found {len(matches)}")
    return int(matches[0])


def contribution_badges(commits: int, pull_requests: int) -> str:
    """Render clear, accessible footer statistics without stars or fork icons."""
    return f'''<g id="contribution-summary-commits" role="group" aria-label="{commits} commits">
  <title>{commits} GitHub commits in the generated activity period</title>
  <rect x="572" y="786" width="204" height="55" rx="12" fill="#102538" stroke="#367e89" stroke-width="1.3"></rect>
  <path d="M587 812H593 M607 812H614" stroke="#6be7d5" stroke-width="2.5" stroke-linecap="round"></path>
  <circle cx="600" cy="812" r="7" fill="#102538" stroke="#6be7d5" stroke-width="2.5"></circle>
  <text x="632" y="810" font-size="23" font-weight="bold" class="fill-fg">{commits}</text>
  <text x="632" y="830" font-size="13" font-weight="bold" fill="#82e5db">COMMITS</text>
</g>
<g id="contribution-summary-pull-requests" role="group" aria-label="{pull_requests} pull requests">
  <title>{pull_requests} GitHub pull requests in the generated activity period</title>
  <rect x="788" y="786" width="218" height="55" rx="12" fill="#1b183d" stroke="#8072d9" stroke-width="1.3"></rect>
  <circle cx="812" cy="802" r="4" fill="none" stroke="#bea9ff" stroke-width="2"></circle>
  <circle cx="812" cy="825" r="4" fill="none" stroke="#bea9ff" stroke-width="2"></circle>
  <circle cx="833" cy="802" r="4" fill="none" stroke="#bea9ff" stroke-width="2"></circle>
  <path d="M812 806V821 M833 806V812Q833 818 825 818H823" fill="none" stroke="#bea9ff" stroke-width="2" stroke-linecap="round"></path>
  <text x="852" y="810" font-size="23" font-weight="bold" class="fill-fg">{pull_requests}</text>
  <text x="852" y="830" font-size="13" font-weight="bold" fill="#c9b8ff">PULL REQUESTS</text>
</g>'''


def update_svg(svg: str) -> str:
    commits = unique_count(COMMIT_PATTERN, svg, "commit")
    prs = unique_count(PULL_PATTERN, svg, "pull request")

    # Repeated executions must not create duplicate counters.
    already_commits = COMMIT_BADGE_ID in svg
    already_prs = PR_BADGE_ID in svg
    if already_commits or already_prs:
        if not (already_commits and already_prs):
            raise ValueError("Only one custom contribution badge is present")
        if (f'aria-label="{commits} commits"' not in svg or
                f'aria-label="{prs} pull requests"' not in svg):
            raise ValueError("Badge counts do not match the generated radar data")
        return svg

    matches = list(LEGACY_SOCIAL_METRICS.finditer(svg))
    if len(matches) != 1:
        raise ValueError(
            f"Upstream SVG footer changed: expected one star/fork pair, "
            f"found {len(matches)}. Refusing to publish stale or invented numbers."
        )

    rendered = contribution_badges(commits, prs)
    match = matches[0]
    return svg[:match.start()] + rendered + svg[match.end():]


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    args = parser.parse_args()
    current = args.image.read_text(encoding="utf-8")
    updated = update_svg(current)
    if updated != current:
        args.image.write_text(updated, encoding="utf-8")

    commits = unique_count(COMMIT_PATTERN, updated, "commit")
    prs = unique_count(PULL_PATTERN, updated, "pull request")
    print(f"3D contribution footer verified: {commits} commits, {prs} pull requests")


if __name__ == "__main__":
    main()
