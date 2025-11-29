export interface MemoryTrace {
    topic: string;
    lastStudied: Date;
    strength: number; // 1 (weak) to 100 (strong)
    stability: number; // Days until 90% retention loss
}

export class NemesisEngine {
    private memories: Map<string, MemoryTrace> = new Map();

    constructor() {
        // Initialize empty. Memories are formed only when tasks are completed.
    }

    public updateMemory(topic: string, result: 'pass' | 'fail') {
        let trace = this.memories.get(topic);
        if (!trace) {
            trace = { topic, lastStudied: new Date(), strength: 10, stability: 1 };
        }

        const now = new Date();
        trace.lastStudied = now;

        if (result === 'pass') {
            trace.strength = Math.min(100, trace.strength + 20);
            trace.stability *= 2; // Spaced Repetition: Double the interval
        } else {
            trace.strength = Math.max(0, trace.strength - 30);
            trace.stability = 1; // Reset
        }

        this.memories.set(topic, trace);
    }

    public checkForAmbush(): string | null {
        const now = new Date();
        let ambushTopic: string | null = null;
        let lowestRetention = 1.0;

        this.memories.forEach(trace => {
            const daysElapsed = (now.getTime() - trace.lastStudied.getTime()) / (1000 * 60 * 60 * 24);
            // Ebbinghaus Forgetting Curve: R = e^(-t/S)
            const retention = Math.exp(-daysElapsed / trace.stability);

            // Ambush Zone: Retention between 10% and 20% (Critical Danger Zone)
            // We don't ambush if retention is too high (waste of time) or too low (already forgotten)
            if (retention < 0.2 && retention > 0.05) {
                if (retention < lowestRetention) {
                    lowestRetention = retention;
                    ambushTopic = trace.topic;
                }
            }
        });

        // 30% chance to trigger even if not strictly in zone, to keep user on toes
        if (!ambushTopic && Math.random() < 0.3 && this.memories.size > 0) {
            const keys = Array.from(this.memories.keys());
            ambushTopic = keys[Math.floor(Math.random() * keys.length)];
        }

        return ambushTopic;
    }
}
