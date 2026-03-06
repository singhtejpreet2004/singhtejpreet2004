"""GitHub stats SVG generator.

Fetches contribution and repository data from the GitHub GraphQL API
and writes self-hosted SVG cards to assets/generated/.
"""

import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

USERNAME = "singhtejpreet2004"
OUTPUT_DIR = Path(__file__).parent.parent / "assets" / "generated"

GRAPHQL_URL = "https://api.github.com/graphql"
REST_URL = f"https://api.github.com/users/{USERNAME}/repos?per_page=100&sort=stars"

QUERY = """
query($login: String!) {
  user(login: $login) {
    repositories(first: 100, ownerAffiliations: OWNER, isFork: false) {
      nodes { stargazerCount forks { totalCount } primaryLanguage { name } }
    }
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays { contributionCount date }
        }
      }
    }
    followers { totalCount }
    following { totalCount }
  }
}
"""


def fetch_data(token: str) -> dict:
    """Fetch user stats via GitHub GraphQL API."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    resp = requests.post(
        GRAPHQL_URL,
        headers=headers,
        json={"query": QUERY, "variables": {"login": USERNAME}},
        timeout=30,
    )
    resp.raise_for_status()
    body = resp.json()
    if "errors" in body:
        raise RuntimeError(f"GraphQL errors: {body['errors']}")
    return body["data"]["user"]


def compute_streak(weeks: list[dict]) -> dict[str, int]:
    """Compute current and longest streak from contribution calendar weeks."""
    days = [
        day
        for week in weeks
        for day in week["contributionDays"]
    ]
    days.sort(key=lambda d: d["date"])

    current = 0
    longest = 0
    tmp = 0
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    for day in reversed(days):
        if day["date"] > today_str:
            continue
        if day["contributionCount"] > 0:
            if current == 0:
                current += 1
            else:
                current += 1
        else:
            break

    for day in days:
        if day["contributionCount"] > 0:
            tmp += 1
            longest = max(longest, tmp)
        else:
            tmp = 0

    return {"current": current, "longest": longest}


def make_stats_svg(data: dict) -> str:
    """Generate a dark-theme stats card SVG."""
    repos = data["repositories"]["nodes"]
    total_stars = sum(r["stargazerCount"] for r in repos)
    total_forks = sum(r["forks"]["totalCount"] for r in repos)

    contrib = data["contributionsCollection"]
    total_commits = contrib["totalCommitContributions"]
    total_prs = contrib["totalPullRequestContributions"]
    total_issues = contrib["totalIssueContributions"]
    total_contribs = contrib["contributionCalendar"]["totalContributions"]

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    rows = [
        ("Total Contributions", str(total_contribs), "⚡"),
        ("Commits This Year",   str(total_commits),  "📝"),
        ("Pull Requests",       str(total_prs),       "🔀"),
        ("Issues Opened",       str(total_issues),    "🐛"),
        ("Total Stars Earned",  str(total_stars),     "⭐"),
        ("Total Forks",         str(total_forks),     "🍴"),
    ]

    row_svgs = "\n".join(
        f'<text x="24" y="{130 + i * 36}" fill="#8b949e" font-size="13" font-family="Fira Code, monospace">'
        f'{icon} {label}</text>'
        f'<text x="376" y="{130 + i * 36}" fill="#e6edf3" font-size="13" '
        f'font-family="Fira Code, monospace" text-anchor="end" font-weight="600">{value}</text>'
        for i, (label, value, icon) in enumerate(rows)
    )

    return f"""<svg width="400" height="360" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#667eea" stop-opacity="0.15"/>
      <stop offset="100%" stop-color="#764ba2" stop-opacity="0.05"/>
    </linearGradient>
    <filter id="glow"><feGaussianBlur stdDeviation="3" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <rect width="400" height="360" rx="12" fill="#161b22" stroke="#30363d" stroke-width="1"/>
  <rect width="400" height="360" rx="12" fill="url(#g)"/>
  <rect x="24" y="60" width="60" height="3" rx="2" fill="#667eea"/>
  <text x="24" y="48" fill="#e6edf3" font-size="18" font-weight="700"
        font-family="Fira Code, monospace" filter="url(#glow)">📊 GitHub Stats</text>
  <text x="24" y="78" fill="#667eea" font-size="11" font-family="Fira Code, monospace">@{USERNAME}</text>
  <line x1="24" y1="100" x2="376" y2="100" stroke="#30363d" stroke-width="1"/>
  {row_svgs}
  <line x1="24" y1="336" x2="376" y2="336" stroke="#30363d" stroke-width="1"/>
  <text x="24" y="352" fill="#30363d" font-size="10" font-family="Fira Code, monospace">Updated: {now}</text>
