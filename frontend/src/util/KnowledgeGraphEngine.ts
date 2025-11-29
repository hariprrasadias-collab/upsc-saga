// Knowledge Graph Engine - The Nexus

// Knowledge Graph Engine - The Nexus

export interface GraphNode {
    id: string;
    label: string;
    group: 'History' | 'Geography' | 'Polity' | 'Economy' | 'Science' | 'Environment' | 'Core';
    radius: number;
    mastery: number; // 0 to 100
    isBridge?: boolean; // New: Centrality Flag
    x?: number;
    y?: number;
    vx?: number;
    vy?: number;
}

export interface GraphLink {
    source: string;
    target: string;
    type: 'dependency' | 'related';
    strength: number;
}

export class KnowledgeGraphEngine {
    private nodes: GraphNode[] = [];
    private links: GraphLink[] = [];

    constructor() {
        this.initializeGraph();
    }

    private initializeGraph() {
        // Core Nodes (The Pillars)
        this.nodes = [
            { id: 'UPSC', label: 'UPSC CSE', group: 'Core', radius: 40, mastery: 0 },

            // History Cluster
            { id: 'Hist_Ancient', label: 'Ancient History', group: 'History', radius: 25, mastery: 0 },
            { id: 'Hist_Medieval', label: 'Medieval History', group: 'History', radius: 25, mastery: 0 },
            { id: 'Hist_Modern', label: 'Modern History', group: 'History', radius: 30, mastery: 0 },
            { id: 'Hist_Culture', label: 'Art & Culture', group: 'History', radius: 20, mastery: 0 },

            // Polity Cluster
            { id: 'Pol_Const', label: 'Constitution', group: 'Polity', radius: 35, mastery: 0 },
            { id: 'Pol_Gov', label: 'Governance', group: 'Polity', radius: 25, mastery: 0 },
            { id: 'Pol_IR', label: 'Intl Relations', group: 'Polity', radius: 25, mastery: 0 },

            // Economy Cluster
            { id: 'Eco_Macro', label: 'Macro Economy', group: 'Economy', radius: 30, mastery: 0 },
            { id: 'Eco_Banking', label: 'Banking', group: 'Economy', radius: 20, mastery: 0 },
            { id: 'Eco_Budget', label: 'Budget & Survey', group: 'Economy', radius: 25, mastery: 0 },

            // Geography Cluster
            { id: 'Geo_Physical', label: 'Physical Geo', group: 'Geography', radius: 30, mastery: 0 },
            { id: 'Geo_Indian', label: 'Indian Geo', group: 'Geography', radius: 30, mastery: 0 },
            { id: 'Geo_Climate', label: 'Climatology', group: 'Geography', radius: 20, mastery: 0 },

            // Environment
            { id: 'Env_Eco', label: 'Ecology', group: 'Environment', radius: 25, mastery: 0 },
            { id: 'Env_Bio', label: 'Biodiversity', group: 'Environment', radius: 25, mastery: 0 },

            // Science
            { id: 'Sci_Tech', label: 'Sci & Tech', group: 'Science', radius: 25, mastery: 0 },
        ];

        this.links = [
            // Core Connections
            { source: 'UPSC', target: 'Hist_Modern', type: 'dependency', strength: 1 },
            { source: 'UPSC', target: 'Pol_Const', type: 'dependency', strength: 1 },
            { source: 'UPSC', target: 'Eco_Macro', type: 'dependency', strength: 1 },
            { source: 'UPSC', target: 'Geo_Physical', type: 'dependency', strength: 1 },

            // History Dependencies
            { source: 'Hist_Ancient', target: 'Hist_Culture', type: 'related', strength: 0.8 },
            { source: 'Hist_Medieval', target: 'Hist_Culture', type: 'related', strength: 0.8 },
            { source: 'Hist_Modern', target: 'Pol_Const', type: 'dependency', strength: 0.5 }, // Constitution evolved from modern history

            // Geography Dependencies
            { source: 'Geo_Physical', target: 'Geo_Indian', type: 'dependency', strength: 0.9 },
            { source: 'Geo_Physical', target: 'Geo_Climate', type: 'dependency', strength: 0.9 },
            { source: 'Geo_Climate', target: 'Env_Eco', type: 'dependency', strength: 0.7 }, // Climate affects ecology
            { source: 'Geo_Indian', target: 'Eco_Macro', type: 'related', strength: 0.3 }, // Resources affect economy

            // Polity Dependencies
            { source: 'Pol_Const', target: 'Pol_Gov', type: 'dependency', strength: 0.9 },
            { source: 'Pol_Gov', target: 'Pol_IR', type: 'related', strength: 0.6 },

            // Economy Dependencies
            { source: 'Eco_Macro', target: 'Eco_Banking', type: 'dependency', strength: 0.8 },
            { source: 'Eco_Macro', target: 'Eco_Budget', type: 'dependency', strength: 0.7 },
            { source: 'Eco_Budget', target: 'Pol_Gov', type: 'related', strength: 0.5 }, // Budget is a political tool
        ];
    }

    public getGraphData() {
        return {
            nodes: this.nodes,
            links: this.links
        };
    }

    public updateMastery(completedItems: { subject: string, topic: string }[]) {
        // Create a frequency map for subjects
        const subjectCounts: { [key: string]: number } = {};
        completedItems.forEach(item => {
            subjectCounts[item.subject] = (subjectCounts[item.subject] || 0) + 1;
        });

        this.nodes = this.nodes.map(node => {
            let boost = 0;

            // 1. Group Boost: If you completed tasks in this subject, increase mastery
            if (subjectCounts[node.group]) {
                boost += subjectCounts[node.group] * 2; // +2% per task in this subject
            }

            // 2. Specific Topic Boost: If the task topic contains the node label
            const directHits = completedItems.filter(item =>
                item.topic.toLowerCase().includes(node.label.toLowerCase()) ||
                node.label.toLowerCase().includes(item.topic.toLowerCase())
            ).length;

            if (directHits > 0) {
                boost += directHits * 10; // +10% for direct topic match
            }

            // Cap mastery at 100. Start from 0.
            const newMastery = Math.min(100, 0 + boost);

            return {
                ...node,
                mastery: newMastery
            };
        });

        this.calculateCentrality();
    }

    private calculateCentrality() {
        // Simplified Betweenness Centrality
        // Nodes with > 3 connections are considered "Bridges" for this MVP
        const connectionCounts: { [key: string]: number } = {};

        this.links.forEach(link => {
            connectionCounts[link.source] = (connectionCounts[link.source] || 0) + 1;
            connectionCounts[link.target] = (connectionCounts[link.target] || 0) + 1;
        });

        this.nodes = this.nodes.map(node => ({
            ...node,
            isBridge: (connectionCounts[node.id] || 0) >= 3
        }));
    }
}
