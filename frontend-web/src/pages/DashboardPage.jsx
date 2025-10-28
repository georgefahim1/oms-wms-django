// frontend-web/src/pages/DashboardPage.jsx
import React, { useEffect, useState } from 'react';
import { useAuth } from '@/hooks/useAuth';
import * as dashboardService from '@/services/dashboardService';

// Import necessary components
import PTORequestForm from '@/components/Dashboard/PTORequestForm';
import PTOApprovalList from '@/components/Dashboard/PTOApprovalList';
import StatusOverrideTool from '@/components/Dashboard/StatusOverrideTool'; 
import AttendanceToggle from '@/components/Dashboard/AttendanceToggle';

function DashboardPage() {
    const { user, hasRole, isManager } = useAuth();
    const [kpis, setKpis] = useState(null);
    const [auditLog, setAuditLog] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // Fetch data only for managers who need it (HLM/MLM/EM)
    useEffect(() => {
        if (isManager) {
            const fetchData = async () => {
                try {
                    const [kpiData, auditData] = await Promise.all([
                        dashboardService.getKPIs(),
                        dashboardService.getStatusAuditLog(),
                    ]);
                    setKpis(kpiData);
                    setAuditLog(auditData);
                } catch (err) {
                    console.error("Dashboard data fetch failed:", err);
                    setError("Failed to load management data. Access denied or API error.");
                } finally {
                    setLoading(false);
                }
            };
            fetchData();
        } else {
            setLoading(false);
        }
    }, [isManager]);

    // ---------------------------------------------------
    // RENDER FUNCTIONS (Defined once inside component)
    // ---------------------------------------------------
    
    const renderKpiCards = () => {
        if (loading) return <p>Loading KPIs...</p>;
        if (error) return <p style={{color: 'red'}}>{error}</p>;
        if (!kpis) return null;

        return (
            <div style={styles.kpiContainer}>
                <div style={styles.kpiCard}>
                    <h4>Average Cycle Time</h4>
                    <p style={styles.kpiValue}>{kpis.average_cycle_time_minutes || 0} min</p>
                    <small>Order Creation to Delivery</small>
                </div>
                <div style={styles.kpiCard}>
                    <h4>Protocol Adherence %</h4>
                    <p style={styles.kpiValue}>{kpis.protocol_adherence_percent || 0}%</p>
                    <small>QC Photo compliance for store orders</small>
                </div>
                <div style={styles.kpiCard}>
                    <h4>Sales Adherence Rate</h4>
                    <p style={styles.kpiValue}>{kpis.sales_planning_adherence_rate || 0}%</p>
                    <small>Planned vs. Missed Visits</small>
                </div>
            </div>
        );
    };

    const renderAuditLog = () => {
        if (!auditLog) return null;
        return (
            <div style={styles.auditContainer}>
                <h3>Staff Status Audit Log</h3>
                <table style={styles.table}>
                    <thead>
                        <tr>
                            <th>Time</th>
                            <th>User</th>
                            <th>Override By</th>
                            <th>Status Change</th>
                            <th>Reason</th>
                        </tr>
                    </thead>
                    <tbody>
                        {auditLog.map(log => (
                            <tr key={log.id}>
                                <td>{new Date(log.change_time).toLocaleTimeString()}</td>
                                <td>{log.user_email}</td>
                                <td>{log.changed_by_email}</td>
                                <td>{log.old_status} &rarr; {log.new_status}</td>
                                <td>{log.status_reason}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        );
    };

    const getRoleSpecificContent = () => {
        // HLM/MLM/EM roles get the management tools
        if (hasRole(['High-Level Manager', 'Middle-Level Manager', 'Employee Manager'])) {
            return (
                <div style={styles.managerView}>
                    {/* KPI Cards and Audit Logs */}
                    {renderKpiCards()}
                    {renderAuditLog()} 

                    {/* Manager Approval View (MLM/EM) */}
                    {(hasRole(['Middle-Level Manager', 'Employee Manager'])) && <PTOApprovalList />}
                    
                    {/* Status Override Component (MLM/EM) */}
                    <StatusOverrideTool /> 
                </div>
            );
        }
        
        // Employee-level roles need the Execution tools
        if (hasRole(['Sales Rep', 'Delivery Personnel', 'Store Personnel', 'Lab Personnel', 'Front Desk'])) {
            return (
                <div style={styles.executionView}>
                    <h3>{user.role} Execution Portal</h3>
                    
                    {/* Clock In/Out button */}
                    <AttendanceToggle /> 
                    
                    {/* PTO Form for employees */}
                    <PTORequestForm /> 
                    
                </div>
            );
        }

        return null;
    };
    
    // ---------------------------------------------------
    // STYLES (Defined once outside component body)
    // ---------------------------------------------------
    const styles = {
        managerView: { marginTop: '20px' },
        kpiContainer: { display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px', marginBottom: '30px' },
        kpiCard: { padding: '15px', background: '#e9ecef', borderRadius: '8px', boxShadow: '0 4px 6px rgba(0,0,0,0.05)' },
        kpiValue: { fontSize: '1.8rem', fontWeight: 'bold', color: '#007bff', margin: '5px 0' },
        auditContainer: { marginTop: '30px', borderTop: '1px solid #ccc', paddingTop: '20px' },
        table: { width: '100%', borderCollapse: 'collapse', marginTop: '15px' },
        tableHead: { background: '#f2f2f2' },
        primaryButton: { padding: '10px 20px', background: '#28a745', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' },
        executionView: { padding: '20px', background: '#f0fff0', border: '1px solid #28aa45', borderRadius: '8px' }
    };
    
    // ---------------------------------------------------
    // MAIN RENDER
    // ---------------------------------------------------

    return (
        <div style={{ padding: '20px' }}>
            <h2>Welcome, {user.first_name}! | {user.role} Dashboard</h2>
            {getRoleSpecificContent()}
        </div>
    );
}
    
export default DashboardPage;