import React, { useState, useEffect } from 'react';
import './StudyPlanDashboard.css';
import FlashcardsManager from '../Flashcards/FlashcardsManager';
import {
    BarChart, Bar, XAxis, YAxis, Tooltip as RechartsTooltip, ResponsiveContainer,
    PieChart, Pie, Cell, AreaChart, Area, CartesianGrid,
    Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis
} from 'recharts';

import { generateCSVTaskId } from '../../util/taskUtils';
import { GeneticScheduler } from '../../util/GeneticScheduler';
import type { Task as GTask, TimeSlot } from '../../util/GeneticScheduler';
import { RLAgent, type AgentState, type AgentAction } from '../../util/RLAgent';
import { ArbitrageEngine, type ArbitrageOpportunity } from '../../util/ArbitrageEngine';
import { KnowledgeGraphEngine, type GraphNode } from '../../util/KnowledgeGraphEngine';
import NexusGraph from './NexusGraph';

import { BayesianOracle, type SimulationResult } from '../../util/BayesianOracle';
import { FlowAudioEngine } from '../../util/FlowAudioEngine';
import { NemesisEngine } from '../../util/NemesisEngine';
import { CausalInferenceEngine, type CausalWarning } from '../../util/CausalInferenceEngine';

import { audioManager } from '../../util/AudioManager';

interface Slot {
    id: string;
    time: string;
    subject: string;
    activity: string;
    status: 'pending' | 'completed' | 'skipped' | 'rescheduled';
    resource_link?: string;
}

interface DayPlan {
    date: string;
    day: string;
    slots: Slot[];
}

type ViewMode = 'daily' | 'weekly' | 'monthly' | 'yearly' | 'overall' | 'flashcards' | 'nexus';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d'];

