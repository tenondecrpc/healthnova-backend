## ADDED Requirements

### Requirement: ZIP validation reads only the central directory via byte-range requests
The `validate-file` and `extract-manifest` Lambda functions SHALL use S3 byte-range GET requests to read the ZIP central directory, rather than loading the full file body into memory.

#### Scenario: validate-file processes a 1 GB export without OOM
- **WHEN** a valid 1 GB Apple Health export ZIP is uploaded
- **THEN** the `validate-file` Lambda completes successfully without exceeding its 512 MB memory allocation

#### Scenario: extract-manifest processes a 500 MB export without OOM
- **WHEN** a valid 500 MB Apple Health export ZIP is uploaded
- **THEN** the `extract-manifest` Lambda completes successfully and returns the correct file manifest without exceeding its 512 MB memory allocation

#### Scenario: byte-range read correctly identifies exportar.xml
- **WHEN** `validate-file` reads the ZIP central directory of any Apple Health export
- **THEN** it correctly identifies the presence or absence of `exportar.xml` / `export.xml`

#### Scenario: invalid ZIP is still detected via byte-range read
- **WHEN** an uploaded file is not a valid ZIP archive
- **THEN** `validate-file` raises a validation error without loading the full file

#### Scenario: file size limit is enforced before byte-range read
- **WHEN** the uploaded file exceeds 2 GB (checked via head_object)
- **THEN** the validation step fails immediately without issuing any byte-range GET request

### Requirement: Memory usage during ZIP validation is bounded regardless of file size
Neither `validate-file` nor `extract-manifest` SHALL load more than 256 KB of an S3 object body into Lambda memory at any time during ZIP processing.

#### Scenario: Large export does not exhaust Lambda memory
- **WHEN** a 2 GB export is validated
- **THEN** peak Lambda memory usage remains below 256 MB (well within the 512 MB limit)
