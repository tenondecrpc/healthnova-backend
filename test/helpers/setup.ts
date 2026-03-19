import * as cdk from 'aws-cdk-lib';
import { Template } from 'aws-cdk-lib/assertions';
import { MainStack } from '../../lib/stack/main-stack';

// Use environment variables if available, otherwise use generic test values
export const TEST_ENV = {
  account: process.env.AWS_ACCOUNT || 'xxxxxxxx672',
  region: process.env.AWS_REGION || 'us-east-1',
};

export const TEST_PARAMS = {
  envName: process.env.ENV_NAME || 'dev',
  projectName: process.env.PROJECT_NAME || 'healthnova',
  isProd: false,
};

let _template: Template | undefined;

export function getTemplate(): Template {
  if (!_template) {
    const app = new cdk.App();
    const stack = new MainStack(app, 'TestStack', {
      env: TEST_ENV,
      params: TEST_PARAMS,
      githubOrg: 'test-org',
      githubRepo: 'test-repo',
      monthlyBudgetUsd: 100,
      budgetAlertEmails: ['test@example.com'],
    });
    _template = Template.fromStack(stack);
  }
  return _template;
}

export function getResources(): Record<string, { Type: string; Properties?: Record<string, unknown> }> {
  return getTemplate().toJSON().Resources;
}
