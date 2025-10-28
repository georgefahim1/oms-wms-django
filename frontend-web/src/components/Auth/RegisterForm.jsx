// src/components/Auth/RegisterForm.jsx
import React, { useState } from 'react';
import { useAuth } from '@/hooks/useAuth';
function RegisterForm() {
    const { registerUser, loading, user } = useAuth();
    const [formData, setFormData] = useState({
        email: '', 
        password: '', 
        first_name: '', 
        last_name: '', 
        role_key: 'Sales Rep', 
        reporting_manager_id: user?.id || ''
    });
    const [message, setMessage] = useState('');
    const [isError, setIsError] = useState(false);

    const ALL_ROLES = [
        'High-Level Manager', 'Middle-Level Manager', 'Employee Manager', 
        'Sales Rep', 'Front Desk', 'Store Personnel', 'Lab Personnel', 
        'Delivery Personnel'
    ];

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setMessage('Creating user...');
        setIsError(false);

        // NOTE: The reporting_manager_id is automatically set to the logged-in manager's ID
        const payload = {
             ...formData,
             reporting_manager: formData.reporting_manager_id 
        };

        const result = await registerUser(payload);

        if (result.success) {
            setMessage(result.message);
            // Clear form except manager ID
            setFormData(prev => ({
                email: '', password: '', first_name: '', last_name: '', role_key: 'Sales Rep', reporting_manager_id: prev.reporting_manager_id
            }));
        } else {
            setIsError(true);
            setMessage(`Error: ${result.message}`);
        }
    };

    return (
        <form onSubmit={handleSubmit} style={styles.form}>
            {message && <p style={isError ? styles.error : styles.success}>{message}</p>}

            <input type="email" name="email" placeholder="Email" value={formData.email} onChange={handleChange} required style={styles.input} disabled={loading} />
            <input type="password" name="password" placeholder="Password" value={formData.password} onChange={handleChange} required style={styles.input} disabled={loading} />
            <input type="text" name="first_name" placeholder="First Name" value={formData.first_name} onChange={handleChange} required style={styles.input} disabled={loading} />
            <input type="text" name="last_name" placeholder="Last Name" value={formData.last_name} onChange={handleChange} required style={styles.input} disabled={loading} />

            <select name="role_key" value={formData.role_key} onChange={handleChange} required style={styles.input} disabled={loading}>
                {ALL_ROLES.map(role => (
                    <option key={role} value={role}>{role}</option>
                ))}
            </select>

            <p style={{fontSize: '12px', color: '#666'}}>
                Reporting Manager (Default: Your ID): {formData.reporting_manager_id}
            </p>

            <button type="submit" style={styles.button} disabled={loading}>
                {loading ? 'Creating...' : 'Create User'}
            </button>
        </form>
    );
}

const styles = {
    form: { display: 'flex', flexDirection: 'column', gap: '15px' },
    input: { padding: '10px', borderRadius: '4px', border: '1px solid #ddd' },
    button: { padding: '10px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' },
    success: { color: '#155724', backgroundColor: '#d4edda', padding: '10px', borderRadius: '4px', textAlign: 'center' },
    error: { color: '#dc3545', backgroundColor: '#f8d7da', padding: '10px', borderRadius: '4px', textAlign: 'center' }
};

export default RegisterForm;