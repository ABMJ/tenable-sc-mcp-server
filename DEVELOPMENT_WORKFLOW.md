# Development Workflow & Branching Strategy

**Version:** 1.0  
**Created:** 2026-06-19  
**Last Updated:** 2026-06-19  
**Project:** Tenable.sc MCP Server

---

## Overview

This document establishes the development workflow that keeps `main` branch production-ready while enabling continuous feature development. It defines branching strategies, release processes, and best practices for contributing to this project.

---

## Branching Strategy

We follow a **GitHub Flow** variant with production-ready `main` and feature branches.

### Branch Structure

```
main (production-ready, protected)
  ├── develop (integration branch for testing)
  ├── feature/os-exact-matching
  ├── feature/plugin-family-lookup
  ├── bugfix/cache-memory-leak
  └── hotfix/critical-auth-issue
```

### Branch Types

| Branch Type | Naming Convention | Purpose | Merges To |
|-------------|-------------------|---------|-----------|
| `main` | `main` | Production-ready code, tagged releases | N/A (protected) |
| `develop` | `develop` | Integration branch for testing features | `main` |
| `feature/*` | `feature/<short-description>` | New features and enhancements | `develop` |
| `bugfix/*` | `bugfix/<issue-description>` | Non-critical bug fixes | `develop` |
| `hotfix/*` | `hotfix/<critical-issue>` | Critical production fixes | `main` + `develop` |
| `docs/*` | `docs/<doc-name>` | Documentation-only changes | `main` or `develop` |
| `release/*` | `release/v<version>` | Release preparation and testing | `main` |

---

## Workflow Details

### 1. Feature Development Workflow

**Use Case:** Adding new tools, filters, or non-breaking enhancements

**Steps:**

```bash
# 1. Create feature branch from develop
git checkout develop
git pull origin develop
git checkout -b feature/user-ioes-summary

# 2. Develop and commit frequently
# Follow commit message conventions (see below)
git add .
git commit -m "feat: Add tsc_summarize_users_ioes tool"

# 3. Push feature branch regularly
git push -u origin feature/user-ioes-summary

# 4. Create Pull Request to develop
# - Add description of changes
# - Reference any related issues
# - Request code review
# - Ensure tests pass

# 5. After approval, merge to develop
# GitHub will handle merge via PR interface

# 6. Delete feature branch after merge
git branch -d feature/user-ioes-summary
git push origin --delete feature/user-ioes-summary
```

**Key Points:**
- Always branch from `develop`, not `main`
- Keep feature branches short-lived (1-5 days)
- Commit early and often with clear messages
- Pull from `develop` regularly to stay current
- Run tests locally before pushing

---

### 2. Release Workflow

**Use Case:** Preparing a new version for production deployment

**Steps:**

```bash
# 1. Create release branch from develop
git checkout develop
git pull origin develop
git checkout -b release/v1.4.0

# 2. Bump version number
# Edit pyproject.toml: version = "1.4.0"
git add pyproject.toml
git commit -m "chore: Bump version to 1.4.0"

# 3. Update CHANGELOG.md (if exists) or release notes
# Document all changes since last release

# 4. Final testing and bug fixes
# Only fixes go in release branch - no new features
git commit -m "fix: Resolve edge case in OS matching"

# 5. Create PR to main for final review
# Title: "Release v1.4.0"
# Include full changelog in PR description

# 6. After approval, merge to main
# This can be done via GitHub PR or manually:
git checkout main
git merge --no-ff release/v1.4.0
git tag -a v1.4.0 -m "Release v1.4.0: <summary>"
git push origin main --tags

# 7. Merge back to develop
git checkout develop
git merge --no-ff release/v1.4.0
git push origin develop

# 8. Delete release branch
git branch -d release/v1.4.0
git push origin --delete release/v1.4.0

# 9. Create GitHub Release
gh release create v1.4.0 \
  --title "v1.4.0 - <Feature Summary>" \
  --notes-file RELEASE_NOTES_v1.4.0.md
```

**Version Numbering (Semantic Versioning):**
- **Major (x.0.0)**: Breaking changes, API incompatibility
- **Minor (1.x.0)**: New features, backward compatible
- **Patch (1.2.x)**: Bug fixes, no new features

