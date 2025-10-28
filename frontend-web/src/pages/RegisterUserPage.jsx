// src/pages/RegisterUserPage.jsx
import React from 'react';
import { useAuth } from '../hooks/useAuth';
import RegisterForm from '../components/Auth/RegisterForm'; // Component we will create next
import { Navigate } from 'react-router-dom';

function RegisterUserPage() {
    const { user, hasRole } = useAuth();

    // CRITICAL RBAC CHECK: Only HLM and MLM can access this page
    if (!hasRole(['High-Level Manager', 'Middle-Level Manager'])) {
        // Redirect unauthorized users away
        return <Navigate to="/dashboard" replace />;
    }

    return (
        <div style={{ padding: '20px', maxWidth: '600px', margin: '50px auto', border: '1px solid #007bff', borderRadius: '8px' }}>
            <h2 style={{ textAlign: 'center', color: '#007bff' }}>New User Registration</h2>
            <p style={{ textAlign: 'center', color: '#666' }}>Manager portal for creating new employees.</p>
            <RegisterForm managerId={user.id} />
        </div>
    );
}

export default RegisterUserPage;