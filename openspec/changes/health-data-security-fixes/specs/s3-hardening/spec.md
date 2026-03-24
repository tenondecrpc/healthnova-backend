## ADDED Requirements

### Requirement: Photos bucket blocks all public access
The photos S3 bucket SHALL have `BlockPublicAccess.BLOCK_ALL` enabled and SHALL NOT have `publicReadAccess: true`. Objects in the photos bucket SHALL only be accessible via presigned URLs or explicit IAM grants.

#### Scenario: Photos bucket has no public bucket policy
- **WHEN** the CDK stack is synthesized
- **THEN** the photos bucket resource SHALL have all four `BlockPublicAccess` properties set to `true`: `BlockPublicAcls`, `IgnorePublicAcls`, `BlockPublicPolicy`, `RestrictPublicBuckets`

#### Scenario: Photos bucket does not grant public read via bucket policy
- **WHEN** the CDK stack is synthesized
- **THEN** no `AWS::S3::BucketPolicy` resource SHALL contain a statement with `"Principal": "*"` and `"Action": "s3:GetObject"` on the photos bucket

#### Scenario: Unauthenticated request to photos bucket is denied
- **WHEN** an unauthenticated HTTP GET is made directly to any photos bucket object URL
- **THEN** S3 returns HTTP 403

### Requirement: Exports bucket CORS SHALL be restricted to PUT method only
The health exports bucket SHALL restrict CORS to `PUT` method. This requirement ensures the constraint is maintained and documents it explicitly.

#### Scenario: Exports bucket CORS only allows PUT
- **WHEN** the CDK stack is synthesized
- **THEN** the exports bucket CORS configuration allows only `PUT` HTTP method — `GET`, `DELETE`, `POST` are not in the allowed methods list
