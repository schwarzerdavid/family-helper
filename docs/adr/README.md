# Architecture Decision Records (ADRs)

Documents recording key architectural and technical decisions made during the development of the Family Helper platform.

## Purpose

ADRs capture the context, options considered, and rationale behind important technical choices to:
- Provide historical context for future developers
- Document trade-offs and constraints that influenced decisions
- Enable informed re-evaluation as requirements change
- Maintain institutional knowledge across team changes

## ADR Format

Each ADR follows this structure:

```markdown
# ADR-XXX: [Decision Title]

**Status:** [Proposed | Accepted | Deprecated | Superseded]
**Date:** YYYY-MM-DD  
**Deciders:** [List of people involved]

## Context

What is the issue that we're seeing that is motivating this decision or change?

## Decision

What is the change that we're proposing or have agreed to implement?

## Consequences

What becomes easier or more difficult to do and any risks introduced by this change?

## Alternatives Considered

What other options were evaluated and why were they not chosen?
```

## Current ADRs

Based on the main architecture document and Phase 0 implementation, key decisions include:

### ADR-001: Event Bus Technology Selection
- **Decision**: Use AWS SNS+SQS FIFO over Apache Kafka
- **Rationale**: Lower operational overhead, built-in reliability, cost-effective for expected message volumes
- **Trade-off**: Less flexibility than Kafka, vendor lock-in concerns

### ADR-002: Repository Structure  
- **Decision**: Poly-repo approach with shared platform packages
- **Rationale**: Clear service ownership, independent deployment cycles, versioned shared libraries
- **Trade-off**: Cross-service changes require coordination, dependency management complexity

### ADR-003: Container Orchestration Platform
- **Decision**: ECS with Fargate over EKS
- **Rationale**: Simpler operations, pay-per-use pricing, faster development velocity
- **Trade-off**: Less Kubernetes ecosystem benefits, potential future migration needs

### ADR-004: Platform Wrapper Interface Enhancement
- **Decision**: Enhanced platform interfaces beyond minimum requirements
- **Rationale**: Future-proofing, developer experience, comprehensive platform service coverage
- **Trade-off**: Increased complexity, more interfaces to maintain

### ADR-005: Dependency Injection Pattern for Platform Services
- **Decision**: Constructor injection with fallback logger pattern for stub services
- **Rationale**: Clean architecture, consistent logging, testability, no circular dependencies
- **Trade-off**: Slight complexity increase, interface coupling

### ADR-006: Factory Pattern for Service Container Creation
- **Decision**: Factory function alongside direct exports for service container management
- **Rationale**: Dependency wiring, configurability, testability, backward compatibility
- **Trade-off**: More complex API surface, two patterns to maintain

### ADR-007: Comprehensive Testing Strategy for Platform Wrapper
- **Decision**: Extensive test coverage (82 tests, 88%+ coverage) with documentation-focused approach
- **Rationale**: Quality assurance, living documentation, CI/CD integration, regression prevention
- **Trade-off**: Higher development time investment, test maintenance overhead

## Creating New ADRs

When making significant architectural decisions:

1. Create a new file: `adr/ADR-XXX-title.md`
2. Use the next sequential number
3. Fill in all sections with thorough analysis
4. Get review from relevant stakeholders  
5. Update status from "Proposed" to "Accepted" after consensus

## Review Process

ADRs should be reviewed for:
- Completeness of context and alternatives
- Clear articulation of trade-offs
- Alignment with platform principles
- Technical accuracy and feasibility