# Development Conventions

## Git Strategy

Git Flow

main
│
develop
│
feature/*
│
release/*
│
hotfix/*

---

## Commit Convention

Conventional Commits

Examples

feat(api): create employee endpoint
fix(validation): datetime parser
docs(readme): update architecture
refactor(database): improve repository pattern
test(api): add employee tests
chore(docker): update compose

---

## Branch Naming

Pattern: `feature/<wbs-phase-slug>`

Examples used in this project:

feature/project-setup
feature/development-environment
feature/aws-infrastructure
feature/database-schema
feature/historical-loader
feature/rest-api
feature/validation-engine
feature/backup-restore
feature/sql-reports
feature/testing
feature/github-actions
feature/aws-deployment
feature/final-documentation
release/v1.0

Branch names must match exactly the `Branch` column in `project-status.md`.

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