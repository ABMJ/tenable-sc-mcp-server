# Releasing

Use this lightweight checklist for each release.

This repository is community-maintained and is not an officially supported Tenable project.

## 1) Prepare

- Ensure `main` is green in CI.
- Confirm `CHANGELOG.md` includes release notes.
- Confirm docs updates are included for behavior changes.

## 2) Verify Locally

```bash
pip install -e .[dev]
ruff check src tests
mypy src
pytest -q
```

## 3) Tag And Release

- Create tag and GitHub release (for example `v0.1.1`).
- Keep notes focused on user-visible changes.

## 4) Post-Release

- Move/assign open issues to next milestone.
- Label urgent regressions as `priority:high`.
