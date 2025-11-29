export interface ScheduleEvent {
    subject: string;
    timeOfDay: 'MORNING' | 'AFTERNOON' | 'EVENING';
    duration: number;
    completionStatus: 'completed' | 'skipped';
}

export interface CausalWarning {
    cause: string;
    effect: string;
    confidence: number;
    message: string;
}

export class CausalInferenceEngine {
    private history: ScheduleEvent[] = [];

    constructor() {
        // Mock History
        this.history = [
            { subject: 'History', timeOfDay: 'EVENING', duration: 120, completionStatus: 'skipped' },
            { subject: 'History', timeOfDay: 'MORNING', duration: 60, completionStatus: 'completed' },
            { subject: 'Math', timeOfDay: 'EVENING', duration: 120, completionStatus: 'completed' },
            { subject: 'History', timeOfDay: 'EVENING', duration: 90, completionStatus: 'skipped' },
        ];
    }

    public analyzePatterns(): CausalWarning[] {
        const warnings: CausalWarning[] = [];

        // 1. Detect "Evening History" Fatigue
        const eveningHistory = this.history.filter(e => e.subject === 'History' && e.timeOfDay === 'EVENING');
        const skippedEveningHistory = eveningHistory.filter(e => e.completionStatus === 'skipped');

        if (eveningHistory.length > 0) {
            const failRate = skippedEveningHistory.length / eveningHistory.length;
            if (failRate > 0.6) {
                warnings.push({
                    cause: 'Studying History in the Evening',
                    effect: 'High Skip Rate',
                    confidence: failRate,
                    message: `👹 Demon's Insight: You skip History 60% of the time when scheduled in the evening. Move it to Morning.`
                });
            }
        }

        // 2. Detect "Marathon Burnout" (Duration > 90m)
        const longSessions = this.history.filter(e => e.duration > 90);
        const skippedLong = longSessions.filter(e => e.completionStatus === 'skipped');
        if (longSessions.length > 0) {
            const burnoutRate = skippedLong.length / longSessions.length;
            if (burnoutRate > 0.5) {
                warnings.push({
                    cause: 'Sessions longer than 90 mins',
                    effect: 'Burnout / Skipping',
                    confidence: burnoutRate,
                    message: `👹 Demon's Insight: Long sessions (>90m) have a high failure rate. Break them down.`
                });
            }
        }

        return warnings;
    }

    public getConfidence(): number {
        const warnings = this.analyzePatterns();
        if (warnings.length === 0) return 0;
        // Return the highest confidence found in warnings, converted to percentage
        return Math.max(...warnings.map(w => w.confidence)) * 100;
    }
}
