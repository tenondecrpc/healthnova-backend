import { getTemplate } from '../helpers/setup';

describe('Glue Job: parse-health-xml', () => {
  test('creates parse-health-xml Glue ETL job with G.1X workers', () => {
    getTemplate().hasResourceProperties('AWS::Glue::Job', {
      Name: 'healthnova-dev-parse-health-xml',
      Command: {
        Name: 'glueetl',
      },
      WorkerType: 'G.1X',
      NumberOfWorkers: 2,
    });
  });

  test('Glue job timeout is 30 minutes', () => {
    getTemplate().hasResourceProperties('AWS::Glue::Job', {
      Name: 'healthnova-dev-parse-health-xml',
      Timeout: 30,
    });
  });

  test('Glue job disables continuous CloudWatch logging', () => {
    getTemplate().hasResourceProperties('AWS::Glue::Job', {
      Name: 'healthnova-dev-parse-health-xml',
      DefaultArguments: {
        '--enable-continuous-cloudwatch-log': 'false',
      },
    });
  });

  test('Glue job IAM role has scoped S3 and DynamoDB access', () => {
    getTemplate().hasResourceProperties('AWS::IAM::Role', {
      RoleName: 'healthnova-dev-parse-health-xml-role',
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
