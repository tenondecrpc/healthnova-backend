import { Construct } from 'constructs';
import { LayerConstruct } from '../../construct/layer-construct';
import { ParamsConfig } from '../shared/util/env-config';

export interface LayerFactoryProps {
  params: ParamsConfig;
}

/**
 * Centralized factory for creating all Lambda Layers in the application
 */
export class LayerFactory extends Construct {
  /**
   * Common Python utilities layer
   */
  public readonly pythonCommonLayer: LayerConstruct;

  /**
   * Python dependencies layer (boto3, requests, etc.)
   */
  public readonly pythonDependenciesLayer?: LayerConstruct;

  /**
   * Node.js common utilities layer (future use)
   */
  public readonly nodeCommonLayer?: LayerConstruct;

  constructor(scope: Construct, id: string, props: LayerFactoryProps) {
    super(scope, id);

    const { params } = props;
    const { envName, projectName } = params;

    // Create Python common utilities layer
    this.pythonCommonLayer = LayerConstruct.createPythonCommonLayer(
      this, 
      `${projectName}-${envName}-python-common`, 
      params,
      {
        description: 'Common Python utilities for Lambda functions (logging, response helpers, CORS)',
        tags: {
          Service: 'Lambda',
          Component: 'Layer',
          Type: 'CommonUtilities'
        }
      }
    );

    // Create Python dependencies layer
    // this.pythonDependenciesLayer = LayerConstruct.createDependenciesLayer(
    //   this,
    //   `${projectName}-${envName}-python-dependencies`,
    //   params,
    //   {
    //     layerName: 'python-dependencies',
    //     assetPath: 'src/layers/python-dependencies',
    //     runtime: PYTHON_RUNTIME,
    //     description: 'Common Python dependencies (boto3, requests, pydantic, etc.)',
    //     tags: {
    //       Service: 'Lambda',
    //       Component: 'Layer',
    //       Type: 'Dependencies'
    //     }
    //   }
    // );

    // Create Node.js common layer if needed (commented for now)
    // this.nodeCommonLayer = LayerConstruct.createNodeCommonLayer(
    //   this,
    //   `${projectName}-${envName}-node-common`,
    //   params,
    //   {
    //     description: 'Common utilities for Node.js Lambda functions',
    //     tags: {
    //       Service: 'Lambda',
    //       Component: 'Layer',
    //       Type: 'NodeCommonUtilities'
    //     }
    //   }
    // );
  }

  /**
   * Gets all Python layers for Lambda functions
   */
  public get pythonLayers(): LayerConstruct[] {
    const layers = [this.pythonCommonLayer];
    if (this.pythonDependenciesLayer) {
      layers.push(this.pythonDependenciesLayer);
    }
    return layers;
  }

  /**
   * Gets all Node.js layers for Lambda functions
   */
  public get nodeLayers(): LayerConstruct[] {
    return this.nodeCommonLayer ? [this.nodeCommonLayer] : [];
  }

  /**
   * Gets all layers
   */
  public get allLayers(): LayerConstruct[] {
    return [
      ...this.pythonLayers,
      ...this.nodeLayers
    ];
  }
}
