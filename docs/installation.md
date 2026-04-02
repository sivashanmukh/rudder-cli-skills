# Installation Guide

This guide covers installing RudderStack CLI skills for Claude Code.

## Prerequisites

### Claude Code

Install Claude Code CLI if you haven't already:

```bash
npm install -g @anthropic-ai/claude-code
```

### Rudder CLI

Install the Rudder CLI from the [rudder-iac repository](https://github.com/rudderlabs/rudder-iac):

```bash
# macOS (Homebrew)
brew tap rudderlabs/rudder-iac
brew install rudder-cli

# Or download from releases
# https://github.com/rudderlabs/rudder-iac/releases
```

### RudderStack Authentication

Get an access token from your RudderStack dashboard:

1. Go to **Settings → Access Tokens**
2. Create a new token with appropriate permissions
3. Run `rudder-cli auth login` and enter your token

Verify authentication:

```bash
rudder-cli workspace info
```

## Installing Skills

### Option 1: Symlink (Recommended)

Symlinks keep skills updated when you pull changes:

```bash
# Clone once
git clone https://github.com/rudderlabs/rudder-cli-skills.git ~/rudder-cli-skills

# In each project that needs skills
mkdir -p .claude/skills
ln -s ~/rudder-cli-skills/skills/rudder-cli-workflow .claude/skills/
ln -s ~/rudder-cli-skills/skills/rudderstack-transformations .claude/skills/
```

### Option 2: Copy

Copy skills directly into your project:

```bash
# Clone or download
git clone https://github.com/rudderlabs/rudder-cli-skills.git /tmp/rudder-cli-skills

# Copy to your project
mkdir -p .claude/skills
cp -r /tmp/rudder-cli-skills/skills/* .claude/skills/
```

### Option 3: Git Submodule

Add as a submodule for version-controlled dependency:

```bash
# Add submodule
git submodule add https://github.com/rudderlabs/rudder-cli-skills.git .rudder-skills

# Create symlinks
mkdir -p .claude/skills
ln -s ../.rudder-skills/skills/rudder-cli-workflow .claude/skills/
ln -s ../.rudder-skills/skills/rudderstack-transformations .claude/skills/
```

## Verifying Installation

After installing, verify skills are detected:

```bash
# Start Claude Code in your project
claude

# Ask about available skills
You: What RudderStack skills do you have available?
```

Claude should list `rudder-cli-workflow` and `rudderstack-transformations`.

## Project Structure

After installation, your project should look like:

```
your-project/
├── .claude/
│   └── skills/
│       ├── rudder-cli-workflow/
│       │   └── SKILL.md
│       └── rudderstack-transformations/
│           └── SKILL.md
├── transformations/          # Your transformation specs
│   ├── my-lib.yaml
│   ├── my-transformation.yaml
│   └── javascript/
│       ├── my-lib.js
│       └── my-transformation.js
└── ...
```

## Optional: Claude Settings

You can add project-specific Claude Code settings in `.claude/settings.local.json`:

```json
{
  "permissions": {
    "allow": [
      "Bash(rudder-cli validate -l ./)",
      "Bash(rudder-cli apply --dry-run -l ./)",
      "Bash(rudder-cli transformations test --all -l ./)"
    ]
  }
}
```

This pre-approves common Rudder CLI commands. Note: Do not commit `settings.local.json` to version control (it's user-specific).

## Updating Skills

### If using symlinks:

```bash
cd ~/rudder-cli-skills
git pull
```

### If using copies:

Re-copy the skills from a fresh clone.

### If using submodules:

```bash
git submodule update --remote .rudder-skills
```

## Troubleshooting

### Skills not detected

1. Verify the directory structure: `.claude/skills/<skill-name>/SKILL.md`
2. Check file permissions
3. Restart Claude Code

### "rudder-cli not found"

1. Ensure Rudder CLI is installed: `which rudder-cli`
2. Check your PATH includes the CLI location
3. Try the full path: `/usr/local/bin/rudder-cli`

### Authentication errors

```bash
# Re-authenticate
rudder-cli auth login

# Verify
rudder-cli workspace info
```

## Skill Authoring

To create your own skills:

1. Create `skills/<skill-name>/SKILL.md`
2. Add YAML frontmatter:
   ```yaml
   ---
   name: my-skill
   description: When to use this skill
   ---
   ```
3. Write the skill content in markdown
4. Test by installing in a project

See existing skills for examples of structure and content.
