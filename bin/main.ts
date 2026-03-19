#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { MainStack } from '../lib/stack/main-stack';
import { config } from '../lib/stack/shared/util/env-config';
import { capitalizeFirstLetter } from '../lib/stack/shared/util/capitalize';


const app = new cdk.App();
const { env, params } = config;
const { envName, projectName } = params;
const mainStackName = `${capitalizeFirstLetter(projectName)}${capitalizeFirstLetter(envName)}Stack`;

new MainStack(app, mainStackName, {
  env,
  params,
  githubOrg: process.env.GITHUB_ORG ?? '',
  githubRepo: process.env.GITHUB_REPO ?? '',
  monthlyBudgetUsd: Number(process.env.MONTHLY_BUDGET_USD ?? '100'),
  budgetAlertEmails: (process.env.BUDGET_ALERT_EMAILS ?? '').split(',').filter(Boolean),
});