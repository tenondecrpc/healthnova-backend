import { getResources } from '../helpers/setup';

function getPoliciesForLambda(lambdaSubstring: string): string[] {
  const resources = getResources();
  return Object.keys(resources).filter(
    k =>
      resources[k].Type === 'AWS::IAM::Policy' &&
      JSON.stringify(resources[k]).includes(lambdaSubstring),
  );
}

describe('IAM Scoped Policies — no wildcards', () => {
  test('no IAM policy grants s3:* on *', () => {
    const resources = getResources();
    const wildcardS3 = Object.keys(resources).filter(k => {
      if (resources[k].Type !== 'AWS::IAM::Policy') return false;
      const doc = JSON.stringify(resources[k]);
      return doc.includes('"s3:*"') && doc.includes('"Resource":"*"');
    });
    expect(wildcardS3).toHaveLength(0);
  });

  test('no IAM policy grants dynamodb:* on *', () => {
    const resources = getResources();
    const wildcardDdb = Object.keys(resources).filter(k => {
      if (resources[k].Type !== 'AWS::IAM::Policy') return false;
      const doc = JSON.stringify(resources[k]);
      return doc.includes('"dynamodb:*"') && doc.includes('"Resource":"*"');
    });
    expect(wildcardDdb).toHaveLength(0);
  });

  test('post-confirmation-signup Lambda has scoped dynamodb:PutItem on user table', () => {
    const resources = getResources();
    const keys = getPoliciesForLambda('post-confirmation-signup');
    expect(keys.length).toBeGreaterThan(0);
    const doc = JSON.stringify(resources[keys[0]]);
    expect(doc).toContain('dynamodb:PutItem');
    expect(doc).not.toContain('"dynamodb:*"');
  });


});
