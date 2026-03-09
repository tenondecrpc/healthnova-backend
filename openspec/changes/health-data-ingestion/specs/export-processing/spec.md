## ADDED Requirements

### Requirement: Trigger processing workflow on upload
The system SHALL automatically start a Step Functions Standard Workflow execution when an export ZIP is uploaded to the `exports/` S3 prefix.

#### Scenario: ZIP uploaded triggers workflow
- **WHEN** a `.zip` file is uploaded to `exports/{user_id}/`
- **THEN** a Step Functions execution is started within 10 seconds with the S3 key as input

#### Scenario: Non-ZIP upload does not trigger workflow
- **WHEN** a non-ZIP file is uploaded to the exports bucket
- **THEN** no Step Functions execution is started

### Requirement: Validate export file before processing
The system SHALL validate the uploaded ZIP file structure before dispatching to any parsing step.

#### Scenario: Valid export ZIP proceeds to parsing
- **WHEN** the validation step receives a ZIP containing `exportar.xml`
- **THEN** the workflow proceeds to the manifest extraction step

#### Scenario: Invalid or empty ZIP fails gracefully
- **WHEN** the validation step receives a malformed or empty ZIP
- **THEN** the workflow transitions to a failure state and logs the error (without PHI)

#### Scenario: ZIP exceeds maximum allowed size
- **WHEN** the uploaded file exceeds 2GB
- **THEN** the validation step fails and records the rejection reason in DynamoDB job status

### Requirement: Parse health records from exportar.xml using Glue
The system SHALL process `exportar.xml` using an AWS Glue Python Shell job that stream-reads the XML from S3 and writes normalized health records to DynamoDB.

#### Scenario: Successful XML parsing
- **WHEN** the Glue job receives the S3 key for a valid export ZIP
- **THEN** it streams the XML, extracts all health record entries, and batch-writes them to DynamoDB with keys `PK=USER#{user_id}` and `SK=RECORD#{type}#{timestamp}`

#### Scenario: XML parsing completes without memory errors
- **WHEN** the Glue job processes an `exportar.xml` file larger than 500MB
- **THEN** it completes without out-of-memory errors by using iterparse streaming

#### Scenario: Partial write failure is retried
- **WHEN** a DynamoDB batch write fails due to throttling
- **THEN** the Glue job retries unprocessed items with exponential backoff

### Requirement: Parse ECG data from CSV files
The system SHALL parse electrocardiogram CSV files from the export and store structured ECG records in DynamoDB.

#### Scenario: ECG CSVs are processed in parallel
- **WHEN** the workflow reaches the parallel branch step
- **THEN** a Lambda function reads all files in `electrocardiograms/` and writes ECG records to DynamoDB

#### Scenario: No ECG files present
- **WHEN** the export ZIP contains no ECG CSV files
- **THEN** the ECG Lambda step succeeds without writing any records

### Requirement: Parse workout routes from GPX files
The system SHALL parse GPX workout route files and store structured route records in DynamoDB.

#### Scenario: GPX files are processed in parallel
- **WHEN** the workflow reaches the parallel branch step
- **THEN** a Lambda function reads all files in `workout-routes/` and writes route records to DynamoDB

#### Scenario: No GPX files present
- **WHEN** the export ZIP contains no GPX files
- **THEN** the GPX Lambda step succeeds without writing any records

### Requirement: Record processing job status
The system SHALL maintain a job status record in DynamoDB for each upload, updated at each workflow step.

#### Scenario: Job status progresses through states
- **WHEN** a workflow execution runs
- **THEN** the job status transitions through: `PENDING → VALIDATING → PROCESSING → COMPLETED`

#### Scenario: Job failure is recorded
- **WHEN** any workflow step fails after exhausting retries
- **THEN** the job status is set to `FAILED` with the failed step name logged (no PHI)

### Requirement: No PHI in logs or execution history
The system SHALL never log health record field values, user names, or other personally identifiable or protected health information.

#### Scenario: Logs contain only metadata
- **WHEN** any Lambda or Glue job writes to CloudWatch
- **THEN** log entries contain only record counts, durations, step names, and error codes — never record field values
