import { Construct } from 'constructs';
import { Duration } from 'aws-cdk-lib';
import * as sfn from 'aws-cdk-lib/aws-stepfunctions';
import * as tasks from 'aws-cdk-lib/aws-stepfunctions-tasks';
import * as events from 'aws-cdk-lib/aws-events';
import * as eventsTargets from 'aws-cdk-lib/aws-events-targets';
import * as cloudwatch from 'aws-cdk-lib/aws-cloudwatch';
import * as glue from 'aws-cdk-lib/aws-glue';
import { ParamsConfig } from '../shared/util/env-config';
import { LambdaFactory } from '../lambda';
import { S3Factory } from '../s3';

export interface StepFunctionsFactoryProps {
  params: ParamsConfig;
  lambdaFactory: LambdaFactory;
  s3Factory: S3Factory;
  glueJobName?: string;
}

export class StepFunctionsFactory extends Construct {
  public readonly stateMachine: sfn.StateMachine;

  constructor(scope: Construct, id: string, props: StepFunctionsFactoryProps) {
    super(scope, id);

    const { params, lambdaFactory, s3Factory, glueJobName } = props;
    const { envName, projectName } = params;

    // Step 0: Extract userId and jobId from the S3 key path
    // Key format: exports/{userId}/{timestamp}.zip
    const parseInput = new sfn.Pass(this, 'ParseInput', {
      parameters: {
        'bucket.$': '$.bucket',
        'key.$': '$.key',
        'userId.$': "States.ArrayGetItem(States.StringSplit($.key, '/'), 1)",
        'jobId.$': "States.ArrayGetItem(States.StringSplit(States.ArrayGetItem(States.StringSplit($.key, '/'), 2), '.'), 0)",
      },
    });

    // Step 1: Validate file
    const validateFile = new tasks.LambdaInvoke(this, 'ValidateFile', {
      lambdaFunction: lambdaFactory.validateFileLambda.function,
      outputPath: '$.Payload',
      retryOnServiceExceptions: true,
    });

    // Step 2: Extract manifest
    const extractManifest = new tasks.LambdaInvoke(this, 'ExtractManifest', {
      lambdaFunction: lambdaFactory.extractManifestLambda.function,
      outputPath: '$.Payload',
      retryOnServiceExceptions: true,
    });

    // Step 3a: Parse XML via Glue job
    let parseXml: sfn.IChainable;
    if (glueJobName) {
      parseXml = new tasks.GlueStartJobRun(this, 'ParseHealthXML', {
        glueJobName: glueJobName,
        integrationPattern: sfn.IntegrationPattern.RUN_JOB,
        arguments: sfn.TaskInput.fromObject({
          '--BUCKET': sfn.JsonPath.stringAt('$.bucket'),
          '--KEY': sfn.JsonPath.stringAt('$.key'),
          '--USER_ID': sfn.JsonPath.stringAt('$.userId'),
          '--HEALTH_JOB_ID': sfn.JsonPath.stringAt('$.jobId'),
        }),
        resultPath: '$.glueResult',
      });
    } else {
      parseXml = new sfn.Pass(this, 'ParseHealthXMLPlaceholder', {
        comment: 'Glue job not yet configured — placeholder',
        resultPath: '$.glueResult',
      });
    }

    // Step 3b: Parse ECG CSVs (Lambda)
    const parseEcg = new tasks.LambdaInvoke(this, 'ParseECG', {
      lambdaFunction: lambdaFactory.parseEcgLambda.function,
      outputPath: '$.Payload',
      retryOnServiceExceptions: true,
    });

    // Step 3c: Parse GPX routes (Lambda)
    const parseGpx = new tasks.LambdaInvoke(this, 'ParseGPX', {
      lambdaFunction: lambdaFactory.parseGpxLambda.function,
      outputPath: '$.Payload',
      retryOnServiceExceptions: true,
    });

    // Parallel branch: XML + (ECG, GPX)
    const parallelParsing = new sfn.Parallel(this, 'ParallelParsing', {
      resultPath: '$.parseResults',
    });
    parallelParsing.branch(parseXml);
    parallelParsing.branch(parseEcg);
    parallelParsing.branch(parseGpx);

    // Step 4: Mark complete (success path)
    const markComplete = new tasks.LambdaInvoke(this, 'MarkComplete', {
      lambdaFunction: lambdaFactory.markCompleteLambda.function,
      outputPath: '$.Payload',
      retryOnServiceExceptions: true,
    });

    // Step 4b: Mark failed (error path)
    const markFailed = new tasks.LambdaInvoke(this, 'MarkFailed', {
      lambdaFunction: lambdaFactory.markCompleteLambda.function,
      payload: sfn.TaskInput.fromObject({
        userId: sfn.JsonPath.stringAt('$.userId'),
        jobId: sfn.JsonPath.stringAt('$.jobId'),
        status: 'FAILED',
        errorStep: sfn.JsonPath.stringAt('$.errorStep'),
      }),
      outputPath: '$.Payload',
    });

    // Error handler: catch and mark failed
    const handleError = new sfn.Pass(this, 'HandleError', {
      parameters: {
        'userId.$': '$.userId',
        'jobId.$': '$.jobId',
        'errorStep': 'ParallelParsing',
      },
    });
    handleError.next(markFailed);

    parallelParsing.addCatch(handleError, {
      resultPath: '$.error',
    });

    // Chain the workflow
    const definition = parseInput
      .next(validateFile)
      .next(extractManifest)
      .next(parallelParsing)
      .next(markComplete);

    // Create state machine
    this.stateMachine = new sfn.StateMachine(this, 'IngestionWorkflow', {
      stateMachineName: `${projectName}-${envName}-health-ingestion`,
      definitionBody: sfn.DefinitionBody.fromChainable(definition),
      stateMachineType: sfn.StateMachineType.STANDARD,
      timeout: Duration.hours(4),
    });

    // EventBridge rule: S3 ObjectCreated → Step Functions
    const rule = new events.Rule(this, 'ExportUploadRule', {
      ruleName: `${projectName}-${envName}-export-upload`,
      eventPattern: {
        source: ['aws.s3'],
        detailType: ['Object Created'],
        detail: {
          bucket: { name: [s3Factory.exportsBucket.bucketName] },
          object: { key: [{ prefix: 'exports/' }, { suffix: '.zip' }] },
        },
      },
    });

    rule.addTarget(new eventsTargets.SfnStateMachine(this.stateMachine, {
      input: events.RuleTargetInput.fromObject({
        bucket: events.EventField.fromPath('$.detail.bucket.name'),
        key: events.EventField.fromPath('$.detail.object.key'),
      }),
    }));

    // CloudWatch alarm: execution duration > 4 hours
    new cloudwatch.Alarm(this, 'LongExecutionAlarm', {
      alarmName: `${projectName}-${envName}-ingestion-long-execution`,
      metric: this.stateMachine.metricTime({
        period: Duration.minutes(5),
        statistic: 'Maximum',
      }),
      threshold: Duration.hours(4).toMilliseconds(),
      evaluationPeriods: 1,
      comparisonOperator: cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
      alarmDescription: 'Health data ingestion workflow exceeded 4-hour execution time',
    });
  }
}