</svg>"""


def make_streak_svg(streak: dict[str, int]) -> str:
    """Generate a streak card SVG."""
    current = streak["current"]
    longest = streak["longest"]
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return f"""<svg width="400" height="180" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="sg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#f78166" stop-opacity="0.15"/>
      <stop offset="100%" stop-color="#764ba2" stop-opacity="0.05"/>
    </linearGradient>
  </defs>
  <rect width="400" height="180" rx="12" fill="#161b22" stroke="#30363d" stroke-width="1"/>
  <rect width="400" height="180" rx="12" fill="url(#sg)"/>
  <text x="200" y="44" fill="#8b949e" font-size="12" font-family="Fira Code, monospace"
        text-anchor="middle">🔥 CONTRIBUTION STREAK</text>
  <text x="200" y="108" fill="#f78166" font-size="56" font-weight="700"
        font-family="Inter, sans-serif" text-anchor="middle">{current}</text>
  <text x="200" y="132" fill="#8b949e" font-size="12" font-family="Fira Code, monospace"
        text-anchor="middle">current streak (days)</text>
  <text x="200" y="162" fill="#667eea" font-size="11" font-family="Fira Code, monospace"
        text-anchor="middle">longest: {longest} days &nbsp;•&nbsp; {now}</text>
</svg>"""


def make_languages_svg(repos: list[dict]) -> str:
    """Generate a top languages bar SVG."""
    lang_counts: dict[str, int] = {}
    for repo in repos:
        lang = repo.get("primaryLanguage")
        if lang and lang.get("name"):
            lang_counts[lang["name"]] = lang_counts.get(lang["name"], 0) + 1

    top = sorted(lang_counts.items(), key=lambda x: -x[1])[:6]
    total = sum(c for _, c in top) or 1

    lang_colors = {
        "Python": "#3572A5", "SQL": "#e38c00", "Shell": "#89e051",
        "JavaScript": "#f1e05a", "TypeScript": "#2b7489", "Go": "#00ADD8",
        "Rust": "#dea584", "Dockerfile": "#384d54", "HCL": "#844FBA",
        "YAML": "#cb171e",
    }

    bars = ""
    x = 0
    for lang, count in top:
        pct = count / total
        color = lang_colors.get(lang, "#8b949e")
        bars += f'<rect x="{24 + x:.1f}" y="80" width="{352 * pct:.1f}" height="12" rx="3" fill="{color}"/>'
        x += 352 * pct

    labels = "\n".join(
        f'<text x="{24 + i * 64}" y="116" fill="#8b949e" font-size="10" '
        f'font-family="Fira Code, monospace">'
        f'<tspan fill="{lang_colors.get(lang, "#8b949e")}">■</tspan> {lang} {count / total * 100:.0f}%'
        f'</text>'
        for i, (lang, count) in enumerate(top)
    )

    return f"""<svg width="400" height="130" xmlns="http://www.w3.org/2000/svg">
  <rect width="400" height="130" rx="12" fill="#161b22" stroke="#30363d" stroke-width="1"/>
  <text x="24" y="44" fill="#e6edf3" font-size="14" font-weight="700"
        font-family="Fira Code, monospace">🧠 Top Languages</text>
  <rect x="24" y="56" width="60" height="2" rx="1" fill="#667eea"/>
  {bars}
  {labels}
</svg>"""


def main() -> None:
    """Entry point — fetch data and write SVGs."""
    token = os.environ.get("GH_TOKEN")
    if not token:
        log.error("GH_TOKEN environment variable is not set")
        sys.exit(1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    log.info("Fetching GitHub data for @%s", USERNAME)
    data = fetch_data(token)

    weeks = data["contributionsCollection"]["contributionCalendar"]["weeks"]
    streak = compute_streak(weeks)
    repos = data["repositories"]["nodes"]

    log.info("Writing stats SVG")
    (OUTPUT_DIR / "stats.svg").write_text(make_stats_svg(data), encoding="utf-8")

    log.info("Writing streak SVG (current=%d, longest=%d)", streak["current"], streak["longest"])
    (OUTPUT_DIR / "streak.svg").write_text(make_streak_svg(streak), encoding="utf-8")

    log.info("Writing languages SVG")
    (OUTPUT_DIR / "languages.svg").write_text(make_languages_svg(repos), encoding="utf-8")

    log.info("Done — all SVGs written to %s", OUTPUT_DIR)


if __name__ == "__main__":
    main()