---

### 3. Hotfix Workflow

**Use Case:** Critical bug in production requiring immediate fix

**Steps:**

```bash
# 1. Create hotfix branch from main
git checkout main
git pull origin main
git checkout -b hotfix/auth-token-leak

# 2. Implement fix with tests
git commit -m "fix: Prevent token leak in error responses"

# 3. Test thoroughly
pytest tests/

# 4. Merge to main immediately
git checkout main
git merge --no-ff hotfix/auth-token-leak
git tag -a v1.3.1 -m "Hotfix v1.3.1: Security - token leak"
git push origin main --tags

# 5. Merge to develop to prevent regression
git checkout develop
git merge --no-ff hotfix/auth-token-leak
git push origin develop

# 6. Delete hotfix branch
git branch -d hotfix/auth-token-leak

# 7. Create GitHub Release for hotfix
gh release create v1.3.1 \
  --title "v1.3.1 - SECURITY HOTFIX" \
  --notes "Critical security fix for authentication token leak"
```

---

### 4. Documentation-Only Changes

**Use Case:** README updates, typo fixes, documentation improvements

**Steps:**

```bash
# If docs are related to unreleased features:
git checkout develop
git checkout -b docs/api-examples

# If docs are for current production version:
git checkout main
git checkout -b docs/readme-clarification

# Make changes and commit
git commit -m "docs: Clarify installation steps in README"

# Create PR to appropriate branch (main or develop)
# After approval, merge and delete branch
```

---

## Commit Message Conventions

We follow **Conventional Commits** for clear, semantic commit messages.

### Format

```
<type>(<scope>): <subject>

<body> (optional)

<footer> (optional)
```

### Types

| Type | Description | Example |
|------|-------------|---------|
| `feat` | New feature | `feat: Add tsc_list_operating_systems tool` |
| `fix` | Bug fix | `fix: Resolve cache memory leak` |
| `docs` | Documentation only | `docs: Update FILTER_FORMAT_REFERENCE.md` |
| `style` | Code style (formatting, no logic change) | `style: Apply black formatting` |
| `refactor` | Code refactoring (no behavior change) | `refactor: Extract build_filters helpers` |
| `perf` | Performance improvement | `perf: Optimize cache lookup algorithm` |
| `test` | Adding or updating tests | `test: Add unit tests for OS matching` |
| `chore` | Build/tooling changes | `chore: Update Docker base image` |
| `ci` | CI/CD pipeline changes | `ci: Add GitHub Actions workflow` |
| `revert` | Revert previous commit | `revert: Revert "feat: Add experimental feature"` |

### Scopes (Optional)

Examples: `tools`, `filters`, `cache`, `client`, `docs`, `tests`

```bash
git commit -m "feat(tools): Add user IoE summarization tool"
git commit -m "fix(cache): Prevent Redis connection leak"
git commit -m "docs(readme): Update installation instructions"
```

### Examples

**Good Commits:**
```
feat: Add operating system exact matching filter
fix: Resolve plugin family ID lookup failure
docs: Document two-tier OS filtering approach
refactor: Extract smart lookup helpers to convenience_tools
test: Add integration tests for OS matching
chore: Bump version to 1.3.0
```

**Bad Commits:**
```
fixed stuff                    # Too vague
WIP                            # Work in progress, not descriptive
Updated files                  # What files? Why?
bug fix                        # What bug? Where?
```

---

## Pull Request Guidelines

### PR Template

When creating a PR, include:

```markdown
## Description
Brief summary of changes and motivation.

## Type of Change
- [ ] Bug fix (non-breaking)
- [ ] New feature (non-breaking)
- [ ] Breaking change
- [ ] Documentation update

## Related Issues
Closes #123
Relates to #456

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated (if applicable)
- [ ] No new warnings or errors
- [ ] Tests pass locally
- [ ] Commit messages follow conventions
```

### PR Review Process

1. **Author** creates PR with clear description
2. **Reviewer** checks:
   - Code quality and readability
   - Test coverage
   - Documentation updates
   - Follows design principles
   - No security vulnerabilities
3. **Approval** required before merge
4. **Merge** via GitHub (squash or merge commit)
5. **Delete branch** after merge

