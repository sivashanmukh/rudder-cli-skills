---
name: rudder-import-and-evolve
description: Imports existing RudderStack workspace resources into YAML files for git-based management. Use when importing existing RudderStack resources to CLI management and evolving them safely
allowed-tools: "Bash(rudder-cli *), Read, Write, Edit"
---

# Import and Evolve Workflow

This skill teaches how to **import existing RudderStack resources** into CLI management and **safely evolve** your tracking schema over time.

## When to Use This Skill

- You have existing tracking plans, events, or properties in RudderStack
- You want to manage them via YAML files and git
- You need to make changes without breaking production SDKs
- You're migrating from UI-based management to CLI

## Import Workflow

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   RudderStack   │────▶│   Import to     │────▶│   Local YAML    │
│    Workspace    │     │   Local Files   │     │     Files       │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                        │
                                                        ▼
                                               ┌─────────────────┐
                                               │   Git Version   │
                                               │    Control      │
                                               └─────────────────┘
```

### Step 1: Authenticate

```bash
rudder-cli auth login
```

Select your workspace when prompted.

### Step 2: Verify Connection

```bash
rudder-cli workspace info
```

Should show your workspace name and ID.

### Step 3: Import Resources

```bash
rudder-cli import workspace
```

This imports:
- Events
- Properties
- Categories
- Custom types
- Tracking plans
- Event stream sources (if applicable)
- Transformations and libraries

### Step 4: Review Imported Files

```
imported/
├── data-catalog/
│   ├── events/
│   │   └── *.yaml
│   ├── properties/
│   │   └── *.yaml
│   ├── categories/
│   │   └── *.yaml
│   └── custom-types/
│       └── *.yaml
└── tracking-plans/
    └── *.yaml
```

Each file includes **import metadata**:

```yaml
version: "rudder/v1"
kind: "event"
metadata:
  name: "events"
  import:
    id: "evt_abc123xyz"        # Links to workspace resource
    workspace: "ws_xyz789"
spec:
  name: "Product Viewed"
  # ... rest of spec
```

**Important:** The `metadata.import` section links local files to workspace resources. Don't modify these IDs.

## Safe Evolution Patterns

### Pattern 1: Adding a New Property

**Scenario:** Add `discount_code` to Order Completed event.

```bash
# 1. Create the property
```

```yaml
# properties/order-properties.yaml
version: "rudder/v1"
kind: "property"
metadata:
  name: "properties"
spec:
  name: "discount_code"
  type: "string"
  description: "Applied discount code"
  config:
    maxLength: 50
```

```bash
# 2. Add to event (optional, not required)
```

```yaml
# events/order-completed.yaml
spec:
  name: "Order Completed"
  rules:
    # ... existing rules
    - property: "urn:rudder:property/discount_code"
      required: false  # Start optional!
```

```bash
# 3. Validate → Dry-run → Apply
rudder-cli validate -l ./
rudder-cli apply --dry-run -l ./
rudder-cli apply -l ./
```

**Safe because:** New optional property doesn't break existing SDKs.

### Pattern 2: Making a Property Required

**Scenario:** `session_id` was optional, now must be required.

**Phased approach:**

```yaml
# Phase 1: Add to tracking plan as required (not event definition)
# tracking-plans/web-app.yaml
spec:
  events:
    - event: "urn:rudder:event/product-viewed"
      rules:
        - property: "urn:rudder:property/session_id"
          required: true  # Required for this plan only
```

```bash
# Apply and monitor for violations
rudder-cli apply -l ./
```

```yaml
# Phase 2: After SDKs updated, make required at event level
# events/product-viewed.yaml
spec:
  rules:
    - property: "urn:rudder:property/session_id"
      required: true  # Now required everywhere
```

**Safe because:** Tracking plan override catches violations before hard requirement.

### Pattern 3: Renaming an Event (Breaking Change)

**Scenario:** Rename `Product View` to `Product Viewed`.

**Never do this directly!** It breaks existing SDKs.

```bash
# 1. Create new event with correct name
```

```yaml
# events/product-viewed.yaml (NEW)
version: "rudder/v1"
kind: "event"
metadata:
  name: "events"
spec:
  name: "Product Viewed"  # New name
  rules:
    # Same rules as old event
```

```bash
# 2. Add both to tracking plans
```

```yaml
# tracking-plans/web-app.yaml
spec:
  events:
    - event: "urn:rudder:event/product-view"      # Old (deprecated)
    - event: "urn:rudder:event/product-viewed"    # New
```

```bash
# 3. Update SDKs to use new event name
# 4. Monitor both events in analytics
# 5. After transition period, remove old event
```

```yaml
# tracking-plans/web-app.yaml (after transition)
spec:
  events:
    # - event: "urn:rudder:event/product-view"  # Removed
    - event: "urn:rudder:event/product-viewed"
```

```bash
# 6. Delete old event definition
rudder-cli apply -l ./  # Will show "Deleted [event] Product View"
```

### Pattern 4: Deprecating an Event

**Scenario:** Remove `Legacy Signup` event.

```bash
# 1. Add deprecation notice
```

```yaml
# events/legacy-signup.yaml
spec:
  name: "Legacy Signup"
  description: "DEPRECATED: Use 'Signed Up' instead. Will be removed 2024-06-01."
