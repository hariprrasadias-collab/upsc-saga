// /frontend/src/components/AnkiDojo/ebisuAlgorithm.ts
/**
 * Simplified Ebisu Algorithm Implementation for GoodNotes-style Smart Learn
 * 
 * Ebisu is a Bayesian spaced repetition algorithm that:
 * - Tracks a "half-life" for each card (time until 50% recall probability)
 * - Updates beliefs based on performance using Bayesian statistics
 * - Calculates optimal review intervals
 */

export interface CardMemory {
    cardId: number;
    halfLife: number;        // Time (in hours) until 50% recall probability
    lastReviewTime: number;  // Timestamp of last review
    alpha: number;           // Beta distribution parameter (successes)
    beta: number;            // Beta distribution parameter (failures)
    reviewCount: number;     // Total number of reviews
}

// Default initial parameters (GoodNotes-like settings)
const INITIAL_HALF_LIFE = 24;        // 1 day
const MULTIPLIER_CORRECT = 1.3;      // GoodNotes uses ~1.3x multiplier
const MULTIPLIER_INCORRECT = 0.5;    // Reduce half-life on failure
const MIN_HALF_LIFE = 1;             // Minimum 1 hour
const MAX_HALF_LIFE = 24 * 365;      // Maximum 1 year

export class EbisuScheduler {
    private cardMemories: Map<number, CardMemory> = new Map();

    /**
     * Initialize or get card memory
     */
    getCardMemory(cardId: number): CardMemory {
        if (!this.cardMemories.has(cardId)) {
            this.cardMemories.set(cardId, {
                cardId,
                halfLife: INITIAL_HALF_LIFE,
                lastReviewTime: Date.now(),
                alpha: 3,  // Prior: slight bias towards success
                beta: 1,
                reviewCount: 0
            });
        }
        return this.cardMemories.get(cardId)!;
    }

    /**
     * Calculate recall probability based on elapsed time and half-life
     * P(recall) = 2^(-elapsed / halfLife)
     */
    calculateRecallProbability(memory: CardMemory): number {
        const elapsed = (Date.now() - memory.lastReviewTime) / (1000 * 60 * 60); // hours
        return Math.pow(2, -elapsed / memory.halfLife);
    }

    /**
     * Update card memory based on performance (Bayesian update)
     * @param cardId - The card ID
     * @param ease - 1=Again(Wrong), 2=Hard, 3=Good, 4=Easy
     */
    updateAfterReview(cardId: number, ease: number): CardMemory {
        const memory = this.getCardMemory(cardId);
        const now = Date.now();


        // Bayesian update based on performance
        const isSuccess = ease >= 3; // Good or Easy counts as success

        if (isSuccess) {
            // Update Beta distribution: add success
            memory.alpha += 1;

            // Increase half-life (Ebisu-style update)
            let multiplier = MULTIPLIER_CORRECT;
            if (ease === 4) {
                // "Easy" cards get extra boost
                multiplier = MULTIPLIER_CORRECT * 1.5;
            }
            memory.halfLife = Math.min(
                memory.halfLife * multiplier,
                MAX_HALF_LIFE
            );
        } else {
            // Update Beta distribution: add failure
            memory.beta += 1;

            // Decrease half-life
            let multiplier = MULTIPLIER_INCORRECT;
            if (ease === 1) {
                // "Wrong" cards get even shorter interval
                multiplier = MULTIPLIER_INCORRECT * 0.8;
            }
            memory.halfLife = Math.max(
                memory.halfLife * multiplier,
                MIN_HALF_LIFE
            );
        }

        memory.lastReviewTime = now;
        memory.reviewCount += 1;

        return memory;
    }

    /**
     * Calculate when to review next (in hours)
     */
    getNextReviewInterval(cardId: number): number {
        const memory = this.getCardMemory(cardId);
        // Review when recall probability drops to ~50%
        return memory.halfLife;
    }

    /**
     * Get cards that are due for review based on recall probability threshold
     */
    getDueCards(threshold: number = 0.7): number[] {
        const dueCards: number[] = [];

        this.cardMemories.forEach((memory, cardId) => {
            const recallProb = this.calculateRecallProbability(memory);
            if (recallProb <= threshold) {
                dueCards.push(cardId);
            }
        });

        return dueCards;
    }

    /**
     * Sort cards by priority (lowest recall probability first)
     */
    sortCardsByPriority(cardIds: number[]): number[] {
        return cardIds.sort((a, b) => {
            const memA = this.getCardMemory(a);
            const memB = this.getCardMemory(b);
            const probA = this.calculateRecallProbability(memA);
            const probB = this.calculateRecallProbability(memB);
            return probA - probB; // Lowest probability first
        });
    }

    /**
     * Get statistics for a card
     */
    getCardStats(cardId: number) {
        const memory = this.getCardMemory(cardId);
        const recallProb = this.calculateRecallProbability(memory);
        const nextReview = this.getNextReviewInterval(cardId);

        return {
            halfLife: memory.halfLife,
            recallProbability: recallProb,
            nextReviewHours: nextReview,
            reviewCount: memory.reviewCount,
            successRate: memory.alpha / (memory.alpha + memory.beta)
        };
    }

    /**
     * Export memory state (for persistence)
     */
    exportState(): string {
        return JSON.stringify(Array.from(this.cardMemories.entries()));
    }

    /**
     * Import memory state (from persistence)
     */
    importState(state: string) {
        try {
            const entries = JSON.parse(state);
            this.cardMemories = new Map(entries);
        } catch (e) {
            console.error('Failed to import Ebisu state:', e);
        }
    }
}

// Singleton instance
export const ebisuScheduler = new EbisuScheduler();
