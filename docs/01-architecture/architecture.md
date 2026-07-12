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

dame project-status y wbs.md completosOrchestrated documento regeneration con alineación y actualizacionesOrchestrated documento regeneration con alineación y actualizacionesdocs/00-project/project-status.md
markdown# Project Status

**Project:** Globant Data Engineering Challenge

**Current Version:** v0.1.0

**Current Branch:** feature/database-schema

**Last Update:** 2026-07-12

---

# Overall Progress

| Phase | Progress | Branch | Status |
|--------|---------:|-------------------------------|---------|
| Project Setup | 100% | feature/project-setup | ✅ Completed |
| Development Environment | 100% | feature/development-environment | ✅ Completed |
| AWS Infrastructure | 100% | feature/aws-infrastructure | ✅ Completed |
| Database | 100% | feature/database-schema | ✅ Completed |
| Historical Data Migration | 0% | feature/historical-loader | ⏳ Pending |
| REST API | 0% | feature/rest-api | ⏳ Pending |
| Validation Engine | 0% | feature/validation-engine | ⏳ Pending |
| Backup & Restore | 0% | feature/backup-restore | ⏳ Pending |
| SQL Reports | 0% | feature/sql-reports | ⏳ Pending |
| Testing | 0% | feature/testing | ⏳ Pending |
| CI/CD | 0% | feature/github-actions | ⏳ Pending |
| Deployment | 0% | feature/aws-deployment | ⏳ Pending |
| Project Closure | 0% | feature/final-documentation | ⏳ Pending |
| Release | 0% | release/v1.0 | ⏳ Pending |

---

# Current Sprint

## Active Branch
feature/database-schema

## Current Goal

- Complete repository documentation
- Merge into develop

## Next Branch
feature/historical-loader

---

