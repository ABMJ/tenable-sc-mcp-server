# Quick Branch Ruleset Setup - Visual Guide

## What You See on the Page vs What You Need to Do

---

### 1. RULESET NAME
**What you see:**
```
Ruleset Name
*
[empty text box]
```

**What to type:**
```
Protect main branch
```

---

### 2. ENFORCEMENT STATUS
**What you see:**
```
Enforcement status
[Dropdown menu]
```

**What to select:**
```
Active (should already be selected)
```

---

### 3. BYPASS LIST
**What you see:**
```
Bypass list
Exempt roles, teams, agents, apps, and users from this ruleset by adding them to the bypass list.

Bypass list is empty
[Add bypass button]
```

**What to do:**
```
DO NOTHING - Leave it empty

This means NO ONE (including you) can bypass the rules.
If you want emergency access, click "Add bypass" and add your username.
```

---

### 4. TARGET BRANCHES
**What you see:**
```
Target branches
Which branches should be matched?

Branch targeting criteria
Branch targeting has not been configured
[Add target button]
```

**What to do:**
```
1. Click "Add target"
2. Select "Include by pattern"
3. Type: main
4. Click "Add inclusion pattern"

After this, you should see:
"Include: main" under "Branch targeting criteria"
```

---

### 5. RULES
**What you see:**
```
Rules
Which rules should be applied?

Branch rules

⬜ Restrict creations
⬜ Restrict updates
⬜ Restrict deletions
⬜ Require linear history
⬜ Require deployments to succeed
⬜ Require signed commits
⬜ Require a pull request before merging
⬜ Require status checks to pass
⬜ Block force pushes
⬜ Require code scanning results
⬜ Require code quality results
⬜ Automatically request Copilot code review
```

**What to CHECK (click the checkboxes):**

```
☑ Require a pull request before merging
  (When you check this, MORE OPTIONS will appear below it)
  
  Inside this expanded section, you'll see:
  
  Required number of approvals before merging
  [Dropdown: select "1"]
  
  ☑ Dismiss stale pull request approvals when new commits are pushed
  ☑ Require approval of the most recent reviewable push
  ☐ Require review from Code Owners (only if you have CODEOWNERS file)

☑ Block force pushes

☑ Restrict deletions
```

**What to LEAVE UNCHECKED:**
- Restrict creations
- Restrict updates
- Require linear history (optional - check if you want clean history)
- Require deployments to succeed
- Require signed commits (optional - check if you use GPG signing)
- Require status checks to pass
- Require code scanning results
- Require code quality results
- Automatically request Copilot code review

---

### 6. SAVE
**What you see at the bottom:**
```
[Cancel button]  [Create button (green)]
```

**What to do:**
```
Click the green "Create" button
```

---

## After You Click Create

You should be redirected back to the Rulesets page, and you'll see:

```
Rulesets

[New ruleset dropdown]

Active rulesets

Protect main branch
Branch · Active · 3 rules
[View/Edit buttons]
```

This means it worked!

---

## Test That It Works

Open a terminal and try to push to main:

```bash
cd /home/abmj/apps/tenable-sc-mcp-server
git checkout main
echo "test" >> README.md
git add README.md
git commit -m "test: direct push"
git push origin main
```

You should see an error like:
```
remote: error: GH013: Repository rule violations found for refs/heads/main
remote: 
remote: - MERGE REQUEST REQUIRED
remote: 
remote: Cannot push directly to this branch. Use a pull request.
```

If you see this error, CONGRATULATIONS - your branch is protected!

---

## What This Means for Users

**Users CAN:**
- Clone your repository
- Fork your repository
- Use your MCP server
- Create issues
- Submit pull requests

**Users CANNOT:**
- Push directly to your main branch
- Delete your main branch
- Force-push and rewrite history
- Modify your code without your approval

**YOU (as owner):**
- Cannot push directly to main (protected from accidents)
- Must create a branch, make changes, and open a PR
- Must approve your own PR (or have someone else approve it)
- This is GOOD - it prevents accidental breaking changes

---

## Quick Troubleshooting

**Problem: "Add target" button doesn't work**
- Try refreshing the page
- Make sure JavaScript is enabled in your browser

**Problem: Can't find "Include by pattern" option**
- After clicking "Add target", you should see a menu
- Select "Include by pattern" (not "Include default branch" or "Include all branches")

**Problem: Ruleset created but protection not working**
- Check "Enforcement status" is "Active" (not "Disabled" or "Evaluate")
- Verify "Target branches" shows "Include: main"
- Wait 1-2 minutes for GitHub to apply the rules

**Problem: Too restrictive - I can't work**
- You can add yourself to the "Bypass list" if you need emergency access
- Or temporarily set "Enforcement status" to "Disabled" while you work
- Remember to re-enable it after!

---

## Summary Checklist

Before you click "Create", verify:

- ☑ Ruleset Name: "Protect main branch"
- ☑ Enforcement status: Active
- ☑ Target branches shows: "Include: main"
- ☑ "Require a pull request before merging" is checked
- ☑ "Block force pushes" is checked
- ☑ "Restrict deletions" is checked

Then click the green "Create" button!
