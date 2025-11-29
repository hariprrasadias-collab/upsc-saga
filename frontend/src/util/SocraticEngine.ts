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
}

export class SocraticEngine {
    private agents: DebateAgent[] = [
        {
            id: 'skeptic',
            name: 'Socrates the Skeptic',
            role: 'The Challenger',
            persona: 'Questions assumptions, demands definitions, exposes contradictions.',
            color: '#e74c3c', // Red
            avatar: '🤔'
        },
        {
            id: 'idealist',
            name: 'Plato the Idealist',
            role: 'The Visionary',
            persona: 'Focuses on moral ideals, perfect forms, and "what ought to be".',
            color: '#3498db', // Blue
            avatar: '✨'
        },
        {
            id: 'realist',
            name: 'Aristotle the Realist',
            role: 'The Pragmatist',
            persona: 'Focuses on empirical evidence, practical implementation, and "what is".',
            color: '#2ecc71', // Green
            avatar: '📜'
        }
    ];

    private topic: string = "";
    private history: DebateTurn[] = [];

    constructor() { }

    public startDebate(topic: string): DebateTurn {
        this.topic = topic;
        this.history = [];

        // Initial Argument by the Idealist
        const turn: DebateTurn = {
            speakerId: 'idealist',
            text: `We must consider "${topic}" not just as a syllabus item, but as a fundamental pillar of a just society. Its theoretical perfection offers a blueprint for governance.`,
            type: 'ARGUMENT',
            timestamp: Date.now()
        };
        this.history.push(turn);
        return turn;
    }

    public nextTurn(): DebateTurn {
        // AI vs AI simulation (Legacy)
        return this.processUserResponse("");
    }

    public processUserResponse(userText: string): DebateTurn {
        const lastTurn = this.history[this.history.length - 1];
        let nextSpeaker: DebateAgent;
        let text = "";
        let type: DebateTurn['type'] = 'ARGUMENT';

        // 1. Analyze User Input (Simple Keyword Heuristics)
        const lowerText = userText.toLowerCase();
        const isIdealistic = lowerText.includes('should') || lowerText.includes('must') || lowerText.includes('ideal') || lowerText.includes('vision');
        const isFactual = lowerText.includes('data') || lowerText.includes('fact') || lowerText.includes('evidence') || lowerText.includes('history');
        // const isUncertain = lowerText.includes('maybe') || lowerText.includes('think') || lowerText.includes('unsure');

        // 2. Select Next Speaker based on User's Stance
        // If user is Idealistic -> Realist attacks with practicality
        // If user is Factual -> Idealist attacks with moral purpose
        // If user is Uncertain -> Skeptic attacks with doubt
        // Default -> Rotate

        if (userText === "") {
            // Simulation Mode (Auto-play)
            if (lastTurn.speakerId === 'idealist') {
                nextSpeaker = this.agents.find(a => a.id === 'skeptic')!;
                text = `But is that truly feasible? You speak of ideals regarding "${this.topic}", but have you considered the inherent contradictions?`;
                type = 'QUESTION';
            } else if (lastTurn.speakerId === 'skeptic') {
                nextSpeaker = this.agents.find(a => a.id === 'realist')!;
                text = `While the skepticism is valid, we have empirical data. Historically, "${this.topic}" has functioned when specific practical constraints are met.`;
                type = 'REBUTTAL';
            } else {
                nextSpeaker = this.agents.find(a => a.id === 'idealist')!;
                text = `But mechanics without vision are aimless! "${this.topic}" must first serve a higher purpose.`;
                type = 'ARGUMENT';
            }
        } else {
            // Interactive Mode
            if (isIdealistic) {
                nextSpeaker = this.agents.find(a => a.id === 'realist')!;
                text = `Your vision is noble, but how does it survive contact with reality? In the real world, "${this.topic}" faces logistical and economic barriers you are ignoring.`;
                type = 'REBUTTAL';
            } else if (isFactual) {
                nextSpeaker = this.agents.find(a => a.id === 'idealist')!;
                text = `Data is cold and meaningless without a moral compass. Even if the facts support you, does "${this.topic}" align with the ultimate good of society?`;
                type = 'QUESTION';
            } else {
                nextSpeaker = this.agents.find(a => a.id === 'skeptic')!;
                text = `You seem unsure. If you cannot define "${this.topic}" with certainty, how can you claim to understand it? Define your terms precisely.`;
                type = 'QUESTION';
            }
        }

        const turn: DebateTurn = {
            speakerId: nextSpeaker.id,
            text,
            type,
            timestamp: Date.now()
        };
        this.history.push(turn);
        return turn;
    }

    public getAgents(): DebateAgent[] {
        return this.agents;
    }

    public getHistory(): DebateTurn[] {
        return this.history;
    }
}
