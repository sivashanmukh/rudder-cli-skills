---
name: rudder-tracking-plans
description: Creates and manages tracking plans that validate events against schema contracts. Use when creating or managing tracking plans that define which events are allowed for a source
allowed-tools: "Bash(rudder-cli *), Read, Write, Edit"
---

# RudderStack Tracking Plans Management

This skill teaches how to assemble events into **tracking plans** - contracts that define which events a source can send and what properties each event must have.

## What is a Tracking Plan?

A tracking plan is a schema that:
- Defines **which events** are allowed from a source
- Specifies **required vs optional properties** for each event
- Enables **validation** at event ingestion time
- Provides **governance** over what data enters your warehouse

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│     Source      │────▶│  Tracking Plan  │────▶│   Destination   │
│  (Web App SDK)  │     │   (Validator)   │     │   (Warehouse)   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                        Validates events
                        against schema
```

## YAML Schema

### Basic Tracking Plan

```yaml
version: "rudder/v1"
kind: "tracking-plan"
metadata:
  name: "tracking-plans"
spec:
  name: "Web App Tracking Plan"
  description: "Events for the main e-commerce web application"
  events:
    - event: "urn:rudder:event/product-viewed"
    - event: "urn:rudder:event/product-added-to-cart"
    - event: "urn:rudder:event/order-completed"
```

### Tracking Plan with Rule Overrides

Override event-level rules at the tracking plan level:

```yaml
version: "rudder/v1"
kind: "tracking-plan"
metadata:
  name: "tracking-plans"
spec:
  name: "Mobile App Tracking Plan"
  description: "Events for iOS and Android apps"
  events:
    - event: "urn:rudder:event/product-viewed"
      rules:
        # Make session_id required for mobile (optional in event definition)
        - property: "urn:rudder:property/session_id"
          required: true
        # Make device_id required for mobile attribution
        - property: "urn:rudder:property/device_id"
          required: true
    - event: "urn:rudder:event/product-added-to-cart"
    - event: "urn:rudder:event/order-completed"
```

## Rule Precedence

When the same property appears at multiple levels:

```
1. Tracking Plan event rules  (highest priority)
2. Event-level rules          (default)
3. Property definitions       (validation config only)
```

**Example:** If `session_id` is optional in the event definition but required in the tracking plan, it's **required** for that tracking plan.

## Real-World Example: E-Commerce Platform

### Scenario
An e-commerce company has:
- **Web App** - Full shopping experience
- **Mobile App** - Simplified checkout flow
- **Kiosk** - In-store product lookup only

Each needs different tracking rules from the same event catalog.

### Shared Events (Data Catalog)

```yaml
# events/ecommerce.yaml
version: "rudder/v1"
kind: "event"
metadata:
  name: "events"
spec:
  name: "Product Viewed"
  description: "User viewed a product detail page"
  category: "urn:rudder:category/ecommerce"
  rules:
    - property: "urn:rudder:property/product"
      required: true
      customType: "urn:rudder:custom-type/product-type"
    - property: "urn:rudder:property/page_url"
    - property: "urn:rudder:property/referrer_url"
    - property: "urn:rudder:property/session_id"
    - property: "urn:rudder:property/device_id"
---
version: "rudder/v1"
kind: "event"
metadata:
  name: "events"
spec:
  name: "Product Added to Cart"
  description: "User added a product to their cart"
  category: "urn:rudder:category/ecommerce"
  rules:
    - property: "urn:rudder:property/product"
      required: true
      customType: "urn:rudder:custom-type/product-type"
    - property: "urn:rudder:property/quantity"
      required: true
    - property: "urn:rudder:property/cart_total"
    - property: "urn:rudder:property/session_id"
---
version: "rudder/v1"
kind: "event"
metadata:
  name: "events"
spec:
  name: "Order Completed"
  description: "Customer completed a purchase"
  category: "urn:rudder:category/ecommerce"
  rules:
    - property: "urn:rudder:property/order_id"
      required: true
    - property: "urn:rudder:property/order_total"
      required: true
    - property: "urn:rudder:property/customer_email"
      required: true
    - property: "urn:rudder:property/products"
      required: true
    - property: "urn:rudder:property/shipping_address"
      customType: "urn:rudder:custom-type/address-type"
    - property: "urn:rudder:property/billing_address"
      customType: "urn:rudder:custom-type/address-type"
```

### Web App Tracking Plan

Full e-commerce funnel with attribution tracking:

```yaml
# tracking-plans/web-app.yaml
version: "rudder/v1"
kind: "tracking-plan"
metadata:
  name: "tracking-plans"
spec:
  name: "Web App Tracking Plan"
  description: "Full e-commerce experience for web browsers"
  events:
    - event: "urn:rudder:event/product-viewed"
      rules:
        # Require page context for web attribution
        - property: "urn:rudder:property/page_url"
          required: true
        - property: "urn:rudder:property/referrer_url"
          required: true
    - event: "urn:rudder:event/product-added-to-cart"
    - event: "urn:rudder:event/order-completed"
      rules:
        # Require both addresses for web orders
        - property: "urn:rudder:property/shipping_address"
          required: true
        - property: "urn:rudder:property/billing_address"
          required: true
