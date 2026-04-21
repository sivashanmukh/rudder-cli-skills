---
name: rudder-data-graphs
description: Use when modeling entities and their relationships in RudderStack — defining entity types, relationship edges, identity resolution patterns, or data-graph YAML specs. Fires on mentions of "data graph", "datagraph", entity modeling, cross-source identity, or when editing data-graph resources via rudder-cli, Terraform, or MCP.
---

# RudderStack Data Graphs

A **data graph** describes the entities and events in a workspace's warehouse and how they relate — the shape a downstream Profiles / Identity Resolution / Activation workload consumes. Entities (e.g., User, Account) have stable primary IDs; events (e.g., Page View, Order Completed) have timestamps. Relationships connect them with cardinality.

## When to use

The user is authoring, reviewing, or debugging a `data-graph` YAML spec — or asks how to model users/accounts/events for downstream activation or identity resolution.

## Top-level shape

```yaml
version: rudder/v1
kind: data-graph
spec:
  id: my-data-graph
  account_id: wh-account-123        # warehouse account the graph is rooted in
  models:
    - id: user
      display_name: User
      type: entity                   # entity | event
      table: db.schema.users         # 3-part reference: catalog.schema.table
      primary_id: user_id            # required for entity; forbidden on event
      root: true                     # optional; marks the anchor of the graph
      description: Registered users
      relationships:
        - id: user-account
          display_name: User Account
          cardinality: one-to-one
          target: "#data-graph-model:account"
          source_join_key: account_id
          target_join_key: account_id

    - id: page_view
      display_name: Page View
      type: event
      table: db.schema.page_views
      timestamp: viewed_at           # required for event; forbidden on entity
      relationships:
        - id: pageview-user
          display_name: PageView User
          cardinality: many-to-one
          target: "#data-graph-model:user"
          source_join_key: user_id
          target_join_key: user_id
```

## Validation rules

- `table` must be a **3-part reference** (`catalog.schema.table`).
- Entity models require `primary_id` and must not set `timestamp`. Event models require `timestamp` and must not set `primary_id`.
- Cardinality between **event → event is forbidden**. Event→entity is always `many-to-one`; entity→event is always `one-to-many`. Entity↔entity can be any cardinality.
- `target` uses URN syntax `#data-graph-model:<model-id>` and must resolve to a model in the **same** spec.
- All `display_name` values across models and relationships in one graph must be unique.

## CLI commands

Data graphs are managed through the generic apply/validate/dry-run cycle:

```bash
rudder-cli data-graphs validate --all
rudder-cli data-graphs validate --modified
rudder-cli data-graphs validate model <id>
rudder-cli data-graphs validate relationship <id>
```

Apply/dry-run happens as part of the overall project apply cycle (see `rudder-cli-workflow`); there is no dedicated `data-graph apply` subcommand.

## Don't do this

- Don't create event↔event relationships — they are rejected at validation time.
- Don't set `primary_id` on event models or `timestamp` on entity models.
- Don't reference `target` models by short id — always use the `#data-graph-model:<id>` URN.

## Gotchas

- **Entity vs. event confusion** is the #1 failure mode. If validation complains about `primary_id`/`timestamp`, recheck the model's `type`.
- `target` references are validated semantically: a typo that passes YAML syntax still fails validation.

> **[DRAFT]** First-cut drawn from `@rudder-iac/cli/internal/providers/datagraph/`. Verify against the latest provider code before publishing.
