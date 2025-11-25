import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface AnalyticsData {
    xp: number;
    level: number;
    study_hours: number;
    streak_days: number;
    activities_completed: number;
    max_xp?: number;
    next_level_xp?: number;
    hacksilver?: number;
}

interface AnalyticsContextType {
    analytics: AnalyticsData | null;
    loading: boolean;
    refreshAnalytics: (force?: boolean) => Promise<void>;
    incrementActivity: () => void;
}

const AnalyticsContext = createContext<AnalyticsContextType | undefined>(undefined);

export const useAnalytics = () => {
    const context = useContext(AnalyticsContext);
    if (!context) {
        throw new Error('useAnalytics must be used within AnalyticsProvider');
    }
    return context;
};

interface AnalyticsProviderProps {
    children: ReactNode;
}

export const AnalyticsProvider: React.FC<AnalyticsProviderProps> = ({ children }) => {
    const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
    const [loading, setLoading] = useState(true);
    const [lastFetch, setLastFetch] = useState<number>(0);

    const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

    const refreshAnalytics = async (force = false) => {
        const now = Date.now();

        // Skip if cached and not forced
        if (!force && lastFetch && (now - lastFetch) < CACHE_DURATION) {
            console.log('Using cached analytics data');
            return;
        }

        try {
            setLoading(true);
            const res = await fetch('http://localhost:5000/api/analytics/overview?timeframe=all');

            if (res.ok) {
                const data = await res.json();
                setAnalytics(data);
                setLastFetch(now);
            } else {
                console.error('Failed to fetch analytics');
            }
        } catch (err) {
            console.error('Error fetching analytics:', err);
        } finally {
            setLoading(false);
        }
    };

    const incrementActivity = () => {
        // Optimistic update - increment locally before refresh
        if (analytics) {
            setAnalytics({
                ...analytics,
                activities_completed: analytics.activities_completed + 1
            });
        }
        // Force refresh to get accurate XP/level data
        refreshAnalytics(true);
    };

    // Initial fetch on mount
    useEffect(() => {
        refreshAnalytics();
    }, []);

    const value: AnalyticsContextType = {
        analytics,
        loading,
        refreshAnalytics,
        incrementActivity
    };

    return (
        <AnalyticsContext.Provider value={value}>
            {children}
        </AnalyticsContext.Provider>
    );
};
