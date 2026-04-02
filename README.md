# RudderStack CLI Skills

Claude Code skills for working with [RudderStack](https://www.rudderstack.com/) resources using the [Rudder CLI](https://github.com/rudderlabs/rudder-iac).

## What Are Skills?

Skills are reusable prompts that teach Claude Code domain-specific workflows. When you install these skills, Claude Code gains expertise in:

- **RudderStack Transformations** - Creating, testing, and deploying transformations and libraries
- **Rudder CLI Workflow** - The validate → dry-run → apply iteration cycle

## Quick Start

### 1. Install Skills

Copy or symlink the skills into your project's `.claude/skills/` directory:

```bash
# Clone this repository
git clone https://github.com/rudderlabs/rudder-cli-skills.git

# In your RudderStack project, create the skills directory
mkdir -p .claude/skills

# Option A: Symlink (recommended - stays updated)
ln -s /path/to/rudder-cli-skills/skills/rudder-cli-workflow .claude/skills/
ln -s /path/to/rudder-cli-skills/skills/rudderstack-transformations .claude/skills/

# Option B: Copy
cp -r /path/to/rudder-cli-skills/skills/* .claude/skills/
```

### 2. Use in Claude Code

Once installed, Claude Code automatically detects and uses these skills when relevant:

```
You: Create a base64 encoding library for my transformations

Claude: [Invokes rudderstack-transformations skill]
        I'll help you create a Base64 library. Let me set up the YAML spec
        and JavaScript implementation following RudderStack conventions...
```

Or invoke explicitly:

```
You: /rudderstack-transformations

Claude: [Loads skill and guides you through transformation development]
```

## Available Skills

### `rudder-cli-workflow`

**When to use:** Iterating on RudderStack resources with validate → dry-run → apply

**What it teaches Claude:**
- Authentication prerequisites (`rudder-cli auth login`)
- The iteration cycle workflow
- Reading and interpreting CLI output
- Common validation errors and fixes
- Troubleshooting techniques

### `rudderstack-transformations`

**When to use:** Creating, editing, or managing transformations and libraries

**What it teaches Claude:**
- YAML spec schemas for transformations and libraries
- JavaScript/Python code patterns
- Library import conventions (`import_name` must be camelCase of `name`)
- Testing with input/output fixtures
- Porting external libraries to RudderStack's sandbox

## Directory Structure

```
rudder-cli-skills/
├── README.md                           # This file
├── LICENSE                             # MIT License
├── skills/                             # Skills to install
│   ├── rudder-cli-workflow/
│   │   └── SKILL.md
│   └── rudderstack-transformations/
│       └── SKILL.md
├── docs/                               # Documentation
│   └── installation.md                 # Detailed installation guide
└── examples/                           # Example projects
    └── transformations-workflow/       # Complete transformation example
        ├── README.md
        ├── .claude/
        │   └── settings.example.json   # Example Claude Code permissions
        └── transformations/
            ├── base64-lib.yaml
            ├── test-transformation.yaml
            ├── javascript/
            │   ├── base64-lib.js
            │   └── test-transformation.js
            └── tests/
                ├── input/
                └── output/
```

## Examples

The `examples/` directory contains complete working projects demonstrating skill usage:

### [Transformations Workflow](examples/transformations-workflow/)

A complete example showing:
- Base64 encoding/decoding library ported to RudderStack
- Transformation using the library
- Test fixtures with input/output events
- YAML specs following conventions

## Prerequisites

- [Claude Code](https://claude.ai/code) CLI installed
- [Rudder CLI](https://github.com/rudderlabs/rudder-iac) installed
- RudderStack workspace with access token

## Documentation

- [Installation Guide](docs/installation.md) - Detailed setup instructions
- [RudderStack Transformations Docs](https://www.rudderstack.com/docs/features/transformations/)
- [Rudder CLI Documentation](https://github.com/rudderlabs/rudder-iac)

## Contributing

Contributions welcome! To add or improve skills:

1. Fork this repository
2. Create your skill in `skills/<skill-name>/SKILL.md`
3. Add an example in `examples/` if applicable
4. Submit a pull request

See [docs/installation.md](docs/installation.md) for skill authoring guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.
