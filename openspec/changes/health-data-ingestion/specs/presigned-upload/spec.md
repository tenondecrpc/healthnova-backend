## ADDED Requirements

### Requirement: Generate presigned upload URL
The system SHALL expose a `POST /upload/presigned-url` endpoint that returns a time-limited S3 presigned URL scoped to the authenticated user's folder.

#### Scenario: Authenticated user requests upload URL
- **WHEN** an authenticated user sends `POST /upload/presigned-url`
- **THEN** the system returns a presigned S3 PUT URL valid for 1 hour, scoped to `exports/{user_id}/{timestamp}.zip`

#### Scenario: Unauthenticated request is rejected
- **WHEN** a request is made without a valid Cognito JWT
- **THEN** the system returns HTTP 401

#### Scenario: Presigned URL expires
- **WHEN** the user attempts to upload using a presigned URL older than 1 hour
- **THEN** S3 rejects the upload with HTTP 403

### Requirement: Enforce user-scoped S3 prefix
The presigned URL SHALL be restricted to the `exports/{user_id}/` S3 prefix via IAM condition key `s3:prefix`, preventing cross-user access.

#### Scenario: Upload to correct user prefix succeeds
- **WHEN** the user uploads a file using the presigned URL
- **THEN** the file is stored at `exports/{user_id}/{timestamp}.zip`

#### Scenario: Upload to different user prefix is rejected
- **WHEN** a presigned URL for user A is used to attempt an upload to user B's prefix
- **THEN** S3 rejects the request with HTTP 403
