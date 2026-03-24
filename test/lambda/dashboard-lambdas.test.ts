import { getResources } from '../helpers/setup';

describe('Dashboard Lambdas Infrastructure', () => {
  test('Snapshot: getDashboardMetricsLambda generated correctly', () => {
    const resources = getResources();
    const lambdas = Object.keys(resources)
      .filter((k) => resources[k].Type === 'AWS::Lambda::Function')
      .filter((k) => (resources[k] as any).Properties?.FunctionName === 'healthnova-dev-get-dashboard-metrics');

    expect(lambdas.length).toBe(1);
    const lambda = resources[lambdas[0]] as any;
    expect(lambda.Properties.Handler).toBe('index.handler');
    expect(lambda.Properties.Environment.Variables.HEALTH_RECORDS_TABLE_NAME).toBeDefined();
    expect(lambda).toMatchSnapshot();
  });

  test('Snapshot: getDashboardEcgLambda generated correctly', () => {
    const resources = getResources();
    const lambdas = Object.keys(resources)
      .filter((k) => resources[k].Type === 'AWS::Lambda::Function')
      .filter((k) => (resources[k] as any).Properties?.FunctionName === 'healthnova-dev-get-dashboard-ecg');

    expect(lambdas.length).toBe(1);
    const lambda = resources[lambdas[0]] as any;
    expect(lambda.Properties.Handler).toBe('index.handler');
    expect(lambda.Properties.Environment.Variables.HEALTH_RECORDS_TABLE_NAME).toBeDefined();
    expect(lambda).toMatchSnapshot();
  });

  test('Snapshot: getDashboardWorkoutsLambda generated correctly', () => {
    const resources = getResources();
    const lambdas = Object.keys(resources)
      .filter((k) => resources[k].Type === 'AWS::Lambda::Function')
      .filter((k) => (resources[k] as any).Properties?.FunctionName === 'healthnova-dev-get-dashboard-workouts');

    expect(lambdas.length).toBe(1);
    const lambda = resources[lambdas[0]] as any;
    expect(lambda.Properties.Handler).toBe('index.handler');
    expect(lambda.Properties.Environment.Variables.HEALTH_RECORDS_TABLE_NAME).toBeDefined();
    expect(lambda).toMatchSnapshot();
  });

  test('Snapshot: getDashboardJobsLambda generated correctly', () => {
    const resources = getResources();
    const lambdas = Object.keys(resources)
      .filter((k) => resources[k].Type === 'AWS::Lambda::Function')
      .filter((k) => (resources[k] as any).Properties?.FunctionName === 'healthnova-dev-get-dashboard-jobs');

    expect(lambdas.length).toBe(1);
    const lambda = resources[lambdas[0]] as any;
    expect(lambda.Properties.Handler).toBe('index.handler');
    expect(lambda.Properties.Environment.Variables.HEALTH_RECORDS_TABLE_NAME).toBeDefined();
    expect(lambda).toMatchSnapshot();
  });

  test('Snapshot: getDashboardSummaryLambda generated correctly', () => {
    const resources = getResources();
    const lambdas = Object.keys(resources)
      .filter((k) => resources[k].Type === 'AWS::Lambda::Function')
      .filter((k) => (resources[k] as any).Properties?.FunctionName === 'healthnova-dev-get-dashboard-summary');

    expect(lambdas.length).toBe(1);
    const lambda = resources[lambdas[0]] as any;
    expect(lambda.Properties.Handler).toBe('index.handler');
    expect(lambda.Properties.Environment.Variables.HEALTH_RECORDS_TABLE_NAME).toBeDefined();
    expect(lambda).toMatchSnapshot();
  });

  test('Snapshot: dashboard REST API routes generated correctly', () => {
    const resources = getResources();
    const apiMethods = Object.keys(resources)
      .filter((k) => resources[k].Type === 'AWS::ApiGateway::Method')
      .filter((k) => (resources[k] as any).Properties?.HttpMethod === 'GET');

    // Filter to find the dashboard methods by their operation Name / ID etc
    // In CDK, the path is often defined in AWS::ApiGateway::Resource
    const apiResources = Object.keys(resources)
      .filter((k) => resources[k].Type === 'AWS::ApiGateway::Resource')
      .filter((k) => {
        const pathPart = (resources[k] as any).Properties?.PathPart;
        return ['metrics', 'ecg', 'workouts', 'jobs', 'summary', 'dashboard'].includes(pathPart);
      })
      .map(k => resources[k]);

    // Snapshot just the relevant resources
    expect(apiResources).toMatchSnapshot();
  });
});
