# Deployment & Infrastructure Setup

This document describes, step by step, how to provision the AWS infrastructure
required by this project from a clean AWS account. It complements:

- `docs/00-project/decisions.md` — ADR-001 to ADR-006 explain *why* each
  service/pattern was chosen.
- `docs/00-project/risk-register.md` — R-021 and R-022 document two
  IAM permission gaps discovered while executing the commands below.

All commands assume AWS CLI v2, region `us-east-1`, and the AWS account used
for this project. Replace every `<PLACEHOLDER>` with your own values —
**never commit real credentials, IPs, or secrets to this file or to `.env`**.

---

## Prerequisites

- AWS CLI v2 installed (`aws --version`).
- An existing IAM user/root with console access, used **once** to create the
  project's dedicated deployer user below.
- A local `.env` file populated from `.env.example` (gitignored).

---

## 1. AWS Budget (Zero Spend)

Manual step, via AWS Console (no CLI equivalent used in this project):

1. Billing and Payments → Budgets → Create budget.
2. Budget type: **Use a template (simplified)** → **Zero spend budget**.
3. Budget name: `globant-de-challenge-zero-spend`.
4. Email recipients: your monitored email address.
5. Scope: All AWS services (default).
6. Create budget.

This alerts by email on any spend above $0.01 — detection, not prevention.
Combine with the resource-level free-tier choices below (`db.t4g.micro`,
20GB storage, no Multi-AZ).

---

## 2. IAM — Deployer User & Policies

### 2.1 Create the IAM user (CLI-only, no console access)

```bash
aws iam create-user --user-name globant-de-challenge-deployer
```

### 2.2 Create the Bootstrap policy (temporary, provisioning-only)

Save as `bootstrap-policy.json` — full content in `decisions.md` under the
IAM Policy Design section. Includes: RDS provisioning, EC2 networking for
RDS, S3 bucket provisioning, CloudWatch Log Group provisioning, SSM
Parameter provisioning, plus two permissions added after real-world gaps:

- `iam:CreateServiceLinkedRole` (scoped via `iam:AWSServiceName` condition) — see R-021.
- `rds:DescribeDBEngineVersions` — see R-022.

```bash
aws iam create-policy \
  --policy-name globant-de-challenge-bootstrap \
  --policy-document file://bootstrap-policy.json \
  --description "Temporary provisioning permissions for RDS, S3, CloudWatch, SSM. Detach after infrastructure is created."
```

### 2.3 Create the Runtime policy (permanent, least-privilege)

Save as `runtime-policy.json` — scoped to specific resource ARNs, no
creation/deletion permissions.

```bash
aws iam create-policy \
  --policy-name globant-de-challenge-runtime \
  --policy-document file://runtime-policy.json \
  --description "Permanent least-privilege permissions for application runtime."
```

### 2.4 Attach both policies to the deployer user

```bash
aws iam attach-user-policy \
  --user-name globant-de-challenge-deployer \
  --policy-arn arn:aws:iam::<ACCOUNT_ID>:policy/globant-de-challenge-bootstrap

aws iam attach-user-policy \
  --user-name globant-de-challenge-deployer \
  --policy-arn arn:aws:iam::<ACCOUNT_ID>:policy/globant-de-challenge-runtime
```

### 2.5 Generate access keys and configure the CLI

Via Console: IAM → Users → `globant-de-challenge-deployer` → Security
credentials → Create access key → Use case: **Command Line Interface (CLI)**.

```bash
aws configure
# AWS Access Key ID: <paste, never commit>
# AWS Secret Access Key: <paste, never commit>
# Default region name: us-east-1
# Default output format: json
```

Verify:

```bash
aws sts get-caller-identity
```

Expected: `Account` matches `<ACCOUNT_ID>`, `Arn` ends in
`user/globant-de-challenge-deployer`.

---

## 3. IAM — RDS Service-Linked Role (one-time, admin-privileged)

> **See `risk-register.md` R-021.** The Bootstrap policy grants
> `iam:CreateServiceLinkedRole`, but AWS still requires the role to exist at
> account level before `create-db-subnet-group`/`create-db-instance` will
> succeed. This step must run with **admin-level credentials**, not the
> deployer user — it is a one-time action per AWS account.

```bash
# Temporary admin profile — remove immediately after this step
aws configure --profile admin
# paste admin/root access keys

aws iam create-service-linked-role \
  --aws-service-name rds.amazonaws.com \
  --profile admin
```

Cleanup after success:

```bash
# Edit ~/.aws/credentials and remove the [admin] block manually
nano ~/.aws/credentials
```

Then, via Console: deactivate and delete the admin access key used for this
step.

Secure the credentials file (flagged by a CLI warning during this project):

```bash
chmod 600 ~/.aws/credentials
chmod 600 ~/.aws/config
```

---

## 4. Networking — Security Group

```bash
aws ec2 create-security-group \
  --group-name globant-de-challenge-rds-sg \
  --description "RDS PostgreSQL access - Globant DE Challenge" \
  --vpc-id <VPC_ID>
```

Note the returned `GroupId`, then restrict ingress to a single IP:

```bash
aws ec2 authorize-security-group-ingress \
  --group-id <SG_ID> \
  --protocol tcp \
  --port 5432 \
  --cidr <YOUR_PUBLIC_IP>/32
```

Get your current public IP if needed:

```bash
curl -s https://checkip.amazonaws.com
```

> Dynamic residential IPs may change over time — if connectivity fails later,
> re-run the `authorize-security-group-ingress` command (after first revoking
> the stale rule) with the new IP.

---

