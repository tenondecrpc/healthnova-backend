This is an AWS CDK infrastructure project for processing Apple Health data (HIPAA-sensitive).

Focus on:

## IAM & Access Control
- IAM policies that violate least privilege (wildcard actions or resources on sensitive services)
- Overly permissive OIDC trust conditions (missing repo/branch constraints)
- Lambda execution roles with write access to services they should only read
- API Gateway endpoints missing authentication or authorization

## Data Protection (HIPAA)
- S3 buckets or DynamoDB tables missing encryption at rest (SSE)
- Missing server-side encryption on S3 uploads
- Presigned URL TTLs exceeding 1 hour
- DynamoDB access patterns that could expose PHI/PII without audit trail
- CloudWatch logs that could capture health data or PII
- Missing CloudTrail for data access events on health records

## Secrets & Credentials
- Hardcoded AWS account IDs, credentials, API keys, or secrets in code
- Secrets passed as environment variables instead of Secrets Manager / Parameter Store
- CDK constructs exposing sensitive values as plaintext CfnOutputs

## Prompt Injection
- User-controlled or external data passed directly into AI/LLM prompts without sanitization (look for f-strings, template literals, or string concatenation where untrusted input meets a prompt)
- Lambda functions calling Bedrock, SageMaker, or any LLM API where the input includes health record fields without escaping
- Missing validation of content before it is embedded in structured prompts (XML/JSON injection into prompts)
- YAML or JSON configs that construct prompts dynamically from untrusted sources
- Any pattern where `event`, `request.body`, DynamoDB item fields, or S3 object content feeds directly into a prompt string

## Supply Chain
- CDK dependencies pinned to overly wide version ranges
- Lambda layers referencing external URLs or unpinned package versions
- GitHub Actions steps using mutable tags (e.g., `@main`, `@master`) instead of pinned SHA commits

## Configuration Security
- S3 buckets with public access enabled
- Missing VPC endpoints for services handling PHI
- CDK RemovalPolicy.DESTROY on prod resources containing health data

Deprioritize:
- Style issues or code formatting
- Missing comments or documentation
- TypeScript strict mode warnings unrelated to security
- Test files (unless they embed real credentials or PHI)
