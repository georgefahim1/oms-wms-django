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

// --- HR & PTO Management ---

// 4. Employee submits a new time-off request
export const createTimeOffRequest = async (requestData) => {
    return api.post('hr/time-off/', requestData);
};

// 5. Manager views pending time-off requests
export const getPendingTimeOffRequests = async () => {
    return api.get('hr/time-off/');
};

// 6. Manager approves or rejects a time-off request
export const updateTimeOffRequestStatus = async (requestId, newStatus) => {
    return api.patch(`hr/time-off/${requestId}/approve/`, { status: newStatus });
};

// 7. Manager overrides an employee's status to Unavailable
export const overrideStaffStatus = async (userId, reason) => {
    return api.post('managers/status/override/', { 
        user_id: userId, 
        new_status: 'Unavailable', 
        status_reason: reason
    });
};

// 8. Fetch the list of all employees (Non-Paginated List)
export const getAllEmployees = async () => {
    // Uses the custom NonPaginatedUserListView path
    const response = await api.get('users/employee-list/'); 
    
    // Returns the direct array, as pagination is disabled on the backend view
    return { results: response.data }; 
};