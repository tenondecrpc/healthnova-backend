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

    // Validate CORS origins - no wildcards allowed for security
    const corsOrigins = process.env.CORS_ALLOWED_ORIGINS?.split(',').map(o => o.trim()) || [];
    if (corsOrigins.length === 0 || corsOrigins.includes('*')) {
      throw new Error(
        'CORS_ALLOWED_ORIGINS must be defined and cannot contain wildcard (*). ' +
        'Please specify explicit origins in .env file for security.'
      );
    }

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
        allowOrigins: corsOrigins,
        allowMethods: process.env.CORS_ALLOWED_METHODS?.split(',').map(m => m.trim()) || ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
        allowHeaders: process.env.CORS_ALLOWED_HEADERS?.split(',').map(h => h.trim()) || [
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
        maxAge: Duration.seconds(parseInt(process.env.CORS_MAX_AGE || '86400')),
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
      // ETL ROUTES
      // ===================
      {
        path: '/upload/presigned-url',
        method: 'POST',
        lambda: lambdaFactory.presignedUrlExportLambda.function,
        requireAuth: true,
      },
      // ===================
      // DASHBOARD ROUTES
      // ===================
      {
        path: '/dashboard/metrics',
        method: 'GET',
        lambda: lambdaFactory.getDashboardMetricsLambda.function,
        requireAuth: true,
      },
      {
        path: '/dashboard/ecg',
        method: 'GET',
        lambda: lambdaFactory.getDashboardEcgLambda.function,
        requireAuth: true,
      },
      {
        path: '/dashboard/workouts',
        method: 'GET',
        lambda: lambdaFactory.getDashboardWorkoutsLambda.function,
        requireAuth: true,
      },
      {
        path: '/dashboard/jobs',
        method: 'GET',
        lambda: lambdaFactory.getDashboardJobsLambda.function,
        requireAuth: true,
      },
      {
        path: '/dashboard/summary',
        method: 'GET',
        lambda: lambdaFactory.getDashboardSummaryLambda.function,
        requireAuth: true,
      },
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
