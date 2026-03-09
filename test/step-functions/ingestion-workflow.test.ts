import { getTemplate } from '../helpers/setup';

describe('Step Functions Ingestion Workflow', () => {
  test('creates ingestion state machine', () => {
    getTemplate().hasResourceProperties('AWS::StepFunctions::StateMachine', {
      StateMachineName: 'healthnova-dev-health-ingestion',
      StateMachineType: 'STANDARD',
    });
  });

  test('creates EventBridge rule for S3 upload events', () => {
    getTemplate().hasResourceProperties('AWS::Events::Rule', {
      Name: 'healthnova-dev-export-upload',
      EventPattern: {
        source: ['aws.s3'],
        'detail-type': ['Object Created'],
      },
    });
  });

  test('creates CloudWatch alarm for long-running executions', () => {
    getTemplate().hasResourceProperties('AWS::CloudWatch::Alarm', {
      AlarmName: 'healthnova-dev-ingestion-long-execution',
    });
  });
});
