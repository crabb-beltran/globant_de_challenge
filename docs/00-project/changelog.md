# Changelog

All notable changes to this project will be documented in this file.

The format is based on **Keep a Changelog** and the project follows **Semantic Versioning (SemVer)**.

---

## [Unreleased]

### Added

#### Project Foundation

- Established the initial project structure following Git Flow.
- Added comprehensive project documentation (README, WBS, Backlog, Roadmap, Risk Register, Project Status).
- Added Architecture Decision Records (ADR) to document key architectural decisions.
- Defined project development conventions and commit standards.

#### Development Environment

- Added Docker-based local development environment.
- Created `docker-compose.yml` to orchestrate application services.
- Added Dockerfile for containerizing the FastAPI application.
- Configured PostgreSQL container for local database development.
- Configured LocalStack container for AWS service emulation.

#### API

- Initialized the FastAPI application (`app/main.py`).
- Added `/health` endpoint for application health checks.
- Verified successful execution inside Docker Compose.

#### Dependencies

- Added the initial project dependencies in `requirements.txt`.
- Included the required libraries for FastAPI, PostgreSQL connectivity, Docker execution, and AVRO processing.

#### Architecture

- Added **ADR-008** documenting the selection of **fastavro** as the AVRO serialization library.

---

## [0.1.0] - 2026-07-10

### Added

- Initial repository creation.
- Project documentation.
- GitHub configuration.
- Repository templates.