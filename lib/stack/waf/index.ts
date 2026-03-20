import { Construct } from 'constructs';
import { WafConstruct } from '../../construct/waf-construct';
import { ParamsConfig } from '../shared/util/env-config';
import { RestApiFactory } from '../rest-api';

export interface WafFactoryProps {
  params: ParamsConfig;
  restApiFactory: RestApiFactory;
}

export class WafFactory extends Construct {
  public readonly wafConstruct: WafConstruct;

  constructor(scope: Construct, id: string, props: WafFactoryProps) {
    super(scope, id);

    const { params, restApiFactory } = props;

    this.wafConstruct = new WafConstruct(this, 'Waf', {
      params,
      apiGatewayStageArn: restApiFactory.stage.stageArn,
    });
  }
}
