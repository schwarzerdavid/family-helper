# ADR-001: Use Poetry for Python Package Management

## Status
Accepted

## Context
The Python Platform Wrapper needs a robust package management solution for dependencies, virtual environments, and build processes. Several options were considered:

1. **pip + requirements.txt**: Traditional approach with manual virtual environment management
2. **pipenv**: Higher-level package management with Pipfile
3. **Poetry**: Modern dependency management with pyproject.toml
4. **conda**: Package management focused on scientific computing

The Phase 0 specification explicitly called for Poetry usage, and we needed to evaluate whether this was the right technical choice.

## Decision
We will use **Poetry** for Python package management and project structure.

## Rationale

### Advantages of Poetry:
1. **Specification Compliance**: Follows Phase 0 requirements exactly
2. **Dependency Resolution**: Superior dependency resolution compared to pip
3. **Lock Files**: Provides poetry.lock for reproducible builds
4. **Virtual Environment Management**: Integrated virtual environment handling
5. **Build System**: Modern build system using pyproject.toml (PEP 518/621)
6. **Publishing**: Built-in publishing to PyPI
7. **Dev Dependencies**: Clean separation of development and production dependencies

### Technical Benefits:
- **Deterministic Builds**: Lock file ensures consistent dependency versions across environments
- **Conflict Resolution**: Automatically resolves dependency conflicts
- **Modern Standards**: Uses pyproject.toml following modern Python packaging standards
- **Integrated Workflow**: Single tool for dependency management, building, and publishing

### Implementation Details:
- Uses `pyproject.toml` for configuration
- Separates main dependencies (asyncpg, aioredis, boto3, pydantic) from dev dependencies (pytest, mypy)
- Manages virtual environment automatically
- Provides consistent CLI interface

## Consequences

### Positive:
- Simplified dependency management workflow
- Reproducible builds across development and production
- Better dependency conflict resolution
- Modern Python packaging standards compliance
- Integrated development workflow

### Negative:
- Additional tooling requirement (Poetry must be installed)
- Learning curve for team members unfamiliar with Poetry
- Potential CI/CD pipeline adjustments needed

### Mitigation:
- Poetry installation documented in project README
- Virtual environment fallback using standard Python venv
- CI/CD pipelines can use Poetry or install from lock file

## Alternatives Considered

### pip + requirements.txt
- **Pros**: Universal availability, simple
- **Cons**: No lock file, poor dependency resolution, manual virtual environment management
- **Rejected**: Doesn't meet modern package management requirements

### pipenv
- **Pros**: Lock files, virtual environment management
- **Cons**: Slower than Poetry, less reliable dependency resolution
- **Rejected**: Poetry provides better developer experience

### conda
- **Pros**: Excellent for scientific computing, manages system dependencies
- **Cons**: Overkill for web applications, different ecosystem
- **Rejected**: Not suitable for general-purpose Python web services

## Implementation
- Package structure defined in `pyproject.toml`
- Dependencies managed via `poetry add` and `poetry install`
- Virtual environment activated via `poetry shell` or `poetry run`
- Build process uses Poetry's built-in build system
- Development workflow integrated with Poetry commands

## Review Date
This decision should be reviewed if:
- Poetry introduces breaking changes
- Team productivity is significantly impacted
- Alternative tools provide substantially better features
- Phase 1 requirements conflict with Poetry usage