import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { ParamsConfig, EnvironmentConfig } from './shared/util/env-config';
import { DynamoFactory } from './dynamo';
import { LayerFactory } from './layer';
import { LambdaFactory } from './lambda';
import { CognitoFactory } from './cognito';
import { RestApiFactory } from './rest-api';
import { S3Factory } from './s3';
import { SetupFactory } from './setup';

interface MainStackProps extends cdk.StackProps {
  env: EnvironmentConfig;
  params: ParamsConfig;
}

export class MainStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: MainStackProps) {
    super(scope, id, props);

    const { params } = props;
    const { envName, projectName } = params;

    const s3Factory = new S3Factory(this, 'S3Factory', {
      params,
    });
    const dynamoFactory = new DynamoFactory(this, 'DynamoFactory', {
      params,
    });
    const layerFactory = new LayerFactory(this, 'LayerFactory', {
      params,
    });
    const lambdaFactory = new LambdaFactory(this, 'LambdaFactory', {
      params,
      dynamoFactory,
      s3Factory,
      layerFactory,
    });
    const cognitoFactory = new CognitoFactory(this, 'CognitoFactory', {
      params,
      lambdaFactory,
    });
    const restApiFactory = new RestApiFactory(this, 'RestApiFactory', {
      params,
      cognitoFactory,
      lambdaFactory
    });
    const setupFactory = new SetupFactory(this, 'SetupFactory', {
      lambdaFactory,
      cognitoFactory,
    });

    cdk.Tags.of(this).add('Project', projectName);
    cdk.Tags.of(this).add('Environment', envName);
  }
}
