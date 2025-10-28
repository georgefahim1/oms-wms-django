// src/components/Dashboard/AttendanceToggle.jsx
import React, { useState, useEffect } from 'react';
import * as dashboardService from '@/services/dashboardService';
import { useAuth } from '@/hooks/useAuth';

const AttendanceToggle = () => {
    const { isAuthenticated } = useAuth();
    const [isClockedIn, setIsClockedIn] = useState(false);
    const [loading, setLoading] = useState(true);
    const [message, setMessage] = useState(null);

    // Fetch initial status when component loads
    const fetchStatus = async () => {
        if (!isAuthenticated) return;
        try {
            const status = await dashboardService.getAttendanceStatus();
            setIsClockedIn(status);
        } catch (error) {
            console.error("Failed to fetch attendance status:", error);
            setMessage({ type: 'error', text: 'Failed to load status.' });
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchStatus();
    }, [isAuthenticated]);

    const handleToggle = async () => {
        setLoading(true);
        setMessage(null);
        try {
            if (isClockedIn) {
                await dashboardService.clockOut();
                setMessage({ type: 'success', text: 'Clocked Out successfully.' });
                setIsClockedIn(false);
            } else {
                await dashboardService.clockIn();
                setMessage({ type: 'success', text: 'Clocked In successfully. Start tracking tasks.' });
                setIsClockedIn(true);
            }
        } catch (error) {
            const errorMsg = error.response?.data?.detail || 'Action failed.';
            setMessage({ type: 'error', text: errorMsg });
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <div style={styles.statusBox}>Checking Status...</div>;

    return (
        <div style={styles.container}>
            <p style={styles.statusBox}>
                Status: <strong style={{ color: isClockedIn ? 'green' : 'red' }}>
                    {isClockedIn ? 'CLOCK IN ACTIVE' : 'CLOCKED OUT'}
                </strong>
            </p>
            {message && <p style={message.type === 'error' ? styles.error : styles.success}>{message.text}</p>}
            <button 
                onClick={handleToggle} 
                disabled={loading}
                style={{...styles.button, backgroundColor: isClockedIn ? '#dc3545' : '#28a745'}}
            >
                {isClockedIn ? 'CLOCK OUT' : 'CLOCK IN'}
            </button>
        </div>
    );
};

const styles = {
    container: { border: '1px solid #ddd', padding: '15px', borderRadius: '8px', marginTop: '15px', textAlign: 'center' },
    statusBox: { fontWeight: '500', fontSize: '1.1rem', marginBottom: '10px' },
    button: { padding: '10px 30px', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '1.1rem' },
    error: { color: 'white', background: '#dc3545', padding: '5px', borderRadius: '4px', textAlign: 'center', marginBottom: '10px' },
    success: { color: 'white', background: '#28a745', padding: '5px', borderRadius: '4px', textAlign: 'center', marginBottom: '10px' },
};

export default AttendanceToggle;