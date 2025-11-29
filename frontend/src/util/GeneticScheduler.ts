

// --- Types ---

export interface Task {
    id: string;
    subject: string;
    topic: string; // "Activity" in the dashboard
    durationMinutes: number; // Estimated duration
    deadline?: Date;
    priority: 'high' | 'medium' | 'low';
    originalDate?: string;
}

export interface TimeSlot {
    date: string; // YYYY-MM-DD
    startTime: number; // Minutes from midnight (e.g., 9:00 AM = 540)
    endTime: number;
    isWorkHours: boolean; // False for 11 PM - 6 AM
}

export interface ScheduleGene {
    taskId: string;
    assignedSlotIndex: number; // Index in the availableSlots array
}

export interface Genome {
    genes: ScheduleGene[];
    fitness: number;
}

export interface SchedulerConfig {
    workStartHour: number; // e.g., 6 (6 AM)
    workEndHour: number;   // e.g., 23 (11 PM)
    maxDailySlots: number; // e.g., 6
    populationSize: number;
    generations: number;
    mutationRate: number;
}

// --- Constants ---
const SUBJECT_WEIGHTS: { [key: string]: number } = {
    'History': 0.8, // Heavy
    'Economy': 0.9, // Heavy
    'Polity': 0.8,
    'Geography': 0.7,
    'Environment': 0.6,
    'Science': 0.6,
    'Current Affairs': 0.5,
    'CSAT': 0.4, // Light
    'Ethics': 0.5
};

// --- Core Genetic Algorithm ---

// --- Core Genetic Algorithm with Simulated Annealing (Hybrid GA-SA) ---

import type { GraphLink } from './KnowledgeGraphEngine';

// --- Core Genetic Algorithm with Simulated Annealing (Hybrid GA-SA) ---

export class GeneticScheduler {
    private tasks: Task[];
    private availableSlots: TimeSlot[];
    private config: SchedulerConfig;
    private links: GraphLink[]; // Semantic Knowledge Graph

    constructor(tasks: Task[], availableSlots: TimeSlot[], config: SchedulerConfig, links: GraphLink[] = []) {
        this.tasks = tasks;
        this.availableSlots = availableSlots;
        this.config = config;
        this.links = links;
    }

    public optimize(): ScheduleGene[] {
        let population = this.initializePopulation();

        // Phase 1: Global Search (Genetic Algorithm)
        for (let gen = 0; gen < this.config.generations; gen++) {
            // 1. Evaluate Fitness
            population.forEach(genome => {
                genome.fitness = this.calculateFitness(genome);
            });

            // Sort by fitness (descending)
            population.sort((a, b) => b.fitness - a.fitness);

            // 2. Selection (Elitism + Tournament)
            const nextGeneration: Genome[] = [];

            // Keep top 10% (Elitism)
            const eliteCount = Math.floor(this.config.populationSize * 0.1);
            nextGeneration.push(...population.slice(0, eliteCount));

            // Fill rest
            while (nextGeneration.length < this.config.populationSize) {
                const parentA = this.tournamentSelect(population);
                const parentB = this.tournamentSelect(population);

                let child = this.crossover(parentA, parentB);

                // 3. Mutation
                if (Math.random() < this.config.mutationRate) {
                    child = this.mutate(child);
                }

                nextGeneration.push(child);
            }

            population = nextGeneration;
        }

        // Get best candidate from GA
        population.forEach(g => g.fitness = this.calculateFitness(g));
        population.sort((a, b) => b.fitness - a.fitness);
        let bestGenome = population[0];

        // Phase 2: Local Refinement (Simulated Annealing)
        // Refine the best candidate to find local optima
        bestGenome = this.simulatedAnnealing(bestGenome);

        return bestGenome.genes;
    }

