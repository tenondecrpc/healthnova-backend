import { Construct } from 'constructs';
import * as glue from 'aws-cdk-lib/aws-glue';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as s3assets from 'aws-cdk-lib/aws-s3-assets';
import { ParamsConfig } from '../shared/util/env-config';
import { S3Factory } from '../s3';
import { DynamoFactory } from '../dynamo';

export interface GlueFactoryProps {
  params: ParamsConfig;
  s3Factory: S3Factory;
  dynamoFactory: DynamoFactory;
}

export class GlueFactory extends Construct {
  public readonly parseHealthXmlJobName: string;

  constructor(scope: Construct, id: string, props: GlueFactoryProps) {
    super(scope, id);

    const { params, s3Factory, dynamoFactory } = props;
    const { envName, projectName } = params;

    this.parseHealthXmlJobName = `${projectName}-${envName}-parse-health-xml`;

    // Upload Glue script to S3
    const glueScript = new s3assets.Asset(this, 'ParseHealthXmlScript', {
      path: 'src/glue/parse_health_xml.py',
    });

    // IAM role for Glue job
    const glueRole = new iam.Role(this, 'ParseHealthXmlRole', {
      roleName: `${projectName}-${envName}-glue-parse-health-xml`,
      assumedBy: new iam.ServicePrincipal('glue.amazonaws.com'),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSGlueServiceRole'),
      ],
    });

    // S3 read access scoped to exports bucket
    glueRole.addToPolicy(new iam.PolicyStatement({
      actions: ['s3:GetObject'],
      resources: [s3Factory.exportsBucket.arnForObjects('exports/*')],
    }));

    // S3 read access to CDK assets bucket so Glue can load the script
    glueScript.grantRead(glueRole);

    // DynamoDB write access scoped to health-records table
    glueRole.addToPolicy(new iam.PolicyStatement({
      actions: ['dynamodb:PutItem', 'dynamodb:BatchWriteItem'],
      resources: [
        dynamoFactory.healthRecordsTable.tableArn,
        `${dynamoFactory.healthRecordsTable.tableArn}/index/*`,
      ],
    }));

    // Glue Python Shell job
    new glue.CfnJob(this, 'ParseHealthXmlJob', {
      name: this.parseHealthXmlJobName,
      role: glueRole.roleArn,
      command: {
        name: 'pythonshell',
        pythonVersion: '3.9',
        scriptLocation: glueScript.s3ObjectUrl,
      },
      maxCapacity: 0.0625,
      defaultArguments: {
        '--TABLE_NAME': dynamoFactory.healthRecordsTable.tableName,
        '--enable-metrics': 'true',
        '--job-language': 'python',
        '--enable-continuous-cloudwatch-log': 'false',
        '--job-bookmark-option': 'job-bookmark-disable',
      },
      maxRetries: 1,
      timeout: 240, // 4 hours — aligned with state machine timeout
      glueVersion: '3.0',
    });
  }
}