const StudyPlanDashboard: React.FC = () => {
    const [plan, setPlan] = useState<DayPlan[]>([]);
    const [loading, setLoading] = useState(false);
    const [viewMode, setViewMode] = useState<ViewMode>('daily');
    const [selectedTask, setSelectedTask] = useState<Slot | null>(null);
    const [isOptimizing, setIsOptimizing] = useState(false);

    // Strategos Agent State
    const [agent] = useState(() => new RLAgent());
    const [agentSuggestion, setAgentSuggestion] = useState<string>("");
    const [agentAction, setAgentAction] = useState<AgentAction>('MAINTAIN_PACE');

    // Syllabus Arbitrage Engine
    const [arbitrageEngine] = useState(() => new ArbitrageEngine());
    const [nexusEngine] = useState(() => new KnowledgeGraphEngine());

    // Socratic Debate State
    const [isDebateOpen, setIsDebateOpen] = useState(false);

    // Market Opportunities
    const [marketOpportunities, setMarketOpportunities] = useState<ArbitrageOpportunity[]>([]);

    useEffect(() => {
        setMarketOpportunities(arbitrageEngine.getArbitrageOpportunities());
    }, [arbitrageEngine]);

    // The Oracle
    const [oracle] = useState(() => new BayesianOracle());
    const [oraclePrediction, setOraclePrediction] = useState<SimulationResult | null>(null);

    // Flow State Audio
    const [flowEngine] = useState(() => new FlowAudioEngine());
    const [isFlowMode, setIsFlowMode] = useState(false);

    // Nemesis (Adversarial Forgetting)
    const [nemesis] = useState(() => new NemesisEngine());
    const [ambushTopic, setAmbushTopic] = useState<string | null>(null);

    // Laplace's Demon (Causal Inference)
    const [demon] = useState(() => new CausalInferenceEngine());
    const [demonWarnings, setDemonWarnings] = useState<CausalWarning[]>([]);

    // Phase 14: Deep Sync State
    const [filterTopic, setFilterTopic] = useState<string | null>(null);

    // Phase 17: Gamification & Mastery
    const [xp, setXp] = useState<number>(() => parseInt(localStorage.getItem('mimir_xp') || '0'));
    const [godMode, setGodMode] = useState<boolean>(false);

    const level = Math.floor(xp / 100) + 1;
    const nextLevelXp = level * 100;

    useEffect(() => {
        localStorage.setItem('mimir_xp', xp.toString());
    }, [xp]);

    // --- Helper Functions for AI Actions ---

    const executeAgentAction = (action: AgentAction) => {
        audioManager.play('click');
        if (action === 'SCHEDULE_MOCK') {
            const today = new Date().toISOString().split('T')[0];
            const mockTask: Slot = {
                id: `mock-${Date.now()}`,
                time: '09:00 AM',
                subject: 'Mock Test',
                activity: 'Full Length Mock Test (Strategos Ordered)',
                status: 'pending',
                resource_link: 'https://upsc-portal.com/mock-test'
            };

            setPlan(prev => prev.map(d => {
                if (d.date === today) {
                    return { ...d, slots: [mockTask, ...d.slots] };
                }
                return d;
            }));
            alert("Strategos: Mock Test scheduled for today. Good luck, Commander.");
        } else if (action === 'SUGGEST_BREAK') {
            alert("Strategos: Break time logged. Go for a walk.");
        }
        setAgentAction('MAINTAIN_PACE'); // Reset action
    };

    const rescheduleTask = (taskSubject: string) => {
        // Find the task and move it to tomorrow
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        const tomorrowStr = tomorrow.toISOString().split('T')[0];

        setPlan(prev => {
            let taskToMove: Slot | undefined;
            // Remove from current day
            const newPlan = prev.map(d => {
                const found = d.slots.find(s => s.activity.includes(taskSubject));
                if (found) {
                    taskToMove = found;
                    return { ...d, slots: d.slots.filter(s => s.id !== found.id) };
                }
                return d;
            });

            // Add to tomorrow
            if (taskToMove) {
                return newPlan.map(d => {
                    if (d.date === tomorrowStr) {
                        return { ...d, slots: [...d.slots, { ...taskToMove!, status: 'rescheduled' }] };
                    }
                    return d;
                });
            }
            return newPlan;
        });
    };



    const fixSchedule = () => {
        // Simple heuristic: Move last task of today to tomorrow
        const today = new Date().toISOString().split('T')[0];
        setPlan(prev => {
            const todayPlan = prev.find(d => d.date === today);
            if (!todayPlan || todayPlan.slots.length === 0) return prev;

            const lastTask = todayPlan.slots[todayPlan.slots.length - 1];

            // Remove from today
            const step1 = prev.map(d => d.date === today ? { ...d, slots: d.slots.slice(0, -1) } : d);

            // Add to tomorrow
            const tomorrow = new Date();
            tomorrow.setDate(tomorrow.getDate() + 1);
            const tomorrowStr = tomorrow.toISOString().split('T')[0];

            return step1.map(d => d.date === tomorrowStr ? { ...d, slots: [...d.slots, { ...lastTask, status: 'rescheduled' }] } : d);
        });
    };

    // Activity Tracking for Flow Mode
    useEffect(() => {
        // Check for Ambush
        const ambush = nemesis.checkForAmbush();
        if (ambush) {
            setAmbushTopic(ambush);
            audioManager.startLoop('rage');
        }

        // Check for Demon Warnings
        const warnings = demon.analyzePatterns();
        setDemonWarnings(warnings);

        if (!isFlowMode) return;

        let activityScore = 0;
        const decay = setInterval(() => {
            activityScore = Math.max(0, activityScore - 0.05);
            flowEngine.updateIntensity(Math.min(1, activityScore));
        }, 500);

        const handleActivity = () => {
            activityScore = Math.min(1, activityScore + 0.1);
        };

        window.addEventListener('mousemove', handleActivity);
        window.addEventListener('keydown', handleActivity);

        flowEngine.start();

        return () => {
            clearInterval(decay);
            window.removeEventListener('mousemove', handleActivity);
            window.removeEventListener('keydown', handleActivity);
            flowEngine.stop();
        };
    }, [isFlowMode, nemesis, demon, flowEngine]);

    const toggleFlowMode = () => {
        if (isFlowMode) {
            flowEngine.stop();
        }
        setIsFlowMode(!isFlowMode);
    };

    const parseCSV = (csvText: string): DayPlan[] => {
        const lines = csvText.split('\n').filter(line => line.trim() !== '');
        // Skip headers
        const dataRows = lines.slice(1);

        const dayMap: { [key: string]: DayPlan } = {};
        const completedTasks = new Set(JSON.parse(localStorage.getItem('completedTasks') || '[]'));

        dataRows.forEach((row) => {
            // Simple split for now as data seems simple and doesn't contain quoted commas in our generation script
            const columns = row.split(',').map(c => c.trim());

            // Date,Day,Slot_Type,Time,Subject,Topic,Activity_Type,Resources
            const date = columns[0];
            const dayName = columns[1];
            const time = columns[3];
            const subject = columns[4];
            const topic = columns[5];
            const activityType = columns[6];
            const resources = columns[7];

            if (!date || columns.length < 5) return;

            if (!dayMap[date]) {
                dayMap[date] = {
                    date: date,
                    day: dayName,
                    slots: []
                };
            }

            // Use content-based ID to prevent collisions on CSV regeneration
            const taskId = generateCSVTaskId(date, time, subject, topic);
            const isCompleted = completedTasks.has(taskId);

            dayMap[date].slots.push({
                id: taskId, // Now a string
                time: time,
                subject: subject,
                activity: `${topic} (${activityType})`,
                status: isCompleted ? 'completed' : 'pending',
                resource_link: resources !== 'N/A' ? resources : undefined
            });
        });

        return Object.values(dayMap).sort((a, b) => a.date.localeCompare(b.date));
    };

    const fetchCSVPlan = async () => {
        setLoading(true);
        try {
            const response = await fetch('/UPSC_Scheduler.csv');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const csvText = await response.text();
            const parsedPlan = parseCSV(csvText);
            setPlan(parsedPlan);
        } catch (err) {
            console.error("Failed to fetch CSV plan:", err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchCSVPlan();
    }, []);

    // Global Shortcut for ESC
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if (e.key === 'Escape') {
                if (selectedTask) setSelectedTask(null);
                if (ambushTopic) setAmbushTopic(null);
                if (isDebateOpen) setIsDebateOpen(false);
                if (filterTopic) setFilterTopic(null);
            }
        };
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [selectedTask, ambushTopic, isDebateOpen, filterTopic]);

    const handleTaskClick = (slot: Slot) => {
        setSelectedTask(slot);
    };

    const closeModal = () => {
        setSelectedTask(null);
    };

    const toggleTaskStatus = async (task: Slot) => {
        const newStatus: 'pending' | 'completed' | 'skipped' | 'rescheduled' = task.status === 'completed' ? 'pending' : 'completed';

        // Optimistic Update
        const updatedPlan = plan.map(day => ({
            ...day,
            slots: day.slots.map(s => s.id === task.id ? { ...s, status: newStatus } : s)
        }));
        setPlan(updatedPlan);

        if (selectedTask && selectedTask.id === task.id) {
            setSelectedTask({ ...selectedTask, status: newStatus });
        }

        // Persist to LocalStorage
        const completedTasks = new Set(JSON.parse(localStorage.getItem('completedTasks') || '[]'));
        if (newStatus === 'completed') {
            completedTasks.add(task.id);
            setXp(prev => prev + 10); // +10 XP for completion
            audioManager.play('success');

            // Nemesis: Form a memory trace
            // Only track the main topic/activity to avoid clutter
            nemesis.updateMemory(task.activity, 'pass');
        } else {
            completedTasks.delete(task.id);
            setXp(prev => Math.max(0, prev - 10)); // -10 XP for undo
        }
        localStorage.setItem('completedTasks', JSON.stringify(Array.from(completedTasks)));

        // Dispatch event for other components
        window.dispatchEvent(new Event('taskUpdate'));

        // --- Strategos Learning Step ---
        // Reward: +10 for completion, -5 for un-completion (backtracking)
        const reward = newStatus === 'completed' ? 10 : -5;

        // Calculate new state
        const currentState = calculateAgentState();
        agent.learn(reward, currentState);

        // Get new decision
        const newAction = agent.decide(currentState);
        setAgentAction(newAction);
        setAgentSuggestion(agent.getSuggestionText(newAction));
    };

    const calculateAgentState = (): AgentState => {
        const hour = new Date().getHours();
        let timeOfDay: 'MORNING' | 'AFTERNOON' | 'EVENING' | 'NIGHT' = 'MORNING';
        if (hour >= 12 && hour < 17) timeOfDay = 'AFTERNOON';
        else if (hour >= 17 && hour < 22) timeOfDay = 'EVENING';
        else if (hour >= 22 || hour < 5) timeOfDay = 'NIGHT';

        const pendingCount = plan.flatMap(d => d.slots).filter(s => s.status === 'pending').length;
        let backlogLevel: 'NONE' | 'LOW' | 'HIGH' | 'CRITICAL' = 'LOW';
        if (pendingCount === 0) backlogLevel = 'NONE';
        else if (pendingCount > 10) backlogLevel = 'HIGH';
        else if (pendingCount > 20) backlogLevel = 'CRITICAL';

        // Simplified Energy Model (decays with time of day)
        let energyLevel: 'HIGH' | 'MEDIUM' | 'LOW' | 'BURNOUT' = 'HIGH';
        if (hour > 14) energyLevel = 'MEDIUM';
        if (hour > 20) energyLevel = 'LOW';
        if (backlogLevel === 'CRITICAL') energyLevel = 'BURNOUT';

        return {
            timeOfDay,
            backlogLevel,
            energyLevel,
            lastActionSuccess: true, // Simplified
            oracleRisk: oraclePrediction?.riskFactor
        };
    };

    useEffect(() => {
        if (plan.length > 0) {
            // Run Oracle Prediction FIRST so Agent can see it
            const totalPending = plan.flatMap(d => d.slots).filter(s => s.status === 'pending').length;
            const completedLast7Days = plan.slice(0, 7).flatMap(d => d.slots).filter(s => s.status === 'completed').length;
            const velocity = Math.max(1, completedLast7Days / 7); // Avoid 0 velocity
            const targetDate = new Date();
            targetDate.setMonth(targetDate.getMonth() + 6); // Mock Exam Date: 6 months from now

            const prediction = oracle.predict(totalPending, velocity, targetDate);
            setOraclePrediction(prediction);

            // Then Run Agent
            const state = calculateAgentState();
            // Inject the just-calculated risk manually since state update is async
            state.oracleRisk = prediction.riskFactor;

            const action = agent.decide(state);
            setAgentAction(action);
            setAgentSuggestion(agent.getSuggestionText(action));
        }
    }, [plan]);

    // --- Dynamic Flow Engine ---
    const [isDynamicMode, setIsDynamicMode] = useState<boolean>(() => {
        return localStorage.getItem('mimir_dynamic_mode') === 'true';
    });

    useEffect(() => {
        localStorage.setItem('mimir_dynamic_mode', String(isDynamicMode));
    }, [isDynamicMode]);

    const generateDynamicPlan = (originalPlan: DayPlan[]): DayPlan[] => {
        if (!isDynamicMode) return originalPlan;

        const today = new Date();
        today.setHours(0, 0, 0, 0);

        // 1. Separate Backlogs and Future Tasks
        const backlogs: Slot[] = [];
        const futureMap: { [date: string]: Slot[] } = {};
        const historyMap: { [date: string]: Slot[] } = {};

        originalPlan.forEach(day => {
            const dayDate = new Date(day.date);
            dayDate.setHours(0, 0, 0, 0);

            day.slots.forEach(slot => {
                if (slot.status === 'completed') {
                    if (!historyMap[day.date]) historyMap[day.date] = [];
                    historyMap[day.date].push(slot);
                } else if (slot.subject !== 'Break' && slot.subject !== 'Buffer') {
                    if (dayDate < today) {
                        backlogs.push(slot); // Past due
                    } else {
                        if (!futureMap[day.date]) futureMap[day.date] = [];
                        futureMap[day.date].push(slot); // Future scheduled
                    }
                }
            });
        });

        // 2. Initialize Dynamic Plan with History and Future
        const dynamicPlanMap: { [date: string]: Slot[] } = { ...historyMap, ...futureMap };

        // 3. Smart Backlog Insertion (Load Balancing)
        const SLOTS_PER_DAY = 6;
        let currentDay = new Date(today);

        // Sort backlogs by priority/subject (optional, keeping order for now)

        backlogs.forEach(backlogTask => {
            let inserted = false;
            let attempts = 0;
            // Look for a free slot in the next 30 days
            while (!inserted && attempts < 30) {
                const dateStr = currentDay.toISOString().split('T')[0];
                const currentSlots = dynamicPlanMap[dateStr] || [];

                // Check Capacity
                if (currentSlots.length < SLOTS_PER_DAY) {
                    if (!dynamicPlanMap[dateStr]) dynamicPlanMap[dateStr] = [];
                    // Mark as rescheduled
                    const rescheduledTask = { ...backlogTask, status: 'rescheduled' as const };
                    dynamicPlanMap[dateStr].push(rescheduledTask);
                    inserted = true;
                } else {
                    // Try next day
                    currentDay.setDate(currentDay.getDate() + 1);
                    attempts++;
                }
            }

            // If still not inserted (schedule full), append to the last checked day
            if (!inserted) {
                const dateStr = currentDay.toISOString().split('T')[0];
                if (!dynamicPlanMap[dateStr]) dynamicPlanMap[dateStr] = [];
                const rescheduledTask = { ...backlogTask, status: 'rescheduled' as const };
                dynamicPlanMap[dateStr].push(rescheduledTask);
            }

            // Reset currentDay to today for the next backlog task to find the earliest slot
            currentDay = new Date(today);
        });

        // 4. Convert Map to Array and Sort
        const sortedDates = Object.keys(dynamicPlanMap).sort();
        return sortedDates.map(date => ({
            date,
            day: new Date(date).toLocaleDateString('en-US', { weekday: 'long' }),
            slots: dynamicPlanMap[date]
        }));
    };

    // --- Jarvis Genetic Scheduler ---
    const runJarvisOptimization = async () => {
        setIsOptimizing(true);

        // Allow UI to update before heavy computation
        setTimeout(() => {
            try {
                const allSlots = plan.flatMap(d => d.slots);
                const pendingSlots = allSlots.filter(s => s.status !== 'completed' && s.subject !== 'Break' && s.subject !== 'Buffer');

                // 1. Prerequisite Filtering (NCERT First Protocol)
                const tasksBySubject: { [key: string]: Slot[] } = {};
                pendingSlots.forEach(s => {
                    if (!tasksBySubject[s.subject]) tasksBySubject[s.subject] = [];
                    tasksBySubject[s.subject].push(s);
                });

                const schedulableSlots: Slot[] = [];
                const blockedSlots: Slot[] = [];

                Object.keys(tasksBySubject).forEach(subject => {
                    const subjectTasks = tasksBySubject[subject];

                    // Check if any NCERT is pending for this subject
                    const hasPendingNCERT = subjectTasks.some(t =>
                        t.activity.toLowerCase().includes('ncert') ||
                        t.activity.toLowerCase().includes('class 6') ||
                        t.activity.toLowerCase().includes('class 7') ||
                        t.activity.toLowerCase().includes('class 8') ||
                        t.activity.toLowerCase().includes('class 9') ||
                        t.activity.toLowerCase().includes('class 10') ||
                        t.activity.toLowerCase().includes('class 11') ||
                        t.activity.toLowerCase().includes('class 12')
                    );

                    if (hasPendingNCERT) {
                        // If NCERTs are pending, ONLY allow NCERTs. Block everything else (Standard Books).
                        subjectTasks.forEach(t => {
                            const isNCERT = t.activity.toLowerCase().includes('ncert') ||
                                t.activity.toLowerCase().includes('class 6') ||
                                t.activity.toLowerCase().includes('class 7') ||
                                t.activity.toLowerCase().includes('class 8') ||
                                t.activity.toLowerCase().includes('class 9') ||
                                t.activity.toLowerCase().includes('class 10') ||
                                t.activity.toLowerCase().includes('class 11') ||
                                t.activity.toLowerCase().includes('class 12');

                            if (isNCERT) {
                                schedulableSlots.push(t);
                            } else {
                                blockedSlots.push(t);
                            }
                        });
                    } else {
                        // No pending NCERTs, allow all tasks (Standard Books, etc.)
                        schedulableSlots.push(...subjectTasks);
                    }
                });

                // 1.5 Scope Limitation (Focus on "Now")
                // Sort by original date (Overdue first)
                schedulableSlots.sort((a, b) => {
                    const dateA = plan.find(d => d.slots.includes(a))?.date || '9999-99-99';
                    const dateB = plan.find(d => d.slots.includes(b))?.date || '9999-99-99';
                    return dateA.localeCompare(dateB);
                });

                // Take top 50, move rest to blocked (Backlog)
                if (schedulableSlots.length > 50) {
                    const excessSlots = schedulableSlots.slice(50);
                    blockedSlots.push(...excessSlots);
                    schedulableSlots.splice(50); // Keep only top 50
                }

                // 2. Convert to Genetic Tasks (Only Schedulable)
                const tasks: GTask[] = schedulableSlots.map(s => ({
                    id: s.id,
                    subject: s.subject,
                    topic: s.activity,
                    durationMinutes: 60, // Default 1 hour
                    priority: 'medium',
                    originalDate: plan.find(d => d.slots.includes(s))?.date
                }));

                // 3. Generate Available Slots (Next 60 Days)
                const availableSlots: TimeSlot[] = [];
                const startDate = new Date();
                startDate.setHours(0, 0, 0, 0);

                for (let i = 0; i < 60; i++) {
                    const currentDate = new Date(startDate);
                    currentDate.setDate(startDate.getDate() + i);
                    const dateStr = currentDate.toISOString().split('T')[0];

                    // Create 6 slots per day (Example: 9am, 11am, 2pm, 4pm, 7pm, 9pm)
                    // Minutes from midnight: 9*60=540, 11*60=660, 14*60=840, 16*60=960, 19*60=1140, 21*60=1260
                    const startTimes = [540, 660, 840, 960, 1140, 1260];

                    startTimes.forEach(start => {
                        availableSlots.push({
                            date: dateStr,
                            startTime: start,
                            endTime: start + 60,
                            isWorkHours: true
                        });
                    });
                }

                // 4. Configure & Run Scheduler (Meta-Cognitive)
                // Ask Strategos for the optimal strategy based on current state
                const adaptiveConfig = agent.getSchedulerParams();

                // Get Knowledge Graph Links for Semantic Awareness
                const semanticLinks = nexusEngine.getGraphData().links;

                const scheduler = new GeneticScheduler(tasks, availableSlots, adaptiveConfig, semanticLinks);
                const optimizedGenes = scheduler.optimize();

                // 4. Reconstruct Plan
                const newPlanMap: { [date: string]: Slot[] } = {};

                // Keep history (completed tasks)
                const completedSlots = allSlots.filter(s => s.status === 'completed');
                completedSlots.forEach(s => {
                    const d = plan.find(day => day.slots.includes(s))?.date;
                    if (d) {
                        if (!newPlanMap[d]) newPlanMap[d] = [];
                        newPlanMap[d].push(s);
                    }
                });

                // Add optimized pending tasks
                optimizedGenes.forEach(gene => {
                    const slot = availableSlots[gene.assignedSlotIndex];
                    const originalTask = pendingSlots.find(t => t.id === gene.taskId);

                    if (originalTask && slot) {
                        if (!newPlanMap[slot.date]) newPlanMap[slot.date] = [];

                        // Format time string (e.g., "09:00 AM")
                        const hours = Math.floor(slot.startTime / 60);
                        const mins = slot.startTime % 60;
                        const ampm = hours >= 12 ? 'PM' : 'AM';
                        const timeStr = `${hours % 12 || 12}:${mins.toString().padStart(2, '0')} ${ampm}`;

                        newPlanMap[slot.date].push({
                            ...originalTask,
                            time: timeStr
                        });
                    }
                });

                // 5. Append Blocked Tasks (Future Backlog)
                // Place them starting from Day 61 (after the optimization window)
                if (blockedSlots.length > 0) {
                    const futureStart = new Date();
                    futureStart.setDate(futureStart.getDate() + 61);

                    let currentFutureDate = new Date(futureStart);
                    let slotsInDay = 0;

                    blockedSlots.forEach(task => {
                        const dateStr = currentFutureDate.toISOString().split('T')[0];
                        if (!newPlanMap[dateStr]) newPlanMap[dateStr] = [];

                        newPlanMap[dateStr].push({
                            ...task,
                            status: 'rescheduled', // Mark as rescheduled/future
                            time: 'TBD'
                        });

                        slotsInDay++;
                        if (slotsInDay >= 6) {
                            slotsInDay = 0;
                            currentFutureDate.setDate(currentFutureDate.getDate() + 1);
                        }
                    });
                }

                // Sort slots by time within each day
                Object.keys(newPlanMap).forEach(date => {
                    newPlanMap[date].sort((a, b) => {
                        const timeA = new Date(`1970/01/01 ${a.time}`).getTime();
                        const timeB = new Date(`1970/01/01 ${b.time}`).getTime();
                        return timeA - timeB;
                    });
                });

                const finalPlan: DayPlan[] = Object.entries(newPlanMap).map(([date, slots]) => ({
                    date,
                    day: new Date(date).toLocaleDateString('en-US', { weekday: 'long' }),
                    slots
                })).sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());

                setPlan(finalPlan);
                setIsDynamicMode(true); // Auto-enable dynamic mode to show results

            } catch (error) {
                console.error("Jarvis Optimization Failed:", error);
                alert("Jarvis encountered a cognitive overload. Please try again.");
            } finally {
                setIsOptimizing(false);
            }
        }, 100);
    };

    // Analytics Helpers
    const getWeeklyAnalytics = (weekSlots: Slot[]) => {
        const subjectCounts: { [key: string]: number } = {};
        weekSlots.forEach(slot => {
            if (slot.subject === 'Break' || slot.subject === 'Buffer') return;
            subjectCounts[slot.subject] = (subjectCounts[slot.subject] || 0) + 1;
        });

        const data = Object.entries(subjectCounts).map(([name, value]) => ({ name, value }));
        data.sort((a, b) => b.value - a.value);

        const totalStudySlots = weekSlots.filter(s => s.subject !== 'Break').length;
        const focusSubject = data.length > 0 ? data[0].name : 'General';

        return { data, totalStudySlots, focusSubject };
    };

    const getMonthlyAnalytics = (monthSlots: Slot[]) => {
        const total = monthSlots.length;
        const completed = monthSlots.filter(s => s.status === 'completed').length;
        const consistency = total > 0 ? Math.round((completed / total) * 100) : 0;

        const phase = "Phase 1: Foundation";

        return { consistency, phase };
    };

    const activePlan = React.useMemo(() => {
        const basePlan = generateDynamicPlan(plan);
        if (!filterTopic) return basePlan;
        return basePlan.map(day => ({
            ...day,
            slots: day.slots.filter(s => s.subject.includes(filterTopic) || s.activity.includes(filterTopic))
        }));
    }, [plan, isDynamicMode, filterTopic]);

    const renderContent = () => {
        if (viewMode === 'flashcards') {
            return <FlashcardsManager />;
        } else if (viewMode === 'daily') {
            const today = new Date().toISOString().split('T')[0];
            // In Dynamic Mode, "Today" is always the first incomplete day or actual today
            const todayPlan = activePlan.find(p => p.date === today) || (isDynamicMode ? activePlan.find(p => new Date(p.date) >= new Date(today)) : undefined);

            return (
                <div className="daily-view">
                    {todayPlan ? (
                        <div className="day-card active">
                            <div className="day-header">
                                <h2>{new Date(todayPlan.date).toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}</h2>
                                <span className="day-badge">TODAY'S MISSION</span>
                            </div>
                            <div className="day-slots">
                                {todayPlan.slots.map((slot, idx) => (
                                    <div key={idx} className={`slot-card ${slot.subject.toLowerCase().replace(/\s+/g, '-')}`} onClick={() => handleTaskClick(slot)}>
                                        <div className={`slot-status ${slot.status}`}></div>
                                        <div className="slot-time">{slot.time}</div>
                                        <div className="slot-subject">{slot.subject}</div>
                                        <div className="slot-activity">{slot.activity}</div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    ) : (
                        <div className="empty-state">
                            <h3>No missions scheduled for today. Rest and recover! </h3>
                        </div>
                    )}

                    <h3>Upcoming Days</h3>
                    {activePlan.filter(p => p.date > today).slice(0, 3).map((day, idx) => (
                        <div key={idx} className="day-card">
                            <div className="day-header">
                                <h3>{new Date(day.date).toLocaleDateString('default', { weekday: 'long', month: 'short', day: 'numeric' })}</h3>
                                <span className="day-name">{day.day}</span>
                            </div>
                            <div className="day-slots">
                                {day.slots.length > 0 ? (
                                    day.slots.map((slot, sIdx) => (
                                        <div
                                            key={sIdx}
                                            className={`slot-card ${slot.subject.toLowerCase().replace(/\s+/g, '-')}`}
                                            onClick={() => handleTaskClick(slot)}
                                        >
                                            <div className={`slot-status ${slot.status}`} title={slot.status}></div>
                                            <div className="slot-time">{slot.time}</div>
                                            <div className="slot-subject">{slot.subject}</div>
                                            <div className="slot-activity">{slot.activity}</div>
                                            {slot.resource_link && (
                                                <div className="resource-link"> {slot.resource_link}</div>
                                            )}
                                        </div>
                                    ))
                                ) : (
                                    <div className="no-slots">Rest Day / Buffer</div>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            );
        } else if (viewMode === 'weekly') {
            // Group by Week
            const weeks: DayPlan[][] = [];
            let currentWeek: DayPlan[] = [];

            activePlan.forEach((day, i) => {
                currentWeek.push(day);
                if ((i + 1) % 7 === 0 || i === activePlan.length - 1) {
                    weeks.push(currentWeek);
                    currentWeek = [];
                }
            });

            return weeks.map((week, idx) => {
                const weekSlots = week.flatMap(d => d.slots);
                const { data, totalStudySlots, focusSubject } = getWeeklyAnalytics(weekSlots);
                const completed = week.reduce((acc, day) => acc + day.slots.filter(s => s.status === 'completed').length, 0);
                const totalTasks = week.reduce((acc, day) => acc + day.slots.length, 0);
                const progress = totalTasks > 0 ? (completed / totalTasks) * 100 : 0;
                const startDate = week[0].date;
                const endDate = week[week.length - 1].date;

                let insight = "Maintain steady pace.";
                if (totalStudySlots > 40) insight = " Heavy Load: Prioritize sleep & recovery.";
                else if (focusSubject === 'History') insight = " History Week: Use timelines for better retention.";
                else if (progress > 90) insight = " Crushing it! Consider an extra mock test.";

                return (
                    <div key={idx} className="mission-card">
                        <div className="mission-header">
                            <div className="mission-title">
                                <h3>MISSION {idx + 1}</h3>
                                <span>{startDate} - {endDate}</span>
                            </div>
                            <div className="mission-status">
                                <span className="status-label">{progress === 100 ? 'COMPLETE' : 'IN PROGRESS'}</span>
                                <div className="circular-progress" style={{ background: `conic-gradient(#2ecc71 ${progress}%, #333 ${progress}%)` }}>
                                    <span>{Math.round(progress)}%</span>
                                </div>
                            </div>
                        </div>
                        <div className="mission-body">
                            <div className="mission-intel">
                                <h4>INTEL BRIEF</h4>
                                <p>{insight}</p>
                                <div className="key-stats">
                                    <div className="stat-box"><label>FOCUS</label><span>{focusSubject}</span></div>
                                    <div className="stat-box"><label>LOAD</label><span>{totalStudySlots} Slots</span></div>
                                </div>
                            </div>
                            <div className="mission-radar">
                                <h4>SUBJECT DISTRIBUTION</h4>
                                <ResponsiveContainer width="100%" height={150}>
                                    <BarChart data={data} layout="vertical" margin={{ left: 40, right: 20 }}>
                                        <XAxis type="number" hide />
                                        <YAxis dataKey="name" type="category" width={80} tick={{ fill: '#bdc3c7', fontSize: 10 }} />
                                        <RechartsTooltip contentStyle={{ background: '#1e1e1e', border: 'none' }} />
                                        <Bar dataKey="value" fill="#3498db" radius={[0, 4, 4, 0]}>
                                            {data.map((_, index) => <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />)}
                                        </Bar>
                                    </BarChart>
                                </ResponsiveContainer>
                            </div>
                        </div>
                    </div>
                );
            });
        } else if (viewMode === 'monthly') {
            // Group by Month
            const months: { [key: string]: DayPlan[] } = {};
            activePlan.forEach(day => {
                const monthKey = day.date.substring(0, 7); // YYYY-MM
                if (!months[monthKey]) months[monthKey] = [];
                months[monthKey].push(day);
            });

            return Object.entries(months).map(([month, days]) => {
                const { consistency, phase } = getMonthlyAnalytics(days.flatMap(d => d.slots));
                const subjectCounts: { [key: string]: number } = {};
                days.flatMap(d => d.slots).forEach(s => {
                    if (s.subject !== 'Break') subjectCounts[s.subject] = (subjectCounts[s.subject] || 0) + 1;
                });
                const pieData = Object.entries(subjectCounts).map(([name, value]) => ({ name, value }));

                return (
                    <div key={month} className="strategy-card">
                        <div className="strategy-header">
                            <div className="strategy-title">
                                <h3>{new Date(month + '-01').toLocaleString('default', { month: 'long', year: 'numeric' })}</h3>
                                <span className="phase-badge">{phase}</span>
                            </div>
                            <div className="consistency-score">
                                <label>CONSISTENCY</label>
                                <span className={consistency > 80 ? 'high' : consistency > 50 ? 'med' : 'low'}>{consistency}%</span>
                            </div>
                        </div>
                        <div className="strategy-body">
                            <div className="calendar-grid">
                                {days.map((day, dIdx) => {
                                    const dayTasks = day.slots.length;
                                    const dayCompleted = day.slots.filter(s => s.status === 'completed').length;
                                    const statusClass = dayTasks === 0 ? 'empty' : dayCompleted === dayTasks ? 'full' : dayCompleted > 0 ? 'partial' : 'none';
                                    return (
                                        <div key={dIdx} className={`calendar-day ${statusClass}`} title={`${day.date}: ${dayCompleted}/${dayTasks}`}>
                                            {day.date.split('-')[2]}
                                        </div>
                                    );
                                })}
                            </div>
                            <div className="month-analytics">
                                <h4>DISTRIBUTION</h4>
                                <ResponsiveContainer width="100%" height={180}>
                                    <PieChart>
                                        <Pie data={pieData} cx="50%" cy="50%" innerRadius={40} outerRadius={60} paddingAngle={5} dataKey="value">
                                            {pieData.map((_, index) => <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />)}
                                        </Pie>
                                        <RechartsTooltip contentStyle={{ background: '#1e1e1e', border: 'none', fontSize: '12px' }} />
                                    </PieChart>
                                </ResponsiveContainer>
                                <div className="legend">
                                    {pieData.slice(0, 3).map((entry, index) => (
                                        <div key={index} className="legend-item">
                                            <span style={{ background: COLORS[index % COLORS.length] }}></span>
                                            {entry.name}
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>
                );
            });
        } else if (viewMode === 'yearly') {
            // Calculate Subject Mastery for Radar Chart
            const subjectCounts: { [key: string]: { total: number, completed: number } } = {};
            activePlan.flatMap(d => d.slots).forEach(s => {
                if (s.subject === 'Break' || s.subject === 'Buffer') return;
                if (!subjectCounts[s.subject]) subjectCounts[s.subject] = { total: 0, completed: 0 };
                subjectCounts[s.subject].total++;
                if (s.status === 'completed') subjectCounts[s.subject].completed++;
            });

            const radarData = Object.entries(subjectCounts)
                .map(([subject, stats]) => ({
                    subject,
                    A: Math.round((stats.completed / stats.total) * 100) || 0, // Mastery %
                    fullMark: 100
                }))
                .sort((a, b) => b.A - a.A)
                .slice(0, 6); // Top 6 subjects for cleaner radar

            // Strategic Insights Logic
            const daysElapsed = Math.floor((Date.now() - new Date(activePlan[0]?.date).getTime()) / (1000 * 60 * 60 * 24));
            const safeDaysElapsed = daysElapsed < 0 ? 0 : daysElapsed; // Fix negative days
            const totalCompleted = activePlan.reduce((acc, day) => acc + day.slots.filter(s => s.status === 'completed').length, 0);
            const totalTasks = activePlan.reduce((acc, day) => acc + day.slots.length, 0);
            const completionRate = totalTasks > 0 ? (totalCompleted / totalTasks) * 100 : 0;

            let strategicNote = "Maintain current velocity.";
            if (completionRate < 30 && safeDaysElapsed > 30) strategicNote = "CRITICAL: Velocity below threshold. Increase daily output.";
            else if (completionRate > 80) strategicNote = "EXCELLENT: Exceeding operational targets. Consider advanced modules.";
            else if (safeDaysElapsed < 7) strategicNote = "INITIATION: Establish baseline rhythm.";

            return (
                <div className="grand-strategy-view">
                    <div className="strategy-header-main">
                        <div className="header-content">
                            <h2>THE GRAND STRATEGY</h2>
                            <span className="subtitle">OPERATIONAL COMMAND CENTER</span>
                        </div>
                        <div className="dqn-stats">
                            <div className="stat-item">
                                <span className="label">Epsilon (Exploration):</span>
                                <span className="value">{agent.getStats().epsilon}</span>
                            </div>
                            <div className="stat-item">
                                <span className="label">Loss (Error):</span>
                                <span className="value">{agent.getStats().loss}</span>
                            </div>
                            <div className="stat-item">
                                <span className="label">Memory Size:</span>
                                <span className="value">{agent.getStats().memorySize}</span>
                            </div>
                        </div>

                        {oraclePrediction && oraclePrediction.paths && (
                            <div className="oracle-chart" style={{ marginTop: '20px', height: '200px' }}>
                                <h4>🔮 Project Foresight (Monte Carlo Paths)</h4>
                                <ResponsiveContainer width="100%" height="100%">
                                    <AreaChart data={oraclePrediction.paths.avg.map((p, i) => ({
                                        day: p.day,
                                        avg: p.tasksRemaining,
                                        best: oraclePrediction.paths.best[i]?.tasksRemaining || 0,
                                        worst: oraclePrediction.paths.worst[i]?.tasksRemaining || 0
                                    }))}>
                                        <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                                        <XAxis dataKey="day" stroke="#888" />
                                        <YAxis stroke="#888" />
                                        <RechartsTooltip
                                            contentStyle={{ backgroundColor: '#1a1a1a', border: '1px solid #333' }}
                                            itemStyle={{ color: '#fff' }}
                                        />
                                        <Area type="monotone" dataKey="worst" stackId="1" stroke="#ff4d4d" fill="#ff4d4d" fillOpacity={0.1} name="Worst Case" />
                                        <Area type="monotone" dataKey="avg" stackId="2" stroke="#8884d8" fill="#8884d8" fillOpacity={0.3} name="Likely Path" />
                                        <Area type="monotone" dataKey="best" stackId="3" stroke="#00C49F" fill="#00C49F" fillOpacity={0.3} name="Best Case" />
                                    </AreaChart>
                                </ResponsiveContainer>
                            </div>
                        )}        <div className="war-room-stats">
                            <div className="stat-pod">
                                <label>CAMPAIGN STATUS</label>
                                <span className="active">ACTIVE</span>
                            </div>
                            <div className="stat-pod">
                                <label>DAYS DEPLOYED</label>
                                <span>{safeDaysElapsed}</span>
                            </div>
                            <div className="stat-pod">
                                <label>GLOBAL MASTERY</label>
                                <span>{Math.round(completionRate)}%</span>
                            </div>
                            <div className="stat-pod oracle-pod">
                                <label>SUCCESS PROBABILITY</label>
                                <span className={oraclePrediction?.successProbability && oraclePrediction.successProbability > 70 ? 'high' : 'low'}>
                                    {oraclePrediction?.successProbability}%
                                </span>
                            </div>
                        </div>
                    </div>

                    <div className="strategy-grid">
                        <div className="hud-panel radar-sector">
                            <div className="panel-header">
                                <h3>SUBJECT MASTERY</h3>
                                <div className="panel-decor"></div>
                            </div>
                            <div className="radar-container">
                                <ResponsiveContainer width="100%" height={280}>
                                    <RadarChart cx="50%" cy="50%" outerRadius="70%" data={radarData}>
                                        <PolarGrid stroke="#34495e" strokeDasharray="3 3" />
                                        <PolarAngleAxis dataKey="subject" tick={{ fill: '#bdc3c7', fontSize: 11, fontFamily: 'Orbitron' }} />
                                        <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                                        <Radar
                                            name="Mastery"
                                            dataKey="A"
                                            stroke="#00d2d3"
                                            strokeWidth={2}
                                            fill="#00d2d3"
                                            fillOpacity={0.2}
                                        />
                                        <RechartsTooltip
                                            contentStyle={{ background: 'rgba(20, 20, 20, 0.9)', border: '1px solid #00d2d3', color: '#fff' }}
                                            itemStyle={{ color: '#00d2d3' }}
                                        />
                                    </RadarChart>
                                </ResponsiveContainer>
                            </div>
                        </div>

                        <div className="right-sector">
                            <div className="hud-panel timeline-sector">
                                <div className="panel-header">
                                    <h3>CAMPAIGN TIMELINE</h3>
                                    <div className="panel-decor"></div>
                                </div>
                                <div className="phase-timeline-graphical">
                                    <div className="timeline-track"></div>
                                    <div className="phase-node completed">
                                        <div className="node-dot"></div>
                                        <div className="node-content">
                                            <span className="phase-name">FOUNDATION</span>
                                            <span className="phase-meta">Nov - Dec</span>
                                        </div>
                                    </div>
                                    <div className="phase-node active">
                                        <div className="node-dot"></div>
                                        <div className="node-content">
                                            <span className="phase-name">CORE COMPETENCY</span>
                                            <span className="phase-meta">Jan - May</span>
                                            <div className="pulse-ring"></div>
                                        </div>
                                    </div>
                                    <div className="phase-node">
                                        <div className="node-dot"></div>
                                        <div className="node-content">
                                            <span className="phase-name">PRELIMS SPRINT</span>
                                            <span className="phase-meta">Jun - Aug</span>
                                        </div>
                                    </div>
                                    <div className="phase-node">
                                        <div className="node-dot"></div>
                                        <div className="node-content">
                                            <span className="phase-name">MAINS MASTERY</span>
                                            <span className="phase-meta">Sep - Dec</span>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div className="hud-panel insights-sector">
                                <div className="panel-header">
                                    <h3>STRATEGIC INTEL</h3>
                                    <div className="panel-decor"></div>
                                </div>
                                <div className="intel-content">
                                    {/* Demon's Warnings */}
                                    {demonWarnings.length > 0 && (
                                        <div className="demon-alert-box">
                                            <div className="demon-header">
                                                <span className="demon-icon"></span>
                                                <h4>LAPLACE'S WARNING</h4>
                                            </div>
                                            {demonWarnings.map((warning, idx) => (
                                                <div key={idx} className="warning-item">
                                                    <p>{warning.message}</p>
                                                    <button
                                                        className="fix-schedule-btn"
                                                        onClick={() => {
                                                            audioManager.play('success');
                                                            fixSchedule();
                                                            alert("Optimizing schedule to resolve conflict...");
                                                            setDemonWarnings(prev => prev.filter((_, i) => i !== idx));
                                                        }}
                                                    >
                                                        Fix Schedule
                                                    </button>
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>

                                <div className="intel-row">
                                    <span className="intel-label">MARKET WATCH</span>
                                    <div className="market-ticker">
                                        {marketOpportunities.map((op, idx) => (
                                            <div key={idx} className="ticker-item">
                                                <span className="ticker-symbol">{op.topic.substring(0, 3).toUpperCase()}</span>
                                                <span className="ticker-price"> {op.score}</span>
                                                <button
                                                    className="debate-btn"
                                                    onClick={() => console.log("Debate feature temporarily disabled")}
                                                >
                                                    ⚔️ Challenge (Coming Soon)
                                                </button>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                                <div className="intel-row">
                                    <span className="intel-label">COMMANDER'S NOTE:</span>
                                    <span className="intel-value typing-effect">{strategicNote}</span>
                                </div>
                                <div className="heatmap-mini">
                                    <h4>ACTIVITY SIGNATURE</h4>
                                    <div className="heatmap-grid">
                                        {activePlan.slice(0, 180).map((day, idx) => {
                                            const dayTasks = day.slots.length;
                                            const dayCompleted = day.slots.filter(s => s.status === 'completed').length;
                                            const intensity = dayTasks === 0 ? 0 : Math.ceil((dayCompleted / dayTasks) * 4);
                                            return (
                                                <div
                                                    key={idx}
                                                    className={`heatmap-cell intensity-${intensity}`}
                                                    title={`${day.date}: ${dayCompleted}/${dayTasks}`}
                                                ></div>
                                            );
                                        })}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {oraclePrediction && (
                        <div className="hud-panel oracle-sector">
                            <div className="panel-header">
                                <h3> THE ORACLE</h3>
                                <div className="panel-decor"></div>
                            </div>
                            <div className="oracle-content">
                                <div className="oracle-row">
                                    <span>Projected Finish:</span>
                                    <span className="oracle-value">{oraclePrediction.averageDate}</span>
                                </div>
                                <div className="oracle-row">
                                    <span>Best Case:</span>
                                    <span className="oracle-value best">{oraclePrediction.bestCaseDate}</span>
                                </div>
                                <div className="oracle-row">
                                    <span>Worst Case:</span>
                                    <span className="oracle-value worst">{oraclePrediction.worstCaseDate}</span>
                                </div>
                                <div className="oracle-risk">
                                    <label>SUCCESS PROBABILITY DISTRIBUTION</label>
                                    <ResponsiveContainer width="100%" height={100}>
                                        <AreaChart data={[
                                            { day: 'Now', prob: oraclePrediction.successProbability - 10 },
                                            { day: 'Month 1', prob: oraclePrediction.successProbability - 5 },
                                            { day: 'Month 3', prob: oraclePrediction.successProbability },
                                            { day: 'Month 6', prob: Math.min(100, oraclePrediction.successProbability + 15) },
                                        ]}>
                                            <defs>
                                                <linearGradient id="colorProb" x1="0" y1="0" x2="0" y2="1">
                                                    <stop offset="5%" stopColor="#00d2d3" stopOpacity={0.8} />
                                                    <stop offset="95%" stopColor="#00d2d3" stopOpacity={0} />
                                                </linearGradient>
                                            </defs>
                                            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#333" />
                                            <XAxis dataKey="day" hide />
                                            <YAxis hide domain={[0, 100]} />
                                            <RechartsTooltip contentStyle={{ background: '#1e1e1e', border: 'none' }} />
                                            <Area type="monotone" dataKey="prob" stroke="#00d2d3" fillOpacity={1} fill="url(#colorProb)" />
                                        </AreaChart>
                                    </ResponsiveContainer>
                                    <p className="risk-text">Risk Factor: {oraclePrediction.riskFactor}</p>
                                </div>
                            </div>
                        </div>
                    )}

                </div>

            );
        } else if (viewMode === 'overall') {
            const totalTasks = activePlan.reduce((acc, day) => acc + day.slots.length, 0);
            const completedTasks = activePlan.reduce((acc, day) => acc + day.slots.filter(s => s.status === 'completed').length, 0);
            const overallProgress = totalTasks > 0 ? (completedTasks / totalTasks) * 100 : 0;

            return (
                <div className="overall-view">
                    <h2> 2-Year Strategy Overview</h2>
                    <div className="stats-grid">
                        <div className="stat-card">
                            <h3>Total Tasks</h3>
                            <p>{totalTasks}</p>
                        </div>
                        <div className="stat-card">
                            <h3>Completion</h3>
                            <p>{Math.round(overallProgress)}%</p>
                        </div>
                        <div className="stat-card">
                            <h3>Projected End</h3>
                            <p>{activePlan.length > 0 ? activePlan[activePlan.length - 1].date : 'N/A'}</p>
                        </div>
                    </div>
                    <div className="subject-progress">
                        <h3>Subject Breakdown</h3>
                        {['History', 'Geography', 'Polity', 'Economy', 'Science', 'Environment'].map(subject => {
                            const subjectTasks = activePlan.flatMap(d => d.slots).filter(s => s.subject === subject).length;
                            const subjectCompleted = activePlan.flatMap(d => d.slots).filter(s => s.subject === subject && s.status === 'completed').length;
                            const subProgress = subjectTasks > 0 ? (subjectCompleted / subjectTasks) * 100 : 0;

                            return (
                                <div key={subject} className="progress-item">
                                    <span>{subject} ({subjectCompleted}/{subjectTasks})</span>
                                    <div className="progress-bar"><div style={{ width: `${subProgress}%` }}></div></div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            );
        } else if (viewMode === 'nexus') {
            return (
                <div className="nexus-view">
                    <h2> The Nexus: Knowledge Graph</h2>
                    <NexusGraph
                        engine={nexusEngine}
                        completedItems={plan.flatMap(d => d.slots)
                            .filter(s => s.status === 'completed')
                            .map(s => ({ subject: s.subject, topic: s.activity }))}
                        onDebateClick={(_topic: string) => console.log("Debate disabled")}
                        onNodeClick={(node: GraphNode) => {
                            setFilterTopic(node.label);
                            setViewMode('daily'); // Switch to daily view to see filtered tasks
                            alert(`Filtering Dashboard for: ${node.label}`);
                        }}
                    />
                </div>
            );
        }
    };

    return (
        <div className={`study-plan-dashboard ${isFlowMode ? 'flow-mode-active' : ''}`}>
            <div className="planner-header">
                {/* Row 1: Branding & Identity */}
                <div className="header-branding">
                    <h1> Mimir's Advanced Scheduler</h1>
                    <div className="gamification-hud">
                        <div className="xp-container" title={`XP: ${xp} / ${nextLevelXp}`}>
                            <div className="level-badge">Lvl {level}</div>
                            <div className="xp-bar-bg">
                                <div className="xp-bar-fill" style={{ width: `${(xp % 100) / 100 * 100}%` }}></div>
                            </div>
                        </div>
                        <button
                            className={`god-mode-toggle ${godMode ? 'active' : ''}`}
                            onClick={() => setGodMode(!godMode)}
                            title="Toggle God Mode (Debug Stats)"
                        >

                        </button>
                    </div>
                </div>

                {/* Row 2: Toolbar (Navigation & Controls) */}
                <div className="header-toolbar">
                    <div className="toolbar-left">
                        {filterTopic && (
                            <button className="clear-filter-btn" onClick={() => setFilterTopic(null)}>
                                Filter: {filterTopic}
                            </button>
                        )}
                        <div className="view-tabs">
                            <button className={viewMode === 'daily' ? 'active' : ''} onClick={() => setViewMode('daily')}>Daily</button>
                            <button className={viewMode === 'weekly' ? 'active' : ''} onClick={() => setViewMode('weekly')}>Weekly</button>
                            <button className={viewMode === 'monthly' ? 'active' : ''} onClick={() => setViewMode('monthly')}>Monthly</button>
                            <button className={viewMode === 'yearly' ? 'active' : ''} onClick={() => setViewMode('yearly')}>Yearly</button>
                            <button className={viewMode === 'overall' ? 'active' : ''} onClick={() => setViewMode('overall')}>Overall</button>
                            <button className={viewMode === 'nexus' ? 'active' : ''} onClick={() => setViewMode('nexus')}> The Nexus</button>
                            <button className={viewMode === 'flashcards' ? 'active' : ''} onClick={() => setViewMode('flashcards')}> Flashcards</button>
                        </div>
                    </div>

                    <div className="toolbar-right">
                        <div className="controls">
                            <button
                                className={`toggle-btn ${isDynamicMode ? 'active' : ''}`}
                                onClick={() => setIsDynamicMode(!isDynamicMode)}
                                title="Dynamic Mode: Automatically reschedules pending tasks"
                            >
                                {isDynamicMode ? ' Auto-Pilot ON' : ' Static Mode'}
                            </button>
                            <button
                                className={`jarvis-btn ${isOptimizing ? 'pulsing' : ''}`}
                                onClick={runJarvisOptimization}
                                disabled={isOptimizing}
                                title="Run Genetic Algorithm to optimize schedule"
                            >
                                {isOptimizing ? ' Evolving...' : ' Jarvis Optimize'}
                            </button>
                            <button
                                className={`flow-btn ${isFlowMode ? 'active' : ''}`}
                                onClick={toggleFlowMode}
                                title="Bio-Adaptive Binaural Beats (40Hz Gamma)"
                            >
                                {isFlowMode ? ' Flow ON' : ' Flow OFF'}
                            </button>
                            <button onClick={fetchCSVPlan} disabled={loading}>
                                Refresh Plan
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            {loading ? (
                <div className="loading-container">
                    <div className="loading-spinner"></div>
                    <p>Mimir is calibrating your schedule...</p>
                </div>
            ) : activePlan.length > 0 ? (
                <div className="plan-timeline">
                    {/* Strategos Banner */}
                    <div className={`strategos-banner ${agentAction.toLowerCase().replace('_', '-')}`}>
                        <div className="strategos-icon"></div>
                        <div className="strategos-content">
                            <span className="strategos-label">STRATEGOS AI COMMAND</span>
                            <p>{agentSuggestion}</p>
                        </div>
                        {agentAction !== 'MAINTAIN_PACE' && (
                            <button
                                className="strategos-action-btn"
                                onClick={() => executeAgentAction(agentAction)}
                            >
                                {agentAction === 'SUGGEST_BREAK' ? ' Take Break' :
                                    agentAction === 'SCHEDULE_MOCK' ? ' Schedule Mock' :
                                        ' Acknowledge'}
                            </button>
                        )}
                    </div>

                    {/* God Mode Debug Panel */}
                    {godMode && (
                        <div className="god-mode-panel">
                            <h3> GOD MODE: SYSTEM INTERNALS</h3>
                            <div className="debug-grid">
                                <div className="debug-item">
                                    <label>Strategos Brain (DQN):</label>
                                    <div className="dqn-stats">
                                        <div>Loss: {agent.getStats().loss}</div>
                                        <div>Epsilon: {agent.getStats().epsilon}</div>
                                        <div>Memory: {agent.getStats().memorySize}</div>
                                    </div>
                                </div>
                                <div className="debug-item">
                                    <label>Demon Confidence:</label>
                                    <span>{demon.getConfidence()}%</span>
                                </div>
                                <div className="debug-item">
                                    <label>Oracle Risk:</label>
                                    <span>{oraclePrediction?.riskFactor}</span>
                                </div>
                            </div>
                        </div>
                    )}

                    {renderContent()}
                </div>
            ) : (
                <div className="empty-state">
                    <h2>No Plan Data Available</h2>
                    <p>Please click "Refresh Plan" or check your CSV file.</p>
                </div>
            )}

            {selectedTask && (
                <div className="modal-overlay" onClick={closeModal}>
                    <div className="task-modal" onClick={e => e.stopPropagation()}>
                        <div className="modal-header">
                            <h2>{selectedTask.subject}</h2>
                            <button onClick={closeModal}></button>
                        </div>
                        <div className="modal-body">
                            <div className="modal-row">
                                <label>Topic:</label>
                                <p>{selectedTask.activity}</p>
                            </div>
                            <div className="modal-row">
                                <label>Time:</label>
                                <p>{selectedTask.time}</p>
                            </div>
                            <div className="modal-row">
                                <label>Status:</label>
                                <span className={`status-badge ${selectedTask.status}`}>{selectedTask.status}</span>
                            </div>
                            {selectedTask.resource_link && (
                                <div className="modal-row">
                                    <label>Resources:</label>
                                    <a href="#" onClick={(e) => e.preventDefault()}>{selectedTask.resource_link}</a>
                                </div>
                            )}
                            <div className="modal-notes">
                                <label>Notes:</label>
                                <textarea placeholder="Add your notes here..."></textarea>
                            </div>
                        </div>
                        <div className="modal-footer">
                            <button
                                className="debate-btn"
                                onClick={() => {
                                    closeModal();
                                    console.log("Debate disabled");
                                }}
                            >
                                Debate This
                            </button>
                            <button
                                className={`complete-btn ${selectedTask.status === 'completed' ? 'completed' : ''}`}
                                onClick={() => toggleTaskStatus(selectedTask)}
                            >
                                {selectedTask.status === 'completed' ? 'Mark Pending' : 'Mark Complete'}
                            </button>
                        </div>
                    </div>
                </div>
            )}


            {ambushTopic && (
                <div className="modal-overlay ambush-overlay">
                    <div className="ambush-modal">
                        <div className="ambush-header">
                            <h1> SUDDEN DEATH </h1>
                            <p>Nemesis has ambushed you!</p>
                        </div>
                        <div className="ambush-content">
                            <h3>Topic: {ambushTopic}</h3>
                            <p>Retention Critical! Prove your knowledge or suffer memory decay.</p>
                        </div>
                        <div className="ambush-actions">
                            <button
                                className="fight-btn"
                                onClick={() => {
                                    audioManager.play('click');
                                    audioManager.stopLoop('rage');
                                    alert(`Starting Flashcard Session for ${ambushTopic}`);
                                    setViewMode('flashcards');
                                    setAmbushTopic(null);
                                }}
                            >
                                FIGHT BACK (Start Quiz)
                            </button>
                            <button
                                className="surrender-btn"
                                onClick={() => {
                                    audioManager.stopLoop('rage');
                                    rescheduleTask(ambushTopic!);
                                    alert(`${ambushTopic} has been rescheduled for tomorrow.`);
                                    setAmbushTopic(null);
                                }}
                            >
                                SURRENDER (Reschedule)
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default StudyPlanDashboard;

