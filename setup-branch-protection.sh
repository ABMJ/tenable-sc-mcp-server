#!/bin/bash
# Branch Protection Setup Script
# This script will guide you through setting up branch protection

echo "=========================================="
echo "GitHub Branch Protection Setup"
echo "=========================================="
echo ""
echo "Your repository is already PUBLIC! ✅"
echo ""
echo "Now we need to set up branch protection using the GitHub web interface."
echo "This is easier to do in the browser than via CLI."
echo ""

# Check if we can open browser
if command -v xdg-open &> /dev/null; then
    OPEN_CMD="xdg-open"
elif command -v open &> /dev/null; then
    OPEN_CMD="open"
else
    OPEN_CMD=""
fi

echo "=========================================="
echo "STEP 1: Protect MAIN Branch"
echo "=========================================="
echo ""
echo "I'll open the branch protection settings page for you."
echo "Follow these steps when the page opens:"
echo ""
echo "1. Click the green 'Add branch protection rule' button"
echo "2. In 'Branch name pattern' field, type: main"
echo "3. Check these boxes:"
echo "   ✓ Require a pull request before merging"
echo "   ✓ Require approvals (set to 1)"
echo "   ✓ Dismiss stale pull request approvals"
echo "   ✓ Require review from Code Owners"
echo "   ✓ Require conversation resolution before merging"
echo "   ✓ Include administrators"
echo "4. Scroll to bottom and click 'Create' button"
echo ""
read -p "Press ENTER to open the branch settings page..."

if [ -n "$OPEN_CMD" ]; then
    $OPEN_CMD "https://github.com/ABMJ/tenable-sc-mcp-server/settings/branches" 2>/dev/null
else
    echo ""
    echo "Please open this URL in your browser:"
    echo "https://github.com/ABMJ/tenable-sc-mcp-server/settings/branches"
fi

echo ""
read -p "After you've set up protection for MAIN branch, press ENTER to continue..."

echo ""
echo "=========================================="
echo "STEP 2: Protect DEVELOP Branch"
echo "=========================================="
echo ""
echo "Now let's protect the develop branch."
echo "The page should still be open. If not, I'll open it again."
echo ""
echo "1. Click 'Add branch protection rule' again"
echo "2. In 'Branch name pattern' field, type: develop"
echo "3. Check the same boxes as before:"
echo "   ✓ Require a pull request before merging"
echo "   ✓ Require approvals (set to 1)"
echo "   ✓ Require review from Code Owners"
echo "   ✓ Include administrators"
echo "4. Scroll to bottom and click 'Create' button"
echo ""
read -p "Press ENTER to continue..."

echo ""
echo "=========================================="
echo "STEP 3: Configure Pull Request Settings"
echo "=========================================="
echo ""
echo "Finally, let's configure PR settings for clean history."
echo ""
echo "I'll open the general settings page."
echo "When it opens:"
echo ""
echo "1. Scroll down to 'Pull Requests' section"
echo "2. Check these boxes:"
echo "   ✓ Allow squash merging"
echo "   ✓ Automatically delete head branches"
echo "3. Optionally uncheck (for cleaner history):"
echo "   ☐ Allow merge commits"
echo "   ☐ Allow rebase merging"
echo "4. Click 'Save' button"
echo ""
read -p "Press ENTER to open the settings page..."

if [ -n "$OPEN_CMD" ]; then
    $OPEN_CMD "https://github.com/ABMJ/tenable-sc-mcp-server/settings" 2>/dev/null
else
    echo ""
    echo "Please open this URL in your browser:"
    echo "https://github.com/ABMJ/tenable-sc-mcp-server/settings"
fi

echo ""
read -p "After configuring PR settings, press ENTER to finish..."

echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "Your repository is now configured as:"
echo ""
echo "✅ Public (users can view, clone, fork)"
echo "✅ Main branch protected (requires PR + approval)"
echo "✅ Develop branch protected (requires PR + approval)"
echo "✅ CODEOWNERS assigns PRs to you automatically"
echo "✅ PR template discourages external contributions"
echo ""
echo "Test the protection:"
echo ""
echo "  # This should FAIL (protected branch):"
echo "  git checkout main"
echo "  echo 'test' >> README.md"
echo "  git commit -am 'test'"
echo "  git push origin main"
echo ""
echo "  # This should WORK (via PR):"
echo "  git checkout -b test/protection"
echo "  git push origin test/protection"
echo "  gh pr create --base main"
echo ""
echo "=========================================="
echo "See DESIGN_PRINCIPLES.md for workflow details"
echo "=========================================="
