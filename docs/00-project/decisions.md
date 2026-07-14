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

# ADR-009

## Title
CDC / SCD Type 2 Implementation

### Status
Rejected

### Context
Historical portfolio experience (LedgerFlow) applies CDC and SCD Type 2
for tracking changing financial attributes over time.

### Decision
Not implemented in this project.

### Rationale
The challenge's data model has no changing-attribute dimension requiring
point-in-time historical tracking, and no external mutable source requiring
incremental change capture. `hired_employees.department_id`/`job_id`
represent a fact at hire time, not a slowly changing attribute. Applying
SCD/CDC here would be unjustified complexity relative to the rubric's
explicit guidance to prioritize correctness and clarity over
over-engineering (see risk-register.md R-016).


# ADR-010

## Title

Idempotency Strategy for Historical Data Loaders

### Status

Accepted

### Context

The challenge does not specify whether historical CSV loaders will be
re-executed (e.g. re-run after a partial failure, or re-run if the source
file is updated with additional records). Without an explicit strategy,
re-running a loader against already-loaded data would violate the
non-auto-incrementing `PRIMARY KEY` constraint (see `database.md`),
causing the entire batch transaction to fail and roll back — including
valid new records in the same run.

### Alternatives

| Option | Pros | Cons |
|---------|------|------|
| Skip-if-exists | Simple, safe by default, idempotent, never silently overwrites data | Does not apply corrections to already-loaded records |
| Upsert (INSERT ON CONFLICT DO UPDATE) | Applies corrections from updated source files | Silently overwrites data; risky without an explicit "this is a correction" signal |
| Full replace (truncate + reload) | Simple mental model | Destroys any data inserted through other means (e.g. future REST API), not safe for a mixed-ingestion system |

### Decision

Skip-if-exists: before inserting, load the set of existing primary key IDs
once per run; any CSV row whose `id` already exists in the database is
skipped (counted separately from both "inserted" and "rejected").

### Rationale

- The challenge describes this as a historical migration, not a continuous
  synchronization process — there is no stated requirement to apply
  corrections to already-loaded records.
- Idempotency by default is the safer choice: the loader can be re-run any
  number of times without side effects, which is valuable during
  development and testing.
- Applying corrections (upsert) is a distinct, explicit use case better
  suited to a dedicated API endpoint (`PUT`/`PATCH`, Phase 6) than to a
  silent re-run of a batch loader.
- This same pattern is applied uniformly to `departments`/`jobs`
  (`loaders/reference_data.py`) and `hired_employees`
  (`loaders/historical.py`).

### Consequences

**Positive**

- Loaders are safely re-runnable without manual cleanup.
- No risk of accidental data overwrite from a stale or duplicated source file.
- Consistent behavior across all three reference/historical loaders.

**Negative**

- Does not support correcting already-loaded records via re-run; a
  correction requires a separate, explicit mechanism (future API endpoint).


# ADR-011

## Title

Validation Engine — Decentralized Two-Layer Model, No Separate Component

### Status

Accepted

### Context

`wbs.md` Phase 7 originally scoped a "Validation Engine" covering six rules:
required fields, ISO datetime format, FK validation, batch size, null
validation, and duplicate validation. By the time this phase was opened,
all six rules were already implemented — distributed across Phase 5
(Pydantic schemas, `validators/business_rules.py`) and Phase 6
(`services/ingestion.py`, router-level batch size checks). No dedicated
"validation engine" module existed, nor was one clearly missing.

The question this ADR answers: should Phase 7 build a centralized
validation engine to consolidate these rules into a single component, or
formalize the existing two-layer split as the intended design?

### Alternatives

| Option | Pros | Cons |
|---------|------|------|
| Centralized validation engine (new module, all rules routed through it) | Single place to read all validation logic; easier onboarding for a new contributor | Duplicates responsibility already correctly split by *when* a rule can be checked (structural vs DB-state); would require re-wiring schemas and services that already work; directly contradicts R-016 (Overengineering) |
| Decentralized two-layer model (current state, formalized) | No new abstraction; validation lives where the information needed to perform it already lives (Pydantic has the raw payload, `business_rules.py`/`ingestion.py` has DB session access) | Requires reading two locations (`schemas/`, `validators/` + `services/ingestion.py`) to see the full picture of "what makes a record valid" |

