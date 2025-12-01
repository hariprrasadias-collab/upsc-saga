import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import type { Message, Synapse, Insight, Action } from './types';

const API_BASE_URL = 'http://localhost:5000/api/brain';

export const useBrain = () => {
    const navigate = useNavigate();
    const [messages, setMessages] = useState<Message[]>([
        {
            id: 'init',
            text: "I am the Central Nervous System. I am listening.",
            sender: 'brain',
            timestamp: new Date()
        }
    ]);
    const [isThinking, setIsThinking] = useState(false);
    const [synapses, setSynapses] = useState<Synapse[]>([]);
    const [insights, setInsights] = useState<Insight[]>([]);
    const [isLoadingInsights, setIsLoadingInsights] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const clearError = useCallback(() => setTimeout(() => setError(null), 3000), []);

    const handleError = useCallback((msg: string, err: any) => {
        console.error(msg, err);
        setError(msg);
        clearError();
    }, [clearError]);

    const addMessage = useCallback((msg: Partial<Message>) => {
        setMessages(prev => [...prev, {
            id: Date.now().toString(),
            timestamp: new Date(),
            text: '',
            sender: 'brain',
            ...msg
        } as Message]);
    }, []);

    const fetchSynapses = useCallback(async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/status`);
            if (!response.ok) throw new Error('Failed to fetch status');
            const data = await response.json();

            const flatSynapses: Synapse[] = [];
            if (data.active_modules) {
                data.active_modules.forEach((module: string) => {
                    flatSynapses.push({ name: module, category: 'Module', description: 'Connected', status: 'online' });
                });
            } else if (data.synapses) {
                Object.entries(data.synapses).forEach(([category, items]: [string, any]) => {
                    items.forEach((item: string) => {
                        flatSynapses.push({ name: item, category: category, description: 'Connected', status: 'online' });
                    });
                });
            }
            setSynapses(flatSynapses);
        } catch (err) {
            handleError('Failed to load synapses', err);
        }
    }, [handleError]);

    const fetchProactiveInsights = useCallback(async () => {
        setIsLoadingInsights(true);
        try {
            const response = await fetch(`${API_BASE_URL}/proactive`);
            if (!response.ok) throw new Error('Failed to fetch insights');
            const data = await response.json();
            setInsights(data.insights || []);
        } catch (err) {
            handleError('Failed to load insights', err);
        } finally {
            setIsLoadingInsights(false);
        }
    }, [handleError]);

    const executeAction = useCallback(async (action: Action) => {
        try {
            const response = await fetch(`${API_BASE_URL}/execute`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ type: action.type, payload: action.payload }),
            });
            const result = await response.json();

            addMessage({
                text: `Action Executed: ${result.message || result.error || 'Completed'}`,
                sender: 'brain'
            });

            // Auto-Navigation Logic
            if (result.success) {
                switch (action.type) {
                    case 'CREATE_FLASHCARDS':
                        navigate('/flashcards');
                        break;
                    case 'SCHEDULE_REVISION':
                    case 'GENERATE_STUDY_PLAN':
                        navigate('/study-plan');
                        break;
                    case 'START_MOCK_TEST':
                    case 'CREATE_MOCK_TEST':
                        navigate('/mock-tests');
                        break;
                    case 'ANALYZE_WEAK_AREAS':
                        navigate('/weak-areas');
                        break;
                }
            }
        } catch (err) {
            handleError('Action execution failed', err);
        }
    }, [addMessage, handleError, navigate]);

    const optimizeSystem = useCallback(async () => {
        setIsThinking(true);
        try {
            const response = await fetch(`${API_BASE_URL}/optimize`, { method: 'POST' });
            if (!response.ok) throw new Error('Optimization failed');
            const data = await response.json();

            addMessage({
                text: `**Optimization Complete**\n\n${data.analysis}`,
                sender: 'brain',
                actions: data.actions_taken
            });
            return true;
        } catch (err) {
            handleError('Optimization failed', err);
            return false;
        } finally {
            setIsThinking(false);
        }
    }, [addMessage, handleError]);

    const sendMessage = useCallback(async (text: string) => {
        addMessage({ text, sender: 'user' });
        setIsThinking(true);

        try {
            const response = await fetch(`${API_BASE_URL}/think`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ input: text }),
            });

            if (!response.ok) throw new Error('Brain unreachable');
            const data = await response.json();

            addMessage({
                text: data.response_text || "I'm having trouble thinking right now.",
                sender: 'brain',
                actions: data.suggested_actions
            });
        } catch (err) {
            handleError('Brain disconnected', err);
            addMessage({
                text: "I seem to be disconnected from my cortex. Please check the backend connection.",
                sender: 'brain'
            });
        } finally {
            setIsThinking(false);
        }
    }, [addMessage, handleError]);

    return {
        messages,
        isThinking,
        synapses,
        insights,
        isLoadingInsights,
        error,
        fetchSynapses,
        fetchProactiveInsights,
        executeAction,
        optimizeSystem,
        sendMessage
    };
};
