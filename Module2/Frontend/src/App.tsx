import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';
import { QueryClientProvider } from '@tanstack/react-query';

// Providers and config
import { AuthProvider } from './contexts/AuthContext';
import { NotificationProvider } from './contexts/NotificationContext';
import { theme } from './theme/theme';
import { queryClient } from './utils/queryClient';

// Layout
import { Layout } from './components/common/Layout';
import { ProtectedRoute } from './components/auth/ProtectedRoute';

// Pages
import { Home } from './pages/Home';
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { PublicTodos } from './pages/PublicTodos';
import { PrivateTodos } from './pages/PrivateTodos';

// Routes
import { ROUTES } from './utils/constants';

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <BrowserRouter>
          <AuthProvider>
            <NotificationProvider>
              <Layout>
                <Routes>
                {/* Public Routes */}
                <Route path={ROUTES.HOME} element={<Home />} />
                <Route path={ROUTES.LOGIN} element={<Login />} />
                <Route path={ROUTES.REGISTER} element={<Register />} />
                <Route path={ROUTES.PUBLIC_TODOS} element={<PublicTodos />} />
                
                {/* Protected Routes */}
                <Route
                  path={ROUTES.PRIVATE_TODOS}
                  element={
                    <ProtectedRoute>
                      <PrivateTodos />
                    </ProtectedRoute>
                  }
                />
                
                {/* Fallback */}
                <Route path="*" element={<Navigate to={ROUTES.HOME} replace />} />
                </Routes>
              </Layout>
            </NotificationProvider>
          </AuthProvider>
        </BrowserRouter>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;