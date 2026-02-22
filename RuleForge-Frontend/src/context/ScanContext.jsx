import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { fetchStats } from '../services/api';

const ScanContext = createContext({ hasData: false, loading: true, refresh: () => { } });

export function ScanProvider({ children }) {
    const [hasData, setHasData] = useState(false);
    const [loading, setLoading] = useState(true);

    const refresh = useCallback(async () => {
        try {
            const stats = await fetchStats();
            // hasData is true when at least one rule has been extracted
            setHasData((stats.total_rules || 0) > 0);
        } catch {
            setHasData(false);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => { refresh(); }, [refresh]);

    return (
        <ScanContext.Provider value={{ hasData, loading, refresh }}>
            {children}
        </ScanContext.Provider>
    );
}

export const useScan = () => useContext(ScanContext);
