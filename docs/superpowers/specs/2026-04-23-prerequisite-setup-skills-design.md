# Prerequisite Setup Skills Design

**Date:** 2026-04-23
**Status:** Draft
**Author:** Claude (with user input)

## Summary

Add 4 prerequisite/setup skills to help users install and configure the tools required by other RudderStack skills. These skills follow Approach C (Hybrid): one central environment check in `rudder-core` plus tool-specific setup skills in their respective plugins.

## Problem

Existing skills assume tools like `rudder-cli`, `terraform`, and `rudder-mcp-server` are already installed and configured. Users encountering "command not found" errors have no in-skill guidance for setup. The installation documentation exists but is not integrated into the skill workflow.

## Solution

Create 4 setup skills that auto-invoke when tools are missing and guide users through installation with transparency.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      rudder-core                                │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  rudder-environment-check                                 │  │
│  │  - Checks: rudder-cli, terraform, mcp-server              │  │
│  │  - Output: table of ✓/✗ with "run X-setup" guidance       │  │
│  │  - Auto-invokes: "check prerequisites", "what's missing"  │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
           ┌──────────────────┼──────────────────┐
           ▼                  ▼                  ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│   rudder-cli     │ │ rudder-terraform │ │   rudder-mcp     │
│ ┌──────────────┐ │ │ ┌──────────────┐ │ │ ┌──────────────┐ │
│ │rudder-cli-   │ │ │ │rudder-       │ │ │ │rudder-mcp-   │ │
│ │setup         │ │ │ │terraform-    │ │ │ │setup         │ │
│ │              │ │ │ │setup         │ │ │ │              │ │
│ │- Install CLI │ │ │ │- Install TF  │ │ │ │- Configure   │ │
│ │- Authenticate│ │ │ │- Add provider│ │ │ │  MCP server  │ │
│ │- Verify      │ │ │ │- Configure   │ │ │ │- Verify      │ │
│ └──────────────┘ │ │ └──────────────┘ │ │ └──────────────┘ │
└──────────────────┘ └──────────────────┘ └──────────────────┘
```

**Invocation flow:**
1. User says "help me set up RudderStack" → `rudder-environment-check` fires
2. Check shows "rudder-cli: ✗ missing" → user runs `/rudder-cli-setup`
3. OR user hits "rudder-cli not found" error → `rudder-cli-setup` auto-invokes directly

## Skill Specifications

### 1. rudder-environment-check (rudder-core)

**Purpose:** Quick diagnostic that checks all RudderStack tool prerequisites and provides actionable guidance.

**Triggers (auto-invoke on):**
- "check prerequisites", "check setup", "what do I need to install"
- "rudder environment", "rudderstack setup status"

**Checks performed:**

| Check | Command | Success Criteria |
|-------|---------|------------------|
| rudder-cli installed | `which rudder-cli` | Path returned |
| rudder-cli authenticated | `rudder-cli workspace info` | Workspace ID shown |
| terraform installed | `which terraform` | Path returned |
| terraform provider available | Check `.terraform.lock.hcl` or `terraform providers` | Provider listed |
| rudder-mcp-server reachable | `curl -s https://mcp.rudderstack.com/health` | 200 response |

**Output format:**

```
RudderStack Environment Check
─────────────────────────────
Tool                    Status    Action
─────────────────────────────
rudder-cli              ✓ Ready
  └─ authenticated      ✓ Ready   Workspace: My Workspace
terraform               ✗ Missing Run: /rudder-terraform-setup
  └─ provider           ─ Skipped (terraform required first)
rudder-mcp-server       ✗ Missing Run: /rudder-mcp-setup
─────────────────────────────
```

**Allowed tools:** `Bash(which, curl, rudder-cli workspace info, terraform version, terraform providers)`

---

### 2. rudder-cli-setup (rudder-cli)

**Purpose:** Install rudder-cli, authenticate with RudderStack, and verify the setup works.

**Triggers (auto-invoke on):**
- "install rudder-cli", "setup rudder cli", "configure rudder cli"
- "rudder-cli: command not found", "rudder-cli not found"
- "authenticate rudder", "rudder-cli auth"

**Workflow:**

```
1. Check if installed     ──► which rudder-cli
         │
         ├── Found ──► Skip to step 2
         │
         └── Not found ──► Detect OS, download from GitHub releases
                           - Download binary
                           - chmod +x
                           - Add to PATH

2. Verify installation ──► rudder-cli --version

3. Check authentication ──► rudder-cli workspace info
         │
         ├── Authenticated ──► Show workspace, done
         │
         └── Not authenticated ──► Guide user:
                                   "Get token from Settings → Access Tokens"
                                   "Run: rudder-cli auth login"

4. Verify authentication ──► rudder-cli workspace info
         │
         └── Show workspace name + ID, confirm success
```

**Installation by platform:**

| Platform | Method |
|----------|--------|
| macOS | Download binary from GitHub releases, `chmod +x`, add to PATH |
| Linux | Download binary from GitHub releases, `chmod +x`, add to PATH |
| Windows | Download .exe from GitHub releases, add to PATH |

**GitHub releases URL:** https://github.com/rudderlabs/rudder-iac/releases

**Allowed tools:** `Bash(which, curl, chmod, rudder-cli *), Read`

---

