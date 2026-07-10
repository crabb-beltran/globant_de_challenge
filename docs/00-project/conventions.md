# Development Conventions

## Git Strategy

Git Flow

```
main
│
develop
│
feature/*
│
release/*
│
hotfix/*
```

---

## Commit Convention

Conventional Commits

Examples

```
feat(api): create employee endpoint

fix(validation): datetime parser

docs(readme): update architecture

refactor(database): improve repository pattern

test(api): add employee tests

chore(docker): update compose
```

---

## Branch Naming

```
feature/database

feature/api

feature/validation

feature/reports

feature/aws

bugfix/logging

hotfix/api

release/v1.0
```

---

## Pull Request Rules

Every PR must contain

- Description
- Motivation
- Testing
- Checklist

---

## Code Style

Python

PEP8

Black

Flake8

---

## Documentation

Every feature must update

- README (if needed)
- ADR (if architecture changes)
- Changelog
- API Documentation