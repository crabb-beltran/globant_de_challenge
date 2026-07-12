# Work Breakdown Structure (WBS)

## Phase 0 — Project Initialization

### Objectives

- Understand challenge requirements
- Identify functional requirements
- Identify non-functional requirements
- Create repository
- Define project scope

Status

- [x] Completed

---

## Phase 1 — Project Planning

### Deliverables

- Architecture definition
- Technology selection
- AWS services selection
- Cost analysis
- Git workflow
- Documentation structure

Deliverables

- Architecture Diagram
- ADR
- Roadmap

Status

- [x] Completed

---

## Phase 2 — Development Environment

### Tasks

- Configure Docker
- Configure Docker Compose (Postgres, LocalStack, API)
- Configure Git
- Install AWS CLI
- Configure AWS CLI

Status

- [x] Completed

---

## Phase 3 — AWS Infrastructure

### Tasks

- Create Budget
- Create IAM User
- Create IAM Bootstrap and Runtime Policies
- Create RDS Service-Linked Role
- Create Security Group
- Create DB Subnet Group
- Create RDS PostgreSQL
- Detach Bootstrap Policy (least-privilege downgrade)

Status

- [x] Completed

---

## Phase 4 — Database

### Deliverables

- ER Diagram
- SQL Schema (DDL)
- SQLAlchemy Models
- Alembic Configuration
- Initial Migration

Status

- [x] Completed

---

## Phase 5 — Historical Data Migration

### Tasks

- CSV Loader
- Data Validation
- Batch Processing
- Error Logging
- Data Insertion

Status

- [ ]

---

## Phase 6 — REST API

### Endpoints

- Employees
- Departments
- Jobs
- Reports
- Backup
- Restore

Status

- [ ]

---

## Phase 7 — Validation Engine

### Rules

- Required fields
- ISO Datetime
- FK validation
- Batch Size
- Null validation
- Duplicate validation

Status

- [ ]

---

## Phase 8 — Backup & Restore

### Backup

- AVRO Export
- Upload to S3

### Restore

- Download AVRO
- Restore Database

Status

- [ ]

---

## Phase 9 — SQL Reports

### Reports

- Employees by Quarter
- Departments Above Average

Status

- [ ]

---

## Phase 10 — Testing

### Tests

- Unit Tests
- Integration Tests
- API Tests
- Validation Tests

Status

- [ ]

---

## Phase 11 — CI/CD

### Tasks

- GitHub Actions
- Docker Build
- Quality Checks
- Deployment Pipeline

Status

- [ ]

---

## Phase 12 — Deployment

### AWS

- Create ECR Repository
- Push Docker Image
- Deploy Lambda
- Configure API Gateway
- Configure Environment Variables

Status

- [ ]

---

## Phase 13 — Project Closure

### Deliverables

- README
- Documentation
- Final Review
- Repository Cleanup
- Release v1.0

Status

- [ ]