// src/App.jsx
import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth'; 
import NavBar from '@/components/NavBar'; 
import LoginPage from '@/pages/LoginPage'; 
import DashboardPage from '@/pages/DashboardPage'; 
import RegisterUserPage from '@/pages/RegisterUserPage'; 
import './App.css'; 

// Higher-Order Component to protect routes
const ProtectedRoute = ({ element: Element }) => {
    const { isAuthenticated } = useAuth();
    return isAuthenticated ? Element : <Navigate to="/login" replace />;
};

function App() {
  const { isAuthenticated } = useAuth();

  return (
    <div className="App">
      {isAuthenticated && <NavBar />} 
      
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        
        <Route path="/" element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <Navigate to="/login" replace />} />
        
        <Route path="/dashboard" element={<ProtectedRoute element={<DashboardPage />} />} />
        <Route path="/register" element={<ProtectedRoute element={<RegisterUserPage />} />} />
        
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  );
}

export default App;