```

### Mobile App Tracking Plan

Mobile-specific requirements:

```yaml
# tracking-plans/mobile-app.yaml
version: "rudder/v1"
kind: "tracking-plan"
metadata:
  name: "tracking-plans"
spec:
  name: "Mobile App Tracking Plan"
  description: "iOS and Android shopping apps"
  events:
    - event: "urn:rudder:event/product-viewed"
      rules:
        # Require device_id for mobile attribution (not page_url)
        - property: "urn:rudder:property/device_id"
          required: true
    - event: "urn:rudder:event/product-added-to-cart"
      rules:
        - property: "urn:rudder:property/device_id"
          required: true
    - event: "urn:rudder:event/order-completed"
      rules:
        # Mobile uses saved addresses, only shipping required
        - property: "urn:rudder:property/shipping_address"
          required: true
        - property: "urn:rudder:property/device_id"
          required: true
```

### Kiosk Tracking Plan

Limited event set for in-store kiosks:

```yaml
# tracking-plans/kiosk.yaml
version: "rudder/v1"
kind: "tracking-plan"
metadata:
  name: "tracking-plans"
spec:
  name: "Kiosk Tracking Plan"
  description: "In-store product lookup kiosks"
  events:
    # Only Product Viewed - no cart or checkout
    - event: "urn:rudder:event/product-viewed"
      rules:
        - property: "urn:rudder:property/kiosk_id"
          required: true
        - property: "urn:rudder:property/store_id"
          required: true
```

## Governance Settings

When events violate the tracking plan:

```yaml
spec:
  name: "Strict Tracking Plan"
  governance:
    # Options: block, forward, log
    unplannedEvents: block      # Reject events not in plan
    violatingEvents: forward    # Forward violations with flag
```

| Setting | Behavior |
|---------|----------|
| `block` | Reject event entirely |
| `forward` | Forward event with violation metadata |
| `log` | Allow event, log violation for review |

## Directory Structure

```
tracking-plans/
├── web-app.yaml
├── mobile-app.yaml
├── kiosk.yaml
└── internal-tools.yaml
```

Each tracking plan in its own file for clear git history and code review.

## Workflow: Creating a New Tracking Plan

### Step 1: Identify the Source

What application/SDK will use this tracking plan?
- Web app (JavaScript SDK)
- Mobile app (iOS/Android SDK)
- Server-side (Node.js SDK)

### Step 2: List Required Events

Which events from your data catalog does this source need?

```
Web App needs:
✓ Product Viewed
✓ Product Added to Cart
✓ Order Completed
✗ App Opened (mobile only)
```

### Step 3: Determine Rule Overrides

For each event, what properties should be:
- **Required** for this source specifically?
- **Optional** even if required elsewhere?

### Step 4: Create the YAML

```yaml
version: "rudder/v1"
kind: "tracking-plan"
metadata:
  name: "tracking-plans"
spec:
  name: "Your Tracking Plan Name"
  description: "Clear description of what source uses this"
  events:
    - event: "urn:rudder:event/event-name"
      rules:
        - property: "urn:rudder:property/property-name"
          required: true
```

### Step 5: Validate and Apply

```bash
# Validate
rudder-cli validate -l ./

# Preview
rudder-cli apply --dry-run -l ./

# Apply
rudder-cli apply -l ./
```

### Step 6: Connect to Source

After applying, connect the tracking plan to your source:
- Via RudderStack UI: Sources → Select Source → Tracking Plan
- Via API: Update source configuration

## Common Patterns

### Pattern: Environment-Specific Plans

```yaml
# tracking-plans/web-app-production.yaml
spec:
  name: "Web App - Production"
  governance:
    unplannedEvents: block      # Strict in production
    violatingEvents: block

# tracking-plans/web-app-development.yaml
spec:
  name: "Web App - Development"
  governance:
    unplannedEvents: log        # Lenient in development
    violatingEvents: forward
```

### Pattern: Shared Base + Overrides

Create a comprehensive event catalog, then each tracking plan includes only what it needs:

```
Data Catalog: 50 events defined
├── Web App Plan: 30 events
├── Mobile Plan: 25 events
└── Kiosk Plan: 5 events
```

### Pattern: Gradual Rollout

Start permissive, tighten over time:

```yaml
# Phase 1: Log only
governance:
  unplannedEvents: log
  violatingEvents: log

# Phase 2: Forward violations
governance:
  unplannedEvents: forward
  violatingEvents: forward

# Phase 3: Block violations
governance:
  unplannedEvents: block
  violatingEvents: block
```

## Validation Commands

```bash
# Validate tracking plan references exist
rudder-cli validate -l ./

# Preview what will change
rudder-cli apply --dry-run -l ./

# Apply to workspace
rudder-cli apply -l ./
```

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Event URN not found | Referenced event doesn't exist | Create event in data catalog first |
| Property not in event | Adding property not defined on event | Add property to event rules first |
| Duplicate tracking plan name | Conflict in workspace | Use unique, descriptive names |
| Too strict too fast | Breaking production SDKs | Use `log` mode first, analyze, then tighten |

## Linking to Sources

After creating and applying a tracking plan:

1. **Get tracking plan ID** from workspace
2. **Update source** to use the tracking plan
3. **Test** by sending events and checking validation

Events from the source will now be validated against your tracking plan schema.
