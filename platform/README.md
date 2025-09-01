# Platform Wrappers

This directory contains shared platform abstraction layers that provide consistent interfaces across different programming languages for common infrastructure concerns.

## Purpose

The platform wrappers abstract cloud-specific implementations to:
- Minimize vendor lock-in
- Provide consistent APIs across services written in different languages
- Centralize cross-cutting concerns (logging, config, secrets, etc.)

## Structure

- **`ts/`** - TypeScript/Node.js platform wrapper
- **`python/`** - Python platform wrapper
- **`schemas/`** - Shared event schemas (JSON Schema format)

## Design Principles

Each platform wrapper implements the same set of interfaces:
- Logger (structured logging with metadata)
- Config (environment/parameter store configuration)
- Secrets (secure secret retrieval)
- Database (connection pooling, transactions)
- Cache (Redis abstraction)
- ObjectStorage (S3-compatible storage)
- PubSub (event publishing/subscribing)
- Search (document indexing/querying)
- FeatureFlags (feature toggle management)
- Tracer (distributed tracing)

## Usage

Services import their language-specific platform wrapper to access infrastructure services without coupling to specific cloud provider APIs.

```typescript
// TypeScript example
import { db, pubsub, logger } from "@platform-ts";
```

```python
# Python example  
from platform_py import db, storage, pubsub, log
```