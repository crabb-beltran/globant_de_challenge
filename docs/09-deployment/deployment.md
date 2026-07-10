# Deployment Guide

## Local

- Clone repository
- Configure environment
- Start Docker
- Run migrations
- Start API

---

## AWS

Infrastructure

- IAM
- RDS
- S3
- Lambda
- API Gateway
- CloudWatch
- Parameter Store

Deployment Flow

GitHub

↓

GitHub Actions

↓

Docker Build

↓

Amazon ECR

↓

Lambda Deployment

↓

API Gateway

---

## Environment Variables

Describe every required variable here.

---

## Monitoring

CloudWatch Logs

CloudWatch Metrics

Budget Alerts