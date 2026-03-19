import { Construct } from 'constructs';
import * as cdk from 'aws-cdk-lib';
import { GithubOidcConstruct } from '../../construct/github-oidc-construct';
import { ParamsConfig } from '../shared/util/env-config';

export interface GithubOidcFactoryProps {
  params: ParamsConfig;
  githubOrg: string;
  githubRepo: string;
}

export class GithubOidcFactory extends Construct {
  public readonly roleArn: string;

  constructor(scope: Construct, id: string, props: GithubOidcFactoryProps) {
    super(scope, id);

    const oidc = new GithubOidcConstruct(this, 'GithubOidc', {
      params: props.params,
      githubOrg: props.githubOrg,
      githubRepo: props.githubRepo,
    });

    this.roleArn = oidc.roleArn;

    new cdk.CfnOutput(this, 'GithubActionsCdkDiffRoleArn', {
      value: oidc.roleArn,
      description: 'IAM Role ARN for GitHub Actions CDK diff — set as AWS_CDK_DIFF_ROLE_ARN secret in GitHub',
      exportName: `${props.params.projectName}-${props.params.envName}-github-actions-role-arn`,
    });
  }
}
