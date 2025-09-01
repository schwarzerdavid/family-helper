# Event Schemas

JSON Schema definitions for domain events in the Family Helper platform.

## Role

Centralizes event contract definitions to ensure consistent event structure across all services that publish or consume events.

## Schema Structure

All events follow a common envelope format with versioned payloads:

```json
{
  "$id": "https://familyhelper.dev/schemas/EventEnvelope.json",
  "type": "object",
  "required": ["id", "type", "occurredAt", "payload", "idempotencyKey"],
  "properties": {
    "id": { "type": "string", "format": "uuid" },
    "type": { "type": "string" },
    "occurredAt": { "type": "string", "format": "date-time" },
    "idempotencyKey": { "type": "string" },
    "payload": { "type": "object" },
    "trace": { 
      "type": "object", 
      "properties": { 
        "traceparent": { "type": "string" } 
      } 
    }
  }
}
```

## Core Event Types

### UserCreated:v1
Published by Identity service when a new user registers.

### HouseholdCreated:v1  
Published by Households service when a household is created.

### TaskScheduled:v1
Published by Tasks service when a recurring task is scheduled.

### FileUploaded:v1
Published by Files service when a file upload completes.

### NotificationDispatched:v1
Published by Notifications service when a message is sent.

## Usage

1. Services validate incoming events against these schemas
2. Event producers include schema version in event type (e.g., "UserCreated:v1")
3. Breaking changes require new schema versions
4. Consumers can handle multiple schema versions for backward compatibility

## Validation

```typescript
import { validateEvent } from "@platform-ts/events";

const event = {
  type: "UserCreated:v1",
  payload: { userId: "123", email: "user@example.com" }
};

if (validateEvent(event)) {
  // Process valid event
} else {
  // Handle validation error
}
```

## Versioning Strategy

- Additive changes: same version (add optional fields)
- Breaking changes: new version (remove fields, change types, make required)
- Consumers should gracefully handle unknown event versions