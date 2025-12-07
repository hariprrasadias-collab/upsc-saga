// Socratic Debate Engine - Multi-Agent Dialectic System

export interface DebateAgent {
    id: string;
    name: string;
    role: string;
    persona: string;
    color: string;
    avatar: string;
}

export interface DebateTurn {
    speakerId: string;
    text: string;
    type: 'ARGUMENT' | 'REBUTTAL' | 'QUESTION' | 'CONCLUSION';
    timestamp: number;
    thoughts?: string;
    score?: {
        logic: number;
        relevance: number;
        impact: number;
    };
}

export class SocraticEngine {
    private agents: DebateAgent[] = [
        {
            id: 'skeptic',
            name: 'Socrates',
            role: 'The Skeptic',
            persona: 'Questions assumptions, demands definitions, exposes contradictions.',
            color: '#e74c3c', // Red
            avatar: '🤔'
        },
        {
            id: 'idealist',
            name: 'Plato',
            role: 'The Idealist',
            persona: 'Focuses on moral ideals, perfect forms, and "what ought to be".',
            color: '#3498db', // Blue
            avatar: '✨'
        },
        {
            id: 'realist',
            name: 'Aristotle',
            role: 'The Realist',
            persona: 'Focuses on empirical evidence, practical implementation, and "what is".',
            color: '#2ecc71', // Green
            avatar: '📜'
        },
        {
            id: 'iconoclast',
            name: 'Nietzsche',
            role: 'The Iconoclast',
            persona: 'Challenges values, focuses on Will to Power, critiques slave morality.',
            color: '#8e44ad', // Purple
            avatar: '⚡'
        },
        {
            id: 'sage',
            name: 'Confucius',
            role: 'The Harmonizer',
            persona: 'Focuses on social order, ritual, duty, and ethics.',
            color: '#f1c40f', // Yellow
            avatar: '🎍'
        },
        {
            id: 'strategist',
            name: 'Machiavelli',
            role: 'The Pragmatist',
            persona: 'Focuses on power dynamics, effectiveness, and realpolitik.',
            color: '#34495e', // Dark Blue/Grey
            avatar: '♟️'
        }
    ];

    private topic: string = "";
    private history: DebateTurn[] = [];

    constructor() { }

    public startDebate(topic: string): DebateTurn {
        this.topic = topic;
        this.history = [];

        // Initial Argument by the Idealist (or random in future)
        const turn: DebateTurn = {
            speakerId: 'idealist',
            text: `We must consider "${topic}" not just as a syllabus item, but as a fundamental pillar of a just society. Its theoretical perfection offers a blueprint for governance.`,
            type: 'ARGUMENT',
            timestamp: Date.now()
        };
        this.history.push(turn);
        return turn;
    }



    public async fetchNextTurn(userText: string): Promise<DebateTurn> {
        // 1. Add User Turn to History (if any)
        if (userText) {
            this.history.push({
                speakerId: 'user',
                text: userText,
                type: 'ARGUMENT',
                timestamp: Date.now()
            });
        }

        // 2. Call Backend API
        try {
            const response = await fetch('http://localhost:5000/api/socratic/debate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    topic: this.topic,
                    history: this.history,
                    user_input: userText || null
                })
            });

            if (!response.ok) throw new Error('Failed to fetch debate turn');

            const data = await response.json();

            const turn: DebateTurn = {
                speakerId: data.speakerId,
                text: data.text,
                type: data.type,
                timestamp: Date.now(),
                thoughts: data.thoughts,
                score: data.score
            };

            this.history.push(turn);
            return turn;
        } catch (error) {
            console.error("Socratic Engine Error:", error);
            const errorTurn: DebateTurn = {
                speakerId: 'skeptic',
                text: "I cannot hear the other voices... (Connection Error)",
                type: 'ARGUMENT',
                timestamp: Date.now()
            };
            this.history.push(errorTurn);
            return errorTurn;
        }
    }

    public getAgents(): DebateAgent[] {
        return this.agents;
    }

    public getHistory(): DebateTurn[] {
        return this.history;
    }
}
