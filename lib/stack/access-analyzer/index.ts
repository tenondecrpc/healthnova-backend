import { Construct } from 'constructs';
import { AccessAnalyzerConstruct } from '../../construct/access-analyzer-construct';
import { ParamsConfig } from '../shared/util/env-config';

export interface AccessAnalyzerFactoryProps {
  params: ParamsConfig;
}

export class AccessAnalyzerFactory extends Construct {
  public readonly accessAnalyzerConstruct: AccessAnalyzerConstruct;

  constructor(scope: Construct, id: string, props: AccessAnalyzerFactoryProps) {
    super(scope, id);

    this.accessAnalyzerConstruct = new AccessAnalyzerConstruct(this, 'AccessAnalyzer', {
      params: props.params,
    });
  }
}
