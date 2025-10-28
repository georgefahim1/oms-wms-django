// src/components/Auth/LoginForm.jsx
import React, { useState } from 'react';
import { useAuth } from '@/hooks/useAuth';

function LoginForm() {
    const { login, loading } = useAuth();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [message, setMessage] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setMessage('');
        
        const result = await login(email, password);
        
        if (!result.success) {
            setMessage(result.message);
        }
    };

    return (
        <form onSubmit={handleSubmit} style={styles.form}>
            {message && <p style={styles.error}>{message}</p>}
            
            <input
                type="email"
                placeholder="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                style={styles.input}
                disabled={loading}
            />
            <input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                style={styles.input}
                disabled={loading}
            />
            <button type="submit" style={styles.button} disabled={loading}>
                {loading ? 'Authenticating...' : 'Log In'}
            </button>
        </form>
    );
}

const styles = {
    form: { display: 'flex', flexDirection: 'column', gap: '15px' },
    input: { padding: '10px', borderRadius: '4px', border: '1px solid #ddd' },
    button: { padding: '10px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' },
    error: { color: '#dc3545', backgroundColor: '#f8d7da', padding: '10px', borderRadius: '4px', textAlign: 'center' }
};

export default LoginForm;