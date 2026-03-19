import { Construct } from 'constructs';
import * as budgets from 'aws-cdk-lib/aws-budgets';
import * as ce from 'aws-cdk-lib/aws-ce';
import * as sns from 'aws-cdk-lib/aws-sns';
import * as subscriptions from 'aws-cdk-lib/aws-sns-subscriptions';
import { ParamsConfig } from '../stack/shared/util/env-config';

export interface BudgetConstructProps {
  params: ParamsConfig;
  monthlyLimitUsd: number;
  alertEmails: string[];
}

export class BudgetConstruct extends Construct {
  constructor(scope: Construct, id: string, props: BudgetConstructProps) {
    super(scope, id);

    const { params, monthlyLimitUsd, alertEmails } = props;

    const notificationTopic = new sns.Topic(this, 'BudgetAlertTopic', {
      topicName: `${params.projectName}-${params.envName}-budget-alerts`,
    });

    alertEmails.forEach(email => {
      notificationTopic.addSubscription(new subscriptions.EmailSubscription(email));
    });

    new budgets.CfnBudget(this, 'MonthlyBudget', {
      budget: {
        budgetName: `${params.projectName}-${params.envName}-monthly`,
        budgetType: 'COST',
        timeUnit: 'MONTHLY',
        budgetLimit: {
          amount: monthlyLimitUsd,
          unit: 'USD',
        },
        costFilters: {
          TagKeyValue: [`user:Project$${params.projectName}`],
        },
      },
      notificationsWithSubscribers: [
        {
          notification: {
            notificationType: 'ACTUAL',
            comparisonOperator: 'GREATER_THAN',
            threshold: 80,
            thresholdType: 'PERCENTAGE',
          },
          subscribers: alertEmails.map(email => ({
            subscriptionType: 'EMAIL',
            address: email,
          })),
        },
        {
          notification: {
            notificationType: 'ACTUAL',
            comparisonOperator: 'GREATER_THAN',
            threshold: 100,
            thresholdType: 'PERCENTAGE',
          },
          subscribers: alertEmails.map(email => ({
            subscriptionType: 'EMAIL',
            address: email,
          })),
        },
        {
          notification: {
            notificationType: 'FORECASTED',
            comparisonOperator: 'GREATER_THAN',
            threshold: 100,
            thresholdType: 'PERCENTAGE',
          },
          subscribers: alertEmails.map(email => ({
            subscriptionType: 'EMAIL',
            address: email,
          })),
        },
      ],
    });

    new ce.CfnAnomalySubscription(this, 'AnomalySubscription', {
      subscriptionName: `${params.projectName}-${params.envName}-anomaly-alerts`,
      monitorArnList: [],
      subscribers: alertEmails.map(email => ({
        address: email,
        type: 'EMAIL',
      })),
      threshold: 20,
      frequency: 'DAILY',
    });
  }
}
