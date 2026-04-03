---
name: rudder-typer-workflow
description: Use when generating type-safe event tracking code (Swift/Kotlin) from tracking plans using RudderTyper
---

# RudderTyper Workflow

This skill teaches how to use **RudderTyper** to generate type-safe SDKs from your tracking plan, enabling compile-time validation of analytics calls.

## What is RudderTyper?

RudderTyper generates native code from your tracking plan so developers:
- Get **compile-time validation** of event names and properties
- Have **autocomplete** for events and properties in their IDE
- Catch **instrumentation errors before runtime**
- See **documentation** from your tracking plan inline

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Tracking Plan  │────▶│   RudderTyper   │────▶│  Generated SDK  │
│     (YAML)      │     │   (Generator)   │     │ (Swift/Kotlin)  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                        │
                                                        ▼
                                               ┌─────────────────┐
                                               │   Mobile App    │
                                               │  (Type-safe!)   │
                                               └─────────────────┘
```

## Supported Platforms

| Platform | Language | Use Case |
|----------|----------|----------|
| iOS | Swift | iOS, macOS, tvOS, watchOS apps |
| Android | Kotlin | Android apps, JVM applications |

## Quick Start

### Step 1: Initialize RudderTyper

```bash
rudder-cli typer init
```

Creates `ruddertyper.yml`:

```yaml
version: "1.0.0"
trackingPlan:
  id: "tp_abc123"              # Your tracking plan ID
  workspace: "ws_xyz789"       # Your workspace ID
language: kotlin               # or "swift"
output:
  path: ./generated            # Where to generate code
```

### Step 2: Generate Code

```bash
rudder-cli typer generate
```

### Step 3: Integrate

Add the generated directory to your project and import the Analytics class.

## Real-World Example: E-Commerce App

### Your Tracking Plan

```yaml
# tracking-plan.yaml
version: "rudder/v1"
kind: "tracking-plan"
metadata:
  name: "tracking-plans"
spec:
  name: "Mobile App Tracking Plan"
  events:
    - event: "urn:rudder:event/product-viewed"
    - event: "urn:rudder:event/product-added-to-cart"
    - event: "urn:rudder:event/order-completed"
```

### Generated Kotlin Code

RudderTyper generates:

```kotlin
// generated/Analytics.kt

/**
 * User viewed a product detail page
 */
fun productViewed(
    product: ProductType,
    pageUrl: String? = null,
    referrerUrl: String? = null
) {
    track("Product Viewed", mapOf(
        "product" to product.toMap(),
        "page_url" to pageUrl,
        "referrer_url" to referrerUrl
    ))
}

/**
 * User added a product to their cart
 */
fun productAddedToCart(
    product: ProductType,
    quantity: Int,
    cartTotal: Double? = null,
    productCount: Int? = null
) {
    track("Product Added to Cart", mapOf(
        "product" to product.toMap(),
        "quantity" to quantity,
        "cart_total" to cartTotal,
        "product_count" to productCount
    ))
}

/**
 * Customer completed a purchase
 */
fun orderCompleted(
    orderId: String,
    orderTotal: Double,
    customerEmail: String,
    products: List<ProductType>,
    shippingAddress: AddressType,
    billingAddress: AddressType
) {
    track("Order Completed", mapOf(
        "order_id" to orderId,
        "order_total" to orderTotal,
        "customer_email" to customerEmail,
        "products" to products.map { it.toMap() },
        "shipping_address" to shippingAddress.toMap(),
        "billing_address" to billingAddress.toMap()
    ))
}

// Custom type classes
data class ProductType(
    val productId: String,
    val productSku: String,
    val productName: String,
    val productCategory: ProductCategory,
    val productPrice: Double,
    val productMsrp: Double? = null
)

enum class ProductCategory {
    FOOTWEAR,
    CLOTHING,
    ACCESSORIES
}

data class AddressType(
    val address: String,
    val city: String,
    val state: String,
    val zipcode: String
)
```

### Using Generated Code

**Before RudderTyper** (error-prone):

```kotlin
// Typos won't be caught until runtime
analytics.track("Product Viewd", mapOf(   // Typo in event name!
    "product_id" to "shoes-001",
    "proudct_name" to "Running Shoes",    // Typo in property!
    "price" to "89.99"                    // Wrong type (string vs number)!
))
```

**After RudderTyper** (type-safe):

```kotlin
// IDE autocomplete, compile-time validation
analytics.productViewed(
    product = ProductType(
        productId = "shoes-001",
        productSku = "RUN-001",
        productName = "Running Shoes",
        productCategory = ProductCategory.FOOTWEAR,
        productPrice = 89.99
    )
)
```

Compile errors catch:
- ✓ Wrong event name (method doesn't exist)
- ✓ Wrong property name (parameter doesn't exist)
- ✓ Wrong type (compiler type mismatch)
- ✓ Missing required property (non-optional parameter)

### Swift Example

```swift
// generated/Analytics.swift

/// User viewed a product detail page
func productViewed(
    product: ProductType,
    pageUrl: String? = nil,
    referrerUrl: String? = nil
) {
    track("Product Viewed", properties: [
        "product": product.toDictionary(),
        "page_url": pageUrl,
        "referrer_url": referrerUrl
    ])
}

struct ProductType {
    let productId: String
    let productSku: String
    let productName: String
    let productCategory: ProductCategory
    let productPrice: Double
    let productMsrp: Double?
}

enum ProductCategory: String {
    case footwear = "Footwear"
    case clothing = "Clothing"
    case accessories = "Accessories"
}
```

## Configuration Options

### ruddertyper.yml

```yaml
version: "1.0.0"

