// src/services/authService.js
import axios from 'axios';

const API_URL = 'http://localhost:8000/api/users/';
const TOKEN_API_URL = 'http://localhost:8000/api/token/';

// Helper function to get the current access token
export const getAccessToken = () => {
    return localStorage.getItem('access_token');
};

// 1. Login Function (POST /api/token/)
export const login = async (email, password) => {
    const response = await axios.post(TOKEN_API_URL, { 
        email, 
        password 
    });

    if (response.data.access) {
        localStorage.setItem('access_token', response.data.access);
        localStorage.setItem('refresh_token', response.data.refresh);
        
        // Store remaining user data (ID, email, role, etc.)
        const { access, refresh, ...userData } = response.data;
        localStorage.setItem('user', JSON.stringify(userData));
        return userData;
    }
};

// 2. Logout Function
export const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
};

// 3. Register Function (POST /api/users/register/)
export const register = async (formData) => {
    const token = getAccessToken();
    if (!token) {
        throw new Error("Authentication token missing.");
    }
    return axios.post(API_URL + 'register/', formData, {
        headers: {
            Authorization: `Bearer ${token}`,
        },
    });
};

// 4. API Client Instance with Auth Interceptor (CRITICAL)
export const api = axios.create({
    baseURL: 'http://localhost:8000/api/',
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor to attach JWT to every request
api.interceptors.request.use(
    (config) => {
        const token = getAccessToken();
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);