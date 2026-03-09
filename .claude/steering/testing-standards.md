---
title: Testing Standards
inclusion: auto
---

# Testing Standards

## Estructura de Tests

Todos los tests deben seguir esta estructura organizada por dominio:

```
test/
├── helpers/
│   └── setup.ts          # Configuración compartida (app, stack, template)
├── s3/
│   └── [recurso].test.ts
├── lambda/
│   └── [recurso].test.ts
├── dynamodb/
│   └── [recurso].test.ts
├── step-functions/
│   └── [recurso].test.ts
└── glue/
    └── [recurso].test.ts
```

## Convenciones de Naming

- **Archivos**: `test/[dominio]/[recurso].test.ts`
- **Describes**: Nombre descriptivo del recurso en inglés
- **Tests**: Comportamiento específico que se prueba, comenzando con verbo

### Ejemplos:
- `test/s3/exports-bucket.test.ts`
- `test/lambda/presigned-url-export.test.ts`
- `test/dynamodb/health-records-table.test.ts`
- `test/step-functions/ingestion-workflow.test.ts`

## Setup Compartido

**SIEMPRE** usar el helper de setup para obtener el template:

```typescript
import { getTemplate } from '../helpers/setup';

describe('Nombre del Recurso', () => {
  test('comportamiento específico', () => {
    getTemplate().hasResourceProperties('AWS::Service::Resource', {
      // propiedades esperadas
    });
  });
});
```

### Funciones disponibles en setup:

- `getTemplate()`: Retorna el Template de CDK para assertions
- `getResources()`: Retorna todos los recursos del stack
- `TEST_ENV`: Constante con account y region de test
- `TEST_PARAMS`: Constante con parámetros del stack (envName, projectName, isProd)

## Patrones de Testing

### 1. Verificar propiedades de recursos

```typescript
test('creates resource with expected properties', () => {
  getTemplate().hasResourceProperties('AWS::Lambda::Function', {
    FunctionName: 'healthnova-dev-function-name',
    Runtime: 'python3.11',
  });
});
```

### 2. Verificar políticas IAM

```typescript
test('Lambda has required IAM permissions', () => {
  const resources = getTemplate().toJSON().Resources;
  const policyKeys = Object.keys(resources).filter(
    k => resources[k].Type === 'AWS::IAM::Policy' &&
         JSON.stringify(resources[k]).includes('function-name')
  );
  expect(policyKeys.length).toBeGreaterThan(0);
  const policyDoc = JSON.stringify(resources[policyKeys[0]]);
  expect(policyDoc).toContain('dynamodb:PutItem');
});
```

### 3. Verificar variables de entorno

```typescript
test('Lambda has required environment variables', () => {
  getTemplate().hasResourceProperties('AWS::Lambda::Function', {
    FunctionName: 'healthnova-dev-function-name',
    Environment: {
      Variables: {
        TABLE_NAME: expect.any(Object),
        BUCKET_NAME: expect.any(Object),
      },
    },
  });
});
```

## Reglas Importantes

1. **NO crear múltiples instancias del stack** - Usar `getTemplate()` que cachea el template
2. **Organizar por dominio AWS** - S3, Lambda, DynamoDB, Step Functions, etc.
3. **Un archivo por recurso principal** - No mezclar tests de diferentes recursos
4. **Tests descriptivos** - El nombre del test debe explicar qué se está verificando
5. **Usar relative imports** - `'../helpers/setup'` desde archivos de test

## Cuando crear nuevos tests

- Al agregar nuevos recursos de infraestructura en CDK
- Al modificar propiedades importantes de recursos existentes
- Al agregar nuevas políticas IAM o permisos
- Al crear nuevas integraciones entre servicios

## NO incluir en tests

- Tests de lógica de negocio de Lambda (esos van en tests unitarios de Python)
- Tests de integración end-to-end (esos son separados)
- Tests que requieran deployment real de AWS