```

```bash
# 2. Remove from tracking plans (events still validate)
```

```yaml
# tracking-plans/web-app.yaml
spec:
  events:
    # - event: "urn:rudder:event/legacy-signup"  # Removed from plan
    - event: "urn:rudder:event/signed-up"        # Use this instead
```

```bash
# 3. Communicate to SDK teams
# 4. After deadline, delete event file and apply
rm events/legacy-signup.yaml
rudder-cli apply -l ./
```

### Pattern 5: Adding a Custom Type to Existing Properties

**Scenario:** Group shipping properties into AddressType.

```bash
# 1. Create the custom type
```

```yaml
# custom-types/address-type.yaml
version: "rudder/v1"
kind: "custom-type"
metadata:
  name: "custom-types"
spec:
  name: "AddressType"
  type: "object"
  config:
    properties:
      - property: "urn:rudder:property/street"
        required: true
      - property: "urn:rudder:property/city"
        required: true
      - property: "urn:rudder:property/state"
        required: true
      - property: "urn:rudder:property/zipcode"
        required: true
```

```bash
# 2. Create wrapper property
```

```yaml
# properties/shipping-address.yaml
version: "rudder/v1"
kind: "property"
metadata:
  name: "properties"
spec:
  name: "shipping_address"
  customType: "urn:rudder:custom-type/address-type"
  description: "Customer shipping address"
```

```bash
# 3. Update event to use new property
```

```yaml
# events/order-completed.yaml
spec:
  rules:
    # Old individual properties (keep during transition)
    - property: "urn:rudder:property/shipping_street"
    - property: "urn:rudder:property/shipping_city"
    # ... etc

    # New custom type property
    - property: "urn:rudder:property/shipping_address"
      customType: "urn:rudder:custom-type/address-type"
```

```bash
# 4. After SDKs migrate, remove old properties
```

## Multi-Workspace Management

### Scenario: Dev/Staging/Production

```
workspaces/
├── development/
│   └── (imported from dev workspace)
├── staging/
│   └── (imported from staging workspace)
└── production/
    └── (imported from prod workspace)
```

### Switch Workspaces

```bash
# Login to different workspace
rudder-cli auth login

# Verify current workspace
rudder-cli workspace info
```

### Promote Changes

```bash
# 1. Develop and test in dev workspace
cd workspaces/development
rudder-cli apply -l ./

# 2. Copy to staging, apply
cp -r data-catalog ../staging/
cd ../staging
rudder-cli apply -l ./

# 3. After testing, copy to production
cp -r data-catalog ../production/
cd ../production
rudder-cli apply -l ./
```

## Handling Import Drift

**Problem:** Someone made changes in the UI after import.

**Solution 1: Re-import (overwrites local)**

```bash
# Warning: This overwrites your local changes!
rudder-cli import workspace --force
```

**Solution 2: Manual reconciliation**

```bash
# 1. Compare local vs workspace
rudder-cli apply --dry-run -l ./

# 2. Review differences
# "Updated" means local differs from workspace
# Decide: use local (apply) or use workspace (re-import that file)

# 3. Apply your version
rudder-cli apply -l ./
```

**Best practice:** After import, all changes go through CLI. Disable UI editing for data catalog if possible.

## Import Gotchas

### Pull is Not Supported

Import is a **one-time snapshot**. There's no `rudder-cli pull` to sync changes from workspace.

```bash
# This doesn't exist:
rudder-cli pull  # ❌ Not a command

# Instead, re-import to get latest:
rudder-cli import workspace  # Overwrites local
```

### Import Metadata Must Match

If you copy files between workspaces, update the `metadata.import` section:

```yaml
# Wrong: IDs from different workspace
metadata:
  import:
    id: "evt_from_other_workspace"
    workspace: "ws_different"

# Right: Remove import metadata for new workspace
metadata:
  name: "events"
  # No import section - will create new resource
```

### Partial Import Creates Orphans

If you import, delete some files, then apply:

```bash
# This will DELETE resources from workspace!
rudder-cli apply -l ./  # Shows "Deleted [event] ..."
```

The CLI tracks what was imported. Missing files = deletions.

## CLI Commands Reference

```bash
# Authenticate
rudder-cli auth login

# Show current workspace
rudder-cli workspace info

# Import all resources
rudder-cli import workspace

# Import specific resource types
rudder-cli import workspace --resources events,properties

# Validate imported files
rudder-cli validate -l ./

# Preview changes
rudder-cli apply --dry-run -l ./

# Apply changes
rudder-cli apply -l ./
```

## Handling External Content

When importing resources from RudderStack workspace:

- **Review imported YAML** - verify structure matches expected schema before committing
- **Validate import IDs** - ensure `metadata.import.id` values are legitimate workspace resources
- **Don't blindly trust imported descriptions** - user-generated content may contain unexpected data
- **Sanitize before committing** - review imported files for any sensitive data before git commit
- **Extract only expected fields** - imported YAML should contain only known schema fields

## Checklist: Safe Evolution

Before applying changes:

- [ ] Ran `rudder-cli validate -l ./` - no errors
- [ ] Ran `rudder-cli apply --dry-run -l ./` - reviewed all changes
- [ ] No unexpected "Deleted" resources in dry-run
- [ ] Breaking changes have migration plan (parallel events, deprecation period)
- [ ] SDK teams notified of upcoming changes
- [ ] RudderTyper regenerated if using type-safe code
- [ ] Changes committed to git before applying
