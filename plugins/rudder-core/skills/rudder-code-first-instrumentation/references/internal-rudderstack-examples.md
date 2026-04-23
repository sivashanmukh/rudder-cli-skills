# Internal RudderStack Examples

> **Note:** These examples are specific to RudderStack's web application instrumentation. For general guidance, see the main SKILL.md file.

## RudderStack Web App Code Types

### Workspace Types

```typescript
// src/types/workspace.ts
export enum BillingPlan {
  FREE = 'free',
  STARTER = 'starter',
  GROWTH = 'growth',
  ENTERPRISE = 'enterprise',
}

export enum Region {
  US = 'us',
  EU = 'eu',
}

export interface Workspace {
  id: string;
  name: string;
  orgId: string;
  plan: BillingPlan;
  region: Region;
  isTrial: boolean;
}
```

### Derived Properties

```yaml
# properties/workspace-properties.yaml
version: "rudder/v1"
kind: "property"
metadata:
  name: "properties"
spec:
  name: "billing_plan"
  type: "string"
  description: "Workspace billing plan"
  config:
    enum:
      - "free"
      - "starter"
      - "growth"
      - "enterprise"
---
version: "rudder/v1"
kind: "property"
metadata:
  name: "properties"
spec:
  name: "region"
  type: "string"
  description: "Workspace region"
  config:
    enum:
      - "us"
      - "eu"
```

### Derived Events

```yaml
# events/workspace.yaml
version: "rudder/v1"
kind: "event"
metadata:
  name: "events"
spec:
  name: "Workspace Created"
  description: "User created a new workspace"
  category: "urn:rudder:category/workspace"
  rules:
    - property: "urn:rudder:property/workspace_id"
      required: true
    - property: "urn:rudder:property/workspace_name"
      required: true
    - property: "urn:rudder:property/billing_plan"
      required: true
    - property: "urn:rudder:property/region"
      required: true
---
version: "rudder/v1"
kind: "event"
metadata:
  name: "events"
spec:
  name: "Workspace Switched"
  description: "User switched to a different workspace"
  category: "urn:rudder:category/workspace"
  rules:
    - property: "urn:rudder:property/workspace_id"
      required: true
    - property: "urn:rudder:property/previous_workspace_id"
```

---

## Data Graph Audiences

### Code Types

```typescript
// src/types/audience.ts
export enum ConditionGroupType {
  AND = 'and',
  OR = 'or',
  AUDIENCE = 'audience',
}

export interface AudienceCondition {
  id: string;
  type: ConditionGroupType;
  operator: string;
  value: unknown;
}

export interface Audience {
  id: string;
  name: string;
  conditions: AudienceCondition[];
  status: 'draft' | 'active' | 'archived';
}
```

### Derived Properties

```yaml
# properties/audience-properties.yaml
version: "rudder/v1"
kind: "property"
metadata:
  name: "properties"
spec:
  name: "condition_group_type"
  type: "string"
  description: "Type of condition group"
  config:
    enum:
      - "and"
      - "or"
      - "audience"
---
version: "rudder/v1"
kind: "property"
metadata:
  name: "properties"
spec:
  name: "audience_status"
  type: "string"
  description: "Current status of audience"
  config:
    enum:
      - "draft"
      - "active"
      - "archived"
```

### Instrumentation

```typescript
function trackAudienceCreated(audience: Audience) {
  analytics.track('Audience Created', {
    audience_id: audience.id,
    audience_name: audience.name,
    condition_count: audience.conditions.length,
    condition_types: audience.conditions.map(c => c.type),  // All valid ConditionGroupType values
    audience_status: audience.status,
  });
}
```

---

## Transformations

### Code Types

```typescript
// src/types/transformation.ts
type TransformationLanguage = 'javascript' | 'python';

interface Transformation {
  id: string;
  name: string;
  language: TransformationLanguage;
  code: string;
  createdAt: string;
}
```

### Derived Events

```yaml
# events/transformations.yaml
version: "rudder/v1"
kind: "event"
metadata:
  name: "events"
spec:
  name: "Transformation Created"
  description: "User created a new transformation"
  category: "urn:rudder:category/transformations"
  rules:
    - property: "urn:rudder:property/transformation_id"
      required: true
    - property: "urn:rudder:property/transformation_language"
      required: true
    - property: "urn:rudder:property/template_type"
```

---

## Session Lifecycle in RudderStack App

### Hierarchy

```
User (shanmukh@rudderstack.com)
├── Org: RudderStack (group call when accessed)
│   ├── Workspace: Production (track context)
│   └── Workspace: Development (track context)
└── Org: Personal (group call when accessed)
    └── Workspace: Sandbox (track context)
```

### Implementation

```typescript
class AnalyticsService {
  private currentWorkspaceId: string | null = null;
  private currentOrgId: string | null = null;

  // Called on login
  identifyUser(user: User) {
    analytics.identify(user.id, {
      email: user.email,
      name: user.name,
      created_at: user.createdAt,
    });
  }

  // Called when user accesses an org
  setOrganization(org: Organization) {
    if (org.id !== this.currentOrgId) {
      this.currentOrgId = org.id;
      analytics.group(org.id, {
        name: org.name,
        plan: org.plan,           // 'free' | 'starter' | 'growth' | 'enterprise'
        is_trial: org.isTrial,
      });
    }
  }

  // Called when user switches workspace (no group call needed if same org)
  setWorkspace(workspaceId: string) {
    this.currentWorkspaceId = workspaceId;
    // No analytics call - context flows through track
  }

  // All track calls include workspace context
  track(event: string, properties: Record<string, any>) {
    analytics.track(event, {
      ...properties,
      workspace_id: this.currentWorkspaceId,
    });
  }
}
```

### Usage

```typescript
const analytics = new AnalyticsService();

// User logs in
analytics.identifyUser(user);

// User accesses RudderStack org
analytics.setOrganization(rudderStackOrg);

// User is in Production workspace
analytics.setWorkspace('ws_prod_123');

// User creates a transformation
analytics.track('Transformation Created', {
  transformation_id: 'tr_456',
  language: 'javascript',
});
// Event includes workspace_id: 'ws_prod_123'

// User switches to Development workspace (same org)
analytics.setWorkspace('ws_dev_789');
// No group call needed!

// User creates another transformation
analytics.track('Transformation Created', {
  transformation_id: 'tr_790',
  language: 'python',
});
// Event includes workspace_id: 'ws_dev_789'
```
