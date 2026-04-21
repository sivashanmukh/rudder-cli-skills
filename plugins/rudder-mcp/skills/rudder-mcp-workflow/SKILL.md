---
name: rudder-mcp-workflow
description: Use when connecting Claude or another AI/LLM agent to rudder-mcp-server and managing RudderStack through MCP tool calls — setting up the server, authenticating, listing available tools, and driving workflows over catalog, sources, destinations, transformations, RETL, tracking plans, and live events. Fires on mentions of "rudder-mcp-server", "MCP server for RudderStack", MCP tools for RudderStack, or AI agents managing RudderStack.
---

# RudderStack MCP Server Workflow

TODO: Cover installing and running `rudder-mcp-server`, configuring auth, wiring it to Claude Code (or other MCP clients), the tool catalog it exposes, and representative workflows.

## When to use

TODO

## Preflight

TODO: environment variables, access token, server connectivity check.

## Tool catalog

TODO: summarize the tools `rudder-mcp-server` exposes, grouped by domain (workspace admin, data catalog, sources, destinations, transformations, RETL, tracking plans, live events).

## Common workflows

TODO: example prompt → MCP tool call sequences.

## Don't do this

TODO: tools that mutate shared state; when to prefer rudder-cli over MCP.

## References

TODO: link to `@rudder-mcp-server/` once drafted content lands.
