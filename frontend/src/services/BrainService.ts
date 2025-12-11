import axios from 'axios';

const API_URL = '/api/brain';

export interface BrainAction {
    type: string;
    label?: string;
    payload: any;
}

export interface BrainResponse {
    deep_reasoning?: string;
    response_text: string;
    suggested_actions: BrainAction[];
}

export interface BrainInsight {
    type: string;
    priority: 'High' | 'Medium' | 'Low';
    message: string;
    actions: BrainAction[];
}

class BrainService {
    /**
     * Send user input to the Brain and get a response.
     */
    async think(input: string, context: any = {}): Promise<BrainResponse> {
        try {
            const response = await axios.post(`${API_URL}/think`, {
                input,
                context
            });
            return response.data;
        } catch (error) {
            console.error("Brain Think Error:", error);
            return {
                response_text: "I cannot think right now. The connection to the Cortex is severed.",
                suggested_actions: []
            };
        }
    }

    /**
     * Execute a specific action suggested by the Brain.
     */
    async executeAction(type: string, payload: any): Promise<any> {
        try {
            const response = await axios.post(`${API_URL}/execute`, {
                type,
                payload
            });
            return response.data;
        } catch (error) {
            console.error("Brain Execution Error:", error);
            throw error;
        }
    }

    /**
     * Get proactive insights (optimizations) from the Brain.
     */
    async getProactiveInsights(): Promise<BrainInsight[]> {
        try {
            const response = await axios.get(`${API_URL}/proactive`);
            return response.data.insights || [];
        } catch (error) {
            console.error("Brain Proactive Error:", error);
            return [];
        }
    }

    /**
     * Trigger an immediate optimization scan.
     */
    async triggerOptimization(): Promise<{ analysis: string; actions_taken: any[] }> {
        try {
            const response = await axios.post(`${API_URL}/optimize`);
            return response.data;
        } catch (error) {
            console.error("Brain Optimization Error:", error);
            return {
                analysis: "Optimization failed.",
                actions_taken: []
            };
        }
    }

    /**
     * Check Brain health.
     */
    async getStatus(): Promise<any> {
        try {
            const response = await axios.get(`${API_URL}/status`);
            return response.data;
        } catch (error) {
            return { status: "OFFLINE" };
        }
    }

    /**
     * Ingest a strategic directive (Golden Path).
     */
    async ingestDirective(path: any[]): Promise<boolean> {
        try {
            const response = await axios.post(`${API_URL}/directive`, { path });
            return response.data.success;
        } catch (error) {
            console.error("Brain Directive Error:", error);
            return false;
        }
    }
}

export const brainService = new BrainService();
