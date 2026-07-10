# Product Backlog

Project: Globant Data Engineering Challenge

---

# EPIC 1 — Project Initialization

## Goal

Prepare the repository and project documentation.

### User Story

As a developer, I want a well-organized repository so the project is maintainable and easy to evaluate.

### Tasks

- [X] Create GitHub repository
- [X] Configure .gitignore
- [X] Add MIT License
- [X] Create README.md
- [X] Create documentation structure
- [X] Create WBS
- [X] Create ADR
- [X] Create Roadmap
- [X] Create Backlog

Priority

High

Status

Completed

---

# EPIC 2 — GitHub Project Management

## Goal

Organize development workflow.

### Tasks

- [X] Create develop branch
- [X] Configure branch protection
- [X] Create GitHub Project
- [X] Create Labels
- [X] Create Issue Templates
- [X] Create Pull Request Template

Priority

High

Status

Completed

---

# EPIC 3 — Development Environment

## Goal

Prepare local environment.

### Tasks

- [ ] Install Python
- [ ] Configure Virtual Environment
- [ ] Configure Docker
- [ ] Configure Docker Compose
- [ ] Install PostgreSQL client
- [ ] Install AWS CLI
- [ ] Configure AWS CLI
- [ ] Install Postman
- [ ] Configure VSCode Extensions

Priority

High

Status

Pending

---

# EPIC 4 — AWS Infrastructure

## Goal

Provision AWS services.

### Tasks

- [ ] Create IAM Developer User
- [ ] Create IAM Policies
- [ ] Create Budget Alerts
- [ ] Create SSM Parameter Store
- [ ] Create RDS PostgreSQL
- [ ] Configure Security Groups
- [ ] Create S3 Bucket
- [ ] Create CloudWatch Log Group
- [ ] Create ECR Repository
- [ ] Configure Lambda Environment

Priority

High

Status

Pending

---

# EPIC 5 — Database

## Goal

Implement relational database.

### Tasks

- [ ] Design ER Diagram
- [ ] Create SQL Schema
- [ ] Configure Alembic
- [ ] Create Initial Migration
- [ ] Apply Migration
- [ ] Validate Constraints
- [ ] Configure Indexes

Priority

High

Status

Pending

---

# EPIC 6 — Historical Migration

## Goal

Import CSV historical data.

### Tasks

- [ ] Analyze datasets
- [ ] Design ingestion flow
- [ ] Read CSV files
- [ ] Validate records
- [ ] Insert valid records
- [ ] Log invalid records
- [ ] Batch processing

Priority

High

Status

Pending

---

# EPIC 7 — Validation Engine

## Goal

Guarantee data quality.

### Tasks

- [ ] Required field validation
- [ ] Datetime validation
- [ ] ISO8601 validation
- [ ] Department FK validation
- [ ] Job FK validation
- [ ] Batch size validation
- [ ] Duplicate validation
- [ ] Error response design

Priority

Critical

Status

Pending

---

# EPIC 8 — REST API

## Goal

Expose ingestion endpoints.

### Tasks

- [ ] API architecture
- [ ] Endpoint design
- [ ] Employee endpoint
- [ ] Department endpoint
- [ ] Job endpoint
- [ ] Request validation
- [ ] Response models
- [ ] Error handling
- [ ] API Documentation

Priority

High

Status

Pending

---

# EPIC 9 — Backup

## Goal

Generate AVRO backups.

### Tasks

- [ ] Export database
- [ ] Generate AVRO
- [ ] Upload to S3
- [ ] Create Backup Endpoint
- [ ] Validate backup

Priority

Medium

Status

Pending

---

# EPIC 10 — Restore

## Goal

Recover data from backups.

### Tasks

- [ ] Download AVRO
- [ ] Read AVRO
- [ ] Restore records
- [ ] Restore endpoint
- [ ] Validation after restore

Priority

Medium

Status

Pending

---

# EPIC 11 — SQL Reports

## Goal

Implement analytical queries.

### Tasks

- [ ] Employees per quarter
- [ ] Departments above average
- [ ] Optimize SQL
- [ ] Create report endpoints

Priority

High

Status

Pending

---

# EPIC 12 — Logging

## Goal

Store invalid records.

### Tasks

- [ ] Design log format
- [ ] Configure CloudWatch
- [ ] Structured JSON logs
- [ ] Exception logging
- [ ] API logging

Priority

Medium

Status

Pending

---

# EPIC 13 — Testing

## Goal

Validate application.

### Tasks

- [ ] Unit Tests
- [ ] Integration Tests
- [ ] API Tests
- [ ] Validation Tests
- [ ] Backup Tests
- [ ] Restore Tests
- [ ] SQL Tests

Priority

High

Status

Pending

---

# EPIC 14 — Docker

## Goal

Containerize application.

### Tasks

- [ ] Dockerfile
- [ ] Docker Compose
- [ ] Multi-stage Build
- [ ] Environment Variables
- [ ] Local execution

Priority

High

Status

Pending

---

# EPIC 15 — CI/CD

## Goal

Automate quality checks.

### Tasks

- [ ] GitHub Actions
- [ ] Black
- [ ] Flake8
- [ ] Pytest
- [ ] Docker Build
- [ ] Build Status Badge

Priority

Medium

Status

Pending

---

# EPIC 16 — Deployment

## Goal

Deploy to AWS.

### Tasks

- [ ] Push Docker Image to ECR
- [ ] Deploy Lambda
- [ ] Configure API Gateway
- [ ] Configure Environment Variables
- [ ] Production Validation

Priority

High

Status

Pending

---

# EPIC 17 — Documentation

## Goal

Prepare final delivery.

### Tasks

- [ ] Update README
- [ ] Update Architecture
- [ ] Update ADR
- [ ] Update API Docs
- [ ] Deployment Guide
- [ ] Troubleshooting Guide
- [ ] Final Review

Priority

High

Status

Pending

---

# Definition of Done (DoD)

A task is considered complete when:

- [ ] Code implemented
- [ ] Code reviewed
- [ ] Tests passed
- [ ] Documentation updated
- [ ] Docker verified
- [ ] GitHub pushed
- [ ] Pull Request merged