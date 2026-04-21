---
name: rudder-terraform-workflow
description: Use when managing RudderStack resources via Terraform — configuring the terraform-provider-rudderstack, authoring HCL for sources, destinations, connections, and transformations, running init/plan/apply, or organizing multi-workspace/multi-environment Terraform modules. Fires on mentions of "terraform-provider-rudderstack", Terraform + RudderStack, HCL resources for RudderStack, or IaC workflows for a RudderStack workspace.
---

# RudderStack Terraform Workflow

TODO: Cover provider installation, authentication, authoring HCL for the main resource types, standard init/plan/apply loop, module layout, and state management conventions.

## When to use

TODO

## Preflight

TODO: `terraform init` preconditions, provider version pinning, RudderStack access token, environment configuration.

## Provider configuration

TODO: `required_providers` block, authentication options, workspace selection.

## Resource catalog

TODO: list the resources and data sources the provider exposes, grouped by domain.

## Common workflows

TODO: bootstrap a workspace, manage sources + destinations, migrate from UI-managed to Terraform-managed resources, multi-env setup with workspaces or directories.

## Don't do this

TODO: running `terraform destroy` against a production workspace, mixing Terraform and UI edits to the same resource, forgetting to commit state.

## References

TODO: link to `@terraform-provider-rudderstack/` once drafted content lands.
