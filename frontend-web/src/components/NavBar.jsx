// src/components/NavBar.jsx
import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';

function NavBar() {
    const { user, logout, hasRole } = useAuth();

    return (
        <header style={styles.header}>
            <div style={styles.brand}>OMS/WMS | {user.role}</div>
            <nav style={styles.nav}>
                <Link to="/dashboard" style={styles.link}>Dashboard</Link>
                
                {/* Conditional Link based on RBAC */}
                {hasRole(['High-Level Manager', 'Middle-Level Manager']) && (
                    <Link to="/register" style={styles.link}>Register User</Link>
                )}
                
                <button onClick={logout} style={styles.logoutButton}>
                    Log Out
                </button>
            </nav>
        </header>
    );
}

const styles = {
    header: { backgroundColor: '#343a40', color: 'white', padding: '15px 30px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' },
    brand: { fontSize: '1.2rem', fontWeight: 'bold' },
    nav: { display: 'flex', alignItems: 'center' },
    link: { color: 'white', textDecoration: 'none', marginRight: '20px', fontWeight: '500', transition: 'color 0.2s' },
    logoutButton: { backgroundColor: '#dc3545', color: 'white', border: 'none', padding: '8px 15px', borderRadius: '4px', cursor: 'pointer' }
};

export default NavBar;