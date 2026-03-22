## ADDED Requirements

### Requirement: Lambda IAM policies are scoped to specific resources
Each Lambda function SHALL have IAM policies that grant only the minimum actions on the specific AWS resource ARNs it requires. No shared wildcard policy (`s3:*` on `*` or `dynamodb:*` on `*`) SHALL be used in any Lambda execution role.

#### Scenario: post-confirmation-signup Lambda has scoped DynamoDB write policy
- **WHEN** the CDK stack is synthesized
- **THEN** the `post-confirmation-signup` Lambda execution role SHALL have only `dynamodb:PutItem` on the user table ARN — no wildcard actions or wildcard resource ARNs

#### Scenario: process Lambda has scoped DynamoDB access policy
- **WHEN** the CDK stack is synthesized
- **THEN** the `process` Lambda execution role SHALL have only the DynamoDB actions it requires on the process table ARN — no wildcard actions or wildcard resource ARNs

#### Scenario: shared wildcard policy constructs are removed
- **WHEN** the CDK stack is synthesized
- **THEN** no `AWS::IAM::Policy` resource SHALL contain `"Action": "s3:*"` or `"Action": "dynamodb:*"` with `"Resource": "*"`

### Requirement: Ingestion Lambda IAM policies remain scoped (regression check)
The ingestion Lambdas introduced in `health-data-ingestion` already use scoped policies. They SHALL continue to use only the actions and resource ARNs defined in that change.

#### Scenario: Ingestion Lambda policies are not widened
- **WHEN** the CDK stack is synthesized
- **THEN** `validate-file`, `extract-manifest`, `mark-complete`, `parse-ecg`, and `parse-gpx` Lambda roles SHALL each have policies limited to the exports bucket and/or health-records table with specific action sets — no wildcard actions
