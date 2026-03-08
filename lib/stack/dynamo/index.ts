
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
  }
}