    private simulatedAnnealing(initialGenome: Genome): Genome {
        let currentGenome = { ...initialGenome };
        currentGenome.fitness = this.calculateFitness(currentGenome);

        let bestGenome = { ...currentGenome };

        let temperature = 1000; // Initial temperature
        const coolingRate = 0.95;
        const minTemperature = 1;

        while (temperature > minTemperature) {
            // Create neighbor by mutating slightly
            const neighbor = this.mutate(currentGenome);
            neighbor.fitness = this.calculateFitness(neighbor);

            // Calculate energy delta (we want to maximize fitness, so delta is neighbor - current)
            const delta = neighbor.fitness - currentGenome.fitness;

            // Acceptance probability
            // If better (delta > 0), probability > 1, always accept
            // If worse (delta < 0), probability < 1, accept with probability exp(delta/T)
            if (delta > 0 || Math.random() < Math.exp(delta / temperature)) {
                currentGenome = neighbor;

                if (currentGenome.fitness > bestGenome.fitness) {
                    bestGenome = { ...currentGenome };
                }
            }

            temperature *= coolingRate;
        }

        return bestGenome;
    }

    private initializePopulation(): Genome[] {
        const population: Genome[] = [];
        for (let i = 0; i < this.config.populationSize; i++) {
            const genes: ScheduleGene[] = this.tasks.map(task => ({
                taskId: task.id,
                assignedSlotIndex: Math.floor(Math.random() * this.availableSlots.length)
            }));
            population.push({ genes, fitness: 0 });
        }
        return population;
    }

