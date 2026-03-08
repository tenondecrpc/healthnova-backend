import { Construct } from 'constructs';
import { Duration } from 'aws-cdk-lib';
import { RetentionDays } from 'aws-cdk-lib/aws-logs';
import { RestApiConstruct, RestApiRouteConfig } from '../../construct/rest-api-construct';
import { ParamsConfig } from '../shared/util/env-config';
import { CognitoFactory } from '../cognito';
import { LambdaFactory } from '../lambda';

export interface RestApiFactoryProps {
  params: ParamsConfig;
  cognitoFactory: CognitoFactory;
  lambdaFactory: LambdaFactory;
}

/**
 * Centralized factory for creating REST API resources
 */
export class RestApiFactory extends Construct {
  public readonly restApiConstruct: RestApiConstruct;

  constructor(scope: Construct, id: string, props: RestApiFactoryProps) {
    super(scope, id);

    const { params, cognitoFactory, lambdaFactory } = props;
    const { envName, projectName } = params;

    // Create the main REST API with all routes
    // Using Lambda Authorizer for OAuth 2.0 compliance (accepts Access Tokens)
    this.restApiConstruct = new RestApiConstruct(this, 'RestApi', {
      params,
      cognitoConstruct: cognitoFactory.cognitoConstruct,
      authorizerFunction: lambdaFactory.authorizerLambda.function,
      authorizerType: 'lambda', // Use Lambda Authorizer (accepts Access Token)
      apiName: `${projectName}-${envName}-rest-api`,
      description: `REST API for ${envName} environment`,

      // CORS configuration for web/mobile apps
      corsConfig: {
        allowOrigins: envName === 'prod'
          ? ['https://example.com', 'https://www.example.com']
          : ['http://localhost:3000', 'https://develop.xxxxxxxxxx.amplifyapp.com', 'https://mydomain.com'],
        allowMethods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
        allowHeaders: [
          'Content-Type',
          'Authorization',
          'X-Requested-With',
          'Accept',
          'Origin',
          'X-Api-Key',
          'X-Amz-Date',
          'X-Amz-Security-Token'
        ],
        exposeHeaders: [
          'X-Request-Id',
          'X-Amz-Request-Id'
        ],
        maxAge: Duration.hours(24),
        allowCredentials: false, // Cannot use credentials with multiple origins
      },

      // Throttling for rate limiting
      throttleConfig: {
        burstLimit: envName === 'prod' ? 500 : 200,
        rateLimit: envName === 'prod' ? 250 : 100,
      },

      // Define all REST API routes
      routes: this.createRoutes(lambdaFactory),

      // Enable access logs for monitoring
      enableAccessLogs: true,
      logRetention: RetentionDays.ONE_MONTH,

      // Create CloudFormation outputs
      createOutputs: true,

      tags: {
        Service: 'RestApi',
        Component: 'Api',
        Type: 'REST',
        Environment: envName
      }
    });

    // Add 404 handler for undefined routes
    this.restApiConstruct.addNotFoundHandler(lambdaFactory.notFoundLambda.function);
  }

  /**
   * Creates all routes for application
   */
  private createRoutes(lambdaFactory: LambdaFactory): RestApiRouteConfig[] {
    return [
      // ===================
      // EXAM ROUTES
      // ===================
      {
        path: '/photobook/process',
        method: 'POST',
        lambda: lambdaFactory.processLambda.function,
        requestValidator: 'body',
        requireAuth: true, // (default - user must be authenticated)
      },
      // TODO: Enable authentication for presigned URL upload endpoint in production
      // Change requireAuth to true once proper user management is implemented
      {
        path: '/presigned-url-upload',
        method: 'POST',
        lambda: lambdaFactory.presignedUrlUploadLambda.function,
        requestValidator: 'body',
        requireAuth: true,
      },
      // ===================
      // FUTURE ROUTES (commented for reference)
      // ===================
      // {
      //   path: '/user/profile',
      //   method: 'GET',
      //   lambda: lambdaFactory.getUserProfileLambda.function,
      //   // requireAuth: true (default)
      // },
      // {
      //   path: '/user/profile',
      //   method: 'PUT',
      //   lambda: lambdaFactory.updateUserProfileLambda.function,
      //   requestValidator: 'body',
      // },
    ];
  }

  /**
   * Adds a new route to the REST API after creation
   */
  public addRoute(routeConfig: RestApiRouteConfig): void {
    this.restApiConstruct.addRoute(routeConfig);
  }

  /**
   * Gets the REST API URL for frontend configuration
   */
  public get apiUrl(): string {
    return this.restApiConstruct.apiUrl;
  }

  /**
   * Gets the REST API ID for AWS CLI/SDK operations
   */
  public get apiId(): string {
    return this.restApiConstruct.apiId;
  }

  /**
   * Gets the REST API ARN for IAM policies
   */
  public get apiArn(): string {
    return this.restApiConstruct.apiArn;
  }

  /**
   * Gets the deployment stage for advanced configuration
   */
  public get stage() {
    return this.restApiConstruct.stage;
  }

  /**
   * Gets the Cognito authorizer for custom integrations
   */
  public get cognitoAuthorizer() {
    return this.restApiConstruct.cognitoAuthorizer;
  }
}
