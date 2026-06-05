# Setting Up GitHub Pages - Quick Instructions

## Immediate Setup (5 minutes)

### Step 1: Create gh-pages Branch

```bash
# From your main branch
cd /home/abmj/apps/tenable-sc-mcp-server

# Create orphan branch for GitHub Pages
git checkout --orphan gh-pages

# Remove all files from git
git rm -rf .

# Copy the documentation site
cp docs/gh-pages/index.html index.html

# Add and commit
git add index.html
git commit -m "Initial GitHub Pages setup"

# Push to GitHub
git push origin gh-pages

# Return to main branch
git checkout main
```

### Step 2: Enable GitHub Pages

1. Go to: https://github.com/ABMJ/tenable-sc-mcp-server/settings/pages
2. Under "Build and deployment":
   - **Source**: Deploy from a branch
   - **Branch**: `gh-pages`
   - **Folder**: `/ (root)`
3. Click **Save**

### Step 3: Wait & Verify

- Wait 1-2 minutes for deployment
- Visit: https://abmj.github.io/tenable-sc-mcp-server/
- Your documentation site should be live!

## Update README

Add this badge to README.md:

```markdown
[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://abmj.github.io/tenable-sc-mcp-server/)
```

Add this section:

```markdown
## Documentation

- **Website**: https://abmj.github.io/tenable-sc-mcp-server/
- **Roadmap**: [FINAL_ULTIMATE_ROADMAP.md](FINAL_ULTIMATE_ROADMAP.md)
- **API Reference**: Coming soon
```

## That's It!

Your GitHub Pages site is now live. The site includes:
- Project overview
- Key features
- Development roadmap
- Quick start guide
- Links to all documentation

## Next Steps

1. **Announce the site**: Share URL in project README and social media
2. **Add automation**: Set up GitHub Actions to auto-deploy on changes
3. **Enhance content**: Add more documentation pages as needed
4. **Monitor traffic**: Set up analytics if desired

See [SETUP.md](SETUP.md) for advanced configuration options.
