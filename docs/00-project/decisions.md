# Architecture Decision Records (ADR)

This document records the major architectural decisions made during the development of the Globant Data Engineering Challenge.

---

# ADR-001

## Title

SQL Database Selection

### Status

Accepted

### Context

The challenge requires a relational SQL database capable of supporting transactional workloads and analytical queries.

### Alternatives

| Option | Pros | Cons |
|---------|------|------|
| PostgreSQL | Mature ecosystem, advanced SQL features, excellent analytical capabilities | Slightly more complex administration |
| MySQL | Popular and easy to use | Fewer advanced SQL features |
| SQLite | Lightweight and simple | Not suitable for production-like environments |

### Decision

Amazon RDS PostgreSQL

### Rationale

- Production-ready database engine.
- Strong SQL compliance.
- Excellent analytical capabilities.
- Large community and ecosystem.

### Consequences

**Positive**

- Enterprise-grade relational database.
- Native AWS integration.
- Excellent reporting capabilities.

**Negative**

- Higher operational complexity than SQLite.

---

# ADR-002

## Title

API Framework

### Status

Accepted

### Context

The project requires a REST API with request validation, automatic documentation, and high performance.

### Alternatives

| Option | Pros | Cons |
|---------|------|------|
| FastAPI | High performance, OpenAPI support, Pydantic validation | Smaller ecosystem than Django |
| Flask | Lightweight and flexible | Requires additional libraries |
| Django REST Framework | Mature ecosystem | Heavier framework |

### Decision

FastAPI

### Rationale

- Automatic OpenAPI documentation.
- Native data validation.
- Excellent performance.
- Modern Python ecosystem.

### Consequences

**Positive**

- Faster API development.
- Automatic interactive documentation.
- Reduced validation code.

**Negative**

- Smaller ecosystem compared to Django.

---

# ADR-003

## Title

Compute Platform

### Status

Accepted

### Context

The application will be deployed using AWS services while minimizing operational costs.

### Alternatives

| Option | Pros | Cons |
|---------|------|------|
| AWS Lambda | Serverless, scalable, cost-effective | Execution time limits |
| EC2 | Full control | Infrastructure management |
| ECS Fargate | Container-native | Higher operational complexity |

### Decision

AWS Lambda (Container Image)

### Rationale

- Compatible with Docker.
- No server management.
- Automatic scaling.
- Fits AWS Free Tier.

### Consequences

**Positive**

- Lower operational overhead.
- Cost-efficient deployment.
- Easy scalability.

**Negative**

- Lambda execution limitations.

---

# ADR-004

## Title

Logging Strategy

### Status

Accepted

### Context

Invalid records must be logged without impacting the primary transactional database.

### Alternatives

| Option | Pros | Cons |
|---------|------|------|
| CloudWatch Logs | Native AWS integration, centralized logging | AWS dependency |
| PostgreSQL Table | Easy querying | Increases database load |
| Flat Files | Simple implementation | Difficult monitoring |

### Decision

Amazon CloudWatch Logs

### Rationale

- Centralized logging.
- Native AWS integration.
- Supports monitoring and troubleshooting.

### Consequences

**Positive**

- Easier operational monitoring.
- Better observability.
- Reduced database load.

**Negative**

- AWS service dependency.

---

# ADR-005

## Title

Secrets Management

### Status

Accepted

### Context

Database credentials and sensitive configuration must not be stored in source code.

### Alternatives

| Option | Pros | Cons |
|---------|------|------|
| Parameter Store | Free, SecureString support | Fewer features than Secrets Manager |
| Secrets Manager | Automatic rotation | Additional cost |
| .env Files | Simple | Not suitable for production |

### Decision

AWS Systems Manager Parameter Store

### Rationale

- Secure credential storage.
- Free within expected usage.
- Native AWS integration.

### Consequences

**Positive**

- Improved security.
- Centralized configuration.

**Negative**

- AWS dependency.

---

# ADR-006

## Title

Backup Strategy

### Status

Accepted

### Context

The challenge requires exporting and restoring database information using Apache AVRO.

### Alternatives

| Option | Pros | Cons |
|---------|------|------|
| Apache AVRO | Compact, schema evolution, binary format | Requires serialization library |
| CSV | Human-readable | No schema support |
| JSON | Flexible | Larger files |

### Decision

Apache AVRO stored in Amazon S3

### Rationale

- Compact binary format.
- Supports schema evolution.
- Cloud-native storage.
- Efficient backup and restore.

### Consequences

**Positive**

- Smaller backup files.
- Reliable restore process.
- Compatible with big data ecosystems.

**Negative**

- Requires AVRO serialization.

---

# ADR-007

## Title

Development Workflow

### Status

Accepted

### Context

The project requires an organized workflow to maintain traceability between planning, implementation, and releases.

### Alternatives

| Option | Pros | Cons |
|---------|------|------|
| Git Flow | Structured releases, feature isolation | More branches |
| GitHub Flow | Simpler workflow | Less suited for staged releases |
| Trunk-Based Development | Fast integration | Less release control |

### Decision

Git Flow

### Rationale

- Isolated feature development.
- Controlled releases.
- Clear project history.

### Consequences

**Positive**

- Better traceability.
- Cleaner release management.
- Easier code reviews.

**Negative**

- Additional branch management.

---

# ADR-008

## Title

AVRO Serialization Library

### Status

Accepted

### Context

The backup and restore modules require a Python library capable of reading and writing Apache AVRO files efficiently.

### Alternatives

| Option | Pros | Cons |
|---------|------|------|
| fastavro | High performance, actively maintained, lightweight | Third-party implementation |
| avro-python3 | Official Apache implementation | Lower performance |

### Decision

fastavro

### Rationale

- Reported better serialization/deserialization throughput in high-volume 
  batch scenarios (per project documentation; not independently benchmarked 
  for this challenge).
- Actively maintained, widely adopted in data engineering pipelines 
  (Spark, Kafka ecosystems).
- Lower memory overhead for large batch reads/writes, relevant given 
  Lambda's memory-based pricing.
- Simpler API surface for schema-driven read/write compared to the 
  official Apache implementation.

### Consequences

**Positive**

- Faster backup generation.
- Faster restore operations.
- Better scalability.
- Lower Lambda execution time.

**Negative**

- Additional external dependency.