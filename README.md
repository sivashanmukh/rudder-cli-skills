# RudderStack Agent Skills

A Claude Code plugin **marketplace** that teaches Claude how to drive every programmatic [RudderStack](https://www.rudderstack.com/) surface — CLI, MCP server, and Terraform — with the right preflight checks, commands, and recovery paths.

## What's inside

One marketplace (`rudder-agent-skills`) bundling four plugins. Install the ones you use.

| Plugin | Status | Scope |
|---|---|---|
| [`rudder-core`](plugins/rudder-core/) | ✅ Available | Cross-tool domain knowledge: data catalog, tracking plans, data graphs, instrumentation planning & debugging |
| [`rudder-cli`](plugins/rudder-cli/) | ✅ Available | Workflows for [`rudder-cli`](https://github.com/rudderlabs/rudder-iac) and [`rudder-typer`](https://www.rudderstack.com/docs/features/ruddertyper/) |
| [`rudder-mcp`](plugins/rudder-mcp/) | ✅ Available | Workflows for [`rudder-mcp-server`](https://github.com/rudderlabs/rudder-mcp-server) |
| [`rudder-terraform`](plugins/rudder-terraform/) | ✅ Available | Workflows for the [Terraform provider](https://github.com/rudderlabs/terraform-provider-rudderstack) |

Most users drive RudderStack with more than one tool. Install `rudder-core` plus whichever tool plugins you use; the domain knowledge lives in `rudder-core` so it never duplicates across tool-specific plugins.

## Installation

### Option 1: Skills CLI (Recommended)

The [Skills CLI](https://github.com/vercel-labs/skills) works with 40+ coding agents including Claude Code, Cursor, Cline, OpenCode, and more.

```bash
# List available skills first
npx skills add rudderlabs/rudder-agent-skills --list

# Install specific skills interactively
npx skills add rudderlabs/rudder-agent-skills

# Install specific skills to Claude Code
npx skills add rudderlabs/rudder-agent-skills -a claude-code --skill rudder-cli-workflow --skill rudder-data-catalog

# Install all skills globally
npx skills add rudderlabs/rudder-agent-skills -g --all
```

To update:

```bash
npx skills update
```

### Option 2: Claude Code Plugin System

#### Pre-release / Manual Installation

Until this marketplace is published, install manually by cloning to the Claude Code plugins directory:

```bash
# Clone to the marketplaces directory (directory name must be "rudder-agent-skills")
git clone https://github.com/rudderlabs/rudder-agent-skills.git \
  ~/.claude/plugins/marketplaces/rudder-agent-skills

# Then in Claude Code, install the plugins:
/plugin install rudder-core@rudder-agent-skills
/plugin install rudder-cli@rudder-agent-skills
```

To update, pull the latest changes:

```bash
cd ~/.claude/plugins/marketplaces/rudder-agent-skills && git pull
```

#### After Release

Once published to GitHub under `rudderlabs/rudder-agent-skills`:

```bash
/plugin marketplace add rudderlabs/rudder-agent-skills
/plugin install rudder-core@rudder-agent-skills
/plugin install rudder-cli@rudder-agent-skills
```

Or non-interactively:

```bash
claude plugin marketplace add rudderlabs/rudder-agent-skills
claude plugin install rudder-core@rudder-agent-skills
claude plugin install rudder-cli@rudder-agent-skills
```

Pin to a release by appending `@v1.0.0` to the marketplace slug. Update later with `/plugin marketplace update rudder-agent-skills`.

## Available skills

### `rudder-core`

| Skill | When to use |
|---|---|
| `rudder-data-catalog` | Creating or managing events, properties, categories, or custom types |
| `rudder-data-graphs` | Modeling entities, events, and relationships for Audiences |
| `rudder-tracking-plans` | Creating tracking plans to group events for specific sources |
| `rudder-instrumentation-planning` | Designing event taxonomy from scratch or restructuring |
| `rudder-instrumentation-debugging` | Fixing validation errors, schema issues, or instrumentation problems |
| `rudder-environment-check` | Checking prerequisites and setup status |

### `rudder-cli`

| Skill | When to use |
|---|---|
| `rudder-cli-workflow` | Iterating on RudderStack resources with validate → dry-run → apply |
| `rudder-import-and-evolve` | Importing existing RudderStack resources to CLI management |
| `rudder-typer-workflow` | Generating type-safe SDKs (Swift/Kotlin) from tracking plans |
| `rudder-transformations` | Creating, editing, or managing transformations and libraries |
| `rudder-cli-setup` | Installing and authenticating rudder-cli |

### `rudder-mcp`

| Skill | When to use |
|---|---|
| `rudder-mcp-workflow` | Connecting AI/LLM agents to RudderStack via MCP server |
| `rudder-mcp-setup` | Configuring Claude Code to connect to MCP server |

### `rudder-terraform`

| Skill | When to use |
|---|---|
| `rudder-terraform-workflow` | Managing RudderStack resources via Terraform provider |
| `rudder-terraform-setup` | Installing Terraform and the RudderStack provider |

## How skills work together

```
                       ┌───────────────────────────────┐
                       │ instrumentation-planning      │
                       │ (design the taxonomy)         │
                       └──────────────┬────────────────┘
                                      │
               ┌──────────────────────┼──────────────────────┐
               │                      │                      │
               ▼                      ▼                      ▼
        ┌─────────────┐        ┌──────────────┐        ┌─────────────┐
        │data-catalog │        │  import-and  │        │  tracking   │
        │(build vocab)│        │    evolve    │        │   plans     │
        └──────┬──────┘        └──────┬───────┘        └──────┬──────┘
               └──────────────────────┼───────────────────────┘
                                      ▼
                          ┌───────────────────────┐
                          │   cli-workflow        │
                          │  (validate / apply)   │
                          └───────────┬───────────┘
                                      │
             ┌────────────────────────┼────────────────────────┐
             ▼                        ▼                        ▼
     ┌───────────────┐      ┌────────────────┐       ┌──────────────────┐
     │ typer-workflow│      │ transformations│       │    debugging     │
     │(generate code)│      │ (data transform│       │  (fix issues)    │
     └───────────────┘      └────────────────┘       └──────────────────┘
```

## Directory structure

```
rudder-agent-skills/
├── README.md                    # this file
├── CONTRIBUTING.md              # authoring + PR guidelines
├── LICENSE
├── .claude-plugin/
│   └── marketplace.json
├── docs/
│   ├── installation.md
│   └── superpowers/specs/       # design docs for changes at this scale
├── examples/                    # end-to-end worked examples
└── plugins/
    ├── rudder-core/
    │   ├── .claude-plugin/plugin.json
    │   └── skills/<skill>/SKILL.md
    ├── rudder-cli/
    │   ├── .claude-plugin/plugin.json
    │   └── skills/<skill>/SKILL.md
    ├── rudder-mcp/
    │   ├── .claude-plugin/plugin.json
    │   └── skills/<skill>/SKILL.md
    └── rudder-terraform/
        ├── .claude-plugin/plugin.json
        └── skills/<skill>/SKILL.md
```

## Prerequisites

A compatible AI coding agent (Claude Code, Cursor, Cline, OpenCode, or any of the [40+ supported agents](https://github.com/vercel-labs/skills)).

Each plugin includes a setup skill that guides you through installing and configuring tool-specific prerequisites:

| Plugin | Setup Skill | What it installs |
|--------|-------------|------------------|
| `rudder-cli` | `/rudder-cli-setup` | Downloads `rudder-cli` binary, authenticates with RudderStack |
| `rudder-mcp` | `/rudder-mcp-setup` | Configures Claude Code to connect to `rudder-mcp-server` |
| `rudder-terraform` | `/rudder-terraform-setup` | Installs Terraform, configures the RudderStack provider |

After installing a plugin, run its setup skill to get started. Use `/rudder-environment-check` to verify your full setup.

## Examples

`examples/` contains worked end-to-end projects that demonstrate skills in action — the current example covers the transformations workflow.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for authoring conventions, testing steps, and PR expectations.

## License

MIT License — see [LICENSE](LICENSE) for details.
