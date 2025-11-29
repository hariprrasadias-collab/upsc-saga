// Strategos RL Agent - Deep Q-Network (DQN) Implementation
import { NeuralNetwork } from './NeuralNetwork';

// --- Types ---

export type TimeOfDay = 'MORNING' | 'AFTERNOON' | 'EVENING' | 'NIGHT';
export type BacklogLevel = 'NONE' | 'LOW' | 'HIGH' | 'CRITICAL';
export type EnergyLevel = 'HIGH' | 'MEDIUM' | 'LOW' | 'BURNOUT';

export interface AgentState {
    timeOfDay: TimeOfDay;
    backlogLevel: BacklogLevel;
    energyLevel: EnergyLevel;
    lastActionSuccess: boolean;
    oracleRisk?: string;
}

export type AgentAction =
    | 'MAINTAIN_PACE'
    | 'SUGGEST_BREAK'
    | 'SWITCH_SUBJECT'
    | 'INCREASE_INTENSITY'
    | 'SCHEDULE_MOCK'
    | 'CRISIS_MODE';

interface Experience {
    state: number[];
    action: number;
    reward: number;
    nextState: number[];
    done: boolean;
}

// --- Constants ---

const ACTIONS: AgentAction[] = [
    'MAINTAIN_PACE',
    'SUGGEST_BREAK',
    'SWITCH_SUBJECT',
    'INCREASE_INTENSITY',
    'SCHEDULE_MOCK',
    'CRISIS_MODE'
];

const LEARNING_RATE = 0.01;
const DISCOUNT_FACTOR = 0.95; // Gamma
const EPSILON_START = 1.0;
const EPSILON_END = 0.1;
const EPSILON_DECAY = 0.995;
const BATCH_SIZE = 32;
const MEMORY_SIZE = 2000;
const TARGET_UPDATE_FREQ = 10; // Update target network every N steps

// --- Agent Class ---

export class RLAgent {
    private policyNet: NeuralNetwork;
    private targetNet: NeuralNetwork;
    private memory: Experience[] = [];
    private epsilon: number = EPSILON_START;
    private steps: number = 0;
    private lastLoss: number = 0;

    private lastState: AgentState | null = null;
    private lastActionIndex: number | null = null;

    constructor() {
        // Input: 4 features (Time, Backlog, Energy, Success)
        // Hidden: 16 neurons
        // Output: 6 actions
        this.policyNet = new NeuralNetwork([4, 16, 6], LEARNING_RATE);
        this.targetNet = new NeuralNetwork([4, 16, 6], LEARNING_RATE);
        this.targetNet.copyWeightsFrom(this.policyNet);

        this.loadBrain();
    }

    // --- Core Logic ---

    public decide(state: AgentState): AgentAction {
        // 0. Crisis Check (Oracle Override)
        if (state.oracleRisk && state.oracleRisk.includes("High")) {
            return 'CRISIS_MODE';
        }

        const stateVector = this.encodeState(state);

        let actionIndex: number;

        // Epsilon-Greedy Strategy
        if (Math.random() < this.epsilon) {
            // Explore
            actionIndex = Math.floor(Math.random() * ACTIONS.length);
        } else {
            // Exploit
            const qValues = this.policyNet.predict(stateVector);
            actionIndex = qValues.indexOf(Math.max(...qValues));
        }

        // Store for learning step
        this.lastState = state;
        this.lastActionIndex = actionIndex;

        return ACTIONS[actionIndex];
    }

    public learn(reward: number, newState: AgentState): void {
        if (!this.lastState || this.lastActionIndex === null) return;

        const stateVector = this.encodeState(this.lastState);
        const nextStateVector = this.encodeState(newState);

        // Store experience
        this.memory.push({
            state: stateVector,
            action: this.lastActionIndex,
            reward: reward,
            nextState: nextStateVector,
            done: false
        });

        if (this.memory.length > MEMORY_SIZE) {
            this.memory.shift(); // Remove oldest
        }

        // Train if enough memory
        if (this.memory.length >= BATCH_SIZE) {
            this.replay();
        }

        // Decay Epsilon
        if (this.epsilon > EPSILON_END) {
            this.epsilon *= EPSILON_DECAY;
        }

        // Update Target Network
        this.steps++;
        if (this.steps % TARGET_UPDATE_FREQ === 0) {
            this.targetNet.copyWeightsFrom(this.policyNet);
        }

        this.saveBrain();
    }

    private replay() {
        // Sample Mini-batch
        const batch = [];
        for (let i = 0; i < BATCH_SIZE; i++) {
            const index = Math.floor(Math.random() * this.memory.length);
            batch.push(this.memory[index]);
        }

        let totalLoss = 0;

        batch.forEach(exp => {
            const currentQ = this.policyNet.predict(exp.state);
            const nextQ = this.targetNet.predict(exp.nextState);

            const maxNextQ = Math.max(...nextQ);
            const targetQ = [...currentQ];

            // Bellman Equation: Q(s,a) = r + gamma * max(Q(s',a'))
            targetQ[exp.action] = exp.reward + DISCOUNT_FACTOR * maxNextQ;

            totalLoss += this.policyNet.train(exp.state, targetQ);
        });

        this.lastLoss = totalLoss / BATCH_SIZE;
    }

