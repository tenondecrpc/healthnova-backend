import { getTemplate } from '../helpers/setup';

describe('Ingestion Lambda Functions', () => {
  test('creates validate-file Lambda', () => {
    getTemplate().hasResourceProperties('AWS::Lambda::Function', {
      FunctionName: 'healthnova-dev-validate-file',
    });
  });

  test('creates extract-manifest Lambda', () => {
    getTemplate().hasResourceProperties('AWS::Lambda::Function', {
      FunctionName: 'healthnova-dev-extract-manifest',
    });
  });

  test('creates mark-complete Lambda', () => {
    getTemplate().hasResourceProperties('AWS::Lambda::Function', {
      FunctionName: 'healthnova-dev-mark-complete',
    });
  });

  test('creates parse-ecg Lambda', () => {
    getTemplate().hasResourceProperties('AWS::Lambda::Function', {
      FunctionName: 'healthnova-dev-parse-ecg',
    });
  });

  test('creates parse-gpx Lambda', () => {
    getTemplate().hasResourceProperties('AWS::Lambda::Function', {
      FunctionName: 'healthnova-dev-parse-gpx',
    });
  });
});
