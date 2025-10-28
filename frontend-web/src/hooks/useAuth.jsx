// src/hooks/useAuth.jsx
import React, { createContext, useContext, useState, useEffect } from 'react';
import * as authService from '@/services/authService';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(JSON.parse(localStorage.getItem('user')) || null);
    const [loading, setLoading] = useState(false);

    const login = async (email, password) => {
        setLoading(true);
        try {
            const userData = await authService.login(email, password);
            setUser(userData);
            setLoading(false);
            return { success: true };
        } catch (error) {
            setLoading(false);
            // Handling the nested Django error structure
            const errorMessage = error.response?.data?.detail || 'Login failed. Check credentials/server.';
            return { success: false, message: errorMessage };
        }
    };

    const logout = () => {
        authService.logout();
        setUser(null);
    };

    const registerUser = async (formData) => {
        try {
            await authService.register(formData);
            return { success: true, message: "User registered successfully." };
        } catch (error) {
            const errorMsg = error.response?.data?.detail || error.response?.data?.email || error.response?.data?.role_key || "Registration failed.";
            return { success: false, message: error.response?.data?.email?.[0] || error.response?.data?.password?.[0] || errorMsg };
        }
    };
    
    const contextValue = {
        user,
        loading,
        login,
        logout,
        registerUser,
        isAuthenticated: !!user,
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