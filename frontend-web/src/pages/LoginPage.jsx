// src/pages/LoginPage.jsx
import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import LoginForm from '@/components/Auth/LoginForm';

function LoginPage() {
    const { isAuthenticated } = useAuth();
    
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