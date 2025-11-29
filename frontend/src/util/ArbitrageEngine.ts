// Syllabus Arbitrage Engine - Game Theory Implementation

export interface TopicROI {
    topic: string;
    probability: number;       // 0-1: Likelihood of appearing in exam
    complexity: number;        // 0-1: Difficulty to master (Cost)
    competitionMastery: number; // 0-1: How well others know this (Saturation)
    roiScore: number;          // Calculated Arbitrage Score
}

export interface ArbitrageOpportunity {
    topic: string;
    score: number;
    reason: string;
    action: 'BUY' | 'HOLD' | 'SELL'; // BUY = Study Now, HOLD = Revise, SELL = Skip/Low Priority
}

export class ArbitrageEngine {
    private topics: TopicROI[] = [];

    constructor() {
        this.initializeMarketData();
    }

    // --- Market Data Initialization (Simulated for now) ---
    private initializeMarketData() {
        // In a real app, this would come from analyzing past papers and user stats
        this.topics = [
            { topic: 'Modern History', probability: 0.9, complexity: 0.4, competitionMastery: 0.8, roiScore: 0 },
            { topic: 'Art & Culture', probability: 0.6, complexity: 0.8, competitionMastery: 0.3, roiScore: 0 }, // High Arbitrage?
            { topic: 'Polity', probability: 0.95, complexity: 0.3, competitionMastery: 0.9, roiScore: 0 },      // Saturated
            { topic: 'Environment', probability: 0.8, complexity: 0.5, competitionMastery: 0.6, roiScore: 0 },
            { topic: 'Science & Tech', probability: 0.7, complexity: 0.7, competitionMastery: 0.4, roiScore: 0 },
            { topic: 'Ethics', probability: 0.85, complexity: 0.4, competitionMastery: 0.5, roiScore: 0 },
            { topic: 'Economics', probability: 0.8, complexity: 0.6, competitionMastery: 0.7, roiScore: 0 },
            { topic: 'International Relations', probability: 0.6, complexity: 0.5, competitionMastery: 0.5, roiScore: 0 }
        ];

        this.calculateMarketMetrics();
    }

    // --- Core Game Theory Logic ---

    private calculateMarketMetrics() {
        this.topics.forEach(t => {
            // ROI Formula: (Probability / Complexity) * (1 - CompetitionMastery)
            // We want High Probability, Low Complexity, and Low Competition

            // 1. Value = Probability / (Complexity + 0.1) -> Avoid div by zero
            const intrinsicValue = t.probability / (t.complexity + 0.2);

            // 2. Arbitrage Multiplier = 1 + (1 - CompetitionMastery)
            // If everyone knows it (0.9), multiplier is small (1.1). If no one knows it (0.1), multiplier is large (1.9).
            const arbitrageMultiplier = 1 + (1 - t.competitionMastery);

            t.roiScore = intrinsicValue * arbitrageMultiplier;
        });
    }

    public getArbitrageOpportunities(): ArbitrageOpportunity[] {
        // Sort by ROI descending
        const sortedTopics = [...this.topics].sort((a, b) => b.roiScore - a.roiScore);

        return sortedTopics.map(t => {
            let action: 'BUY' | 'HOLD' | 'SELL' = 'HOLD';
            let reason = '';

            if (t.roiScore > 2.0) {
                action = 'BUY';
                reason = 'High Yield, Low Competition (Hidden Gem)';
            } else if (t.roiScore > 1.2) {
                action = 'HOLD';
                reason = 'Stable Returns, Moderate Competition';
            } else {
                action = 'SELL';
                reason = 'Over-saturated / Low Yield';
            }

            return {
                topic: t.topic,
                score: parseFloat(t.roiScore.toFixed(2)),
                reason,
                action
            };
        });
    }

    public getTopOpportunities(count: number = 3): ArbitrageOpportunity[] {
        return this.getArbitrageOpportunities()
            .filter(op => op.action === 'BUY')
            .slice(0, count);
    }

    public getTopicColor(topicName: string): string {
        const opp = this.getArbitrageOpportunities().find(o => topicName.includes(o.topic));
        if (!opp) return '';

        switch (opp.action) {
            case 'BUY': return '#f1c40f'; // Gold
            case 'HOLD': return '#3498db'; // Blue
            case 'SELL': return '#e74c3c'; // Red
            default: return '';
        }
    }
}
