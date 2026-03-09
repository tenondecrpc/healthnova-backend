import { getTemplate } from '../helpers/setup';

describe('S3 Photos Bucket', () => {
  test('photos bucket blocks all public access', () => {
    getTemplate().hasResourceProperties('AWS::S3::Bucket', {
      BucketName: 'healthnova-dev-photos',
      PublicAccessBlockConfiguration: {
        BlockPublicAcls: true,
        BlockPublicPolicy: true,
        IgnorePublicAcls: true,
        RestrictPublicBuckets: true,
      },
    });
  });

  test('photos bucket has no public read bucket policy', () => {
    const resources = getTemplate().toJSON().Resources;
    const publicPolicies = Object.keys(resources).filter(k => {
      if (resources[k].Type !== 'AWS::S3::BucketPolicy') return false;
      const doc = JSON.stringify(resources[k]);
      return doc.includes('"Principal":"*"') && doc.includes('s3:GetObject') && doc.includes('photos');
    });
    expect(publicPolicies).toHaveLength(0);
  });
});
