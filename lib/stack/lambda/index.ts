import { Construct } from "constructs";
import { Duration, RemovalPolicy } from "aws-cdk-lib";
import { LambdaConstruct } from "../../construct/lambda-construct";
import { Code, LayerVersion } from "aws-cdk-lib/aws-lambda";
import { RetentionDays } from "aws-cdk-lib/aws-logs";
import { ParamsConfig } from "../shared/util/env-config";
import { DynamoFactory } from "../dynamo";
import { PYTHON_RUNTIME } from "../shared/util/runtime";
import { dynamoPolicy, s3Policy } from "../shared/policy";
import { S3Factory } from "../s3";
import { LayerFactory } from "../layer";

export interface LambdaFactoryProps {
  params: ParamsConfig;
  dynamoFactory: DynamoFactory;
  s3Factory: S3Factory;
  layerFactory: LayerFactory;
}

/**
 * Centralized factory for creating all Lambda functions in the application
 */
export class LambdaFactory extends Construct {
  public readonly postConfirmationSignupLambda: LambdaConstruct;
  public readonly preSignupLambda: LambdaConstruct;
  public readonly processLambda: LambdaConstruct;
  public readonly presignedUrlUploadLambda: LambdaConstruct;
  public readonly notFoundLambda: LambdaConstruct;
  public readonly authorizerLambda: LambdaConstruct;

  constructor(scope: Construct, id: string, props: LambdaFactoryProps) {
    super(scope, id);

    const { params, dynamoFactory, s3Factory, layerFactory } = props;
    const { envName, projectName } = params;
    const isProd = envName === 'prod';
    const logRemovalPolicy = isProd ? RemovalPolicy.RETAIN : RemovalPolicy.DESTROY;

    this.postConfirmationSignupLambda = new LambdaConstruct(this, 'PostConfirmationSignupLambda', {
      functionName: `${projectName}-${envName}-post-confirmation-signup`,
      description: 'Handles post-confirmation signup actions',
      code: Code.fromAsset('src/lambda/user/post-confirmation-signup'),
      handler: 'index.handler',
      runtime: PYTHON_RUNTIME,
      layers: [],
      environment: {
        USER_TABLE_NAME: dynamoFactory.userTable.table.tableName,
      },
      additionalPolicies: [dynamoPolicy],
      logging: {
        logRetention: RetentionDays.ONE_MONTH,
        removalPolicy: logRemovalPolicy,
      },
    });

    this.preSignupLambda = new LambdaConstruct(this, 'PreSignupLambda', {
      functionName: `${projectName}-${envName}-pre-signup`,
      description: 'Handles pre-signup validation',
      code: Code.fromAsset('src/lambda/user/pre-signup'),
      handler: 'index.handler',
      runtime: PYTHON_RUNTIME,
      layers: [],
      logging: {
        logRetention: RetentionDays.ONE_MONTH,
        removalPolicy: logRemovalPolicy,
      },
    });

    this.processLambda = new LambdaConstruct(this, 'ProcessLambda', {
      functionName: `${projectName}-${envName}-process`,
      description: 'Executes a main process',
      code: Code.fromAsset('src/lambda/core/process'),
      handler: 'index.handler',
      runtime: PYTHON_RUNTIME,
      layers: [layerFactory.pythonCommonLayer.layer],
      timeout: Duration.seconds(30),
      memorySize: 256,
      environment: {
        PROCESS_TABLE_NAME: dynamoFactory.processTable.table.tableName,
      },
      additionalPolicies: [dynamoPolicy],
      logging: {
        logRetention: RetentionDays.ONE_MONTH,
        removalPolicy: logRemovalPolicy,
      },
    });

    this.presignedUrlUploadLambda = new LambdaConstruct(this, 'PresignedUrlUploadLambda', {
      functionName: `${projectName}-${envName}-presigned-url-upload`,
      description: 'Generates a presigned URL for file upload',
      code: Code.fromAsset('src/lambda/core/presigned-url-upload'),
      handler: 'index.handler',
      runtime: PYTHON_RUNTIME,
      layers: [layerFactory.pythonCommonLayer.layer],
      environment: {
        PHOTOS_BUCKET_NAME: s3Factory.photosBucket.bucket.bucketName,
      },
      additionalPolicies: [s3Policy],
      logging: {
        logRetention: RetentionDays.ONE_MONTH,
        removalPolicy: logRemovalPolicy,
      },
    });

    this.notFoundLambda = new LambdaConstruct(this, 'NotFoundLambda', {
      functionName: `${projectName}-${envName}-not-found`,
      description: 'Handles 404 Not Found responses',
      code: Code.fromAsset('src/lambda/core/not-found'),
      handler: 'index.handler',
      runtime: PYTHON_RUNTIME,
      layers: [layerFactory.pythonCommonLayer.layer],
      logging: {
        logRetention: RetentionDays.ONE_MONTH,
        removalPolicy: logRemovalPolicy,
      },
    });

    // Lambda Authorizer for API Gateway
    // Using Klayers for PyJWT and cryptography dependencies
    const pyJwtLayer = LayerVersion.fromLayerVersionArn(this, 'PyJWTLayer', 'arn:aws:lambda:us-east-1:770693421928:layer:Klayers-p312-PyJWT:1');
    const cryptographyLayer = LayerVersion.fromLayerVersionArn(this, 'CryptographyLayer', 'arn:aws:lambda:us-east-1:770693421928:layer:Klayers-p312-cryptography:18');
    this.authorizerLambda = new LambdaConstruct(this, 'AuthorizerLambda', {
      functionName: `${projectName}-${envName}-authorizer`,
      description: 'Custom Lambda authorizer for API Gateway - validates Cognito JWT tokens',
      code: Code.fromAsset('src/lambda/core/authorizer'),
      handler: 'index.lambda_handler',
      runtime: PYTHON_RUNTIME,
      layers: [pyJwtLayer, cryptographyLayer],
      timeout: Duration.seconds(10),
      memorySize: 256,
      environment: {
        USER_POOL_ID: 'UNDEFINED_BY_DEFAULT',
        APP_CLIENT_ID: 'UNDEFINED_BY_DEFAULT',
      },
      logging: {
        logRetention: RetentionDays.ONE_MONTH,
        removalPolicy: logRemovalPolicy,
      },
    });
  }
}