### Decision

Keep the decentralized two-layer model:

- **Layer 1 (Pydantic schemas, `schemas/*.py`)** — structural validation
  that requires only the request payload: required fields, null/whitespace
  checks, ISO 8601 datetime format, positive-integer IDs, rejection of
  unexpected fields (`extra="forbid"`). Failure here rejects the entire
  request with `422` — these are client-side errors, not data quality
  issues to log and continue past.
- **Layer 2 (`validators/business_rules.py` + `services/ingestion.py`)**
  — validation that requires current database state: FK existence,
  duplicate ID detection. Failure here rejects only the offending record
  within a batch (`207`, `reason_code`), isolated via SAVEPOINT.

No new module was created. Phase 7's actual deliverable was a **gap audit**
against the six original rules, which surfaced four real omissions —
negative/zero IDs, whitespace-only strings, unexpected fields, and (upon
verification) confirmed acceptable behavior for numeric-string ID coercion
and ISO offset rejection — all fixed within the existing schemas, not a
new component.

### Rationale

- The two layers differ fundamentally in *what information is required*
  to evaluate them (payload alone vs payload + DB state) and in *failure
  semantics* (whole-request rejection vs per-record rejection within a
  successful batch). Merging them into one "engine" would need to
  internally re-implement this same split anyway — the abstraction would
  add a layer of indirection without removing any actual logic.
- Consistent with `risk-register.md` R-016 (Scope creep / Overengineering,
  rated High probability and High impact) and the challenge's explicit
  evaluation guidance to prioritize correctness and clarity over
  over-engineering.
- `docs/05-validation/validation.md` already documents the two layers
  explicitly, giving the "single place to understand validation" benefit
  a centralized engine would have provided, without the structural cost.

### Consequences

**Positive**

- No unnecessary abstraction introduced; existing, already-tested code
  paths (Phase 5, Phase 6) remain untouched in structure.
- Gap audit surfaced and fixed real omissions without needing to
  understand or migrate a new component.

**Negative**

- A future contributor unfamiliar with the project must read two
  locations (schemas + business_rules/ingestion service) to get the full
  picture of validation behavior, rather than one. Mitigated by
  `validation.md` serving as the single documentation entry point.

  # ADR-012

## Title

Backup Storage Location — Filesystem vs S3 (ADR-006 Reconciliation)

### Status

Accepted

### Context

ADR-006 specified "Apache AVRO stored in Amazon S3" as the backup
strategy. However, the challenge's literal requirement states: "Export
the full content of each table. Save it in AVRO format **on the
filesystem**" — not S3. This is a direct conflict between an earlier
architectural decision and the graded requirement.

### Decision

Backup/restore for this PoC writes AVRO files to local filesystem
(`/app/backups/`, mounted volume), matching the challenge's literal
requirement. S3 upload is documented as a future extension point
(infrastructure already provisioned in Phase 3), not implemented in
this phase.

### Rationale

- The challenge's evaluation criteria reward correctness against stated
  requirements over inferred "production-grade" alternatives; deviating
  from an explicit instruction ("on the filesystem") to satisfy an
  earlier, more general ADR would be scope substitution, not scope
  improvement.
- S3 remains a documented, low-effort extension (bucket already exists
  from Phase 3 infrastructure) rather than a discarded decision.

### Consequences

**Positive**

- Directly satisfies the graded requirement without ambiguity.
- No added AWS SDK complexity (`boto3` calls, IAM permissions for S3
  write) inside the core backup/restore logic for this phase.

**Negative**

- Backups are ephemeral relative to the API container's filesystem
  unless the backup directory is externally mounted/persisted (see
  `docker-compose.yml` volume configuration in `backup.md`).
- ADR-006 is now partially superseded; cross-referenced here rather
  than rewritten, to preserve historical decision traceability.