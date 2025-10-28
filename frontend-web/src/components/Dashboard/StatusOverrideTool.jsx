// src/components/Dashboard/StatusOverrideTool.jsx
import React, { useState, useEffect } from 'react';
import { useAuth } from '@/hooks/useAuth';
import * as dashboardService from '@/services/dashboardService'; 

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
        const fetchEmployees = async () => {
            try {
                // Fetch non-paginated user list
                const response = await dashboardService.getAllEmployees(); 
                
                // CRITICAL FIX: Ensure 'results' exists and is an array before filtering
                const allStaff = response.results || []; 
                
                // Filter locally to show only low-level staff
                // NOTE: We assume the backend UserSerializer now returns first_name, last_name, and role_key.
                const lowLevelStaff = allStaff.filter(emp => lowLevelRoles.includes(emp.role_key));
                
                setEmployees(lowLevelStaff);
                
                // If there are staff, set the selected ID to the first one
                if (lowLevelStaff.length > 0) {
                    setSelectedUserId(lowLevelStaff[0].id);
                }
            } catch (error) {
                // Log the precise error for future debugging
                console.error("Failed to load employee list:", error.response || error);
                
                // Clear the list and show the failure message
                setEmployees([]);
                setMessage({ 
                    type: 'error', 
                    text: 'Failed to load employee list. Check backend logs for /api/users/employee-list/.' 
                });
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
            // Error handling for mandatory reason compliance or user not clocked in
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
                        <option key={emp.id} value={emp.id}>
                            {emp.first_name} {emp.last_name} ({emp.role_key})
                        </option>
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