### 3. rudder-terraform-setup (rudder-terraform)

**Purpose:** Install Terraform (if missing), configure the RudderStack provider, and verify setup.

**Triggers (auto-invoke on):**
- "install terraform provider", "setup rudder terraform", "configure terraform rudderstack"
- "terraform-provider-rudderstack", "terraform rudderstack provider"
- Error: "provider not found: rudderlabs/rudderstack"

**Workflow:**

```
1. Check Terraform installed ──► terraform version
         │
         ├── Found ──► Show version, skip to step 2
         │
         └── Not found ──► Guide installation:
                           macOS: brew install terraform
                           Linux: apt/yum or download
                           Or: tfenv for version management

2. Check provider configured ──► Look for required_providers block
         │
         ├── Found ──► Skip to step 3
         │
         └── Not found ──► Create/update versions.tf:
                           terraform {
                             required_providers {
                               rudderstack = {
                                 source  = "rudderlabs/rudderstack"
                                 version = "~> 4.3.1"
                               }
                             }
                           }

3. Initialize provider ──► terraform init
         │
         └── Downloads provider from registry

4. Configure authentication ──► Check RUDDERSTACK_ACCESS_TOKEN
         │
         ├── Set ──► Verify with terraform plan (empty config)
         │
         └── Not set ──► Guide:
                         "export RUDDERSTACK_ACCESS_TOKEN=<token>"
                         "Get token from Settings → Access Tokens"
```

**Allowed tools:** `Bash(which, terraform *, brew), Read, Write, Edit`

---

### 4. rudder-mcp-setup (rudder-mcp)

**Purpose:** Configure Claude Code to connect to RudderStack's hosted MCP server.

**Triggers (auto-invoke on):**
- "install rudder mcp", "setup mcp server", "configure rudder-mcp-server"
- "connect claude to rudderstack", "mcp rudderstack"

**Workflow:**

```
1. Check npx available ──► which npx
         │
         ├── Found ──► Continue
         │
         └── Not found ──► "Install Node.js first"

2. Choose configuration method
         │
         ├── Option A: /mcp command (recommended)
         │      └── Run: /mcp add rudderstack
         │          Follow prompts to configure endpoint + auth
         │
         └── Option B: Manual configuration
                └── Edit settings file directly (see step 3)

3. (If manual) Choose auth method
         │
         ├── OAuth (recommended) ──► mcp.rudderstack.com/mcp
         ├── Bearer token ──► mcp.rudderstack.com/bearer-auth-mcp
         └── Basic auth ──► mcp.rudderstack.com/basic-auth-mcp

4. (If manual) Configure Claude Code ──► Update settings
         │
         └── Add mcpServers block:
             {
               "mcpServers": {
                 "rudderstack": {
                   "command": "npx",
                   "args": ["-y", "mcp-remote", "https://mcp.rudderstack.com/mcp"]
                 }
               }
             }

5. Verify connection
         │
         └── Restart Claude, test: "List my RudderStack sources"
```

**Allowed tools:** `Bash(which, npx), Read, Write, Edit`

---

## Common Patterns

| Pattern | Implementation |
|---------|----------------|
| Check before install | Always run `which <tool>` before attempting install |
| Guided execution | Show command, explain what it does, ask before running |
| Verification step | After each major step, verify it worked before proceeding |
| Clear error guidance | If a step fails, explain why and how to fix |

## Security Considerations

Following existing skill conventions:

- **Credential Security:** Never echo/log tokens; guide users to use environment variables
- **Token storage:** `RUDDERSTACK_ACCESS_TOKEN` for CLI/Terraform, OAuth flow for MCP
- **.gitignore reminder:** Prompt users to add `.env` to `.gitignore`

## Skill Frontmatter Summary

| Skill | Plugin | allowed-tools |
|-------|--------|---------------|
| `rudder-environment-check` | rudder-core | `Bash(which, curl, rudder-cli workspace info, terraform version, terraform providers)` |
| `rudder-cli-setup` | rudder-cli | `Bash(which, curl, chmod, rudder-cli *), Read` |
| `rudder-terraform-setup` | rudder-terraform | `Bash(which, terraform *, brew), Read, Write, Edit` |
| `rudder-mcp-setup` | rudder-mcp | `Bash(which, npx), Read, Write, Edit` |

## File Locations

```
plugins/
├── rudder-core/skills/
│   └── rudder-environment-check/
│       └── SKILL.md
├── rudder-cli/skills/
│   └── rudder-cli-setup/
│       └── SKILL.md
├── rudder-terraform/skills/
│   └── rudder-terraform-setup/
│       └── SKILL.md
└── rudder-mcp/skills/
    └── rudder-mcp-setup/
        └── SKILL.md
```

## Testing

After implementation, verify:

1. **Auto-invoke test:** Say "rudder-cli not found" → `rudder-cli-setup` should fire
2. **Environment check:** Say "check my rudderstack setup" → `rudder-environment-check` should fire
3. **Non-trigger test:** Say "create a tracking plan" → setup skills should NOT fire

## Out of Scope

- Self-hosted rudder-mcp-server setup (users connect to hosted mcp.rudderstack.com)
- Homebrew tap for rudder-cli (all platforms use GitHub releases download)
- Automatic PATH modification (guided, user executes)