# Release Plan
feature/*
│
▼
develop
│
▼
release/v1.0
│
▼
main

docs/00-project/wbs.md
markdown# Work Breakdown Structure (WBS)

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
Cambios que apliqué en wbs.md, además de lo ya discutido

Fase 2: quité Install Python, Configure virtual environment, Configure VSCode, Configure Postman — ninguno se ejecutó realmente (trabajas 100% dentro de contenedores Docker, y Postman ya lo descartamos por /docs de FastAPI). Lo que sí ejecutaste está ahora reflejado con precisión.
Fase 3: reemplacé la lista genérica original por las tareas que realmente ejecutaste (incluyendo el Service-Linked Role y el downgrade de Bootstrap, que no estaban en la versión original pero fueron trabajo real de esta fase — coherente con lo que ya está en risk-register.md y deployment.md).
Fase 4: agregué "SQLAlchemy Models" como deliverable explícito — estaba implícito en "Alembic Configuration" pero fue un artefacto real y separado (models.py) que merece su propia línea.

Con esto, wbs.md y project-status.md ya no solo coinciden en nombres y orden de fase — también reflejan honestamente el trabajo real ejecutado en las 4 fases completadas, sin listar tareas que nunca ocurrieron.changelog.md72 linesmdconventions.md95 linesmddecisions.md404 linesmdrisk-register.md124 linesmdroadmap.md104 linesmdbacklog.md456 linesmdRevisa y corrige, e indicame si debemos eliminar alguno de estos archivos.Identificó redundancias documentales y recomendó consolidar archivosIdentificó redundancias documentales y recomendó consolidar archivosDiagnóstico general — antes de corregir archivo por archivo
Tienes tres documentos rastreando el mismo progreso de fases (wbs.md, roadmap.md, backlog.md), cada uno con su propia numeración, su propio estado de checkboxes, y ya divergentes entre sí. Es la misma enfermedad que venimos curando toda la sesión, pero a escala de todo el proyecto de golpe:
Fase 3 (AWS Infra)Estado realwbs.md✅ Completedroadmap.mdTodos los checkboxes sin marcar [ ]backlog.md (EPIC 4)Status: Pending, todos sin marcar
Fase 4 (Database) — mismo patrón: completa en wbs.md, sin marcar en los otros dos. Fase 2 en backlog.md (EPIC 3) tiene los checkboxes marcados [X] pero Status: Pending — contradicción interna dentro del mismo archivo.
Recomendación de fondo: elimina roadmap.md
Es 100% redundante con wbs.md — mismo contenido (fases, deliverables), menor detalle, ya desincronizado, y nombra fases distinto a wbs.md (tu propio "Restore" es fase separada ahí pero fase fusionada "Backup & Restore" en wbs.md; "Analytics" ahí vs "SQL Reports" en wbs.md). No aporta información que wbs.md + project-status.md no cubran ya, y mantenerlo solo garantiza que se desincronice de nuevo la próxima vez que actualices una fase y se te olvide tocar los tres archivos.
bashgit rm docs/00-project/roadmap.md
Actualiza tu docs/00-project/README.md (el índice que armamos) quitando esa referencia.
backlog.md — no lo elimines, pero repropósitalo
Aquí está el problema real: cuando armamos el índice de docs/00-project/, definimos explícitamente que backlog.md es "Granular task checklist for the active phase only" — no un tracker de las 17 fases completas del proyecto. Tal como está ahora, viola su propio propósito definido: intenta ser un segundo wbs.md con más detalle, y por eso también se desincronizó (EPIC 3 y 4 muestran Pending cuando ya completaste ambas).
Corrección: backlog.md solo debe contener la fase activa (ahora mismo, Historical Data Migration — Fase 5), reemplazando su contenido completo cada vez que cierras una fase y abres la siguiente. Guarda el Definition of Done al final porque es reutilizable entre fases, no específico de una.
markdown# Sprint Backlog

**Active Phase:** Historical Data Migration (WBS Phase 5)

**Branch:** feature/historical-loader

---

## Goal

Load the historical CSV datasets (`hired_employees`, `departments`, `jobs`)
into PostgreSQL, enforcing the challenge's validation rules and logging
rejected records.

### Tasks

- [ ] Analyze CSV structure and known data quality issues
- [ ] Design ingestion flow (staging vs direct-validated insert — see
      decisions.md if this becomes a real ADR-worthy choice)
- [ ] Implement CSV reader
- [ ] Implement per-record validation (required fields, FK existence)
- [ ] Implement batch processing
- [ ] Implement rejected-record logging (CloudWatch, per ADR-004)
- [ ] Implement valid-record insertion
- [ ] Verify row counts against source CSVs

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
conventions.md — un desajuste real
La sección Branch Naming lista ejemplos genéricos (feature/database, feature/api, feature/aws) que no coinciden con ninguna branch real que hayas usado (feature/database-schema, feature/rest-api, feature/aws-infrastructure). Corrige para que sea la referencia real:
markdown## Branch Naming

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
changelog.md — falta la sección de esta fase
AWS Infrastructure está completa ahí, pero falta toda la Fase 4 (Database) que acabas de cerrar en esta sesión — ER diagram, DDL, modelos SQLAlchemy, configuración de Alembic, migración inicial, ADR-009. Agrega esto bajo [Unreleased], después de la sección AWS Infrastructure:
markdown#### Database

- Designed the entity-relationship model for `departments`, `jobs`, and `hired_employees` (1—N relationships), documented in `docs/02-database/database.md`.
- Defined `TIMESTAMPTZ` for `hired_employees.datetime`, `NOT NULL` on all columns, and `ON DELETE RESTRICT` on both foreign keys — all justified against the challenge's validation rules and audit-data semantics.
- Wrote the initial SQL DDL (`app/ddl.sql`) as a manual reference alongside the SQLAlchemy models.
- Implemented SQLAlchemy 2.0 models (`app/models.py`) using `Mapped`/`mapped_column`, with explicit `autoincrement=False` on all primary keys — IDs are sourced from ingested data, not auto-generated (corrected after the first `alembic revision --autogenerate` incorrectly inferred a `SERIAL` sequence).
- Configured Alembic (`alembic init`, `env.py` wired to `Base.metadata` and to `.env`-sourced connection strings).
- Generated and applied the initial migration; verified the materialized schema directly against PostgreSQL (`\d hired_employees`) to confirm indexes, foreign keys, and constraint behavior matched the design.
- Added **ADR-009**, documenting the decision to reject CDC/SCD Type 2 for this project's data model.
decisions.md y risk-register.md — sin cambios necesarios
Ambos están correctamente sincronizados con el trabajo real ejecutado (ADR-009 ya presente, R-021/022/023 completos con Lessons Learned). No requieren edición en este momento.
Un gap que detecté al revisar todo junto — anótalo, no lo resuelvas ahora
roadmap.md (que vas a eliminar) tenía una tarea que no existe en ningún otro documento: ECR bajo Infrastructure. Tu ADR-003 comprometió "AWS Lambda (Container Image)", lo cual requiere un repositorio ECR para almacenar la imagen — pero ni wbs.md Fase 3 ni Fase 12 (Deployment) lo mencionan explícitamente. No es urgente resolverlo ahora (Fase 12 está lejos), pero agrega una línea a wbs.md Fase 12 para no perderlo:
markdown## Phase 12 — Deployment

### AWS

- Create ECR Repository
- Push Docker Image
- Deploy Lambda
...
¿Aplicas estos 5 cambios (eliminar roadmap.md, reescribir backlog.md, corregir conventions.md, actualizar changelog.md, agregar ECR a wbs.md) y seguimos con el cierre de PR de esta fase?architecture.md94 linesmddeployment.md339 linesmdrevisa y corrigeIdentificó inconsistencias en documentación y arquitectura para corregirIdentificó inconsistencias en documentación y arquitectura para corregirdeployment.md — 3 gaps reales frente a lo que efectivamente ejecutaste
1. Sección 8 (Downgrade IAM) tiene el comando equivocado — literalmente el error que viviste en esta sesión. Tal como está, muestra al deployer desadjuntándose su propia policy, pero ya confirmaste con AccessDenied que un user nunca puede modificarse a sí mismo — tuviste que usar un profile admin/root (R-023). El documento actual describe un comando que sabes que falla.
2. Falta el paso de actualizar la Runtime policy con rds:StopDBInstance/rds:StartDBInstance antes de la Sección 9 — el changelog.md ya lo menciona, pero deployment.md salta directo al stop-db-instance sin mostrar que la policy necesitó esa adición primero (y por qué).
3. Falta una entrada en Known Issues Encountered para el AccessDenied de auto-modificación IAM (R-023) — tienes las otras 4, falta esta.
Correcciones — reemplaza estas dos secciones
Sección 8 corregida:
markdown## 8. Post-Provisioning: Downgrade IAM Permissions

Once all resources above are created and verified, remove the Bootstrap
policy — the deployer user should only retain least-privilege Runtime
permissions going forward.

> **See `risk-register.md` R-023.** An IAM user cannot modify its own
> attached policies — `detach-user-policy` on oneself returns `AccessDenied`
> by design (least-privilege is meaningless if a user can grant/revoke its
> own permissions). This step requires **admin-level credentials**, the
> same temporary-profile pattern used in Section 3.

```bash
# Temporary admin profile — remove immediately after this step
aws configure --profile admin
# paste admin/root access keys

aws iam detach-user-policy \
  --user-name globant-de-challenge-deployer \
  --policy-arn arn:aws:iam:::policy/globant-de-challenge-bootstrap \
  --profile admin

aws iam list-attached-user-policies \
  --user-name globant-de-challenge-deployer \
  --profile admin
```

Expected: only `globant-de-challenge-runtime` remains attached.

Cleanup immediately after (same ritual as Section 3): remove the `[admin]`
block from `~/.aws/credentials`, then deactivate and delete the admin
access key via Console.
Nueva sub-sección 9.1, antes del stop-db-instance actual:
markdown## 9. Cost Management: Stop/Start Discipline

RDS free tier does not apply to accounts older than 12 months — instance
hours and the public IPv4 address bill from hour one (~$17.65/month if left
running 24/7).

### 9.1 Add stop/start permissions to the Runtime policy

The deployer's Runtime policy does not include instance start/stop actions
by default (they are operational, not provisioning, so they were not part
of Bootstrap either). Add to `runtime-policy.json` and update the policy in
IAM (see `docs/09-deployment/policies/runtime-policy.json`):

```json
{
  "Sid": "RDSInstanceOperations",
  "Effect": "Allow",
  "Action": [
    "rds:DescribeDBInstances",
    "rds:StopDBInstance",
    "rds:StartDBInstance"
  ],
  "Resource": "arn:aws:rds:us-east-1::db:globant-de-challenge-db"
}
```

### 9.2 Stop at the end of every work session

```bash
aws rds stop-db-instance --db-instance-identifier globant-de-challenge-db
```

### 9.3 Start at the beginning of the next session (allow 3-5 minutes)

```bash
aws rds start-db-instance --db-instance-identifier globant-de-challenge-db
```

Notes:
- A stopped instance still bills provisioned storage (~$2.30/month for 20GB gp2).
- AWS automatically restarts stopped RDS instances after 7 consecutive days.
- The public IP may map to a changed client-side IP between sessions —
  if connectivity fails after a start, verify both instance status and the
  Security Group ingress rule against your current public IP.
Nueva fila en Known Issues Encountered:
markdown| `DetachUserPolicy` on the deployer's own Bootstrap policy returned `AccessDenied` | An IAM identity cannot modify its own attached policies — a deliberate AWS safeguard | Executed with a temporary admin CLI profile instead of the deployer identity (Section 8) | `risk-register.md` R-023 |

architecture.md — 2 correcciones
1. El "High-Level Flow" describe un pipeline lineal que no es correcto. Reports y Backup no son pasos secuenciales después de la REST API — son dos consumidores independientes de PostgreSQL. Y la carga histórica y la ingesta vía API son dos entradas paralelas a Validation, no una sola cadena. El diagrama actual sugiere que un backup solo ocurre después de que alguien llama a Reports, lo cual es falso.
markdown## High-Level Flow

```
CSV (historical) ──┐
                    ├──▶ Validation ──▶ PostgreSQL ──┬──▶ SQL Reports
REST API (new data)┘                                 └──▶ Backup ──▶ S3

Restore: S3 ──▶ PostgreSQL (reverse of Backup path)
```
2. PostgreSQL debe ser explícito como Amazon RDS (PostgreSQL), coherente con ADR-001 — actualmente es ambiguo entre tu Postgres local de Docker y el real de AWS. Y falta IAM en la lista de componentes, dado el peso real que tuvo en el proyecto (least-privilege bootstrap/runtime, Service-Linked Role).
markdown## Components

- FastAPI
- AWS Lambda
- API Gateway
- Amazon RDS (PostgreSQL)
- Amazon S3
- CloudWatch Logs
- Systems Manager Parameter Store
- IAM (least-privilege Bootstrap/Runtime policies)
- Docker
3. Menor — Future Improvements lista Terraform y CloudFormation como si fueran mejoras independientes, pero son alternativas mutuamente excluyentes de IaC (harías una u otra, no ambas). Aclara la intención:
markdown## Future Improvements

- Infrastructure as Code (Terraform, evaluated over CloudFormation for cloud-agnostic syntax)
- Authentication
- Monitoring Dashboard
¿Aplicas los 5 ajustes (2 en deployment.md, 3 en architecture.md)? Con esto, junto con lo que ya cerramos de roadmap.md/backlog.md/conventions.md/changelog.md, toda la documentación del proyecto queda sincronizada con lo realmente ejecutado hasta la Fase 4.dame el archivo architecture.mdmarkdown# System Architecture

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