## 5. Networking — DB Subnet Group

Requires at least 2 subnets in different Availability Zones:

```bash
aws ec2 describe-subnets \
  --filters "Name=default-for-az,Values=true" \
  --query "Subnets[].{AZ:AvailabilityZone,SubnetId:SubnetId,VpcId:VpcId}" \
  --output table
```

```bash
aws rds create-db-subnet-group \
  --db-subnet-group-name globant-de-challenge-subnet-group \
  --db-subnet-group-description "Subnet group for Globant DE Challenge RDS" \
  --subnet-ids <SUBNET_ID_AZ_1> <SUBNET_ID_AZ_2>
```

---

## 6. RDS PostgreSQL Instance

Verify available engine versions before provisioning:

```bash
aws rds describe-db-engine-versions \
  --engine postgres \
  --query "DBEngineVersions[?starts_with(EngineVersion, '16')].EngineVersion" \
  --output table
```

Load credentials from `.env` to avoid shell interpretation issues with
special characters in the password (see note below):

```bash
source .env

aws rds create-db-instance \
  --db-instance-identifier globant-de-challenge-db \
  --db-instance-class db.t4g.micro \
  --engine postgres \
  --engine-version 16.9 \
  --master-username "$DB_USER_RDS" \
  --master-user-password "$DB_PASSWORD_RDS" \
  --allocated-storage 20 \
  --storage-type gp2 \
  --db-subnet-group-name globant-de-challenge-subnet-group \
  --vpc-security-group-ids <SG_ID> \
  --publicly-accessible \
  --no-multi-az \
  --backup-retention-period 1 \
  --db-name globant_de_challenge \
  --tags Key=Project,Value=globant-de-challenge
```

> **Note:** always wrap `--master-user-password` in a quoted shell variable
> (`"$DB_PASSWORD_RDS"`), never paste the raw password directly in the
> command. Unquoted special characters (`$`, `!`, backticks) are interpreted
> by bash before reaching AWS, silently truncating the password.

Monitor creation status (takes ~5-10 minutes):

```bash
aws rds describe-db-instances \
  --db-instance-identifier globant-de-challenge-db \
  --query "DBInstances[0].DBInstanceStatus" \
  --output text
```

Wait until the output is `available`.

---

## 7. Verify Connectivity

Get the connection endpoint:

```bash
aws rds describe-db-instances \
  --db-instance-identifier globant-de-challenge-db \
  --query "DBInstances[0].Endpoint.{Address:Address,Port:Port}" \
  --output table
```

Store the `Address` as `DB_HOST_RDS` in `.env` (keep it separate from
`DB_HOST`, which points to the local `postgres_rds` Docker service).

Test with `psql` (install via `sudo apt-get install postgresql-client -y`
if not available), or use the containerized client without installing
anything on the host:

```bash
docker run -it --rm postgres:16-alpine \
  psql -h <DB_HOST_RDS> -p 5432 -U <DB_USER_RDS> -d globant_de_challenge
```

A successful connection shows the `globant_de_challenge=>` prompt and
confirms SSL is active by default (RDS enforces TLS automatically).

---

## 8. Post-Provisioning: Downgrade IAM Permissions

Once all resources above are created and verified, remove the Bootstrap
policy — the deployer user should only retain least-privilege Runtime
permissions going forward.

```bash
aws iam detach-user-policy \
  --user-name globant-de-challenge-deployer \
  --policy-arn arn:aws:iam::<ACCOUNT_ID>:policy/globant-de-challenge-bootstrap
```

Verify remaining attached policies:

```bash
aws iam list-attached-user-policies --user-name globant-de-challenge-deployer
```

Expected: only `globant-de-challenge-runtime` remains attached.

---

## 9. Cost Management: Stop/Start Discipline

RDS free tier does not apply to accounts older than 12 months — instance
hours and the public IPv4 address bill from hour one (~$17.65/month if left
running 24/7). Stop the instance at the end of every work session:

```bash
aws rds stop-db-instance --db-instance-identifier globant-de-challenge-db
```

Start it at the beginning of the next session (allow 3-5 minutes):

```bash
aws rds start-db-instance --db-instance-identifier globant-de-challenge-db
```

Notes:
- A stopped instance still bills provisioned storage (~$2.30/month for 20GB gp2).
- AWS automatically restarts stopped RDS instances after 7 consecutive days.
- The public IP may map to a changed client-side IP between sessions —
  if connectivity fails after a start, verify both instance status and the
  Security Group ingress rule against your current public IP.

---

## Known Issues Encountered

| Issue | Root Cause | Resolution | Reference |
|---|---|---|---|
| `CreateDBSubnetGroup` failed with "Missing necessary credentials" | `AWSServiceRoleForRDS` Service-Linked Role did not exist at account level | Created manually with admin credentials (Section 3) | `risk-register.md` R-021 |
| `DescribeDBEngineVersions` returned `AccessDenied` | Bootstrap policy did not include this read-only action | Added `rds:DescribeDBEngineVersions` to Bootstrap policy | `risk-register.md` R-022 |
| `CreateDBInstance` rejected password as "shorter than 8 characters" | Unquoted password with special characters was interpreted by bash before reaching AWS | Loaded password from `.env` via `source .env` and passed as quoted `"$VAR"` | This document, Section 6 |
| RDS billed from hour one despite free-tier planning | RDS 12-month free tier does not apply to accounts older than 12 months; public IPv4 also bills independently | Adopted stop-when-idle discipline (Section 9); Zero Spend Budget detected the deviation within hours | `risk-register.md` R-001, Lessons Learned 2026-07-11 |