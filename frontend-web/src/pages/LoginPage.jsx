// src/pages/LoginPage.jsx
import React from 'react';
import { useAuth } from '../hooks/useAuth';
import LoginForm from '../components/Auth/LoginForm'; // Component we will create next
import { Navigate } from 'react-router-dom';

function LoginPage() {
    const { isAuthenticated, user } = useAuth();

    // Redirect logic: If already authenticated, go to dashboard
    if (isAuthenticated) {
        return <Navigate to="/dashboard" replace />;
    }

    return (
        <div style={{ padding: '20px', maxWidth: '400px', margin: '50px auto', border: '1px solid #ddd', borderRadius: '8px' }}>
            <h2 style={{ textAlign: 'center' }}>OMS/WMS Login</h2>
            <p style={{ textAlign: 'center', color: '#666' }}>Sign in to access the system.</p>
            <LoginForm />
        </div>
    );
}

export default LoginPage;