trackingPlan:
  id: "tp_abc123"
  workspace: "ws_xyz789"

language: kotlin                    # "kotlin" or "swift"

output:
  path: ./app/src/main/java/analytics   # Output directory

# Optional: customize naming
naming:
  eventPrefix: ""                   # Prefix for event methods
  eventSuffix: ""                   # Suffix for event methods

# Optional: include/exclude events
events:
  include:
    - "Product Viewed"
    - "Product Added to Cart"
  # OR
  exclude:
    - "Internal Debug Event"
```

## Iteration Workflow

When your tracking plan changes:

```
┌──────────────────┐
│ 1. Update YAML   │ ← Add/modify events, properties, custom types
└────────┬─────────┘
         ▼
┌──────────────────┐
│ 2. Validate      │ ← rudder-cli validate -l ./
└────────┬─────────┘
         ▼
┌──────────────────┐
│ 3. Apply         │ ← rudder-cli apply -l ./
└────────┬─────────┘
         ▼
┌──────────────────┐
│ 4. Regenerate    │ ← rudder-cli typer generate
└────────┬─────────┘
         ▼
┌──────────────────┐
│ 5. Fix Compile   │ ← Update app code to match new schema
│    Errors        │
└────────┬─────────┘
         ▼
┌──────────────────┐
│ 6. Commit Both   │ ← Spec changes + generated code together
└──────────────────┘
```

### Commands

```bash
# 1. Validate tracking plan
rudder-cli validate -l ./

# 2. Apply changes to workspace
rudder-cli apply -l ./

# 3. Regenerate code
rudder-cli typer generate

# 4. Build app to check for errors
./gradlew build          # Android
xcodebuild               # iOS
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Validate Analytics

on:
  pull_request:
    paths:
      - 'tracking-plan/**'
      - 'ruddertyper.yml'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install rudder-cli
        run: |
          curl -sSL https://cli.rudderstack.com/install.sh | bash

      - name: Validate tracking plan
        run: rudder-cli validate -l ./tracking-plan

      - name: Generate code
        run: rudder-cli typer generate

      - name: Check for changes
        run: |
          if [[ -n $(git status --porcelain generated/) ]]; then
            echo "Generated code is out of date!"
            echo "Run 'rudder-cli typer generate' and commit the changes."
            exit 1
          fi
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Regenerate and check for uncommitted changes
rudder-cli typer generate

if [[ -n $(git diff --name-only generated/) ]]; then
    echo "Error: Generated analytics code is out of sync."
    echo "Please run 'rudder-cli typer generate' and stage the changes."
    exit 1
fi
```

## Multi-Platform Projects

For apps with both iOS and Android:

```yaml
# ruddertyper-android.yml
version: "1.0.0"
trackingPlan:
  id: "tp_abc123"
  workspace: "ws_xyz789"
language: kotlin
output:
  path: ./android/app/src/main/java/analytics
```

```yaml
# ruddertyper-ios.yml
version: "1.0.0"
trackingPlan:
  id: "tp_abc123"
  workspace: "ws_xyz789"
language: swift
output:
  path: ./ios/Analytics
```

Generate both:

```bash
rudder-cli typer generate --config ruddertyper-android.yml
rudder-cli typer generate --config ruddertyper-ios.yml
```

## Common Patterns

### Pattern: Shared Analytics Module

```
project/
├── analytics/                    # Shared tracking plan
│   ├── tracking-plan.yaml
│   └── ruddertyper.yml
├── android/
│   └── app/src/main/java/
│       └── generated/            # Kotlin output
└── ios/
    └── Generated/                # Swift output
```

### Pattern: Monorepo with Multiple Apps

```
monorepo/
├── packages/
│   └── analytics-schema/         # Single source of truth
│       ├── tracking-plan.yaml
│       └── ruddertyper.yml
├── apps/
│   ├── mobile-android/
│   │   └── generated/
│   ├── mobile-ios/
│   │   └── Generated/
│   └── web/                      # TypeScript types (manual for now)
```

### Pattern: Feature Flags for New Events

When adding events that aren't ready for all clients:

```yaml
# events.yaml - add new event
spec:
  name: "Checkout Started"
  description: "User started checkout process (beta)"

# tracking-plan.yaml - only add to beta plan
spec:
  name: "Mobile App - Beta"
  events:
    - event: "urn:rudder:event/checkout-started"
```

## Troubleshooting

### Generated Code Not Updating

```bash
# Ensure tracking plan is applied first
rudder-cli apply -l ./

# Then regenerate
rudder-cli typer generate
```

### Type Mismatch Errors

Check property types in YAML match expected usage:

```yaml
# Wrong: price as string
spec:
  name: "product_price"
  type: "string"

# Right: price as number
spec:
  name: "product_price"
  type: "number"
```

### Missing Required Properties

Generated methods require all `required: true` properties as non-optional parameters:

```kotlin
// This won't compile if productId is required
analytics.productViewed(
    product = ProductType(
        // productId missing - compile error!
        productName = "Test"
    )
)
```

### Custom Types Not Generating

Ensure custom types are:
1. Defined in YAML with correct schema
2. Referenced in event rules
3. Applied to workspace before generating

```bash
rudder-cli validate -l ./
rudder-cli apply -l ./
rudder-cli typer generate
```

## Command Reference

```bash
# Initialize RudderTyper configuration
rudder-cli typer init

# Generate code from tracking plan
rudder-cli typer generate

# Generate with specific config file
rudder-cli typer generate --config path/to/ruddertyper.yml

# Generate with verbose output
rudder-cli typer generate --verbose
```
