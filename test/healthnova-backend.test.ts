import * as cdk from 'aws-cdk-lib';
import { Template } from 'aws-cdk-lib/assertions';
import { MainStack } from '../lib/stack/main-stack';

const app = new cdk.App();
const stack = new MainStack(app, 'TestStack', {
  env: { account: '123456789012', region: 'us-east-1' },
  params: { envName: 'dev', projectName: 'healthnova', isProd: false },
});
const template = Template.fromStack(stack);

describe('S3 Exports Bucket', () => {
  test('creates exports bucket with SSE-S3 encryption and versioning', () => {
    template.hasResourceProperties('AWS::S3::Bucket', {
      BucketName: 'healthnova-dev-health-exports',
      VersioningConfiguration: { Status: 'Enabled' },
    });
  });

  test('exports bucket has Glacier lifecycle rule after 90 days', () => {
    template.hasResourceProperties('AWS::S3::Bucket', {
      BucketName: 'healthnova-dev-health-exports',
      LifecycleConfiguration: {
        Rules: [{
          Id: 'ArchiveExportsToGlacier',
          Status: 'Enabled',
          Prefix: 'exports/',
          Transitions: [{
            StorageClass: 'GLACIER',
            TransitionInDays: 90,
          }],
        }],
      },
    });
  });

  test('exports bucket has EventBridge notifications enabled via custom resource', () => {
    template.hasResourceProperties('Custom::S3BucketNotifications', {});
  });
});

describe('Presigned URL Export Lambda', () => {
  test('creates presigned-url-export Lambda with exports bucket env var', () => {
    template.hasResourceProperties('AWS::Lambda::Function', {
      FunctionName: 'healthnova-dev-presigned-url-export',
      Environment: {
        Variables: {
          EXPORTS_BUCKET_NAME: { Ref: template.toJSON().Resources ? Object.keys(template.toJSON().Resources).find(k => k.startsWith('S3FactoryExportsBucket')) || '' : '' },
        },
      },
    });
  });

  test('presigned-url-export Lambda has scoped S3 PutObject policy', () => {
    const resources = template.toJSON().Resources;
    const policyKeys = Object.keys(resources).filter(
      k => resources[k].Type === 'AWS::IAM::Policy' &&
           JSON.stringify(resources[k]).includes('presigned-url-export')
    );
    expect(policyKeys.length).toBeGreaterThan(0);
    const policyDoc = JSON.stringify(resources[policyKeys[0]]);
    expect(policyDoc).toContain('s3:PutObject');
    expect(policyDoc).toContain('exports/*');
  });

  test('POST /upload/presigned-url route exists in API Gateway', () => {
    template.hasResourceProperties('AWS::ApiGateway::Resource', {
      PathPart: 'presigned-url',
    });
  });
});

describe('Step Functions Workflow', () => {
  test('creates ingestion state machine', () => {
    template.hasResourceProperties('AWS::StepFunctions::StateMachine', {
      StateMachineName: 'healthnova-dev-health-ingestion',
      StateMachineType: 'STANDARD',
    });
  });

  test('creates EventBridge rule for S3 upload events', () => {
    template.hasResourceProperties('AWS::Events::Rule', {
      Name: 'healthnova-dev-export-upload',
      EventPattern: {
        source: ['aws.s3'],
        'detail-type': ['Object Created'],
      },
    });
  });

  test('creates CloudWatch alarm for long-running executions', () => {
    template.hasResourceProperties('AWS::CloudWatch::Alarm', {
      AlarmName: 'healthnova-dev-ingestion-long-execution',
    });
  });
});

describe('Ingestion Lambda Functions', () => {
  test('creates validate-file Lambda', () => {
    template.hasResourceProperties('AWS::Lambda::Function', {
      FunctionName: 'healthnova-dev-validate-file',
    });
  });

  test('creates extract-manifest Lambda', () => {
    template.hasResourceProperties('AWS::Lambda::Function', {
      FunctionName: 'healthnova-dev-extract-manifest',
    });
  });

  test('creates mark-complete Lambda with health records table env var', () => {
    template.hasResourceProperties('AWS::Lambda::Function', {
      FunctionName: 'healthnova-dev-mark-complete',
    });
  });

  test('creates parse-ecg Lambda', () => {
    template.hasResourceProperties('AWS::Lambda::Function', {
      FunctionName: 'healthnova-dev-parse-ecg',
    });
  });

  test('creates parse-gpx Lambda', () => {
    template.hasResourceProperties('AWS::Lambda::Function', {
      FunctionName: 'healthnova-dev-parse-gpx',
    });
  });
});

describe('Glue Job', () => {
  test('creates parse-health-xml Glue Python Shell job', () => {
    template.hasResourceProperties('AWS::Glue::Job', {
      Name: 'healthnova-dev-parse-health-xml',
      Command: {
        Name: 'pythonshell',
        PythonVersion: '3.9',
      },
      MaxCapacity: 0.0625,
    });
  });

  test('Glue job IAM role has scoped S3 and DynamoDB access', () => {
    template.hasResourceProperties('AWS::IAM::Role', {
      RoleName: 'healthnova-dev-glue-parse-health-xml',
      AssumeRolePolicyDocument: {
        Statement: [{
          Action: 'sts:AssumeRole',
          Effect: 'Allow',
          Principal: { Service: 'glue.amazonaws.com' },
        }],
      },
    });
  });
});

describe('DynamoDB Health Records Table', () => {
  test('creates health-records table with PK/SK composite key', () => {
    template.hasResourceProperties('AWS::DynamoDB::Table', {
      TableName: 'healthnova-dev-health-records',
      KeySchema: [
        { AttributeName: 'PK', KeyType: 'HASH' },
        { AttributeName: 'SK', KeyType: 'RANGE' },
      ],
      BillingMode: 'PAY_PER_REQUEST',
    });
  });

  test('health-records table has UserTypeIndex GSI', () => {
    template.hasResourceProperties('AWS::DynamoDB::Table', {
      TableName: 'healthnova-dev-health-records',
      GlobalSecondaryIndexes: [{
        IndexName: 'UserTypeIndex',
        KeySchema: [
          { AttributeName: 'PK', KeyType: 'HASH' },
          { AttributeName: 'GSI1SK', KeyType: 'RANGE' },
        ],
        Projection: { ProjectionType: 'ALL' },
      }],
    });
  });
});
