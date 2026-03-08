import * as s3 from 'aws-cdk-lib/aws-s3';
import { Construct } from "constructs";
import { S3Construct } from "../../construct/s3-construct";
import { ParamsConfig } from "../shared/util/env-config";

interface S3FactoryProps {
  params: ParamsConfig;
}

export class S3Factory extends Construct {
  public readonly photosBucket: S3Construct;

  constructor(scope: Construct, id: string, props: S3FactoryProps) {
    super(scope, id);

    const { params } = props;
    const { projectName, envName } = params;

    // TODO: Bucket is configured as public temporarily for development
    // Change to private in production and configure access via presigned URLs
    this.photosBucket = new S3Construct(this, 'PhotosBucket', {
        params,
        bucketConfig: {
            bucketName: `${projectName}-${envName}-photos`,
            publicReadAccess: true, // TODO: Change to false in production or remove it
            blockPublicAccess: new s3.BlockPublicAccess({ // TODO: Remove this in production
                blockPublicAcls: true,        // Block public ACLs
                ignorePublicAcls: true,       // Ignore existing public ACLs
                blockPublicPolicy: false,     // Allow public bucket policies (needed for publicReadAccess)
                restrictPublicBuckets: false  // Allow public bucket policies to be applied
            }),
            cors: [{
                allowedMethods: [s3.HttpMethods.GET, s3.HttpMethods.POST],
                allowedOrigins: ['*'],
                allowedHeaders: ['*'],
                exposedHeaders: ['ETag', 'Location'],
                maxAge: 3000
            }]
        }
    });
  }
}