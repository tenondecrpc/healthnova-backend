# HealthNova Backend

## Core Rules

- **Comments**: Only add code comments when explicitly requested. All comments must be written in English.

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
2. `/opsx:apply health-data-ingestion` - Implement tasks one by one
3. `/opsx:security health-data-ingestion` - Review security before production
4. `/opsx:archive health-data-ingestion` - Archive when complete

All OpenSpec artifacts live in `/openspec/changes/[change-name]/`

## Development Guidelines

### Python (Lambda Functions)
- Use snake_case naming
- Add type hints and docstrings
- Keep functions under 15MB (use layers for dependencies)
- Stream large files, avoid loading into memory
- No PII in logs

### TypeScript (CDK)
- Use camelCase naming
- Enable strict mode
- Explicit types for all constructs
- Organize by AWS service in /stack

### Security
- Encrypt all data at rest and in transit
- Use least privilege IAM policies
- Time-limited presigned URLs (1 hour max)
- No hardcoded credentials
- HIPAA-aware logging (no PHI)

### Performance
- XML streaming parser for 500MB+ files
- DynamoDB batch writes
- S3 lifecycle policies (archive after 90 days)
- Lambda memory tuning based on file size

## Environment Variables

Set in `.env` (see `.env.example`):
- `AWS_ACCOUNT`: Target AWS account
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
