---
name: rudder-conditional-validation
description: Use when validation rules need to vary based on event property values (e.g., payment_method = "card" requires card_number)
---

# Conditional Validation

This skill teaches how to create **dynamic validation rules** that change based on event context - when different property values require different validation.

## When to Use Conditional Validation

Use conditional validation when:
- Same event has **different property requirements** based on context
- Optional fields become **required** based on other field values
- Validation logic **depends on runtime values**

**Examples:**
- Payment method is "card" → require card_number, card_expiry
- Payment method is "bank" → require bank_name, routing_number
- Country is "US" → require ZIP code with US format
- Country is "CA" → require postal code with Canadian format

## Concept: Variants

A **variant** is a conditional branch of validation rules:

```
Event: Payment Completed
├── Variant: Card Payment (when payment_method = "card")
│   └── Required: card_last_four, card_brand
├── Variant: Bank Transfer (when payment_method = "bank")
│   └── Required: bank_name, account_last_four
└── Variant: Digital Wallet (when payment_method = "wallet")
    └── Required: wallet_type
```

## Event Rule Variants

### Basic Syntax

```yaml
version: "rudder/v1"
kind: "event"
metadata:
  name: "events"
spec:
  name: "Payment Completed"
  description: "Customer completed a payment"
  rules:
    # Always required
    - property: "urn:rudder:property/order_id"
      required: true
    - property: "urn:rudder:property/payment_method"
      required: true
    - property: "urn:rudder:property/amount"
      required: true
  variants:
    - name: "Card Payment"
      condition:
        property: "urn:rudder:property/payment_method"
        operator: "equals"
        value: "card"
      rules:
        - property: "urn:rudder:property/card_last_four"
          required: true
        - property: "urn:rudder:property/card_brand"
          required: true
        - property: "urn:rudder:property/card_expiry_month"
        - property: "urn:rudder:property/card_expiry_year"
    - name: "Bank Transfer"
      condition:
        property: "urn:rudder:property/payment_method"
        operator: "equals"
        value: "bank"
      rules:
        - property: "urn:rudder:property/bank_name"
          required: true
        - property: "urn:rudder:property/account_last_four"
          required: true
    - name: "Digital Wallet"
      condition:
        property: "urn:rudder:property/payment_method"
        operator: "equals"
        value: "wallet"
      rules:
        - property: "urn:rudder:property/wallet_type"
          required: true
```

### Condition Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `equals` | Exact match | `value: "card"` |
| `not_equals` | Not equal to | `value: "test"` |
| `contains` | String contains | `value: "promo"` |
| `not_contains` | String doesn't contain | `value: "internal"` |
| `starts_with` | String starts with | `value: "US-"` |
| `ends_with` | String ends with | `value: "-beta"` |
| `in` | Value in list | `value: ["card", "wallet"]` |
| `not_in` | Value not in list | `value: ["test", "demo"]` |

## Real-World Example: E-Commerce Checkout

### Scenario

An e-commerce checkout has different requirements based on:
- **Shipping method**: Standard vs. Express vs. Store Pickup
- **Payment method**: Card vs. PayPal vs. Apple Pay

### Properties

```yaml
# properties/checkout-properties.yaml
version: "rudder/v1"
kind: "property"
metadata:
  name: "properties"
spec:
  name: "shipping_method"
  type: "string"
  config:
    enum:
      - "standard"
      - "express"
      - "store_pickup"
---
version: "rudder/v1"
kind: "property"
metadata:
  name: "properties"
spec:
  name: "payment_method"
  type: "string"
  config:
    enum:
      - "card"
      - "paypal"
      - "apple_pay"
---
version: "rudder/v1"
kind: "property"
metadata:
  name: "properties"
spec:
  name: "pickup_store_id"
  type: "string"
  description: "Store ID for pickup orders"
---
version: "rudder/v1"
kind: "property"
metadata:
  name: "properties"
spec:
  name: "express_delivery_date"
  type: "string"
  description: "Requested delivery date for express shipping"
  config:
    format: "date"
```

### Event with Variants

