# TypeScript Platform Wrapper

Platform abstraction layer for TypeScript/Node.js services in the Family Helper ecosystem.

## Role

Provides consistent interfaces for infrastructure services used by TypeScript-based microservices (Identity, Integrations, Notifications, Bot Gateway).

## Key Interfaces

```typescript
// Core platform interfaces
export interface Logger { 
  info(msg: string, meta?: Record<string, unknown>): void; 
  error(msg: string, meta?: Record<string, unknown>): void; 
  with(fields: Record<string, unknown>): Logger; 
}

export interface Config { 
  get<T=string>(key: string, opts?: { required?: boolean, default?: T }): T; 
}

export interface Secrets { 
  get(name: string): Promise<string>; 
}

export interface Db { 
  query<T>(sql: string, params?: unknown[]): Promise<T[]>; 
  withTx<T>(fn: (tx: Db) => Promise<T>): Promise<T>; 
}

export interface PubSub { 
  publish(topic: string, event: unknown, opts?: { idempotencyKey?: string }): Promise<void>; 
  subscribe(topic: string, handler: (e: EventEnvelope) => Promise<void>): Unsubscribe; 
}
```

## Usage

1. Install the platform wrapper in your service:
   ```bash
   npm install @family-helper/platform-ts
   ```

2. Import and use in your handlers:
   ```typescript
   import { db, pubsub, logger, authz } from "@platform-ts";
   
   export async function createHousehold(req, res) {
     const user = authz.requireUser(req);
     const [hh] = await db.query(
       "insert into households (name, owner_user_id) values ($1,$2) returning *",
       [req.body.name, user.id]
     );
     await pubsub.publish("HouseholdCreated:v1", { 
       householdId: hh.id, 
       ownerUserId: user.id 
     });
     logger.info("household.created", { id: hh.id });
     res.status(201).json(hh);
   }
   ```

## Implementation Notes

- Uses AWS SDK v3 with credential providers
- Implements connection pooling for database connections
- Provides OpenTelemetry tracing integration
- Supports both callback and Promise-based APIs
- Includes middleware for Express/Fastify integration