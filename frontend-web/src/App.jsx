// frontend-web/src/App.jsx
import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './hooks/useAuth'; 
import NavBar from './components/NavBar'; 
import LoginPage from './pages/LoginPage'; 
import DashboardPage from './pages/DashboardPage'; 
import RegisterUserPage from './pages/RegisterUserPage'; 
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
      {/* NavBar is visible only when authenticated */}
      {isAuthenticated && <NavBar />} 

      <Routes>
        {/* Public Route */}
        <Route path="/login" element={<LoginPage />} />

        {/* Redirect root to login or dashboard */}
        <Route path="/" element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <Navigate to="/login" replace />} />

        {/* Protected Routes */}
        <Route path="/dashboard" element={<ProtectedRoute element={<DashboardPage />} />} />
        <Route path="/register" element={<ProtectedRoute element={<RegisterUserPage />} />} />

        {/* Catch-all redirect */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  );
}

export default App;