```yaml
# events/order-completed.yaml
version: "rudder/v1"
kind: "event"
metadata:
  name: "events"
spec:
  name: "Order Completed"
  description: "Customer completed a purchase"
  rules:
    # Always required for all orders
    - property: "urn:rudder:property/order_id"
      required: true
    - property: "urn:rudder:property/order_total"
      required: true
    - property: "urn:rudder:property/shipping_method"
      required: true
    - property: "urn:rudder:property/payment_method"
      required: true
    - property: "urn:rudder:property/customer_email"
      required: true
  variants:
    # Shipping variants
    - name: "Standard Shipping"
      condition:
        property: "urn:rudder:property/shipping_method"
        operator: "equals"
        value: "standard"
      rules:
        - property: "urn:rudder:property/shipping_address"
          required: true
          customType: "urn:rudder:custom-type/address-type"
    - name: "Express Shipping"
      condition:
        property: "urn:rudder:property/shipping_method"
        operator: "equals"
        value: "express"
      rules:
        - property: "urn:rudder:property/shipping_address"
          required: true
          customType: "urn:rudder:custom-type/address-type"
        - property: "urn:rudder:property/express_delivery_date"
          required: true
    - name: "Store Pickup"
      condition:
        property: "urn:rudder:property/shipping_method"
        operator: "equals"
        value: "store_pickup"
      rules:
        - property: "urn:rudder:property/pickup_store_id"
          required: true
        # No shipping address needed for pickup

    # Payment variants
    - name: "Card Payment"
      condition:
        property: "urn:rudder:property/payment_method"
        operator: "equals"
        value: "card"
      rules:
        - property: "urn:rudder:property/card_last_four"
          required: true
        - property: "urn:rudder:property/card_brand"
          required: true
        - property: "urn:rudder:property/billing_address"
          required: true
          customType: "urn:rudder:custom-type/address-type"
    - name: "PayPal Payment"
      condition:
        property: "urn:rudder:property/payment_method"
        operator: "equals"
        value: "paypal"
      rules:
        - property: "urn:rudder:property/paypal_email"
          required: true
    - name: "Apple Pay"
      condition:
        property: "urn:rudder:property/payment_method"
        operator: "equals"
        value: "apple_pay"
      rules:
        - property: "urn:rudder:property/apple_pay_device_id"
```

### How Validation Works

When an event is received:

```json
{
  "event": "Order Completed",
  "properties": {
    "order_id": "ORD-12345",
    "order_total": 89.99,
    "customer_email": "user@example.com",
    "shipping_method": "express",
    "payment_method": "card",
    "shipping_address": { ... },
    "express_delivery_date": "2024-03-15",
    "card_last_four": "4242",
    "card_brand": "visa",
    "billing_address": { ... }
  }
}
```

Validation checks:
1. ✓ Base rules (order_id, order_total, etc.)
2. ✓ Express Shipping variant (shipping_address + express_delivery_date)
3. ✓ Card Payment variant (card_last_four + card_brand + billing_address)

## Custom Type Variants

Custom types can also have conditional validation based on property values.

### Example: International Address

Different address formats for different countries:

```yaml
# custom-types/international-address.yaml
version: "rudder/v1"
kind: "custom-type"
metadata:
  name: "custom-types"
spec:
  name: "InternationalAddressType"
  type: "object"
  description: "Address with country-specific validation"
  config:
    properties:
      - property: "urn:rudder:property/street"
        required: true
      - property: "urn:rudder:property/city"
        required: true
      - property: "urn:rudder:property/country"
        required: true
  variants:
    - name: "US Address"
      condition:
        property: "urn:rudder:property/country"
        operator: "equals"
        value: "US"
      config:
        properties:
          - property: "urn:rudder:property/state"
            required: true
          - property: "urn:rudder:property/zipcode"
            required: true
            # US ZIP validation: 12345 or 12345-6789
    - name: "Canadian Address"
      condition:
        property: "urn:rudder:property/country"
        operator: "equals"
        value: "CA"
      config:
        properties:
          - property: "urn:rudder:property/province"
            required: true
          - property: "urn:rudder:property/postal_code"
            required: true
            # Canadian postal code: A1A 1A1
    - name: "UK Address"
      condition:
        property: "urn:rudder:property/country"
        operator: "equals"
        value: "UK"
      config:
        properties:
          - property: "urn:rudder:property/postcode"
            required: true
            # UK postcode format
```

