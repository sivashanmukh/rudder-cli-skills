# Rudder Skills Marketplace Reorganization — Design

- Date: 2026-04-20
- Status: Draft, pending user review
- Owner: siva.shanmukh@gmail.com

## 1. Goal

Reorganize the existing `rudder-cli-skills` repo into a Claude Code plugin **marketplace** named `rudder-agent-skills` that covers every programmatic RudderStack surface (CLI, MCP server, Terraform provider) behind a single install entry point.

Optimize for **discoverability of everything** (users see the full surface from one marketplace listing) while giving them **fine-grained control over what gets loaded into their prompt budget** (users pick the plugins for the tools they use).

Ground-truth reference for marketplace/plugin/skill structure: `skills.md` (in parent directory).

## 2. Scope

The reorganization operates **only on what is currently committed to `main`** in the `rudder-cli-skills` repo. The 8 skills on `main` are:

```
rudder-cli-workflow
rudder-data-catalog
rudder-import-and-evolve
rudder-instrumentation-debugging
rudder-instrumentation-planning
rudder-tracking-plans
rudder-typer-workflow
rudderstack-transformations
```

These 8 skills are migrated to the new marketplace layout. Nothing else from the repo (other branches, uncommitted work, draft files) is in scope.

## 3. Design decisions

### 3.1 Naming

- Repo and directory rename: `rudder-cli-skills` → **`rudder-agent-skills`** (matches broadened scope; per `skills.md` §2).
- Prefix: every plugin and skill uses **`rudder-`**. The `rudderstack-transformations` skill is renamed to `rudder-transformations`.
- Tool-plugin seed skill names keep the existing `-workflow` suffix (e.g., `rudder-mcp-workflow`, `rudder-terraform-workflow`, mirroring `rudder-cli-workflow`). Domain skills in the core plugin do not use a suffix (e.g., `rudder-data-catalog`).

### 3.2 Marketplace & plugin split

Four plugins in one marketplace (`rudder-agent-skills`):

| Plugin | Purpose | Initial state on `main` |
|---|---|---|
| `rudder-core` | Cross-tool RudderStack domain knowledge (catalog, tracking plans, instrumentation strategy & debugging) | 4 skills migrated from `main` |
| `rudder-cli` | Workflows that drive `rudder-cli` and the `rudder-typer` CLI | 4 skills migrated from `main` |
| `rudder-mcp` | Workflows for `rudder-mcp-server` (AI/LLM agents managing RudderStack) | Not present on `main`; introduced on `stubs` branch |
| `rudder-terraform` | Workflows for the Terraform provider | Not present on `main`; introduced on `stubs` branch |

Rationale for four plugins (not three, not one):
- `rudder-core` absorbs the shared instrumentation domain so multi-tool users don't pay for duplicated descriptions in their prompt budget.
- Per-tool plugins match users' mental model ("I use the CLI; I use Terraform"). Users install 2–4 plugins based on what they use.
- Single combined plugin would force every user to load every tool's descriptions.

### 3.3 Auto-invocation vs slash-only

`disable-model-invocation: true` in frontmatter makes a skill slash-only (loads only via explicit `/<skill-name>`); the default auto-invokes based on description matching.

**No skills are marked slash-only in the initial reorg.** Selective `disable-model-invocation` remains a tool to apply later if any skill's description starts misfiring.

### 3.4 Progressive disclosure

Large/auxiliary content lives in `references/*.md` within each skill folder so the SKILL.md body stays lean and deeper material only loads on demand. Initial uses are introduced in follow-up commits (§7), not the reorg itself.

## 4. Skill partition (initial migration on `main`)

### 4.1 `rudder-core` (4 skills, auto-invoke)

| New path | Source | Body changes in this commit |
|---|---|---|
| `rudder-data-catalog/SKILL.md` | `skills/rudder-data-catalog/SKILL.md` | None |
| `rudder-tracking-plans/SKILL.md` | `skills/rudder-tracking-plans/SKILL.md` | None |
| `rudder-instrumentation-planning/SKILL.md` | `skills/rudder-instrumentation-planning/SKILL.md` | None |
| `rudder-instrumentation-debugging/SKILL.md` | `skills/rudder-instrumentation-debugging/SKILL.md` | None |

### 4.2 `rudder-cli` (4 skills, auto-invoke)

| New path | Source | Body changes in this commit |
|---|---|---|
| `rudder-cli-workflow/SKILL.md` | `skills/rudder-cli-workflow/SKILL.md` | None |
| `rudder-import-and-evolve/SKILL.md` | `skills/rudder-import-and-evolve/SKILL.md` | None |
| `rudder-typer-workflow/SKILL.md` | `skills/rudder-typer-workflow/SKILL.md` | None (absorption into instrumentation-planning is a separate follow-up commit, §7) |
| `rudder-transformations/SKILL.md` | `skills/rudderstack-transformations/SKILL.md` | Frontmatter `name` field updated to `rudder-transformations`; body unchanged |

