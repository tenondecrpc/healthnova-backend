import { Construct } from "constructs";
import { Duration, RemovalPolicy } from "aws-cdk-lib";
import * as iam from "aws-cdk-lib/aws-iam";
import { LambdaConstruct } from "../../construct/lambda-construct";
import { Code, LayerVersion } from "aws-cdk-lib/aws-lambda";
import { RetentionDays } from "aws-cdk-lib/aws-logs";
import { ParamsConfig } from "../shared/util/env-config";
import { DynamoFactory } from "../dynamo";
import { PYTHON_RUNTIME } from "../shared/util/runtime";
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

  public readonly presignedUrlExportLambda: LambdaConstruct;
  public readonly validateFileLambda: LambdaConstruct;
  public readonly extractManifestLambda: LambdaConstruct;
  public readonly markCompleteLambda: LambdaConstruct;
  public readonly scaleDynamoLambda: LambdaConstruct;
  public readonly parseEcgLambda: LambdaConstruct;
  public readonly parseGpxLambda: LambdaConstruct;
  public readonly notFoundLambda: LambdaConstruct;
  public readonly authorizerLambda: LambdaConstruct;

  // Dashboard Lambdas
  public readonly getDashboardMetricsLambda: LambdaConstruct;
  public readonly getDashboardEcgLambda: LambdaConstruct;
  public readonly getDashboardWorkoutsLambda: LambdaConstruct;
  public readonly getDashboardJobsLambda: LambdaConstruct;
  public readonly getDashboardSummaryLambda: LambdaConstruct;

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
      layers: [layerFactory.pythonCommonLayer.layer],
      environment: {
        USER_TABLE_NAME: dynamoFactory.userTable.table.tableName,
      },
      additionalPolicies: [new iam.PolicyStatement({
        actions: ['dynamodb:PutItem'],
        resources: [dynamoFactory.userTable.tableArn],
      })],
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
      layers: [layerFactory.pythonCommonLayer.layer],
      logging: {
        logRetention: RetentionDays.ONE_MONTH,
        removalPolicy: logRemovalPolicy,
      },
    });

    const exportsBucketPutPolicy = new iam.PolicyStatement({
      actions: ['s3:PutObject'],
      resources: [s3Factory.exportsBucket.arnForObjects('exports/*')],
    });
    this.presignedUrlExportLambda = new LambdaConstruct(this, 'PresignedUrlExportLambda', {
      functionName: `${projectName}-${envName}-presigned-url-export`,
      description: 'Generates a presigned PUT URL for Apple Health export upload',
      code: Code.fromAsset('src/lambda/core/presigned-url-export'),
      handler: 'index.handler',
      runtime: PYTHON_RUNTIME,
      layers: [layerFactory.pythonCommonLayer.layer],
      environment: {
        EXPORTS_BUCKET_NAME: s3Factory.exportsBucket.bucket.bucketName,
        PRESIGNED_URL_EXPIRY_SECONDS: '3600',
      },
      additionalPolicies: [exportsBucketPutPolicy],
      logging: {
        logRetention: RetentionDays.ONE_MONTH,
        removalPolicy: logRemovalPolicy,
      },
    });

    const exportsBucketReadPolicy = new iam.PolicyStatement({
      actions: ['s3:GetObject', 's3:HeadObject'],
      resources: [s3Factory.exportsBucket.arnForObjects('exports/*')],
    });
    const healthRecordsWritePolicy = new iam.PolicyStatement({
      actions: ['dynamodb:PutItem', 'dynamodb:BatchWriteItem'],
      resources: [
        dynamoFactory.healthRecordsTable.tableArn,
        `${dynamoFactory.healthRecordsTable.tableArn}/index/*`,
      ],
    });

    this.validateFileLambda = new LambdaConstruct(this, 'ValidateFileLambda', {
      functionName: `${projectName}-${envName}-validate-file`,
      description: 'Validates uploaded export ZIP integrity and structure',
      code: Code.fromAsset('src/lambda/ingestion/validate-file'),
      handler: 'index.handler',
      runtime: PYTHON_RUNTIME,
      layers: [layerFactory.pythonCommonLayer.layer],
      timeout: Duration.minutes(2),
      memorySize: 512,
      additionalPolicies: [exportsBucketReadPolicy],
      logging: {
        logRetention: RetentionDays.ONE_MONTH,
        removalPolicy: logRemovalPolicy,
      },
    });

    this.extractManifestLambda = new LambdaConstruct(this, 'ExtractManifestLambda', {
      functionName: `${projectName}-${envName}-extract-manifest`,
      description: 'Lists files inside the export ZIP for downstream processing',
      code: Code.fromAsset('src/lambda/ingestion/extract-manifest'),
      handler: 'index.handler',
      runtime: PYTHON_RUNTIME,
      layers: [layerFactory.pythonCommonLayer.layer],
      timeout: Duration.minutes(2),
      memorySize: 512,
      additionalPolicies: [exportsBucketReadPolicy],
      logging: {
        logRetention: RetentionDays.ONE_MONTH,
        removalPolicy: logRemovalPolicy,
      },
    });

    this.markCompleteLambda = new LambdaConstruct(this, 'MarkCompleteLambda', {
      functionName: `${projectName}-${envName}-mark-complete`,
      description: 'Writes final job status to DynamoDB',
      code: Code.fromAsset('src/lambda/ingestion/mark-complete'),
      handler: 'index.handler',
      runtime: PYTHON_RUNTIME,
      layers: [layerFactory.pythonCommonLayer.layer],
      environment: {
        HEALTH_RECORDS_TABLE_NAME: dynamoFactory.healthRecordsTable.table.tableName,
      },
      additionalPolicies: [healthRecordsWritePolicy],
      logging: {
        logRetention: RetentionDays.ONE_MONTH,
        removalPolicy: logRemovalPolicy,
      },
    });

    this.scaleDynamoLambda = new LambdaConstruct(this, 'ScaleDynamoLambda', {
      functionName: `${projectName}-${envName}-scale-dynamo`,
      description: 'Scales DynamoDB health-records table WCU up before ingestion and down after',
      code: Code.fromAsset('src/lambda/ingestion/scale-dynamo'),
      handler: 'index.handler',
      runtime: PYTHON_RUNTIME,
      layers: [layerFactory.pythonCommonLayer.layer],
      timeout: Duration.minutes(6),
      environment: {
        HEALTH_RECORDS_TABLE_NAME: dynamoFactory.healthRecordsTable.table.tableName,
        WCU_HIGH: '7000',
        WCU_LOW: '5',
        RCU: '100',
        GSI_NAME: 'UserTypeIndex',
      },
      additionalPolicies: [new iam.PolicyStatement({
        actions: ['dynamodb:UpdateTable', 'dynamodb:DescribeTable'],
        resources: [dynamoFactory.healthRecordsTable.tableArn],
      })],
      logging: {
        logRetention: RetentionDays.ONE_MONTH,
        removalPolicy: logRemovalPolicy,
      },
    });

    this.parseEcgLambda = new LambdaConstruct(this, 'ParseEcgLambda', {
      functionName: `${projectName}-${envName}-parse-ecg`,
      description: 'Parses ECG CSV files from the export ZIP',
      code: Code.fromAsset('src/lambda/ingestion/parse-ecg'),
      handler: 'index.handler',
      runtime: PYTHON_RUNTIME,
      layers: [layerFactory.pythonCommonLayer.layer],
      timeout: Duration.minutes(5),
      memorySize: 512,
      environment: {
        HEALTH_RECORDS_TABLE_NAME: dynamoFactory.healthRecordsTable.table.tableName,
      },
      additionalPolicies: [exportsBucketReadPolicy, healthRecordsWritePolicy],
      logging: {
        logRetention: RetentionDays.ONE_MONTH,
        removalPolicy: logRemovalPolicy,
      },
    });

    this.parseGpxLambda = new LambdaConstruct(this, 'ParseGpxLambda', {
      functionName: `${projectName}-${envName}-parse-gpx`,
      description: 'Parses GPX workout route files from the export ZIP',
      code: Code.fromAsset('src/lambda/ingestion/parse-gpx'),
      handler: 'index.handler',
      runtime: PYTHON_RUNTIME,
      layers: [layerFactory.pythonCommonLayer.layer],
      timeout: Duration.minutes(5),
      memorySize: 512,
      environment: {
        HEALTH_RECORDS_TABLE_NAME: dynamoFactory.healthRecordsTable.table.tableName,
      },
      additionalPolicies: [exportsBucketReadPolicy, healthRecordsWritePolicy],
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

    // =====================
    // DASHBOARD LAMBDAS
    // =====================
    const healthRecordsReadPolicy = new iam.PolicyStatement({
      actions: ['dynamodb:Query'],
      resources: [
        dynamoFactory.healthRecordsTable.tableArn,
        `${dynamoFactory.healthRecordsTable.tableArn}/index/UserTypeIndex`,
      ],
    });

    this.getDashboardMetricsLambda = new LambdaConstruct(this, 'GetDashboardMetricsLambda', {
      functionName: `${projectName}-${envName}-get-dashboard-metrics`,
      description: 'Queries health metrics with scatter-gather across 10 DynamoDB shards',
      code: Code.fromAsset('src/lambda/dashboard/get-metrics'),
      handler: 'index.handler',
      runtime: PYTHON_RUNTIME,
      layers: [layerFactory.pythonCommonLayer.layer],
      timeout: Duration.seconds(30),
      memorySize: 256,
      environment: {
        HEALTH_RECORDS_TABLE_NAME: dynamoFactory.healthRecordsTable.table.tableName,
      },
      additionalPolicies: [healthRecordsReadPolicy],
      logging: {
        logRetention: RetentionDays.ONE_MONTH,
        removalPolicy: logRemovalPolicy,
      },
    });

    this.getDashboardEcgLambda = new LambdaConstruct(this, 'GetDashboardEcgLambda', {
      functionName: `${projectName}-${envName}-get-dashboard-ecg`,
      description: 'Queries ECG records with cursor-based pagination',
      code: Code.fromAsset('src/lambda/dashboard/get-ecg'),
      handler: 'index.handler',
      runtime: PYTHON_RUNTIME,
      layers: [layerFactory.pythonCommonLayer.layer],
      timeout: Duration.seconds(30),
      memorySize: 256,
      environment: {
        HEALTH_RECORDS_TABLE_NAME: dynamoFactory.healthRecordsTable.table.tableName,
      },
      additionalPolicies: [healthRecordsReadPolicy],
      logging: {
        logRetention: RetentionDays.ONE_MONTH,
        removalPolicy: logRemovalPolicy,
      },
    });

    this.getDashboardWorkoutsLambda = new LambdaConstruct(this, 'GetDashboardWorkoutsLambda', {
      functionName: `${projectName}-${envName}-get-dashboard-workouts`,
      description: 'Queries GPX workout records with cursor-based pagination',
      code: Code.fromAsset('src/lambda/dashboard/get-workouts'),
      handler: 'index.handler',
      runtime: PYTHON_RUNTIME,
      layers: [layerFactory.pythonCommonLayer.layer],
      timeout: Duration.seconds(30),
      memorySize: 256,
      environment: {
        HEALTH_RECORDS_TABLE_NAME: dynamoFactory.healthRecordsTable.table.tableName,
      },
      additionalPolicies: [healthRecordsReadPolicy],
      logging: {
        logRetention: RetentionDays.ONE_MONTH,
        removalPolicy: logRemovalPolicy,
      },
    });

    this.getDashboardJobsLambda = new LambdaConstruct(this, 'GetDashboardJobsLambda', {
      functionName: `${projectName}-${envName}-get-dashboard-jobs`,
      description: 'Lists ingestion job history sorted by most recent',
      code: Code.fromAsset('src/lambda/dashboard/get-jobs'),
      handler: 'index.handler',
      runtime: PYTHON_RUNTIME,
      layers: [layerFactory.pythonCommonLayer.layer],
      timeout: Duration.seconds(30),
      memorySize: 256,
      environment: {
        HEALTH_RECORDS_TABLE_NAME: dynamoFactory.healthRecordsTable.table.tableName,
      },
      additionalPolicies: [healthRecordsReadPolicy],
      logging: {
        logRetention: RetentionDays.ONE_MONTH,
        removalPolicy: logRemovalPolicy,
      },
    });

    this.getDashboardSummaryLambda = new LambdaConstruct(this, 'GetDashboardSummaryLambda', {
      functionName: `${projectName}-${envName}-get-dashboard-summary`,
      description: 'Computes composite health summary with parallel queries for last 7 days',
      code: Code.fromAsset('src/lambda/dashboard/get-summary'),
      handler: 'index.handler',
      runtime: PYTHON_RUNTIME,
      layers: [layerFactory.pythonCommonLayer.layer],
      timeout: Duration.seconds(30),
      memorySize: 256,
      environment: {
        HEALTH_RECORDS_TABLE_NAME: dynamoFactory.healthRecordsTable.table.tableName,
      },
      additionalPolicies: [healthRecordsReadPolicy],
      logging: {
        logRetention: RetentionDays.ONE_MONTH,
        removalPolicy: logRemovalPolicy,
      },
    });
  }
}