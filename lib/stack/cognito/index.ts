import { Construct } from 'constructs';
import { AccountRecovery, OAuthScope } from 'aws-cdk-lib/aws-cognito';
import { CognitoConstruct } from '../../construct/cognito-construct';
import { ParamsConfig } from '../shared/util/env-config';
import { LambdaFactory } from '../lambda';

export interface CognitoFactoryProps {
  params: ParamsConfig;
  lambdaFactory: LambdaFactory;
}

/**
 * Centralized factory for creating Cognito authentication resources
 */
export class CognitoFactory extends Construct {
  public readonly cognitoConstruct: CognitoConstruct;

  constructor(scope: Construct, id: string, props: CognitoFactoryProps) {
    super(scope, id);

    const { params, lambdaFactory } = props;
    const { envName, projectName } = params;

    // Create the main user authentication system
    this.cognitoConstruct = new CognitoConstruct(this, 'UserAuth', {
      params,
      userPoolConfig: {
        userPoolName: `${projectName}-${envName}-user-pool`,
        selfSignUpEnabled: true,
        signInAliases: {
          email: true,
          username: false,
          phone: false
        },
        autoVerify: {
          email: true  // Enable email verification code sending
        },
        passwordPolicy: {
          minLength: 8,
          requireUppercase: true,
          requireLowercase: true,
          requireDigits: true,
          requireSymbols: false,
        },
        accountRecovery: AccountRecovery.EMAIL_AND_PHONE_WITHOUT_MFA,
        customAttributes: {
          stringAttributes: {
            'role': {
              mutable: true,
            }
          }
        }
      },
      userPoolClientConfig: {
        userPoolClientName: `${projectName}-${envName}-web-client`,
        generateSecret: false, // For web/mobile apps
        authFlows: {
          userPassword: true,
          userSrp: true,
          custom: false,
          adminUserPassword: false,
        },
        tokenValidity: {
          accessToken: 1,    // 1 day
          idToken: 1,        // 1 day  
          refreshToken: 30   // 30 days
        },
        // Resource Server configuration for custom scopes
        resourceServer: {
          identifier: `${projectName}-${envName}-api`,
          name: `${projectName} ${envName} API`,
          scopes: [
            {
              scopeName: 'read',
              scopeDescription: 'Read access to API resources'
            },
            {
              scopeName: 'write',
              scopeDescription: 'Write access to API resources'
            },
            {
              scopeName: 'files:upload',
              scopeDescription: 'Upload files to S3'
            },
            {
              scopeName: 'files:download',
              scopeDescription: 'Download files from S3'
            }
          ]
        },
        // OAuth configuration for access tokens
        oAuth: {
          flows: {
            authorizationCodeGrant: true,
            implicitCodeGrant: false,
          },
          scopes: [
            OAuthScope.EMAIL,
            OAuthScope.OPENID,
            OAuthScope.PROFILE,
            // Custom scopes will be added automatically from resource server
          ],
          callbackUrls: envName === 'prod'
            ? ['https://example.com/callback']
            : ['http://localhost:3000/callback', 'http://localhost:3000'],
          logoutUrls: envName === 'prod'
            ? ['https://example.com/logout']
            : ['http://localhost:3000/logout', 'http://localhost:3000'],
        },
      },
      // Configure Lambda triggers if Lambda functions are available
      ...(lambdaFactory && {
        lambdaTriggers: {
          preSignUp: lambdaFactory.preSignupLambda.function,
          postConfirmation: lambdaFactory.postConfirmationSignupLambda.function,
        }
      }),
      createOutputs: true,
      tags: {
        Service: 'Authentication',
        Component: 'UserAuth'
      }
    });
  }

  /**
   * Configures Lambda triggers after Lambda functions are created
   * This method should be called if Lambda functions weren't available during construction
   */
  public configureLambdaTriggers(lambdaFactory: LambdaFactory): void {
    // Note: This would require recreating the User Pool with triggers
    // In practice, it's better to pass lambdaFactory during construction
    console.warn('Lambda triggers should be configured during User Pool creation for better performance');
  }

  /**
   * Gets the User Pool ID for reference
   */
  public get userPoolId(): string {
    return this.cognitoConstruct.userPoolId;
  }

  /**
   * Gets the User Pool Client ID for frontend configuration
   */
  public get userPoolClientId(): string {
    return this.cognitoConstruct.userPoolClientId;
  }

  /**
   * Gets the User Pool ARN for IAM policies
   */
  public get userPoolArn(): string {
    return this.cognitoConstruct.userPoolArn;
  }
}