    // --- Helpers ---

    private encodeState(state: AgentState): number[] {
        // Normalize inputs to 0-1 range roughly
        const timeMap = { 'MORNING': 0, 'AFTERNOON': 0.33, 'EVENING': 0.66, 'NIGHT': 1 };
        const backlogMap = { 'NONE': 0, 'LOW': 0.33, 'HIGH': 0.66, 'CRITICAL': 1 };
        const energyMap = { 'BURNOUT': 0, 'LOW': 0.33, 'MEDIUM': 0.66, 'HIGH': 1 };

        return [
            timeMap[state.timeOfDay],
            backlogMap[state.backlogLevel],
            energyMap[state.energyLevel],
            state.lastActionSuccess ? 1 : 0
        ];
    }

    // --- Persistence ---

    private loadBrain(): void {
        const saved = localStorage.getItem('strategos_dqn_weights');
        if (saved) {
            const weights = JSON.parse(saved);
            // Simple restore logic (assuming structure matches)
            // In a real app, we'd need more robust serialization
            // For now, we just reset epsilon if weights exist
            if (weights) this.epsilon = 0.5;
        }
    }

    private saveBrain(): void {
        // Saving full network state is complex, for this demo we just save a flag
        // In production, we'd serialize layers.weights
        localStorage.setItem('strategos_dqn_weights', 'true');
    }

    // --- Utility for Dashboard ---

    public getStats() {
        return {
            epsilon: this.epsilon.toFixed(4),
            loss: this.lastLoss.toFixed(6),
            memorySize: this.memory.length,
            steps: this.steps
        };
    }

    // --- Meta-Cognitive Control ---
    public getSchedulerParams() {
        // Default Config
        let config = {
            workStartHour: 6,
            workEndHour: 23,
            maxDailySlots: 6,
            populationSize: 50,
            generations: 20,
            mutationRate: 0.1
        };

        if (!this.lastState) return config;

        // Adaptive Logic based on State

        // 1. Crisis / High Backlog -> Increase Capacity
        if (this.lastState.backlogLevel === 'CRITICAL' || this.lastState.backlogLevel === 'HIGH') {
            config.maxDailySlots = 8; // Push harder
            config.generations = 40; // Think harder
        }

        // 2. Burnout / Low Energy -> Reduce Load
        if (this.lastState.energyLevel === 'BURNOUT' || this.lastState.energyLevel === 'LOW') {
            config.maxDailySlots = 4; // Recovery mode
            config.workEndHour = 20; // Stop early
        }

        // 3. Oracle Risk -> High Alert
        if (this.lastState.oracleRisk && this.lastState.oracleRisk.includes('High')) {
            config.maxDailySlots = 7;
            config.mutationRate = 0.3; // Try radical new schedules
        }

        return config;
    }

    public getSuggestionText(action: AgentAction): string {
        const messages: { [key in AgentAction]: string[] } = {
            'MAINTAIN_PACE': [
                "Steady as she goes. Current velocity is optimal.",
                "Systems nominal. Continue current trajectory.",
                "Focus levels stable. Maintain course.",
                "You are in the zone. Don't stop now."
            ],
            'SUGGEST_BREAK': [
                "⚠️ Efficiency dropping. Strategos recommends a 15-min tactical pause.",
                "Cognitive fatigue detected. Refuel required.",
                "Diminishing returns observed. Take a walk, Commander.",
                "System overheating. Cool down for 15 minutes."
            ],
            'SWITCH_SUBJECT': [
                "🔄 Cognitive saturation detected. Switch to a different subject to refresh.",
                "Neural pathways for this topic are exhausted. Rotate engagement.",
                "Cross-training recommended. Switch subjects now.",
                "Variety prevents stagnation. Changing tactical focus."
            ],
            'INCREASE_INTENSITY': [
                "🔥 You are in Flow State. Adding a micro-task to maximize gains.",
                "Performance peaking. Pushing limits.",
                "Opportunity detected. Increasing load.",
                "Strike while the iron is hot. Intensity increased."
            ],
            'SCHEDULE_MOCK': [
                "🎯 Knowledge consolidation required. Scheduling a mini-mock test.",
                "Theory is useless without practice. Mock test initiated.",
                "Testing recall protocols. Prepare for simulation.",
                "Validation required. Schedule a mock test immediately."
            ],
            'CRISIS_MODE': [
                "⚠️ CRITICAL RISK DETECTED. Initiating Emergency Protocols.",
                "📉 Trajectory critical. Cancel all breaks. Focus on high-yield topics.",
                "🚨 DEFCON 1. Immediate intervention required.",
                "Survival mode engaged. Prioritize survival topics."
            ]
        };

        const options = messages[action] || ["Awaiting orders."];
        return options[Math.floor(Math.random() * options.length)];
    }
}