    private calculateFitness(genome: Genome): number {
        let score = 1000; // Base score

        const slotUsage = new Map<number, number>(); // SlotIndex -> Count
        const dailyLoad = new Map<string, number>(); // Date -> Minutes

        genome.genes.forEach(gene => {
            const slot = this.availableSlots[gene.assignedSlotIndex];
            const task = this.tasks.find(t => t.id === gene.taskId);

            if (!task || !slot) return;

            // --- HARD CONSTRAINTS (Heavy Penalties) ---

            // 1. Overbooking: Multiple tasks in same slot
            const currentUsage = slotUsage.get(gene.assignedSlotIndex) || 0;
            if (currentUsage > 0) {
                score -= 500; // Major penalty for collision
            }
            slotUsage.set(gene.assignedSlotIndex, currentUsage + 1);

            // 2. Sleep Protection (11 PM - 6 AM)
            if (!slot.isWorkHours) {
                score -= 1000; // Impossible schedule
            }

            // 3. Daily Load Limit (Burnout Protection)
            const currentLoad = dailyLoad.get(slot.date) || 0;
            if (currentLoad + task.durationMinutes > (this.config.maxDailySlots * 60)) { // Assuming 60 min slots
                score -= 200; // Burnout risk
            }
            dailyLoad.set(slot.date, currentLoad + task.durationMinutes);

            // 3.5 Subject Diversity (Boredom Protection)
            const weight = SUBJECT_WEIGHTS[task.subject] || 0.5;
            const isMorning = slot.startTime < 720;

            if (weight > 0.7 && isMorning) score += 20;
            if (weight > 0.7 && !isMorning) score -= 10;

            // 5. Context Switching
            // (Requires checking adjacent slots, simplified here for performance)

            // 6. Deadline Adherence
            if (task.deadline) {
                const slotDate = new Date(slot.date);
                if (slotDate > task.deadline) {
                    score -= 300; // Missed deadline
                }
            }
        });

        // 6.5 Semantic Coherence Bonus (The Weaver)
        // Reward scheduling related topics close together (Interleaved Learning)
        if (this.links.length > 0) {
            const scheduledTasks = genome.genes.map(g => ({
                task: this.tasks.find(t => t.id === g.taskId)!,
                slot: this.availableSlots[g.assignedSlotIndex]
            })).filter(item => item.task && item.slot).sort((a, b) => {
                const timeA = new Date(a.slot.date).getTime() + a.slot.startTime;
                const timeB = new Date(b.slot.date).getTime() + b.slot.startTime;
                return timeA - timeB;
            });

            for (let i = 0; i < scheduledTasks.length; i++) {
                const current = scheduledTasks[i];
                // Look ahead at next few tasks (e.g., within next 48 hours)
                for (let j = i + 1; j < Math.min(i + 5, scheduledTasks.length); j++) {
                    const next = scheduledTasks[j];

                    // Check time difference (in days)
                    const dateA = new Date(current.slot.date);
                    const dateB = new Date(next.slot.date);
                    const diffDays = Math.abs((dateB.getTime() - dateA.getTime()) / (1000 * 60 * 60 * 24));

                    if (diffDays <= 2) {
                        // Check for semantic link
                        // We check if the task TOPICS or SUBJECTS are linked
                        // The GraphLink uses IDs like 'Hist_Modern', 'Pol_Const'.
                        // Our tasks have 'subject' (History) and 'topic' (NCERT Class 8...).
                        // Mapping is tricky. For MVP, we check if subjects match Graph Groups or if topics contain keywords.

                        // Simplified: Check if subjects are linked in our graph logic
                        // We need a way to map Task -> GraphNode ID.
                        // For now, let's use a heuristic: Check if the link source/target matches the subject/group.

                        const link = this.links.find(l =>
                            (l.source.includes(current.task.subject.substring(0, 3)) && l.target.includes(next.task.subject.substring(0, 3))) ||
                            (l.target.includes(current.task.subject.substring(0, 3)) && l.source.includes(next.task.subject.substring(0, 3)))
                        );

                        if (link) {
                            score += 50 * link.strength; // Bonus for semantic connection
                        }
                    }
                }
            }
        }

        // 7. Prerequisite Check (NCERT First)
        // Ensure Tier 1 (NCERT) tasks are scheduled before Tier 2 (Standard Books) for the same subject
        const subjectSchedules: { [subject: string]: { tier: number, time: number }[] } = {};

        genome.genes.forEach(gene => {
            const slot = this.availableSlots[gene.assignedSlotIndex];
            const task = this.tasks.find(t => t.id === gene.taskId);
            if (!task || !slot) return;

            if (!subjectSchedules[task.subject]) {
                subjectSchedules[task.subject] = [];
            }

            // Determine Tier
            let tier = 2; // Default to Standard
            const lowerTopic = task.topic.toLowerCase();
            if (lowerTopic.includes('ncert') || lowerTopic.includes('class 6') || lowerTopic.includes('class 7') || lowerTopic.includes('class 8') || lowerTopic.includes('class 9') || lowerTopic.includes('class 10') || lowerTopic.includes('class 11') || lowerTopic.includes('class 12')) {
                tier = 1; // Basic
            }

            // Calculate absolute time (approximate for ordering)
            const slotDate = new Date(slot.date).getTime();
            const absoluteTime = slotDate + (slot.startTime * 60 * 1000);

            subjectSchedules[task.subject].push({ tier, time: absoluteTime });
        });

        // Check for violations
        Object.keys(subjectSchedules).forEach(subject => {
            const schedules = subjectSchedules[subject].sort((a, b) => a.time - b.time);

            let maxTierSeen = 0;
            schedules.forEach(s => {
                if (s.tier < maxTierSeen) {
                    // Violation: Found a Tier 1 task AFTER a Tier 2 task
                    score -= 1000; // Massive penalty to enforce prerequisites
                }
                maxTierSeen = Math.max(maxTierSeen, s.tier);
            });
        });

        return score;
    }

    private tournamentSelect(population: Genome[]): Genome {
        const k = 3;
        let best = population[Math.floor(Math.random() * population.length)];
        for (let i = 0; i < k; i++) {
            const contestant = population[Math.floor(Math.random() * population.length)];
            if (contestant.fitness > best.fitness) {
                best = contestant;
            }
        }
        return best;
    }

    private crossover(parentA: Genome, parentB: Genome): Genome {
        // Uniform Crossover
        const childGenes: ScheduleGene[] = [];
        for (let i = 0; i < parentA.genes.length; i++) {
            childGenes.push(Math.random() < 0.5 ? parentA.genes[i] : parentB.genes[i]);
        }
        return { genes: childGenes, fitness: 0 };
    }

    private mutate(genome: Genome): Genome {
        const mutatedGenes = [...genome.genes];
        // Mutate one random gene
        const indexToMutate = Math.floor(Math.random() * mutatedGenes.length);
        mutatedGenes[indexToMutate] = {
            ...mutatedGenes[indexToMutate],
            assignedSlotIndex: Math.floor(Math.random() * this.availableSlots.length)
        };
        return { genes: mutatedGenes, fitness: 0 };
    }
}
