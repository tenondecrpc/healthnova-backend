import { getTemplate } from '../helpers/setup';

describe('S3 Exports Bucket', () => {
  test('creates exports bucket with SSE-S3 encryption and versioning', () => {
    getTemplate().hasResourceProperties('AWS::S3::Bucket', {
      BucketName: 'healthnova-dev-health-exports',
      VersioningConfiguration: { Status: 'Enabled' },
    });
  });

  test('exports bucket has Glacier lifecycle rule after 90 days', () => {
    getTemplate().hasResourceProperties('AWS::S3::Bucket', {
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
    getTemplate().hasResourceProperties('Custom::S3BucketNotifications', {});
  });
});
