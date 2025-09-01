# API Gateway / Edge Service

The entry point for all external traffic into the Family Helper platform.

## Role

Acts as the central ingress point providing:
- **Authentication & Authorization**: OIDC/JWT validation, user context extraction
- **Rate Limiting**: Per-user and global rate limits to prevent abuse
- **WAF Protection**: Web Application Firewall for common attack vectors
- **Request Routing**: Intelligent routing to downstream microservices
- **SSL Termination**: HTTPS/TLS handling
- **Load Balancing**: Traffic distribution across service instances

## Technology Stack

- **Runtime**: Envoy Proxy with Lua scripting OR NGINX with custom modules
- **Auth**: OIDC integration (Cognito/Auth0) with JWT validation
- **Monitoring**: OpenTelemetry tracing, structured logging

## Configuration

The gateway maintains routing rules for:
```yaml
routes:
  - path: "/api/v1/auth/*"
    service: "identity"
    auth_required: false
    
  - path: "/api/v1/households/*" 
    service: "households"
    auth_required: true
    
  - path: "/api/v1/files/*"
    service: "files" 
    auth_required: true
```

## Deployment

- **Container**: Runs as ECS/Fargate service
- **Load Balancer**: Behind AWS Application Load Balancer
- **TLS**: Certificate managed via ACM
- **Scaling**: Horizontal pod autoscaling based on RPS

## Health Checks

- `GET /healthz` - Service health
- `GET /readyz` - Readiness probe  
- `GET /metrics` - Prometheus metrics

## Development

```bash
# Local development with Docker
docker build -t gateway-edge .
docker run -p 8080:8080 gateway-edge

# Configuration via environment variables
UPSTREAM_IDENTITY_URL=http://identity:3000
UPSTREAM_HOUSEHOLDS_URL=http://households:3001
JWT_JWKS_URL=https://cognito.amazonaws.com/.well-known/jwks.json
```