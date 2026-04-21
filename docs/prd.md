# rudder-agent-skills — PRD

- Date: 2026-04-20
- Status: v1 — ships alongside the initial marketplace (main branch)
- Owner: siva.shanmukh@gmail.com
- Companion design doc: [`docs/design.md`](design.md)

## TL;DR

`rudder-agent-skills` is a Claude Code plugin **marketplace** that packages RudderStack's developer-experience surfaces — CLI, MCP server, and Terraform — as **skills** an AI agent (Claude Code, Claude Desktop, any MCP client) can load on demand. Users install the plugins for the tools they use; the agent then knows our YAML/HCL/MCP conventions, the right commands, the right error-recovery moves, and stops guessing.

## 1. Problem

RudderStack ships three programmatic surfaces today.

| Surface | Tool | User today |
|---|---|---|
| CLI | `rudder-cli`, `rudder-typer` | Engineers automating instrumentation |
| MCP | `rudder-mcp-server` | AI agents managing workspaces |
| Terraform | `terraform-provider-rudderstack` | Platform / IaC teams |

These surfaces are increasingly used — a platform team might keep workspaces under Terraform, individual engineers drive day-to-day changes through the CLI, and AI agents triage or explore via MCP. When users bring AI into this loop (and they already do — Claude Code usage among our DevEx customers has been climbing), the agent's effectiveness is gated by how much RudderStack context it has:

- Without context, the agent misremembers YAML field names, suggests flags that don't exist, skips preflight checks (`rudder-cli auth login`), and burns turns on avoidable validation errors.
- With context, the agent behaves like a teammate who's read the docs — auto-invoking the right workflow, staging the right commands, recognizing errors before they ship.

The status-quo way to bridge this gap is per-user effort: custom CLAUDE.md files, pasted runbooks, hand-rolled system prompts. That work is duplicated across every customer and falls out of date the moment we ship a new CLI version.

## 2. Goals

- **Package every DevEx surface as Claude-ready skills** so customers don't re-invent context per repo.
- **Ship one install entry point** — one marketplace, regardless of which surface(s) a customer uses.
- **Respect prompt budget** — users pick the plugins they actually need; shared domain knowledge lives once, in `rudder-core`, so multi-tool users don't pay for duplicates.
- **Evolve alongside the product** — skills are versioned, git-diffable, and contributable from inside any DevEx workflow.

## 3. Non-goals

- Replacing RudderStack's official docs (this is a companion for agent authoring, not a docs replacement).
- Becoming a general-purpose RudderStack assistant for non-authoring use cases (billing Q&A, support ticket triage — out of scope).
- Auto-generating skill content from CLI/provider source — manual authoring with progressive disclosure is the initial approach.

## 4. Users

- **DevEx engineers at our customers** — primary audience. They drive Claude Code/Desktop to author tracking plans, data catalogs, transformations, Terraform modules, and MCP agent workflows.
- **Internal RudderStack engineers** — use the skills while dogfooding the CLI, MCP server, and provider.
- **AI agents** — indirect users; the real consumer of the skill payload at runtime.

## 5. Solution shape

One marketplace (`rudder-agent-skills`), four plugins:

| Plugin | What it contains |
|---|---|
| `rudder-core` | Cross-tool domain knowledge: data catalog, tracking plans, instrumentation planning and debugging. Installed regardless of tool. |
| `rudder-cli` | Driving `rudder-cli` and `rudder-typer` — validate, dry-run, apply, import, transformations. |
| `rudder-mcp` | Driving `rudder-mcp-server` — auth/setup, tool catalog, AI-agent patterns. |
| `rudder-terraform` | Driving the Terraform provider — resource and data-source usage, plan/apply cycles. |

Multi-tool users install 2–4 plugins; domain knowledge is never duplicated. Install:

```bash
/plugin marketplace add rudderlabs/rudder-agent-skills
/plugin install rudder-core@rudder-agent-skills
/plugin install rudder-cli@rudder-agent-skills
```

Structural details (skill file layout, frontmatter rules, naming conventions, branch strategy) are in the companion design doc.

## 6. What is currently in main branch

- **Marketplace + 2 populated plugins** — `rudder-core` (4 skills) and `rudder-cli` (4 skills) migrated from the previous `rudder-cli-skills` repo into the new layout with history-preserving moves.
- **[README.md](../README.md)** rewritten for marketplace-based install, with a per-plugin skill catalog and a coming-soon pointer for MCP and Terraform.
- **[CONTRIBUTING.md](../CONTRIBUTING.md)** — authoring conventions, frontmatter rules, testing checklist, PR expectations, and versioning.
- **Design doc** — captures scope, plugin split, naming, manifests, and the exact commit sequence that produced the reorg.

### Skill catalog

**`rudder-core`:** `rudder-data-catalog`, `rudder-tracking-plans`, `rudder-instrumentation-planning`, `rudder-instrumentation-debugging`.

**`rudder-cli`:** `rudder-cli-workflow`, `rudder-import-and-evolve`, `rudder-typer-workflow`, `rudder-transformations`.

## 7. In draft (stubs branch)

The `stubs` branch parks early-draft work that isn't ready for `main` yet. Two commits:

1. **Scaffolds** — frontmatter-complete SKILL.md stubs (body = TODO) for three additional skills and the plugin shells to host them:
   - `rudder-core/skills/rudder-data-graphs` — entity + relationship modeling
   - `rudder-mcp/skills/rudder-mcp-workflow` — MCP server setup + tool catalog
   - `rudder-terraform/skills/rudder-terraform-workflow` — provider setup + resource catalog

2. **`[DRAFT]` first-cut content** — TODO bodies replaced with first-cut guidance drafted from `@rudder-iac/cli/internal/providers/datagraph/`, `@rudder-mcp-server/`, and `@terraform-provider-rudderstack/`. Flagged as draft so the content is verified against current source repos before merging to `main`.

## 8. Planned follow-ups

Tracked as separate commits on `main` once the reorg is verified:

1. Absorb `rudder-typer-workflow` into `rudder-instrumentation-planning` — RudderTyper is a conditional branch of the planning flow (used when the customer has a tracking plan and wants typed clients), not a standalone workflow.
2. Expand `rudder-data-catalog` body to walk through custom types end-to-end.

## 9. Success signals

- **Customer feedback** via issues/PRs — the lower the "this skill got in my way" reports, the better the descriptions are tuned.
- **Contributions** from inside RudderStack as well as customers, visible as PRs on the repo.

## 10. Open questions

- **Governance** — who reviews and merges PRs? (Noted as TBD in `CONTRIBUTING.md`.)
- **Versioning cadence** — how often do we cut a marketplace release vs. rolling updates?
- **Distribution to Claude.ai / Claude API** — the same skill folders work there per `skills.md` §10, but require separate packaging. Not in scope for v1 but likely useful for customers using non-Claude-Code surfaces.

## 11. References

- Requirements: `This doc`
- CLI source: `@rudder-iac/`
- MCP server source: `@rudder-mcp-server/`
- Terraform provider source: `@terraform-provider-rudderstack/`
