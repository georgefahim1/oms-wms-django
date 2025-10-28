// src/components/Dashboard/PTORequestForm.jsx
import React, { useState } from 'react';
import * as dashboardService from '@/services/dashboardService'; // <-- ABSOLUTE PATH
import { useAuth } from '@/hooks/useAuth'; // <-- ABSOLUTE PATH

const PTORequestForm = () => {
// ... (rest of the component logic remains the same)
    const { user } = useAuth();
    const [formData, setFormData] = useState({
        start_date: '',
        end_date: '',
        request_days: 0,
        reason: '',
    });
    const [message, setMessage] = useState(null);

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setMessage(null);

        try {
            await dashboardService.createTimeOffRequest(formData);
            setMessage({ type: 'success', text: 'Time Off Request submitted successfully!' });
            setFormData({ start_date: '', end_date: '', request_days: 0, reason: '' }); 
        } catch (error) {
            const errorMsg = error.response?.data?.detail || error.response?.data?.request_days?.[0] || 'Submission failed.';
            setMessage({ type: 'error', text: errorMsg });
        }
    };

    return (
        <div style={styles.container}>
            <h3>Submit Time Off Request</h3>
            <p>Available PTO: **{user.pto_balance_days} days**</p>
            {message && <p style={message.type === 'error' ? styles.error : styles.success}>{message.text}</p>}
            
            <form onSubmit={handleSubmit} style={styles.form}>
                <label>Start Date</label>
                <input type="date" name="start_date" value={formData.start_date} onChange={handleChange} required style={styles.input} />

                <label>End Date</label>
                <input type="date" name="end_date" value={formData.end_date} onChange={handleChange} required style={styles.input} />

                <label>Days Requested</label>
                <input type="number" name="request_days" value={formData.request_days} onChange={handleChange} required min="0.5" step="0.5" style={styles.input} />

                <label>Reason</label>
                <textarea name="reason" value={formData.reason} onChange={handleChange} required style={styles.textarea} />

                <button type="submit" style={styles.button}>Submit Request</button>
            </form>
        </div>
    );
};

const styles = {};
styles.container = { padding: '20px', border: '1px solid #ccc', borderRadius: '8px', marginBottom: '20px' };
styles.form = { display: 'grid', gridTemplateColumns: '1fr', gap: '10px' };
styles.input = { padding: '8px', borderRadius: '4px', border: '1px solid #ddd' };
styles.textarea = { padding: '8px', borderRadius: '4px', border: '1px solid #ddd', height: '80px' };
styles.button = { padding: '10px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', marginTop: '10px' };
styles.error = { color: 'white', background: '#dc3545', padding: '10px', borderRadius: '4px', textAlign: 'center' };
styles.success = { color: 'white', background: '#28a745', padding: '10px', borderRadius: '4px', textAlign: 'center' };

export default PTORequestForm;