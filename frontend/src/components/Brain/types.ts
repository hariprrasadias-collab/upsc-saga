export interface Action {
    label: string;
    type: string;
    payload: Record<string, any>;
}

export interface Message {
    id: string;
    text: string;
    sender: 'user' | 'brain';
    timestamp: Date;
    actions?: Action[];
}

export interface Synapse {
    name: string;
    category: string;
    description: string;
    status: 'online' | 'offline';
}

export interface Insight {
    type: string;
    priority: 'High' | 'Medium' | 'Low';
    message: string;
    actions?: Action[];
}
