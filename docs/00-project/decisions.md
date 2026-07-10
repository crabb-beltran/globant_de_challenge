# Architecture Decision Records (ADR)

This document records the major architectural decisions taken during the development of this project.

---

# ADR-001

## Title

SQL Database Selection

### Status

Accepted

### Decision

Amazon RDS PostgreSQL

### Context

The challenge explicitly requires a SQL-based database.

### Rationale

- PostgreSQL is production-ready.
- Excellent SQL capabilities.
- Strong analytical support.
- Mature ecosystem.

### Alternatives

- MySQL
- SQLite

### Trade-offs

Higher operational complexity than SQLite but closer to enterprise environments.

---

# ADR-002

## Title

API Framework

### Status

Accepted

### Decision

FastAPI

### Context

Need for REST API with validation.

### Rationale

- Automatic OpenAPI
- Pydantic validation
- Excellent performance
- Modern Python ecosystem

### Alternatives

- Flask
- Django REST Framework

---

# ADR-003

## Title

Compute Platform

### Status

Accepted

### Decision

AWS Lambda (Container Image)

### Context

Serverless deployment.

### Rationale

- AWS Free Tier
- No idle costs
- Easy scaling
- Docker support

### Alternatives

- EC2
- ECS Fargate

---

# ADR-004

## Title

Logging Strategy

### Status

Accepted

### Decision

CloudWatch Logs

### Context

Challenge requires invalid records to be logged.

### Rationale

- Native AWS integration
- No additional database tables
- Centralized logging
- Easy monitoring

### Alternatives

- PostgreSQL rejected_records table
- Flat files

---

# ADR-005

## Title

Secrets Management

### Status

Accepted

### Decision

AWS Systems Manager Parameter Store

### Context

Secure storage of database credentials.

### Rationale

- Free
- SecureString support
- Native AWS integration

### Alternatives

- Secrets Manager
- .env files

---

# ADR-006

## Title

Backup Strategy

### Status

Accepted

### Decision

Apache AVRO stored in Amazon S3

### Context

Challenge requires backup and restore.

### Rationale

- Compact binary format
- Schema evolution
- Easy restore
- Cloud-native storage

### Alternatives

- CSV
- JSON

---

# ADR-007

## Title

Development Workflow

### Status

Accepted

### Decision

Git Flow

### Context

Maintain clean project history.

### Rationale

- Feature isolation
- Clean releases
- Easier code review

### Branches

- main
- develop
- feature/*
- release/*
- hotfix/*