
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import { Construct } from 'constructs';
import { DynamoConstruct } from '../../construct/dynamo-construct';
import { ParamsConfig } from '../shared/util/env-config';

export interface DynamoFactoryProps {
  params: ParamsConfig;
}

/**
 * Centralized factory for creating all DynamoDB tables in the application
 */
export class DynamoFactory extends Construct {
  public readonly userTable: DynamoConstruct;
  public readonly processTable: DynamoConstruct;
  public readonly healthRecordsTable: DynamoConstruct;

  constructor(scope: Construct, id: string, props: DynamoFactoryProps) {
    super(scope, id);

    const { params } = props;
    const { envName, projectName } = params;

    this.userTable = new DynamoConstruct(this, 'UserTable', {
      params,
      tableConfig: {
        tableName: `${projectName}-${envName}-user`,
        partitionKey: {
          name: 'id',
          type: dynamodb.AttributeType.STRING,
        },
        billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      },
    });

    this.processTable = new DynamoConstruct(this, 'ProcessTable', {
      params,
      tableConfig: {
        tableName: `${projectName}-${envName}-process`,
        partitionKey: {
          name: 'id',
          type: dynamodb.AttributeType.STRING,
        },
        sortKey: {
          name: 'createdAt',
          type: dynamodb.AttributeType.STRING,
        },
        billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      },
    });

    this.healthRecordsTable = new DynamoConstruct(this, 'HealthRecordsTable', {
      params,
      tableConfig: {
        tableName: `${projectName}-${envName}-health-records`,
        partitionKey: {
          name: 'PK',
          type: dynamodb.AttributeType.STRING,
        },
        sortKey: {
          name: 'SK',
          type: dynamodb.AttributeType.STRING,
        },
        billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
        globalSecondaryIndexes: [{
          indexName: 'UserTypeIndex',
          partitionKey: {
            name: 'PK',
            type: dynamodb.AttributeType.STRING,
          },
          sortKey: {
            name: 'GSI1SK',
            type: dynamodb.AttributeType.STRING,
          },
          projectionType: dynamodb.ProjectionType.ALL,
        }],
      },
    });
  }
}
