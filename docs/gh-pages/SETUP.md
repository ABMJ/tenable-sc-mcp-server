# GitHub Pages Setup Guide

This guide explains how to enable and deploy the GitHub Pages documentation site for the Tenable.sc MCP Server.

## Quick Setup

### Option 1: Using GitHub UI (Recommended)

1. **Go to Repository Settings**
   - Navigate to https://github.com/ABMJ/tenable-sc-mcp-server/settings/pages

2. **Configure Source**
   - **Source**: Deploy from a branch
   - **Branch**: `gh-pages`
   - **Folder**: `/ (root)`
   - Click **Save**

3. **Create gh-pages Branch**
   ```bash
   # From main branch
   git checkout -b gh-pages
   
   # Copy only the docs/gh-pages content to root
   cp docs/gh-pages/index.html index.html
   
   # Remove everything else
   git rm -rf src tests .github docs pyproject.toml Dockerfile docker-compose.yml
   
   # Commit and push
   git add index.html
   git commit -m "Initial GitHub Pages setup"
   git push origin gh-pages
   ```

4. **Access Your Site**
   - URL: https://abmj.github.io/tenable-sc-mcp-server/
   - Wait 1-2 minutes for deployment

### Option 2: Automated Deployment with GitHub Actions

1. **Create Deployment Workflow**
   
   Create `.github/workflows/deploy-pages.yml`:

```yaml
name: Deploy GitHub Pages

on:
  push:
    branches:
      - main
    paths:
      - 'docs/gh-pages/**'
      - 'FINAL_ULTIMATE_ROADMAP.md'
      - 'README.md'
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Setup Pages
        uses: actions/configure-pages@v4
      
      - name: Prepare pages content
        run: |
          mkdir -p _site
          cp docs/gh-pages/index.html _site/
          cp FINAL_ULTIMATE_ROADMAP.md _site/
          cp README.md _site/
          cp CHANGELOG.md _site/
      
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: '_site'
  
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

2. **Enable GitHub Actions for Pages**
   - Go to Settings > Pages
   - Source: **GitHub Actions**
   - Save

3. **Trigger Deployment**
   ```bash
   git add .github/workflows/deploy-pages.yml
   git commit -m "Add GitHub Pages deployment workflow"
   git push origin main
   ```

### Option 3: Using MkDocs (Advanced)

For a more sophisticated documentation site:

1. **Install MkDocs**
   ```bash
   pip install mkdocs mkdocs-material
   ```

2. **Create mkdocs.yml**
   ```yaml
   site_name: Tenable.sc MCP Server
   site_url: https://abmj.github.io/tenable-sc-mcp-server
   repo_url: https://github.com/ABMJ/tenable-sc-mcp-server
   
   theme:
     name: material
     palette:
       primary: deep purple
       accent: purple
     features:
       - navigation.tabs
       - navigation.sections
       - toc.integrate
       - search.suggest
   
   nav:
     - Home: index.md
     - Roadmap: roadmap.md
     - Documentation:
         - Configuration: docs/configuration.md
         - Deployment: docs/deployment.md
         - Caching: docs/caching.md
     - Development:
         - Contributing: CONTRIBUTING.md
         - Testing: docs/testing.md
     - About:
         - Changelog: CHANGELOG.md
         - Security: SECURITY.md
   ```

3. **Build and Deploy**
   ```bash
   mkdocs build
   mkdocs gh-deploy
   ```

## Custom Domain (Optional)

1. **Add CNAME file** to `gh-pages` branch:
   ```bash
   echo "docs.tenable-sc-mcp.example.com" > CNAME
   ```

2. **Configure DNS**:
   - Add CNAME record pointing to `abmj.github.io`
   - Or A records:
     - 185.199.108.153
     - 185.199.109.153
     - 185.199.110.153
     - 185.199.111.153

3. **Enable HTTPS** in GitHub Pages settings

## Updating the Site

### Manual Update

```bash
# Switch to gh-pages branch
git checkout gh-pages

# Edit files
vim index.html

# Commit and push
git add .
git commit -m "Update documentation"
git push origin gh-pages

# Switch back to main
git checkout main
```

### Automated Update (if using GitHub Actions)

Just update files in `docs/gh-pages/` on main branch and push:

```bash
# Edit files
vim docs/gh-pages/index.html

# Commit and push
git add docs/gh-pages/
git commit -m "Update GitHub Pages"
git push origin main

# Action will automatically deploy
```

## Verification

1. **Check Build Status**
   - Go to Actions tab
   - Look for "pages build and deployment" workflow
   - Ensure it completed successfully

2. **Access Site**
   - Visit: https://abmj.github.io/tenable-sc-mcp-server/
   - Should see the documentation homepage

3. **Test Links**
   - Verify all navigation links work
   - Check that roadmap link points to FINAL_ULTIMATE_ROADMAP.md
   - Test GitHub links

## Troubleshooting

### Site Not Loading

1. Check Pages settings: Settings > Pages
2. Verify source branch is correct
3. Check Actions for failed deployments
4. Ensure index.html exists in root of gh-pages branch

### 404 Errors

1. Verify file paths in links
2. Check that files exist in gh-pages branch
3. Use relative URLs (not absolute)

### Changes Not Appearing

1. Hard refresh browser (Ctrl+F5)
2. Clear browser cache
3. Wait 1-2 minutes for CDN propagation
4. Check commit was pushed to gh-pages

### Build Failures

1. Check workflow logs in Actions tab
2. Verify YAML syntax in workflow file
3. Ensure permissions are correct

## Best Practices

1. **Keep gh-pages branch clean**
   - Only include built files
   - Don't include source code

2. **Use relative links**
   - Links should work locally and on GitHub Pages
   - Example: `../../ROADMAP.md` not `/ROADMAP.md`

3. **Test locally first**
   - Open index.html in browser before pushing
   - Verify all links work

4. **Automate updates**
   - Use GitHub Actions for automatic deployment
   - Keep main branch as source of truth

5. **Version documentation**
   - Tag documentation releases
   - Keep old versions accessible

## Next Steps

After setting up GitHub Pages:

1. Update README.md with Pages URL
2. Add link to documentation in repo description
3. Share site URL with community
4. Consider adding analytics (Google Analytics, Plausible)
5. Set up automated link checking
6. Add search functionality (Algolia, custom)

## Resources

- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [MkDocs Documentation](https://www.mkdocs.org/)
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
