import { Construct } from 'constructs';
import { BudgetConstruct } from '../../construct/budget-construct';
import { ParamsConfig } from '../shared/util/env-config';

export interface BudgetFactoryProps {
  params: ParamsConfig;
  monthlyLimitUsd: number;
  alertEmails: string[];
}

export class BudgetFactory extends Construct {
  constructor(scope: Construct, id: string, props: BudgetFactoryProps) {
    super(scope, id);

    new BudgetConstruct(this, 'Budget', {
      params: props.params,
      monthlyLimitUsd: props.monthlyLimitUsd,
      alertEmails: props.alertEmails,
    });
  }
}
