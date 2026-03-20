import { Construct } from 'constructs';
import { CloudTrailConstruct } from '../../construct/cloudtrail-construct';
import { ParamsConfig } from '../shared/util/env-config';

export interface CloudTrailFactoryProps {
  params: ParamsConfig;
}

export class CloudTrailFactory extends Construct {
  public readonly cloudTrailConstruct: CloudTrailConstruct;

  constructor(scope: Construct, id: string, props: CloudTrailFactoryProps) {
    super(scope, id);

    this.cloudTrailConstruct = new CloudTrailConstruct(this, 'CloudTrail', {
      params: props.params,
    });
  }
}
