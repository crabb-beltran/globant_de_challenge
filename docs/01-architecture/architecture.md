# System Architecture

## Overview

The solution follows a cloud-native architecture based on AWS managed services.

---

## Components

- FastAPI
- AWS Lambda
- API Gateway
- Amazon RDS (PostgreSQL)
- Amazon S3
- CloudWatch Logs
- Systems Manager Parameter Store
- IAM (least-privilege Bootstrap/Runtime policies)
- Docker

---

## High-Level Flow

CSV (historical) ──┐
├──▶ Validation ──▶ PostgreSQL ──┬──▶ SQL Reports
REST API (new data)┘                                 └──▶ Backup ──▶ S3
Restore: S3 ──▶ PostgreSQL (reverse of Backup path)

---

## Deployment

GitHub
↓
GitHub Actions
↓
Docker
↓
Amazon ECR
↓
Lambda
↓
API Gateway

---

## Future Improvements

- Infrastructure as Code (Terraform, evaluated over CloudFormation for cloud-agnostic syntax)
- Authentication
- Monitoring Dashboard