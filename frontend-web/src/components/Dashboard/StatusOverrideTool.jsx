// src/components/Dashboard/StatusOverrideTool.jsx
import React, { useState, useEffect } from 'react';
import { useAuth } from '@/hooks/useAuth'; // Note: Assuming Absolute Path config is now active
import * as dashboardService from '@/services/dashboardService'; 

// NOTE: We assume your absolute pathing (@/) configuration in vite.config.js is now working.

const StatusOverrideTool = () => {
    const { user } = useAuth();
    const [employees, setEmployees] = useState([]);
    const [selectedUserId, setSelectedUserId] = useState('');
    const [reason, setReason] = useState('');
    const [message, setMessage] = useState(null);
    const [loading, setLoading] = useState(true);

    const lowLevelRoles = [
        'Sales Rep', 'Front Desk', 'Store Personnel', 'Lab Personnel', 'Delivery Personnel'
    ];

    useEffect(() => {
        // Fetch all users to populate the dropdown
        const fetchEmployees = async () => {
            try {
                // Fetch paginated data (response.data contains 'results')
                const response = await dashboardService.getAllEmployees(); 
                
                // CRITICAL FIX: Ensure 'results' exists and is an array before filtering
                const allStaff = response.results || [];
                
                // Filter locally to show only low-level employees
                const lowLevelStaff = allStaff.filter(emp => lowLevelRoles.includes(emp.role));
                
                setEmployees(lowLevelStaff);
                if (lowLevelStaff.length > 0) {
                    setSelectedUserId(lowLevelStaff[0].id);
                }
            } catch (error) {
                console.error("Failed to fetch employees:", error.response || error);
                // Providing a clearer error message
                setMessage({ type: 'error', text: 'Failed to load employee list. Did you create non-managerial staff?' });
            } finally {
                setLoading(false);
            }
        };
        fetchEmployees();
    }, []);
    const handleSubmit = async (e) => {
        e.preventDefault();
        setMessage(null);

        try {
            await dashboardService.overrideStaffStatus(selectedUserId, reason);
            setMessage({ type: 'success', text: `Successfully set employee status to UNVAILABLE and logged audit trail.` });
            setReason('');
        } catch (error) {
            const errorMsg = error.response?.data?.status_reason?.[0] || error.response?.data?.detail || 'Override failed.';
            setMessage({ type: 'error', text: errorMsg });
        }
    };

    if (loading) return <div>Loading Staff List...</div>;

    return (
        <div style={styles.container}>
            <h3>Staff Status Override Tool</h3>
            <p>Role: {user.role} | Use this to log mandatory audits for status changes.</p>
            {message && <p style={message.type === 'error' ? styles.error : styles.success}>{message.text}</p>}

            <form onSubmit={handleSubmit} style={styles.form}>
                <label>Select Employee:</label>
                <select value={selectedUserId} onChange={(e) => setSelectedUserId(e.target.value)} required style={styles.input}>
                    {employees.map(emp => (
                        <option key={emp.id} value={emp.id}>{emp.first_name} {emp.last_name} ({emp.role_key})</option>
                    ))}
                </select>
                
                <label style={{marginTop: '10px'}}>Mandatory Reason for Override:</label>
                <textarea 
                    value={reason} 
                    onChange={(e) => setReason(e.target.value)} 
                    placeholder="E.g., Sent home due to illness, Safety violation, Training..."
                    required 
                    style={styles.textarea}
                />
                
                <p style={{color: 'red', fontSize: '12px'}}>New Status will be: UNAVAILABLE</p>

                <button type="submit" style={styles.button}>Log Status Override</button>
            </form>
        </div>
    );
};

const styles = {};
styles.container = { padding: '20px', border: '1px solid #ffc107', borderRadius: '8px', marginTop: '30px' };
styles.form = { display: 'grid', gridTemplateColumns: '1fr', gap: '10px' };
styles.input = { padding: '8px', borderRadius: '4px', border: '1px solid #ddd' };
styles.textarea = { padding: '8px', borderRadius: '4px', border: '1px solid #ddd', height: '80px' };
styles.button = { padding: '10px', backgroundColor: '#dc3545', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', marginTop: '10px' };
styles.error = { color: 'white', background: '#dc3545', padding: '10px', borderRadius: '4px', textAlign: 'center' };
styles.success = { color: 'white', background: '#28a745', padding: '10px', borderRadius: '4px', textAlign: 'center' };


export default StatusOverrideTool;