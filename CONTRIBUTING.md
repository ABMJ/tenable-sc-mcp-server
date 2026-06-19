# Contributing to Tenable.sc MCP Server

Thank you for your interest in this project!

## 📢 Important Notice

This is a **maintainer-only repository**. External contributions via pull requests are **not accepted** at this time.

---

## For Users

If you're using this MCP server, here's how you can engage:

### 🐛 Bug Reports

Found a bug? Please open a GitHub issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment details (Docker version, Python version, OS)
- Relevant logs or error messages

**[Open a Bug Report](https://github.com/ABMJ/tenable-sc-mcp-server/issues/new?labels=bug)**

### 💡 Feature Requests

Have an idea for improvement? Open a GitHub issue with:
- Clear description of the feature
- Use case and motivation
- Expected behavior
- Any relevant examples or mockups

**[Request a Feature](https://github.com/ABMJ/tenable-sc-mcp-server/issues/new?labels=enhancement)**

### ❓ Questions & Support

Need help? Options:
1. Check existing [documentation](README.md)
2. Review closed issues for similar questions
3. Open a new issue with the `question` label

---

## For Developers

### Can I Contribute Code?

External pull requests are **not accepted** at this time. This is a personal/internal project maintained by @ABMJ following specific architectural principles and roadmap.

### Can I Fork the Repository?

**Yes!** You're welcome to fork this repository and modify it for your own use:

```bash
# Fork on GitHub, then:
git clone https://github.com/YOUR_USERNAME/tenable-sc-mcp-server.git
cd tenable-sc-mcp-server
# Make your modifications
```

**License:** See [LICENSE](LICENSE) for terms of use and redistribution.

### Can I Use This in My Project?

**Yes!** This project is open-source. You can:
- Use the Docker image in your infrastructure
- Include it as a dependency in your projects
- Fork and modify for your specific needs
- Study the code for learning purposes

---

## Repository Philosophy

This repository follows a **maintainer-driven development model**:

- **Single maintainer:** Ensures architectural consistency and quality
- **Strict design principles:** All code follows documented patterns (see DESIGN_PRINCIPLES.md)
- **Planned roadmap:** Features implemented according to TOOLS_ROADMAP.md
- **Quality over quantity:** Every tool is carefully designed, tested, and documented

### Why No External PRs?

1. **Architectural Consistency:** This project follows strict design principles that require deep context
2. **Token Optimization:** Every tool is optimized for LLM token efficiency, requiring specialized knowledge
3. **Roadmap Alignment:** Features are implemented in a specific order for maximum coherence
4. **Maintenance Burden:** Review and integration of external PRs would slow down development

---

## What You Can Do Instead

### 1. Share Your Use Case

Even if you can't contribute code, sharing how you use this MCP server helps:
- Open an issue describing your use case
- Share feedback on existing tools
- Suggest improvements based on real-world usage

### 2. Report Bugs Thoroughly

High-quality bug reports are incredibly valuable:
- Include reproduction steps
- Provide relevant context
- Test with the latest version
- Check if it's already reported

### 3. Improve Documentation

Found unclear documentation? Open an issue:
- Point out confusing sections
- Suggest clarifications
- Share what you wish you'd known

### 4. Build Extensions

Consider building complementary projects:
- Additional MCP servers for other Tenable products
- Tools that consume this MCP server's output
- Integrations with other platforms

### 5. Fork and Customize

Need different features? Fork it:
- Modify for your environment
- Add organization-specific tools
- Experiment with new approaches

**If your fork becomes useful to others, share it!** Open source works best when multiple implementations can coexist.

---

## For Maintainer (@ABMJ)

### Development Workflow

See [DESIGN_PRINCIPLES.md - Development Workflow](DESIGN_PRINCIPLES.md#development-workflow--contribution-guidelines) for:
- Branching strategy (main/develop/feature)
- Commit message conventions
- PR review process
- Release workflow
- CI/CD integration

### Quick Commands

```bash
# Start new feature
git checkout develop && git pull
git checkout -b feature/my-feature

# Commit with conventional message
git commit -m "feat(tools): Add new capability"

# Create PR to develop
gh pr create --base develop

# Release workflow
git checkout -b release/v1.4.0
# ... bump version, test ...
gh pr create --base main --title "Release v1.4.0"
```

---

## Code of Conduct

This project follows the [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold this code.

**In summary:**
- Be respectful and professional
- Focus on constructive feedback
- Assume good intentions
- No harassment or discrimination

---

## Questions?

- **Documentation:** See [README.md](README.md) and [DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)
- **Architecture:** See [ARCHITECTURE.md](ARCHITECTURE.md)
- **Roadmap:** See [TOOLS_ROADMAP.md](TOOLS_ROADMAP.md)
- **Issues:** Check existing [GitHub Issues](https://github.com/ABMJ/tenable-sc-mcp-server/issues)
- **Contact:** Open a new issue with the `question` label

---

**Thank you for understanding!** While this repository doesn't accept external code contributions, your feedback, bug reports, and use cases are still valuable and appreciated. 🙏