---

## Branch Protection Rules

### Main Branch Protection

Settings for `main` branch:
- ✅ Require pull request before merging
- ✅ Require approvals: 1 (increase for team projects)
- ✅ Dismiss stale approvals when new commits pushed
- ✅ Require status checks to pass (CI/CD)
- ✅ Require branches to be up to date
- ✅ Require conversation resolution
- ✅ Restrict who can push (maintainers only)
- ✅ Allow force pushes: **Disabled**
- ✅ Allow deletions: **Disabled**

### Develop Branch Protection

Settings for `develop` branch:
- ✅ Require pull request before merging
- ✅ Require approvals: 1
- ✅ Require status checks to pass
- ❌ Dismiss stale approvals (optional)
- ❌ Require branches to be up to date (optional)

---

## CI/CD Integration

### GitHub Actions Workflow

Example workflow for automated testing:

```yaml
# .github/workflows/ci.yml
name: CI

on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install uv
          uv sync --all-extras
      - name: Run tests
        run: pytest tests/ --cov
      - name: Lint
        run: ruff check .
      - name: Type check
        run: mypy src/
```

### Automated Checks

- **Tests**: All tests must pass
- **Coverage**: Maintain >80% code coverage
- **Linting**: No ruff errors
- **Type Checking**: No mypy errors
- **Security**: Dependabot alerts resolved

---

## Release Checklist

Before releasing a new version:

- [ ] All features merged to `develop`
- [ ] Create release branch from `develop`
- [ ] Bump version in `pyproject.toml`
- [ ] Update documentation (FILTER_FORMAT_REFERENCE.md, README.md)
- [ ] Run full test suite
- [ ] Build Docker image and test
- [ ] Create PR to `main` with release notes
- [ ] Get approval and merge to `main`
- [ ] Tag release with `v<version>`
- [ ] Create GitHub Release with detailed notes
- [ ] Merge back to `develop`
- [ ] Announce release (if applicable)

---

## Local Development Setup

### Initial Setup

```bash
# Clone repository
git clone https://github.com/ABMJ/tenable-sc-mcp-server.git
cd tenable-sc-mcp-server

# Create develop branch if not exists
git checkout -b develop origin/develop || git checkout develop

# Install dependencies
pip install uv
uv sync --all-extras

# Set up pre-commit hooks (optional)
pre-commit install
```

### Daily Development

```bash
# Start of day - update develop
git checkout develop
git pull origin develop

# Create feature branch
git checkout -b feature/my-new-feature

# Make changes, test, commit
# ... development work ...

# Push to remote
git push -u origin feature/my-new-feature

# Create PR when ready
gh pr create --base develop --title "feat: My new feature"
```

---

## Troubleshooting

### Merge Conflicts

```bash
# If conflicts occur during merge:
git checkout develop
git pull origin develop
git checkout feature/my-feature
git merge develop

# Resolve conflicts in files
# Edit conflicting files, then:
git add <resolved-files>
git commit -m "chore: Resolve merge conflicts with develop"
git push
```

### Reset Feature Branch

```bash
# If feature branch is too far behind:
git checkout develop
git pull origin develop
git checkout feature/my-feature
git rebase develop

# If conflicts, resolve and continue:
git add <resolved-files>
git rebase --continue

# Force push (only on feature branches!)
git push --force-with-lease
```

---

## Best Practices Summary

1. **Keep `main` production-ready** - Never commit directly
2. **Use `develop` for integration** - Merge features here first
3. **Feature branches are short-lived** - 1-5 days maximum
4. **Commit early and often** - Small, logical commits
5. **Write clear commit messages** - Follow conventions
6. **Test before pushing** - Run tests locally
7. **Update documentation** - Keep docs current with code
8. **Code review everything** - No direct merges to main/develop
9. **Tag all releases** - Semantic versioning
10. **Keep branches in sync** - Pull regularly

---

## Questions?

- Check existing PRs and issues for examples
- Review CONTRIBUTING.md for code standards
- See DESIGN_PRINCIPLES.md for architecture guidelines
- Contact maintainers for clarification

---

**Version History:**
- v1.0 (2026-06-19): Initial workflow documentation

