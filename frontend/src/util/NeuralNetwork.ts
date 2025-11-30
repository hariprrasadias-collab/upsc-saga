// Lightweight Neural Network for Deep Q-Learning
// Implements a simple Feedforward Neural Network with Backpropagation

export class Layer {
    weights: number[][]; // [input_size][output_size]
    biases: number[];    // [output_size]
    inputSize: number;
    outputSize: number;

    constructor(inputSize: number, outputSize: number) {
        this.inputSize = inputSize;
        this.outputSize = outputSize;
        this.weights = [];
        this.biases = [];

        // Xavier Initialization
        const limit = Math.sqrt(6 / (inputSize + outputSize));
        for (let i = 0; i < inputSize; i++) {
            this.weights[i] = [];
            for (let j = 0; j < outputSize; j++) {
                this.weights[i][j] = Math.random() * 2 * limit - limit;
            }
        }

        for (let j = 0; j < outputSize; j++) {
            this.biases[j] = 0;
        }
    }
}

export class NeuralNetwork {
    layers: Layer[];
    learningRate: number;

    constructor(layerSizes: number[], learningRate: number = 0.01) {
        this.layers = [];
        this.learningRate = learningRate;

        for (let i = 0; i < layerSizes.length - 1; i++) {
            this.layers.push(new Layer(layerSizes[i], layerSizes[i + 1]));
        }
    }

    // ReLU Activation
    private relu(x: number): number {
        return Math.max(0, x);
    }

    private reluDerivative(x: number): number {
        return x > 0 ? 1 : 0;
    }

    // Forward Pass
    public predict(input: number[]): number[] {
        let currentOutput = [...input];

        for (let i = 0; i < this.layers.length; i++) {
            const layer = this.layers[i];
            const nextOutput: number[] = [];

            for (let j = 0; j < layer.outputSize; j++) {
                let sum = layer.biases[j];
                for (let k = 0; k < layer.inputSize; k++) {
                    sum += currentOutput[k] * layer.weights[k][j];
                }
                // Apply ReLU for hidden layers, Linear for output
                if (i < this.layers.length - 1) {
                    nextOutput[j] = this.relu(sum);
                } else {
                    nextOutput[j] = sum;
                }
            }
            currentOutput = nextOutput;
        }

        return currentOutput;
    }

    // Backpropagation Training
    public train(input: number[], target: number[]): number {
        // 1. Forward Pass (Store activations)
        const activations: number[][] = [input];
        const zValues: number[][] = []; // Pre-activation values



        for (let i = 0; i < this.layers.length; i++) {
            const layer = this.layers[i];
            const nextOutput: number[] = [];
            const layerZ: number[] = [];

            for (let j = 0; j < layer.outputSize; j++) {
                let sum = layer.biases[j];
                for (let k = 0; k < layer.inputSize; k++) {
                    sum += activations[i][k] * layer.weights[k][j];
                }
                layerZ[j] = sum;

                if (i < this.layers.length - 1) {
                    nextOutput[j] = this.relu(sum);
                } else {
                    nextOutput[j] = sum;
                }
            }
            zValues.push(layerZ);
            activations.push(nextOutput);

        }

        // Calculate Loss (MSE)
        let loss = 0;
        const outputLayerIndex = this.layers.length - 1;
        const output = activations[activations.length - 1];
        const outputErrors: number[] = [];

        for (let j = 0; j < this.layers[outputLayerIndex].outputSize; j++) {
            const error = output[j] - target[j];
            loss += error * error;
            outputErrors[j] = error; // Derivative of MSE w.r.t output is 2*(output - target), simplified to error for gradient direction
        }

        // 2. Backward Pass
        let layerErrors = outputErrors;

        for (let i = this.layers.length - 1; i >= 0; i--) {
            const layer = this.layers[i];
            const inputActivation = activations[i];
            const prevLayerErrors: number[] = new Array(layer.inputSize).fill(0);

            for (let j = 0; j < layer.outputSize; j++) {
                const errorGradient = layerErrors[j];

                // Update Biases
                layer.biases[j] -= this.learningRate * errorGradient;

                // Update Weights
                for (let k = 0; k < layer.inputSize; k++) {
                    const weightGradient = errorGradient * inputActivation[k];

                    // Propagate error to previous layer
                    prevLayerErrors[k] += layerErrors[j] * layer.weights[k][j];

                    layer.weights[k][j] -= this.learningRate * weightGradient;
                }
            }

            // Apply derivative of activation function for hidden layers
            if (i > 0) {
                for (let k = 0; k < layer.inputSize; k++) {
                    prevLayerErrors[k] *= this.reluDerivative(zValues[i - 1][k]); // Approximation using input activation
                }
            }

            layerErrors = prevLayerErrors;
        }

        return loss / output.length;
    }

    // Clone weights from another network (for Target Network)
    public copyWeightsFrom(other: NeuralNetwork) {
        if (this.layers.length !== other.layers.length) return;

        for (let i = 0; i < this.layers.length; i++) {
            // Deep copy weights
            for (let j = 0; j < this.layers[i].inputSize; j++) {
                this.layers[i].weights[j] = [...other.layers[i].weights[j]];
            }
            // Deep copy biases
            this.layers[i].biases = [...other.layers[i].biases];
        }
    }
}
