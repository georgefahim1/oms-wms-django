// src/hooks/useAuth.jsx
import React, { createContext, useContext, useState, useEffect } from 'react';
import * as authService from '../services/authService';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    // State initialization from local storage
    const [user, setUser] = useState(JSON.parse(localStorage.getItem('user')) || null);
    const [loading, setLoading] = useState(false);

    // --- Core Authentication Actions ---
    
    const login = async (email, password) => {
        setLoading(true);
        try {
            const userData = await authService.login(email, password);
            setUser(userData);
            setLoading(false);
            return { success: true };
        } catch (error) {
            setLoading(false);
            const errorMessage = error.response?.data?.detail || 'Login failed. Check server status.';
            return { success: false, message: errorMessage };
        }
    };

    const logout = () => {
        authService.logout();
        setUser(null);
    };

    const registerUser = async (formData) => {
        const token = authService.getAccessToken();
        if (!token) {
            return { success: false, message: "Authentication token missing." };
        }
        try {
            await authService.register(formData, token);
            return { success: true, message: "User registered successfully." };
        } catch (error) {
            const errorMessage = error.response?.data?.detail || error.response?.data?.email || error.response?.data?.role_key || "Registration failed.";
            return { success: false, message: errorMessage };
        }
    };
    
    // --- Context Value ---
    const contextValue = {
        user,
        loading,
        login,
        logout,
        registerUser,
        isAuthenticated: !!user,
        // Helper function for RBAC checks in the UI
        hasRole: (roles) => user && roles.includes(user.role),
        isManager: user && (user.role === 'High-Level Manager' || user.role === 'Middle-Level Manager' || user.role === 'Employee Manager')
    };

    return (
        <AuthContext.Provider value={contextValue}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    return useContext(AuthContext);
};