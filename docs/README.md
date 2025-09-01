# Documentation

Centralized documentation for the Family Helper platform.

## Structure

- **`adr/`** - Architecture Decision Records

## Purpose

This directory maintains critical project documentation including:
- Technical architecture decisions and rationale
- Operational runbooks and procedures
- API documentation and contracts
- Development guidelines and standards

## Architecture Decision Records (ADRs)

ADRs document significant architectural choices made during development:

- **ADR-001**: Event Bus Technology (SNS+SQS vs Kafka)
- **ADR-002**: Repository Structure (Poly-repo vs Mono-repo)  
- **ADR-003**: Container Orchestration (ECS/Fargate vs EKS)
- **ADR-004**: Authentication Strategy (Cognito vs Auth0)
- **ADR-005**: Database Per Service vs Shared Database

## Documentation Standards

All documentation follows:
- **Markdown format** for easy version control and readability
- **Clear headings** with table of contents for longer documents
- **Code examples** with syntax highlighting
- **Diagrams** using Mermaid for architecture and flow diagrams
- **Regular updates** as the system evolves

## Contributing

When making significant architectural changes:
1. Create an ADR documenting the decision
2. Update relevant API documentation
3. Update runbooks if operational procedures change
4. Keep documentation in sync with implementation