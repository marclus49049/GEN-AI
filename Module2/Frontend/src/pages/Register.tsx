import React from 'react';
import { Navigate } from 'react-router-dom';
import { Container } from '@mui/material';
import { RegisterForm } from '../components/auth/RegisterForm';
import { useAuth } from '../contexts/AuthContext';
import { ROUTES } from '../utils/constants';

export const Register: React.FC = () => {
  const { isAuthenticated } = useAuth();

  // If already authenticated, redirect to private todos
  if (isAuthenticated) {
    return <Navigate to={ROUTES.PRIVATE_TODOS} replace />;
  }

  return (
    <Container maxWidth="sm">
      <RegisterForm />
    </Container>
  );
};