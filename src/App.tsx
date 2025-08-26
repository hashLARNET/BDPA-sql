import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './store/auth.store';
import Layout from './components/Layout';
import LoginForm from './components/auth/LoginForm';
import Dashboard from './components/dashboard/Dashboard';
import AvanceList from './components/avances/AvanceList';
import MedicionList from './components/mediciones/MedicionList';
import ReportGenerator from './components/reportes/ReportGenerator';
import ConfiguracionPanel from './components/configuracion/ConfiguracionPanel';
import PWAInstallPrompt from './components/PWAInstallPrompt';
import PWAUpdatePrompt from './components/PWAUpdatePrompt';
import OfflineIndicator from './components/OfflineIndicator';

// Protected Route Component
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuthStore();
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return <>{children}</>;
};

function App() {
  const { isAuthenticated } = useAuthStore();

  return (
    <Router>
      <div className="App">
        {/* PWA Components */}
        <PWAInstallPrompt />
        <PWAUpdatePrompt />
        <OfflineIndicator />
        
        <Routes>
          {/* Public Routes */}
          <Route 
            path="/login" 
            element={
              isAuthenticated ? <Navigate to="/" replace /> : <LoginForm />
            } 
          />
          
          {/* Protected Routes */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Dashboard />} />
            <Route path="avances" element={<AvanceList />} />
            <Route path="mediciones" element={<MedicionList />} />
            <Route path="reportes" element={<ReportGenerator />} />
            <Route path="configuracion" element={<ConfiguracionPanel />} />
          </Route>
          
          {/* Catch all route */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;