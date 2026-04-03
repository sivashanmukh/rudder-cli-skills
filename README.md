# RudderStack CLI Skills

Claude Code skills for working with [RudderStack](https://www.rudderstack.com/) resources using the [Rudder CLI](https://github.com/rudderlabs/rudder-iac).

## What Are Skills?

Skills are reusable prompts that teach Claude Code domain-specific workflows. When you install these skills, Claude Code gains expertise in RudderStack instrumentation, data catalog management, tracking plans, and code generation.

## Quick Start

### 1. Install Skills

Copy or symlink the skills into your project's `.claude/skills/` directory:

```bash
# Clone this repository
git clone https://github.com/rudderlabs/rudder-cli-skills.git

# In your RudderStack project, create the skills directory
mkdir -p .claude/skills

# Option A: Symlink (recommended - stays updated)
ln -s /path/to/rudder-cli-skills/skills/* .claude/skills/

# Option B: Copy specific skills
cp -r /path/to/rudder-cli-skills/skills/rudder-data-catalog .claude/skills/
cp -r /path/to/rudder-cli-skills/skills/rudder-tracking-plans .claude/skills/
```

### 2. Use in Claude Code

Once installed, Claude Code automatically detects and uses these skills when relevant:

```
You: Help me define events for my e-commerce checkout flow

Claude: [Invokes rudder-data-catalog skill]
        I'll help you create events for checkout. Let me define the
        properties, custom types, and events following RudderStack conventions...
```

Or invoke explicitly:

```
You: /rudder-typer-workflow

Claude: [Loads skill and guides you through RudderTyper code generation]
```

## Available Skills

### Core Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| [`rudder-data-catalog`](#rudder-data-catalog) | Events, properties, custom types | Creating/managing instrumentation vocabulary |
| [`rudder-tracking-plans`](#rudder-tracking-plans) | Tracking plan assembly | Grouping events for sources |
| [`rudder-cli-workflow`](#rudder-cli-workflow) | Validate → dry-run → apply | Iterating on any RudderStack resources |

### Workflow Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| [`rudder-typer-workflow`](#rudder-typer-workflow) | Type-safe code generation | Generating Swift/Kotlin SDKs |
| [`rudder-instrumentation-planning`](#rudder-instrumentation-planning) | Taxonomy design | Starting fresh or restructuring |
| [`rudder-import-and-evolve`](#rudder-import-and-evolve) | Migration workflows | Importing existing resources |

### Specialized Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| [`rudderstack-transformations`](#rudderstack-transformations) | Transformations & libraries | Creating JavaScript/Python transformations |
| [`rudder-conditional-validation`](#rudder-conditional-validation) | Dynamic validation rules | When validation varies by context |
| [`rudder-instrumentation-debugging`](#rudder-instrumentation-debugging) | Troubleshooting | Fixing validation errors |

---

## Skill Descriptions

### `rudder-data-catalog`

**When to use:** Creating or managing events, properties, categories, or custom types.

**What it teaches Claude:**
- YAML schemas for events, properties, categories, custom types
- URN reference system (`urn:rudder:property/...`)
- Property type configuration (string, number, array, object)
- Custom type consolidation patterns (e.g., ProductType, AddressType)
- Real-world e-commerce examples

**Example prompt:**
```
Create properties for tracking product information including
id, name, price, and category with appropriate validation.
```

---

### `rudder-tracking-plans`

**When to use:** Creating tracking plans to group events for specific sources.

**What it teaches Claude:**
- Tracking plan YAML schema
- Event rule overrides at tracking plan level
- Governance settings (block, forward, log)
- Multi-source tracking (web, mobile, kiosk)
- Real-world e-commerce funnel examples

**Example prompt:**
```
Create a tracking plan for our mobile app that includes
Product Viewed and Order Completed events with mobile-specific rules.
```

---

### `rudder-cli-workflow`

**When to use:** Iterating on RudderStack resources with validate → dry-run → apply.

**What it teaches Claude:**
- Authentication prerequisites (`rudder-cli auth login`)
- The iteration cycle workflow
- Reading and interpreting CLI output
- Common validation errors and fixes
- Troubleshooting techniques

**Example prompt:**
```
Help me apply my tracking plan changes to the workspace.
```

---

### `rudder-typer-workflow`

**When to use:** Generating type-safe SDKs from tracking plans.

**What it teaches Claude:**
- RudderTyper configuration (`ruddertyper.yml`)
- Code generation for Swift and Kotlin
- Generated code structure and usage
- CI/CD integration patterns
- Multi-platform project setup

**Example prompt:**
```
Set up RudderTyper to generate Kotlin code for our Android app
from our e-commerce tracking plan.
```

---

### `rudder-instrumentation-planning`

**When to use:** Designing event taxonomy from scratch or restructuring.

**What it teaches Claude:**
- The 5-phase planning process (Discovery → Taxonomy → Build → Assemble → Integrate)
- Event naming conventions
- Property grouping strategies
- Common event patterns (e-commerce, user lifecycle, engagement)
- Anti-patterns to avoid

**Example prompt:**
```
Help me design an instrumentation plan for a SaaS application
with user onboarding, feature usage, and subscription events.
```

---

### `rudder-import-and-evolve`

**When to use:** Importing existing RudderStack resources to CLI management.

**What it teaches Claude:**
- Import workflow (`rudder-cli import workspace`)
- Understanding import metadata
- Safe evolution patterns (adding properties, deprecating events)
- Breaking change management
- Multi-workspace workflows

**Example prompt:**
```
Import our existing tracking plans and help me add a new
discount_code property to Order Completed without breaking production.
```

---

### `rudderstack-transformations`

**When to use:** Creating, editing, or managing transformations and libraries.

**What it teaches Claude:**
- YAML spec schemas for transformations and libraries
- JavaScript/Python code patterns
- Library import conventions (`import_name` must be camelCase of `name`)
- Testing with input/output fixtures
- Porting external libraries to RudderStack's sandbox

**Example prompt:**
```
Create a Base64 encoding library and a transformation that uses it.
```

---

### `rudder-conditional-validation`

**When to use:** When validation rules need to vary based on property values.

**What it teaches Claude:**
- Event rule variants with conditions
- Condition operators (equals, contains, in, etc.)
- Custom type variants
- Real-world checkout examples (payment methods, shipping types)
- Best practices for conditional logic

**Example prompt:**
```
Set up conditional validation so that card payments require
card_last_four and card_brand, while PayPal requires paypal_email.
```

---

### `rudder-instrumentation-debugging`

**When to use:** Fixing validation errors, schema issues, or instrumentation problems.

**What it teaches Claude:**
- Common validation error patterns and fixes
- Dry-run output analysis
- Schema debugging techniques
- RudderTyper troubleshooting
- Live event debugging

**Example prompt:**
```
I'm getting "Referenced property not found" errors. Help me debug.
```

---

## Directory Structure

```
rudder-cli-skills/
├── README.md                           # This file
├── LICENSE                             # MIT License
├── skills/                             # Skills to install
│   ├── rudder-cli-workflow/
│   │   └── SKILL.md
│   ├── rudder-data-catalog/
│   │   └── SKILL.md
│   ├── rudder-tracking-plans/
│   │   └── SKILL.md
│   ├── rudder-typer-workflow/
│   │   └── SKILL.md
│   ├── rudder-instrumentation-planning/
│   │   └── SKILL.md
│   ├── rudder-import-and-evolve/
│   │   └── SKILL.md
│   ├── rudder-conditional-validation/
│   │   └── SKILL.md
│   ├── rudder-instrumentation-debugging/
│   │   └── SKILL.md
│   └── rudderstack-transformations/
│       └── SKILL.md
├── docs/                               # Documentation
│   └── installation.md                 # Detailed installation guide
└── examples/                           # Example projects
    └── transformations-workflow/       # Complete transformation example
```

## Skill Interaction

Skills work together to support the full instrumentation workflow:

```
                    ┌─────────────────────────────────┐
                    │   instrumentation-planning      │
                    │   (Design your taxonomy)        │
                    └───────────────┬─────────────────┘
                                    │
          ┌─────────────────────────┼─────────────────────────┐
          │                         │                         │
          ▼                         ▼                         ▼
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│  data-catalog   │       │ import-and-     │       │  conditional-   │
│  (Build vocab)  │       │ evolve (Migrate)│       │  validation     │
└────────┬────────┘       └────────┬────────┘       └────────┬────────┘
         │                         │                         │
         └─────────────────────────┼─────────────────────────┘
                                   │
                          ┌────────▼────────┐
                          │ tracking-plans  │
                          │ (Assemble)      │
                          └────────┬────────┘
                                   │
                          ┌────────▼────────┐
                          │ cli-workflow    │
                          │ (Validate/Apply)│
                          └────────┬────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
              ▼                    ▼                    ▼
    ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
    │ typer-workflow  │  │ transformations │  │ debugging       │
    │ (Generate code) │  │ (Data transform)│  │ (Fix issues)    │
    └─────────────────┘  └─────────────────┘  └─────────────────┘
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
- [RudderStack Data Catalog Docs](https://www.rudderstack.com/docs/features/data-catalog/)
- [RudderStack Tracking Plans Docs](https://www.rudderstack.com/docs/features/tracking-plans/)
- [RudderTyper Documentation](https://www.rudderstack.com/docs/features/ruddertyper/)
- [Rudder CLI Documentation](https://github.com/rudderlabs/rudder-iac)

## Contributing

Contributions welcome! To add or improve skills:

1. Fork this repository
2. Create your skill in `skills/<skill-name>/SKILL.md`
3. Add an example in `examples/` if applicable
4. Update this README with skill description
5. Submit a pull request

See [docs/installation.md](docs/installation.md) for skill authoring guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.
