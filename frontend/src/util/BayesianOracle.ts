// The Oracle - Bayesian Prediction Engine

export interface Point {
    day: number;
    tasksRemaining: number;
}

export interface SimulationResult {
    successProbability: number; // 0 to 100
    bestCaseDate: string;
    worstCaseDate: string;
    averageDate: string;
    riskFactor: string;
    totalSimulations: number;
    paths: {
        best: Point[];
        avg: Point[];
        worst: Point[];
    };
}

export class BayesianOracle {
    private iterations: number = 1000;

    /**
     * Runs a Monte Carlo simulation to predict syllabus completion.
     * @param totalTasks Total number of tasks in the backlog.
     * @param currentVelocity Average tasks completed per day (last 7 days).
     * @param targetDate The exam date.
     */
    public predict(totalTasks: number, currentVelocity: number, targetDate: Date): SimulationResult {
        if (totalTasks === 0) {
            return {
                successProbability: 100,
                bestCaseDate: new Date().toISOString().split('T')[0],
                worstCaseDate: new Date().toISOString().split('T')[0],
                averageDate: new Date().toISOString().split('T')[0],
                riskFactor: "None. Mission Accomplished.",
                totalSimulations: this.iterations,
                paths: { best: [], avg: [], worst: [] }
            };
        }

        const allPaths: Point[][] = [];
        const completionDates: { date: number, pathIndex: number }[] = [];
        let successCount = 0;
        const today = new Date();
        const targetTime = targetDate.getTime();

        // Monte Carlo Simulation Loop
        for (let i = 0; i < this.iterations; i++) {
            let remainingTasks = totalTasks;
            let currentDay = new Date(today);
            let burnoutFactor = 0;
            const path: Point[] = [];
            let dayCount = 0;

            path.push({ day: dayCount, tasksRemaining: remainingTasks });

            while (remainingTasks > 0) {
                // 1. Simulate Daily Velocity (Randomized based on current velocity)
                const variability = (Math.random() - 0.5) * 2 * (currentVelocity * 0.3);
                let dailyOutput = Math.max(0, currentVelocity + variability);

                // 2. Simulate Random Interruptions (10% chance of a "bad day")
                if (Math.random() < 0.1) {
                    dailyOutput *= 0.5; // 50% output on bad days
                }

                // 3. Simulate Burnout (Cumulative fatigue)
                if (currentDay.getDay() === 0 && Math.random() < 0.2) {
                    burnoutFactor += 0.05; // 5% efficiency loss
                }
                dailyOutput *= (1 - Math.min(0.5, burnoutFactor)); // Max 50% burnout penalty

                remainingTasks -= dailyOutput;
                if (remainingTasks < 0) remainingTasks = 0;

                currentDay.setDate(currentDay.getDate() + 1);
                dayCount++;

                // Record path point every 7 days to save memory, or if finished
                if (dayCount % 7 === 0 || remainingTasks === 0) {
                    path.push({ day: dayCount, tasksRemaining: Math.round(remainingTasks) });
                }

                // Cap simulation at 2 years
                if (dayCount > 730) {
                    break;
                }
            }

            allPaths.push(path);
            completionDates.push({ date: currentDay.getTime(), pathIndex: i });

            if (currentDay.getTime() <= targetTime) {
                successCount++;
            }
        }

        // Analysis
        completionDates.sort((a, b) => a.date - b.date);

        const bestRun = completionDates[Math.floor(this.iterations * 0.05)];
        const avgRun = completionDates[Math.floor(this.iterations * 0.50)];
        const worstRun = completionDates[Math.floor(this.iterations * 0.95)];

        const successProb = (successCount / this.iterations) * 100;

        let risk = "Low";
        if (successProb < 50) risk = "High. Velocity insufficient.";
        else if (successProb < 80) risk = "Moderate. Consistency required.";
        else if (currentVelocity < 2) risk = "Velocity Warning. Pace is slow but steady.";

        return {
            successProbability: Math.round(successProb * 10) / 10,
            bestCaseDate: new Date(bestRun.date).toISOString().split('T')[0],
            averageDate: new Date(avgRun.date).toISOString().split('T')[0],
            worstCaseDate: new Date(worstRun.date).toISOString().split('T')[0],
            riskFactor: risk,
            totalSimulations: this.iterations,
            paths: {
                best: allPaths[bestRun.pathIndex],
                avg: allPaths[avgRun.pathIndex],
                worst: allPaths[worstRun.pathIndex]
            }
        };
    }
}
