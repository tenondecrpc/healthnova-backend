# HealthNova Backend

## Core Rules

- **Comments**: Only add code comments when explicitly requested. All comments must be written in English.
- **Output Constraints**: When using bash commands, always limit output: `grep` add `| head -20`, `find` add `-maxdepth 2`, `ls` add `| head -30`. Never display more than 30 lines of command output.
- **Verification Loops**: ALWAYS run local verification commands (`npx cdk synth --quiet`, `npm run lint`, or `npm test`) to validate your code BEFORE marking a task as complete or proposing a solution. Never assume code works just by writing it.

AWS CDK infrastructure for analyzing Apple Health data exports to provide preventive health insights and cardiovascular disease risk assessment.

## Overview

This backend processes Apple Health export.zip files (containing XML health records, ECG data, and workout GPX files) to generate health dashboards and early warning alerts for potential cardiac issues.

## Tech Stack

- **Infrastructure**: AWS CDK (TypeScript)
- **Runtime**: Python 3.x Lambda functions
- **Storage**: DynamoDB, S3
- **Auth**: Cognito User Pools
- **API**: API Gateway REST API

## Project Structure

```
/lib                    # CDK infrastructure definitions
  /construct            # Reusable CDK constructs
  /stack                # Stack definitions by service
    /shared/policy      # IAM policy builders
/src
  /lambda               # Lambda function code (Python)
    /core               # Core processing functions
    /user               # User management functions
  /layer                # Shared Lambda layers
/openspec               # OpenSpec workflow artifacts
```

## Key Components

### Data Processing Flow
1. Frontend requests presigned URL from API (`POST /upload/presigned-url`)
2. Frontend uploads export.zip directly to S3 using presigned URL
3. S3 event triggers processing Lambda
4. XML parser extracts health records (streaming for large files)
5. Data normalized and stored in DynamoDB
6. Analytics Lambda generates health insights
7. Dashboard API serves aggregated metrics

**Note**: Presigned URLs are time-limited (5 min) and scoped to user's folder in S3

### Apple Health Export Structure
- `exportar.xml`: Main health records (heart rate, HRV, sleep, etc.)
- `electrocardiograms/*.csv`: ECG data for AFib detection
- `workout-routes/*.gpx`: GPS data from workouts

## Common Commands

```bash
# Build and deploy
npm run build && npx cdk deploy

# Check changes before deploy
npx cdk diff

# Run tests
npm test

# Synthesize CloudFormation
npx cdk synth
```

## OpenSpec Workflow

This project uses OpenSpec for structured feature development. Use these commands in Claude/Kiro:

```
/opsx:explore [idea]        # Explore ideas and clarify requirements
/opsx:propose [name]        # Create new change with proposal, design, and tasks
/opsx:apply [change]        # Implement tasks from a change
/opsx:security [change]     # Run security review (HIPAA, IAM, encryption)
/opsx:archive [change]      # Archive completed change
```

**Typical workflow:**
1. `/opsx:propose health-data-ingestion` - Generate structured proposal
2. `/clear` - Start a fresh session to save tokens
3. `/opsx:apply health-data-ingestion` - Implement tasks one by one
4. `/clear` - Keep sessions atomic
5. `/opsx:security health-data-ingestion` - Review security before production
6. `/clear` - Keep sessions atomic
7. `/opsx:archive health-data-ingestion` - Archive when complete

*Note*: Keep your sessions atomic. Clear the context history using `/clear` between different tasks or workflow phases to drastically reduce token consumption and maintain focus.

All OpenSpec artifacts live in `/openspec/changes/[change-name]/`

## Development Guidelines

### TypeScript (CDK)
- Use camelCase naming
- Enable strict mode
- Explicit types for all constructs
- Organize by AWS service in /stack
- **Construct-first pattern**: Every AWS service must have a reusable L2 construct in `/lib/construct/` before being used in a factory (`/lib/stack/<service>/`). The factory composes constructs with project-specific config — it should never create raw Cfn resources directly. Pattern: `Construct → Factory → Stack`. THIS IS AN IMMUTABLE RULE.
- **No L1 Constructs (Cfn*)**: Never use raw CloudFormation constructs (`CfnBucket`, `CfnFunction`) if an L2 construct exists (`Bucket`, `Function`). 
- **Dependency Management**: Remember that changes to constructs might require updating references in multiple stacks.

### Python (Lambda Functions)
- Use snake_case naming
- Add type hints and docstrings
- Keep functions under 15MB (use layers for dependencies)
- No PII in logs
- **Layer Usage**: For Python Lambda functions, always package heavy dependencies (like `pandas`, `numpy`, or large SDKs) in Lambda Layers, not directly in the function deployment package, to avoid hitting the 15MB deployment limit and to speed up deployments.
- **Streaming over Memory**: When handling Apple Health XML files or other large payloads, always use streaming parsers (like `xml.etree.ElementTree.iterparse`). Do NOT read the entire file into memory using `.read()`.
- **Environment Variables**: Always retrieve configuration via environment variables, and ensure the CDK stack provisions them correctly.

### Security
- Encrypt all data at rest and in transit
- Use least privilege IAM policies. Never use `*` in Actions unless absolutely necessary and scoped to specific resources.
- Time-limited presigned URLs (1 hour max)
- No hardcoded credentials
- HIPAA-aware logging (no PHI)

### Performance
- XML streaming parser for 500MB+ files
- DynamoDB batch writes
- S3 lifecycle policies (archive after 90 days)
- Lambda memory tuning based on file size

## Testing Standards

- **Shared Setup**: ALWAYS use the setup helper to get the CDK template `import { getTemplate } from '../helpers/setup';` to avoid instantiating the stack multiple times.
- **Files**: `test/[domain]/[resource].test.ts`
- **Important Rules**: 
  1. Organize by AWS domain (S3, Lambda, DynamoDB, Step Functions).
  2. One file per main resource. Do not mix tests for different resources.
  3. Descriptive tests explaining what specific behavior is being verified.
- **What to test**: Resource configuration (properties, environment variables), and IAM Policies.
- **Do NOT include**: Lambda business logic tests (these go in Python unit tests), E2E tests, or tests that require actual AWS deployment.

## Environment Variables

Set in `.env` (see `.env.example`):
- `AWS_ACCOUNT_ID`: Target AWS account
- `AWS_REGION`: Deployment region
- `STAGE`: dev/staging/prod

## Health Metrics Tracked

- Heart rate & variability (HRV)
- Blood pressure
- Oxygen saturation (SpO2)
- ECG/EKG data
- Sleep analysis
- Activity levels
- Workout performance

## Preventive Health Features

- Atrial fibrillation detection from ECG
- Heart rate anomaly alerts
- HRV trend analysis (stress indicator)
- Sleep quality scoring
- Activity vs. rest balance
- Cardiovascular risk scoring
