import { getTemplate, getResources } from '../helpers/setup';

describe('Presigned URL Export Lambda', () => {
  test('creates presigned-url-export Lambda with exports bucket env var', () => {
    const resources = getResources();
    const exportsBucketKey = Object.keys(resources).find(k => k.startsWith('S3FactoryExportsBucket')) ?? '';

    getTemplate().hasResourceProperties('AWS::Lambda::Function', {
      FunctionName: 'healthnova-dev-presigned-url-export',
      Environment: {
        Variables: {
          EXPORTS_BUCKET_NAME: { Ref: exportsBucketKey },
        },
      },
    });
  });

  test('presigned-url-export Lambda has scoped S3 PutObject policy', () => {
    const resources = getResources();
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
    getTemplate().hasResourceProperties('AWS::ApiGateway::Resource', {
      PathPart: 'presigned-url',
    });
  });
});
