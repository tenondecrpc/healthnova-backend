import { Construct } from 'constructs';
import { GuardDutyConstruct } from '../../construct/guardduty-construct';
import { ParamsConfig } from '../shared/util/env-config';

export interface GuardDutyFactoryProps {
  params: ParamsConfig;
}

export class GuardDutyFactory extends Construct {
  public readonly guardDutyConstruct: GuardDutyConstruct;

  constructor(scope: Construct, id: string, props: GuardDutyFactoryProps) {
    super(scope, id);

    this.guardDutyConstruct = new GuardDutyConstruct(this, 'GuardDuty', {
      params: props.params,
    });
  }
}
