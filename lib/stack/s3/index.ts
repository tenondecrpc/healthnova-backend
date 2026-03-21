import * as s3 from 'aws-cdk-lib/aws-s3';
import { Duration } from 'aws-cdk-lib';
import { Construct } from "constructs";
import { S3Construct } from "../../construct/s3-construct";
import { ParamsConfig } from "../shared/util/env-config";

interface S3FactoryProps {
  params: ParamsConfig;
}

export class S3Factory extends Construct {
  public readonly exportsBucket: S3Construct;

  constructor(scope: Construct, id: string, props: S3FactoryProps) {
    super(scope, id);

    const { params } = props;
    const { projectName, envName } = params;

    this.exportsBucket = new S3Construct(this, 'ExportsBucket', {
        params,
        bucketConfig: {
            bucketName: `${projectName}-${envName}-health-exports`,
            versioned: true,
            encryption: { type: 's3Managed' },
            enforceSSL: true,
            eventBridgeEnabled: true,
            cors: [{
                allowedMethods: [s3.HttpMethods.PUT],
                allowedOrigins: ['*'],
                allowedHeaders: ['*'],
                exposedHeaders: ['ETag'],
                maxAge: 3600,
            }],
            lifecycleRules: [{
                id: 'ArchiveExportsToGlacier',
                enabled: true,
                prefix: 'exports/',
                transitions: [{
                    storageClass: s3.StorageClass.GLACIER,
                    transitionAfter: Duration.days(90),
                }],
                abortIncompleteMultipartUploadAfter: Duration.days(7),
            }],
        },
    });
  }
}