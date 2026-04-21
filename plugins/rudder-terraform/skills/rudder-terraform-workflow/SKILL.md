---
name: rudder-terraform-workflow
description: Use when managing RudderStack resources via Terraform — configuring the terraform-provider-rudderstack, authoring HCL for sources, destinations, connections, and transformations, running init/plan/apply, or organizing multi-workspace/multi-environment Terraform modules. Fires on mentions of "terraform-provider-rudderstack", Terraform + RudderStack, HCL resources for RudderStack, or IaC workflows for a RudderStack workspace.
---

# RudderStack Terraform Workflow

The [`rudderlabs/rudderstack`](https://github.com/rudderlabs/terraform-provider-rudderstack) Terraform provider manages a RudderStack workspace as infrastructure-as-code: sources, destinations, connections, and transformations.

## When to use

The user is authoring HCL for RudderStack, running `terraform plan/apply` against a workspace, migrating from UI-managed to Terraform-managed resources, or organizing multi-env setups.

## Preflight

- [ ] Terraform ≥ 1.0 installed.
- [ ] Access token available as env var `RUDDERSTACK_ACCESS_TOKEN` (preferred) or in the provider block.
- [ ] Optional: override API base URL with `RUDDERSTACK_API_URL` (default: `https://api.rudderstack.com/v2`).
- [ ] Confirm with the user whether the target workspace is dev/staging/prod before any `terraform apply`.

## Provider setup

```hcl
terraform {
  required_providers {
    rudderstack = {
      source  = "rudderlabs/rudderstack"
      version = "~> 4.3.1"
    }
  }
}

provider "rudderstack" {
  # access_token = "..."        # or set RUDDERSTACK_ACCESS_TOKEN
  # api_url      = "https://api.rudderstack.com/v2"
}
```

## Resource catalog (high level)

- **`rudderstack_connection`** — joins a source to a destination. Required for data to flow.
- **Sources (~47):** one resource per source type — e.g. `rudderstack_source_javascript`, `rudderstack_source_nodejs`, `rudderstack_source_python`, `rudderstack_source_android`, `rudderstack_source_ios`, plus HTTP webhooks and SaaS integrations (Slack, Auth0, Braze, Iterable, Segment, PagerDuty, Looker, etc.).
- **Destinations (~48):** one resource per destination type — warehouses (`rudderstack_destination_bigquery`, `_redshift`, `_snowflake`, `_postgres`), analytics (`_google_analytics_4`, `_amplitude`, `_mixpanel`, `_posthog`), marketing (`_salesforce`, `_marketo`, `_braze`, `_hubspot`, `_intercom`), infra (`_kafka`, `_kinesis`, `_redis`, `_gcs`, `_s3`), ad platforms (`_google_ads`, `_facebook_pixel`, `_tiktok_ads`, `_linkedin_ads`), and generic `_webhook` / `_http`.

No data sources are currently exposed — the provider is resource-centric.

## Minimal working example

```hcl
terraform {
  required_providers {
    rudderstack = {
      source  = "rudderlabs/rudderstack"
      version = "~> 4.3.1"
    }
  }
}

provider "rudderstack" {}     # uses RUDDERSTACK_ACCESS_TOKEN from env

resource "rudderstack_source_javascript" "web" {
  name = "my-web-app"
}

resource "rudderstack_destination_webhook" "logs" {
  name = "event-logger"

  config {
    webhook_url    = "https://logs.example.com/events"
    webhook_method = "POST"
  }
}

resource "rudderstack_connection" "main" {
  source_id      = rudderstack_source_javascript.web.id
  destination_id = rudderstack_destination_webhook.logs.id
}
```

## Standard cycle

```bash
terraform init       # fetches the provider
terraform fmt        # canonicalize HCL
terraform validate   # schema check
terraform plan       # preview; review diff with the user
terraform apply      # apply to the workspace
```

## Don't do this

- Don't run `terraform destroy` against a shared/prod workspace without explicit confirmation — all sources, destinations, and connections in the state go away.
- Don't mix Terraform-managed and UI-edited changes to the same resource; manual edits cause drift and surprise diffs on the next plan.
- Don't commit `.tfstate` to git without remote state backend encryption — it contains credentials.

## Gotchas

- **Breaking change at v3.0.0+:** the `onetrust_cookie_categories` destination field was replaced by a general `consent_management` block (oneTrust, Ketch, custom). Migrations that carry over the old field silently lose consent rules.
- **Consent management nesting:** many destinations accept per-platform (`web`, `android`, `ios`, `warehouse`) consent providers. A mismatched resolution strategy or provider name is accepted by the schema but silently dropped at runtime.

> **[DRAFT]** First-cut drawn from `@terraform-provider-rudderstack/`. Resource names and counts reflect the current provider; verify the exact resource list before publishing.
