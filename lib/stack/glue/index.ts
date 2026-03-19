import { Construct } from 'constructs';
import { GlueConstruct } from '../../construct/glue-construct';
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

    const parseHealthXml = new GlueConstruct(this, 'ParseHealthXml', {
      jobName: this.parseHealthXmlJobName,
      scriptPath: 'src/glue/parse_health_xml.py',
      jobType: 'glueetl',
      workerType: 'G.1X',
      numberOfWorkers: 2,
      timeout: 30,
      maxRetries: 1,
      defaultArguments: {
        '--TABLE_NAME': dynamoFactory.healthRecordsTable.tableName,
        '--additional-python-modules': 'lxml',
      },
    });

    parseHealthXml.grantS3Read(
      s3Factory.exportsBucket.bucketArn,
      'exports/*'
    );

    parseHealthXml.grantDynamoDbWrite(
      dynamoFactory.healthRecordsTable.tableArn
    );
  }
}
