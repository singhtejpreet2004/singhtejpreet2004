# singhtejpreet2004 — GitHub Profile README

## What This Repo Is
Special GitHub profile repo (`singhtejpreet2004/singhtejpreet2004`).
- `README.md` — the profile page shown on github.com/singhtejpreet2004
- `docs/` — GitHub Pages site (stats dashboard + D3.js stack visualizer)
- `scripts/generate_stats.py` — generates SVG cards daily via GitHub Action
- `assets/generated/` — auto-committed SVG output (do not edit manually)

## GitHub Pages
Enabled from `docs/` folder on `main` branch.
- Hub: `singhtejpreet2004.github.io/singhtejpreet2004/`
- Stats: `singhtejpreet2004.github.io/singhtejpreet2004/stats/`
- Stack: `singhtejpreet2004.github.io/singhtejpreet2004/stack/`

## Secrets Required
- `GH_TOKEN` — fine-grained PAT with Contents: Read & Write

## Actions
- `update_stats.yml` — daily cron, generates SVGs via GraphQL API
- `snake.yml` — daily cron, generates snake animation to `output` branch

## Things to Update
- LinkedIn URL in README.md (`linkedin.com/in/tejpreet-singh` — verify this)
- Email in README.md
- Add new projects to the featured section as they go public
