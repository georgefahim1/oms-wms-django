// src/pages/DashboardPage.jsx
import React from 'react';
import { useAuth } from '../hooks/useAuth';

function DashboardPage() {
    const { user, hasRole, isManager } = useAuth();

    const getRoleSpecificContent = () => {
        if (hasRole(['High-Level Manager', 'Middle-Level Manager'])) {
            return (
                <div style={{ border: '1px solid #343a40', padding: '20px', background: '#f8f9fa' }}>
                    <h3>Strategic/Tactical Oversight View</h3>
                    <p>Access to KPIs, Audit Logs, and Private Manager Tasks (Phase IV implementation).</p>
                    <p>**Pending Feature:** Implement API calls to /analytics/kpis/ and /manager/tasks/</p>
                </div>
            );
        }

        if (hasRole(['Front Desk'])) {
            return (
                <div style={{ border: '1px solid #17a2b8', padding: '20px', background: '#e9ecef' }}>
                    <h3>Front Desk Order Routing</h3>
                    <p>View and route pending orders, dispatch deliveries (Phase II: Steps 6 & 7).</p>
                </div>
            );
        }

        if (hasRole(['Sales Rep', 'Delivery Personnel', 'Store Personnel', 'Lab Personnel'])) {
            return (
                <div style={{ border: '1px solid #28a745', padding: '20px', background: '#e2f0d9' }}>
                    <h3>Mobile Execution Portal ({user.role})</h3>
                    <p>Clock In/Out, GPS Tracking, and Proof of Execution (QC/POD) forms.</p>
                </div>
            );
        }

        return <p>Loading role view...</p>;
    };

    return (
        <div style={{ padding: '20px' }}>
            <h2>Welcome, {user.first_name} | {user.role} Portal</h2>
            {getRoleSpecificContent()}

            {/* Manager Link */}
            {isManager && (
                <p style={{ marginTop: '20px' }}>
                    <a href="/register" style={{ color: '#007bff', textDecoration: 'none' }}>Go to User Registration Portal</a>
                </p>
            )}
        </div>
    );
}

export default DashboardPage;