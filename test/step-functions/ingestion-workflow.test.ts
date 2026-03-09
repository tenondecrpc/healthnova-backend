import { getTemplate, getResources } from '../helpers/setup';

describe('Step Functions Ingestion Workflow', () => {
  test('state machine definition contains ParseInput state for userId extraction', () => {
    const resources = getResources();
    const smKey = Object.keys(resources).find(
      k => resources[k].Type === 'AWS::StepFunctions::StateMachine',
    );
    expect(smKey).toBeDefined();
    const definition = JSON.stringify(resources[smKey!].Properties);
    expect(definition).toContain('ParseInput');
    expect(definition).toContain('States.StringSplit');
    expect(definition).toContain('States.ArrayGetItem');
  });

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
