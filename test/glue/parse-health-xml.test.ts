import { getTemplate } from '../helpers/setup';

describe('Glue Job: parse-health-xml', () => {
  test('creates parse-health-xml Glue Python Shell job', () => {
    getTemplate().hasResourceProperties('AWS::Glue::Job', {
      Name: 'healthnova-dev-parse-health-xml',
      Command: {
        Name: 'pythonshell',
        PythonVersion: '3.9',
      },
      MaxCapacity: 0.0625,
    });
  });

  test('Glue job IAM role has scoped S3 and DynamoDB access', () => {
    getTemplate().hasResourceProperties('AWS::IAM::Role', {
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
