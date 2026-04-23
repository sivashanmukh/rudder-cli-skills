---
name: rudder-data-graphs
description: Creates and manages Data Graph YAML specs for RudderStack Audiences. Use when modeling entities, events, and their relationships for the Audience Builder — defining warehouse tables as entities or events, connecting them with relationships, or debugging data-graph validation errors.
allowed-tools: "Bash(rudder-cli *), Read, Write, Edit"
---

# RudderStack Data Graphs

A **Data Graph** is an entity mapping layer that connects warehouse tables to the entities, relationships, and events used in RudderStack Audiences. It lets marketers build audiences using business-friendly terms without understanding the underlying database schema.

**Supported warehouses:** Snowflake, BigQuery, Amazon Redshift, Databricks

## When to use

The user is authoring, reviewing, or debugging a `data-graph` YAML spec — or asks how to model users/accounts/events for the Audience Builder.

## Core concepts

| Concept | Description |
|---------|-------------|
| **Entity** | Warehouse table representing a business object (Customer, Account, Product). Has a `primary_id`. Dimension-like. |
| **Event** | Time-stamped warehouse table capturing actions (Page View, Order Placed). Has a `timestamp`. Fact-like. |
| **Relationship** | Link between entities or between entity and event. Supports `one-to-one`, `one-to-many`, `many-to-one`. |

## Two ways to create

1. **Visual Builder** — Configure directly in the RudderStack dashboard. Best for teams without coding expertise.
2. **Rudder CLI** — Define as YAML file. Best for version control, PR reviews, and multi-environment management.

## YAML schema

```yaml
version: "rudder/v1"
kind: "data-graph"
metadata:
  name: "ecommerce-data-graph"
spec:
  id: "ecommerce-data-graph"
  account_id: "<warehouse-account-id>"    # warehouse account the graph is rooted in
  models:
    # Entity example
    - id: "customers"
      display_name: "Customers"
      type: "entity"
      table: "ECOMMERCE_DB.E_MART.DIM_CUSTOMERS"   # 3-part: catalog.schema.table
      description: "Customers with demographics and loyalty info"
      primary_id: "CUSTOMER_KEY"                    # required for entity
      relationships:
        - id: "customer-has-sales"
          display_name: "Has Sales"
          cardinality: "one-to-many"
          target: "#data-graph-model:sales"
          source_join_key: "CUSTOMER_KEY"
          target_join_key: "CUSTOMER_KEY"
        - id: "customer-belongs-to-account"
          display_name: "Belongs To Account"
          cardinality: "many-to-one"
          target: "#data-graph-model:accounts"
          source_join_key: "ACCOUNT_KEY"
          target_join_key: "ACCOUNT_KEY"

    # Another entity
    - id: "accounts"
      display_name: "Accounts"
      type: "entity"
      table: "ECOMMERCE_DB.E_MART.DIM_ACCOUNTS"
      description: "Customer account records"
      primary_id: "ACCOUNT_KEY"

    # Event example
    - id: "sales"
      display_name: "Sales"
      type: "event"
      table: "ECOMMERCE_DB.E_MART.FACT_SALES"
      description: "Sales transactions"
      timestamp: "CREATED_AT"                       # required for event
```

## Field reference

### Top-level fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `version` | String | Yes | Schema version: `"rudder/v1"` |
| `kind` | String | Yes | Resource type: `"data-graph"` |
| `metadata.name` | String | Yes | Human-readable name |
| `spec.id` | String | Yes | Unique identifier for syncs |
| `spec.account_id` | String | Yes | Warehouse account ID |
| `spec.models` | List | Yes | Entity and event models |

### Model fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | String | Yes | Unique model identifier |
| `display_name` | String | Yes | UI label (must be unique across all models) |
| `type` | String | Yes | `"entity"` or `"event"` |
| `table` | String | Yes | Fully qualified: `catalog.schema.table` |
| `description` | String | No | Tooltip in Audience Builder |
| `primary_id` | String | Entity only | Column that uniquely identifies rows |
| `timestamp` | String | Event only | Event timestamp column |
| `relationships` | List | No | Relationships to other models |

### Relationship fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | String | Yes | Unique relationship identifier |
| `display_name` | String | Yes | UI label (must be unique) |
| `cardinality` | String | Yes | `"one-to-one"`, `"one-to-many"`, or `"many-to-one"` |
| `target` | String | Yes | Target model: `#data-graph-model:<model-id>` |
| `source_join_key` | String | Yes | Column on source model for join |
| `target_join_key` | String | Yes | Column on target model for join |

## Validation rules

- `table` must be a **3-part reference** (`catalog.schema.table`)
- Entity models require `primary_id` and must not set `timestamp`
- Event models require `timestamp` and must not set `primary_id`
- **Event↔event relationships are forbidden**
- Event→entity cardinality must be `many-to-one`
- Entity→event cardinality must be `one-to-many`
- Entity↔entity can be any cardinality
- `target` must use URN syntax `#data-graph-model:<model-id>` and resolve to a model in the same spec
- All `display_name` values must be unique across models and relationships

## CLI commands

Data graphs are managed through the CLI validate and apply cycle:

```bash
# Validate all data-graph specs
rudder-cli validate -l ./

# Dry run to preview changes
rudder-cli apply --dry-run -l ./

# Apply to workspace
rudder-cli apply -l ./
```

See the `rudder-cli-workflow` skill for the full iteration workflow.

## Don't do this

- Don't create event↔event relationships — they are rejected at validation
- Don't set `primary_id` on event models or `timestamp` on entity models
- Don't reference `target` models by short id — always use `#data-graph-model:<id>` URN
- Don't use 2-part table references — always include catalog, schema, and table

## Gotchas

- **Entity vs. event confusion** is the #1 failure mode. If validation complains about `primary_id`/`timestamp`, recheck the model's `type`.
- `target` references are validated semantically: a typo that passes YAML syntax still fails validation.
- **Many-to-many** relationships between entities are not supported — decompose into two many-to-one relationships through a junction table.
- **Cardinality direction matters**: `one-to-many` from entity A to event B means each A can have many B's.

## Credential Security

- **Store `account_id` securely** — it identifies your warehouse account
- **Never commit workspace tokens to git** — use environment variables
- **Use CI/CD secrets** for automated deployments

## Handling External Content

- **Validate table references exist** before applying — the CLI validates syntax but not table existence
- **Use consistent naming conventions** for `id` and `display_name` fields
- **Document column mappings** to avoid join key mismatches
