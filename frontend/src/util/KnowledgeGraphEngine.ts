// Knowledge Graph Engine - The Nexus

export interface GraphNode {
    id: string;
    label: string;
    group: 'History' | 'Geography' | 'Polity' | 'Economy' | 'Science' | 'Environment' | 'Core' | 'General';
    radius: number;
    mastery: number; // 0 to 100
    isBridge?: boolean; // New: Centrality Flag
    roi?: number;
    yield?: number;
    effort?: number;
    weakness?: number;
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
        // Initial empty state, data loaded via loadData()
    }

    public async loadData(): Promise<void> {
        try {
            const response = await fetch('http://localhost:5000/api/golden-path/graph');
            const result = await response.json();

            if (result.success && result.data) {
                this.nodes = result.data.nodes.map((n: any) => ({
                    id: String(n.id),
                    label: n.data.label,
                    group: n.data.group || 'General',
                    radius: this.calculateRadius(n.data),
                    mastery: 0, // Mastery updated separately via updateMastery
                    roi: n.data.roi,
                    yield: n.data.yield,
                    effort: n.data.effort,
                    weakness: n.data.weakness
                }));

                this.links = result.data.edges.map((e: any) => ({
                    source: String(e.source),
                    target: String(e.target),
                    type: 'dependency',
                    strength: 1
                }));
            }
        } catch (error) {
            console.error("Failed to load Golden Path graph:", error);
            // Fallback to empty or hardcoded if needed
        }
    }

    private calculateRadius(data: any): number {
        // Radius based on ROI or Importance
        // Base radius 20, max 50
        const roi = data.roi || 1;
        return Math.min(Math.max(20, 20 * roi), 50);
    }

    public getGraphData() {
        return { nodes: this.nodes, links: this.links };
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