## Advanced: Nested Conditions

For complex scenarios, use multiple variants that can apply simultaneously:

```yaml
spec:
  name: "Subscription Changed"
  rules:
    - property: "urn:rudder:property/subscription_id"
      required: true
    - property: "urn:rudder:property/change_type"
      required: true
    - property: "urn:rudder:property/plan_type"
      required: true
  variants:
    # Change type variants
    - name: "Upgrade"
      condition:
        property: "urn:rudder:property/change_type"
        operator: "equals"
        value: "upgrade"
      rules:
        - property: "urn:rudder:property/previous_plan"
          required: true
        - property: "urn:rudder:property/new_plan"
          required: true
    - name: "Downgrade"
      condition:
        property: "urn:rudder:property/change_type"
        operator: "equals"
        value: "downgrade"
      rules:
        - property: "urn:rudder:property/previous_plan"
          required: true
        - property: "urn:rudder:property/new_plan"
          required: true
        - property: "urn:rudder:property/downgrade_reason"
          required: true  # Only required for downgrades

    # Plan type variants (can combine with above)
    - name: "Enterprise Plan"
      condition:
        property: "urn:rudder:property/plan_type"
        operator: "equals"
        value: "enterprise"
      rules:
        - property: "urn:rudder:property/contract_id"
          required: true
        - property: "urn:rudder:property/account_manager"
          required: true
```

An enterprise downgrade would need to satisfy:
- Base rules
- Downgrade variant rules
- Enterprise Plan variant rules

## Best Practices

### 1. Keep Conditions Simple

**Good:**
```yaml
condition:
  property: "urn:rudder:property/payment_method"
  operator: "equals"
  value: "card"
```

**Avoid:** Complex nested conditions that are hard to understand.

### 2. Make Variants Mutually Exclusive When Possible

**Good:**
```yaml
variants:
  - name: "Card"
    condition: { ... value: "card" }
  - name: "Bank"
    condition: { ... value: "bank" }
  - name: "Wallet"
    condition: { ... value: "wallet" }
```

**Risky:** Overlapping conditions that might both apply.

### 3. Document Variant Purpose

```yaml
variants:
  - name: "Express Shipping"
    description: "Requires delivery date for express orders"
    condition: ...
```

### 4. Test All Variant Paths

Create test events for each variant combination:

```bash
# Test standard + card
# Test standard + paypal
# Test express + card
# Test express + paypal
# Test pickup + card
# etc.
```

### 5. Start with Base Rules

Put properties required in ALL cases in the base rules, not variants:

```yaml
rules:
  # These are ALWAYS required
  - property: "urn:rudder:property/order_id"
    required: true
variants:
  # These are conditionally required
  - name: "Express"
    rules:
      - property: "urn:rudder:property/delivery_date"
        required: true
```

## Validation Commands

```bash
# Validate conditional rules
rudder-cli validate -l ./

# Preview changes
rudder-cli apply --dry-run -l ./

# Apply
rudder-cli apply -l ./
```

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Condition on undefined property | Validation fails | Create property first |
| Overlapping conditions | Unpredictable which applies | Make mutually exclusive |
| Too many variants | Hard to maintain | Simplify or use custom types |
| Missing default case | Events without matching variant pass | Add catch-all or ensure coverage |

## When NOT to Use Conditional Validation

Consider alternatives when:
- **Different events** are more appropriate than variants
- **Property is always needed** but validation differs → use custom type variants
- **Logic is too complex** → simplify the event structure

**Example: Instead of variants, use separate events:**

```yaml
# Instead of Order Completed with shipping_method variants:
- Order Completed - Shipped
- Order Completed - Store Pickup
```

This is clearer when the events represent fundamentally different user actions.
