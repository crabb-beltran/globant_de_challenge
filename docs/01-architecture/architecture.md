# System Architecture

## Overview

The solution follows a cloud-native architecture based on AWS managed services.

---

## Components

- FastAPI
- AWS Lambda
- API Gateway
- PostgreSQL
- Amazon S3
- CloudWatch
- Parameter Store
- Docker

---

## High-Level Flow

```
CSV

↓

Historical Loader

↓

Validation

↓

PostgreSQL

↓

REST API

↓

Reports

↓

Backup

↓

S3
```

---

## Deployment

```
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
```

---

## Future Improvements

- Terraform

- CloudFormation

- Authentication

- Monitoring Dashboard