## 5. Final state — `main` after reorg

```
rudder-agent-skills/                             # renamed from rudder-cli-skills
├── README.md                                    # rewritten: catalog + install for all 4 plugins
├── CONTRIBUTING.md                              # NEW: authoring + PR guidelines (§8.3)
├── LICENSE
├── .gitignore
├── .claude-plugin/
│   └── marketplace.json                         # lists only plugins that exist on main
├── docs/
│   ├── design.md                                # this document
│   ├── installation.md                          # preserved as-is
│   └── prd.md                                   # product requirements
├── examples/                                    # preserved as-is
└── plugins/
    ├── rudder-core/
    │   ├── .claude-plugin/plugin.json
    │   └── skills/
    │       ├── rudder-data-catalog/SKILL.md
    │       ├── rudder-tracking-plans/SKILL.md
    │       ├── rudder-instrumentation-planning/SKILL.md
    │       └── rudder-instrumentation-debugging/SKILL.md
    └── rudder-cli/
        ├── .claude-plugin/plugin.json
        └── skills/
            ├── rudder-cli-workflow/SKILL.md
            ├── rudder-import-and-evolve/SKILL.md
            ├── rudder-typer-workflow/SKILL.md
            └── rudder-transformations/SKILL.md
```

**Decision on marketplace listing:** on `main`, `marketplace.json` lists only the two plugins that actually exist (`rudder-core`, `rudder-cli`). Marketplace entries with `source` paths to non-existent directories would fail `claude plugin validate`. Discoverability of `rudder-mcp` and `rudder-terraform` as future plugins is surfaced in `README.md` instead. The `stubs` branch adds the MCP and Terraform entries to `marketplace.json` when the corresponding plugin directories appear.

## 6. Final state — `stubs` branch (off `main`)

Two commits on top of `main`:

### 6.1 `stubs` commit 1 — "Scaffold MCP, Terraform, and data-graphs skills"

Adds:

```
plugins/rudder-core/skills/
└── rudder-data-graphs/SKILL.md                  # frontmatter only; body is TODO

plugins/rudder-mcp/
├── .claude-plugin/plugin.json
└── skills/
    └── rudder-mcp-workflow/SKILL.md             # frontmatter only; body is TODO

plugins/rudder-terraform/
├── .claude-plugin/plugin.json
└── skills/
    └── rudder-terraform-workflow/SKILL.md       # frontmatter only; body is TODO
```

Updates `marketplace.json` to register `rudder-mcp` and `rudder-terraform`.

### 6.2 `stubs` commit 2 — "[DRAFT] First-cut content for data-graphs, MCP, and Terraform skills"

Replaces the three TODO bodies with real first-cut content drafted from:
- `@rudder-iac/cli/internal/providers/datagraph/` for `rudder-data-graphs`
- `@rudder-mcp-server/` for `rudder-mcp-workflow`
- `@terraform-provider-rudderstack/` for `rudder-terraform-workflow`

Commit message prefixed `[DRAFT]` so it's obvious it should not be merged as-is.

## 7. Follow-up commits on `main` (not part of the reorg itself)

Tracked separately so the reorg commits stay mechanical and reviewable:

1. **Absorb `rudder-typer-workflow` into `rudder-instrumentation-planning`** — delete `plugins/rudder-cli/skills/rudder-typer-workflow/`, add `plugins/rudder-core/skills/rudder-instrumentation-planning/references/rudder-typer.md`, update the planning skill body to invoke RudderTyper conditionally when the customer has a tracking plan.
2. **Expand `rudder-data-catalog` body to explicitly cover custom types** end-to-end (currently mentioned in description but underspecified in body).

These can land in either order, in any number of commits.

## 8. Manifests

### 8.1 `marketplace.json`

Path: `.claude-plugin/marketplace.json`

- `name`: `rudder-agent-skills`
- `owner.name`: TBD (ask at execution time)
- `owner.email`: TBD
- `metadata.description`: "Skills for working with RudderStack via CLI, MCP server, and Terraform."
- `metadata.version`: `1.0.0`
- `plugins[]`: entries for each plugin with `source: "./plugins/<plugin-name>"`. Versions live here, not in `plugin.json`, per `skills.md` §3.

### 8.2 `plugin.json` (per plugin)

Path: `plugins/<plugin-name>/.claude-plugin/plugin.json`

Minimal: `name`, `description`. Version omitted (set in `marketplace.json`).

### 8.3 `CONTRIBUTING.md`

