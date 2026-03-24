import { getTemplate } from '../helpers/setup';

describe('DynamoDB Health Records Table', () => {
  test('creates health-records table with PK/SK composite key', () => {
    getTemplate().hasResourceProperties('AWS::DynamoDB::Table', {
      TableName: 'healthnova-dev-health-records',
      KeySchema: [
        { AttributeName: 'PK', KeyType: 'HASH' },
        { AttributeName: 'SK', KeyType: 'RANGE' },
      ],
      ProvisionedThroughput: {
        ReadCapacityUnits: 100,
        WriteCapacityUnits: 5,
      },
    });
  });

  test('health-records table has UserTypeIndex GSI', () => {
    getTemplate().hasResourceProperties('AWS::DynamoDB::Table', {
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
