// src/components/Dashboard/PTOApprovalList.jsx
import React, { useState, useEffect } from 'react';
import * as dashboardService from '@/services/dashboardService'; // <-- ABSOLUTE PATH

const PTOApprovalList = () => {
    const [requests, setRequests] = useState([]);
    const [loading, setLoading] = useState(true);
    const [message, setMessage] = useState(null);

    const fetchRequests = async () => {
        try {
            const data = await dashboardService.getPendingTimeOffRequests();
            setRequests(data);
        } catch (error) {
            setMessage({ type: 'error', text: 'Failed to load pending requests.' });
            console.error("Error fetching PTO requests:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchRequests();
    }, []);

    const handleAction = async (requestId, newStatus) => {
        try {
            await dashboardService.updateTimeOffRequestStatus(requestId, newStatus);
            setMessage({ type: 'success', text: `Request ${requestId} ${newStatus}D.` });
            fetchRequests(); // Refresh the list
        } catch (error) {
            const errorMsg = error.response?.data?.detail || 'Action failed.';
            setMessage({ type: 'error', text: errorMsg });
        }
    };

    if (loading) return <div>Loading Pending Requests...</div>;
    
    return (
        <div style={styles.container}>
            <h3>Pending Time Off Requests ({requests.length})</h3>
            {message && <p style={message.type === 'error' ? styles.error : styles.success}>{message.text}</p>}
            
            {requests.length === 0 ? (
                <p>No requests awaiting your approval.</p>
            ) : (
                <table style={styles.table}>
                    <thead>
                        <tr>
                            <th>Employee (ID)</th>
                            <th>Dates</th>
                            <th>Days</th>
                            <th>Reason</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {requests.map(req => (
                            <tr key={req.id}>
                                <td>{req.user}</td> 
                                <td>{req.start_date} to {req.end_date}</td>
                                <td>{req.request_days}</td>
                                <td>{req.reason}</td>
                                <td>
                                    <button onClick={() => handleAction(req.id, 'Approved')} style={{...styles.actionButton, background: 'green'}}>Approve</button>
                                    <button onClick={() => handleAction(req.id, 'Rejected')} style={{...styles.actionButton, background: 'red'}}>Reject</button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            )}
        </div>
    );
};

const styles = {};
styles.container = { padding: '20px', border: '1px solid #007bff', borderRadius: '8px', marginTop: '30px' };
styles.table = { width: '100%', borderCollapse: 'collapse', marginTop: '15px' };
styles.actionButton = { padding: '5px 10px', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', marginRight: '5px' };
styles.error = { color: 'white', background: '#dc3545', padding: '10px', borderRadius: '4px', textAlign: 'center' };
styles.success = { color: 'white', background: '#28a745', padding: '10px', borderRadius: '4px', textAlign: 'center' };

export default PTOApprovalList;