Path: `CONTRIBUTING.md` at the repo root. Covers the following so new skills and plugins can be added consistently:

- **Repo layout** — pointer to `skills.md` and this design doc as the ground truth for structure; explain the four-plugin split so contributors know which plugin a new skill belongs in.
- **Authoring a new skill** — file layout (`SKILL.md` + optional `references/*.md`), YAML frontmatter requirements (`name` must match folder, `description` ≤ 1024 chars and front-loads trigger keywords), progressive-disclosure guidance from `skills.md` §5.4.
- **Naming conventions** — every plugin and skill uses the `rudder-` prefix; tool-plugin seed skills use `-workflow` suffix; domain skills in `rudder-core` do not.
- **Auto-invocation vs slash-only** — when to add `disable-model-invocation: true` (niche, heavy, or easily-misfiring skills).
- **Testing before PR** — run `claude plugin validate .` at repo root; smoke-test by installing the marketplace locally and verifying the target skill auto-invokes on a representative prompt.
- **PR expectations** — include an example prompt that should trigger the skill and an example that should not; link to the source repo (e.g., a `rudder-iac` PR or an `rudder-mcp-server` tool) the skill is documenting.
- **Versioning** — bump `version` in `marketplace.json` (plugin versions are set there, not in `plugin.json`, for relative-path sources).
- **Governance** — who reviews and merges PRs (TBD: owner to fill in).

## 9. Execution plan

The reorg lands in this commit sequence on `main`:

1. **Add reorg design spec** — write `docs/design.md` (this document) to `main` so it's the first artifact of the reorganization.
2. **Add marketplace + plugin manifests** — create `.claude-plugin/marketplace.json`, `plugins/rudder-core/.claude-plugin/plugin.json`, `plugins/rudder-cli/.claude-plugin/plugin.json`. No skill moves yet.
3. **Migrate `rudder-core` skills** — `git mv skills/rudder-data-catalog plugins/rudder-core/skills/rudder-data-catalog` (and the other three core skills). History-preserving moves.
4. **Migrate `rudder-cli` skills** — `git mv` the four CLI skills into `plugins/rudder-cli/skills/`; rename `rudderstack-transformations` to `rudder-transformations` in the same commit and update its frontmatter `name` field.
5. **Update `README.md`** — replace the install instructions with marketplace-based install (`/plugin marketplace add ...`) and rewrite the catalog table to list the four plugins (with coming-soon notes for MCP and Terraform).
6. **Add `CONTRIBUTING.md`** — author the file per §8.3.
7. **Rename the local directory** from `rudder-cli-skills` to `rudder-agent-skills` (filesystem operation; the GitHub remote rename happens separately when the user is ready).

After step 7, validate locally with `claude plugin validate .` and a smoke install.

Then create the `stubs` branch and push the two commits described in §6.

## 10. Out of scope

- The `feature/conditional-validation-skill` branch and the conditional-validation skill itself — left untouched.
- Uncommitted working-directory changes — not migrated.
- Publishing to external marketplace indexes (buildwithclaude.com, claudemarketplaces.com).
- Cross-surface distribution (Claude.ai zip, Claude API Skills upload).
- GitHub remote rename — documented but not executed here (requires admin access).
- Authoring additional MCP/Terraform skills beyond the single seed skill per plugin.
- A standalone `rudder-typer` plugin. Reconsidered after the typer absorption follow-up lands.

## 11. Validation

Before declaring the reorg done on `main`:

- `claude plugin validate .` at the repo root passes with zero errors.
- Local install round-trip works: from the parent directory, `claude plugin marketplace add ./rudder-agent-skills`, then `claude plugin install rudder-core@rudder-agent-skills` and `claude plugin install rudder-cli@rudder-agent-skills` — each succeeds and Claude Code lists the migrated skills.
- For one skill in each plugin, run a natural-language prompt that should trigger it (e.g., "create a tracking plan for checkout events") and confirm Claude auto-invokes the correct skill.

## 12. Success criteria

- `main` contains every skill that was previously on `origin/main`, reorganized into the four-plugin marketplace layout — no content additions or deletions beyond renames and folder moves.
- `claude plugin validate .` passes.
- `CONTRIBUTING.md` exists at the repo root and covers the §8.3 checklist.
- `stubs` has exactly two commits on top of `main`: one adding scaffolds, one adding drafted content.
- The two follow-up commits (typer absorption, data-catalog expansion) land on `main` after the reorg is verified.

## 13. References

- `skills.md` (parent of this repo) — marketplace/plugin/skill build spec
- Current repo: `rudder-cli-skills/`
- Linked CLI source: `@rudder-iac/`
- Linked MCP server source: `@rudder-mcp-server/`
- Linked Terraform provider source: `@terraform-provider-rudderstack/`
