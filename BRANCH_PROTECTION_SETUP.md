# Simple Step-by-Step Guide: Branch Protection Setup

Your repository is already **PUBLIC** ✅

Now you just need to configure branch protection. This is done through GitHub's website.

---

## Quick Option: Run the Script

I've created a helper script for you:

```bash
cd /home/abmj/apps/tenable-sc-mcp-server
./setup-branch-protection.sh
```

This script will:
- Open the correct GitHub pages for you
- Show you exactly what to click
- Guide you step-by-step

---

## Manual Option: Follow These Steps

### Step 1: Go to Branch Settings

**Open this URL in your browser:**
```
https://github.com/ABMJ/tenable-sc-mcp-server/settings/branches
```

You'll see a page that says "Branch protection rules" with a green button "Add branch protection rule".

---

### Step 2: Protect MAIN Branch

1. **Click** the green "Add branch protection rule" button

2. **Type** `main` in the "Branch name pattern" box at the top

3. **Check these boxes** (scroll down to find them):

   ```
   ☑ Require a pull request before merging
      ☑ Require approvals: [1]
      ☑ Dismiss stale pull request approvals when new commits are pushed
      ☑ Require review from Code Owners
   
   ☑ Require conversation resolution before merging
   
   ☑ Include administrators
   ```

4. **Make sure these are NOT checked:**
   ```
   ☐ Allow force pushes
   ☐ Allow deletions
   ```

5. **Scroll to bottom** and click the green "Create" button

**Result:** Main branch is now protected! ✅

---

### Step 3: Protect DEVELOP Branch

1. **Click** "Add branch protection rule" button again

2. **Type** `develop` in the "Branch name pattern" box

3. **Check the same boxes as before:**
   ```
   ☑ Require a pull request before merging
      ☑ Require approvals: [1]
      ☑ Require review from Code Owners
   
   ☑ Include administrators
   ```

4. **Scroll to bottom** and click "Create"

**Result:** Develop branch is now protected! ✅

---

### Step 4: Configure Pull Request Settings (Optional but Recommended)

1. **Go to:** https://github.com/ABMJ/tenable-sc-mcp-server/settings

2. **Scroll down** to the "Pull Requests" section

3. **Configure these settings:**
   ```
   ☑ Allow squash merging
   ☑ Automatically delete head branches
   
   ☐ Allow merge commits (UNCHECK for cleaner history)
   ☐ Allow rebase merging (UNCHECK for simpler workflow)
   ```

4. **Click** "Save" at the bottom

**Result:** PRs will create clean, squashed commits! ✅

---

## Verify It Works

Test that direct pushes are blocked:

```bash
# This should FAIL with an error about branch protection:
git checkout main
echo "test" >> README.md
git commit -am "test: Direct push"
git push origin main
```

You should see an error like:
```
remote: error: GH006: Protected branch update failed
```

That means it's working! ✅

---

## Visual Reference: What Each Page Looks Like

### Branch Protection Page
```
https://github.com/ABMJ/tenable-sc-mcp-server/settings/branches
```

You'll see:
- Title: "Branches"
- Subtitle: "Branch protection rules"
- Big green button: "Add branch protection rule"
- Any existing rules listed below

### Protection Settings Page

After clicking "Add branch protection rule", you'll see:
- Text box at top: "Branch name pattern" ← Type `main` or `develop` here
- Long list of checkboxes below
- Green "Create" button at bottom

### General Settings Page
```
https://github.com/ABMJ/tenable-sc-mcp-server/settings
```

You'll see:
- Sidebar on left with "General", "Access", "Branches", etc.
- Main content area on right
- Scroll down to find "Pull Requests" section with checkboxes

---

## If You Get Stuck

**Problem:** Can't find the settings page
- Make sure you're logged into GitHub as ABMJ
- Use the direct URLs provided above

**Problem:** Don't see "Add branch protection rule" button
- You might not have admin access (check you're logged in as the repo owner)
- Try refreshing the page

**Problem:** Changes don't save
- Make sure you scroll to the bottom and click "Create" or "Save"
- Check for any red error messages on the page

**Problem:** Want to undo changes
- Go back to the branch protection rules page
- Click "Edit" or "Delete" next to the rule you created

---

## Summary

**What you need to do:**
1. Open https://github.com/ABMJ/tenable-sc-mcp-server/settings/branches
2. Click "Add branch protection rule"
3. Type `main`, check boxes, click "Create"
4. Repeat for `develop` branch
5. Done!

**Time required:** 5 minutes

**Result:** 
- ✅ Repository is public (already done)
- ✅ Main branch protected
- ✅ Develop branch protected
- ✅ Users can view/fork but not push changes
- ✅ You control all code changes via PR approval

---

## Need More Help?

Run the interactive script:
```bash
./setup-branch-protection.sh
```

It will open the correct pages and guide you through each step!
