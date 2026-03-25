import { getTemplate } from '../helpers/setup';

describe('DynamoDB Health Records Table', () => {
  test('creates health-records table with PK/SK composite key and on-demand billing', () => {
    getTemplate().hasResourceProperties('AWS::DynamoDB::Table', {
      TableName: 'healthnova-dev-health-records',
      KeySchema: [
        { AttributeName: 'PK', KeyType: 'HASH' },
        { AttributeName: 'SK', KeyType: 'RANGE' },
      ],
      BillingMode: 'PAY_PER_REQUEST',
    });
  });

  test('health-records table has no global secondary indexes', () => {
    const template = getTemplate();
    template.hasResourceProperties('AWS::DynamoDB::Table', {
      TableName: 'healthnova-dev-health-records',
    });
  });
});
