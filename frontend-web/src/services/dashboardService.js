// src/services/dashboardService.js
import { api } from './authService';

// 1. Fetch Key Performance Indicators (HLM Dashboard)
export const getKPIs = async () => {
    const response = await api.get('analytics/kpis/');
    return response.data;
};

// 2. Fetch Staff Status Audit Log (MLM/HLM Dashboard)
export const getStatusAuditLog = async () => {
    const response = await api.get('audit/status/');
    return response.data;
};

// 3. Fetch GPS Tracking History (MLM/HLM Dashboard)
export const getGpsHistory = async () => {
    const response = await api.get('audit/gps/');
    return response.data;
};

// 8. Fetch the list of all employees (for the manager to choose who to override)
export const getAllEmployees = async () => {
    // Corrected to specifically fetch data from the list view (ListAPIView does not return .data, it returns .data.results)
    const response = await api.get('users/'); 
    
    // FIX: Return the response data directly, which contains the results array and pagination keys
    return response.data; 
};
// 9. Get user's current attendance status
export const getAttendanceStatus = async () => {
    // GET /api/attendance/
    const response = await api.get('attendance/');
    return response.data.is_clocked_in; // Returns true or false
};

// 10. Clock In (POST /api/attendance/)
export const clockIn = async () => {
    return api.post('attendance/');
};

// 11. Clock Out (PUT /api/attendance/)
export const clockOut = async () => {
    return api.put('attendance/');
};