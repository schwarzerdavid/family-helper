# Microservices

This directory contains all microservices that make up the Family Helper platform.

## Phase 0 Services

### gateway-edge/
API Gateway and edge service providing:
- Authentication and authorization (OIDC/JWT validation)
- Rate limiting and WAF protection
- Request routing to downstream services
- mTLS termination

### identity/
Identity and account management service providing:
- User registration and authentication
- OAuth/social login integration
- Role and permission management
- JWT token issuance

## Service Architecture

Each service follows these conventions:

1. **Language-specific structure** (Node.js/TypeScript, Python, Go, Kotlin)
2. **Health check endpoint** at `/healthz`
3. **OpenAPI specification** for HTTP APIs
4. **Event publishing/consuming** via platform wrappers
5. **Docker containerization** with multi-stage builds
6. **Infrastructure as Code** integration

## Development Workflow

1. Each service has its own package.json/requirements.txt/go.mod
2. Services are built and deployed independently
3. Shared platform wrappers provide consistent infrastructure access
4. Inter-service communication via HTTP APIs and events

## Service Communication

- **Synchronous**: HTTP APIs via API Gateway
- **Asynchronous**: Domain events via Event Bus (SNS/SQS)
- **Data**: Each service owns its data domain