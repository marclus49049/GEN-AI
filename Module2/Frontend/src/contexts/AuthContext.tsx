import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useNavigate } from 'react-router-dom';
import { User, LoginCredentials, RegisterData, AuthToken } from '../types';
import { authApi } from '../api/auth';
import { getToken, setToken, removeToken, getStoredUser, setStoredUser, clearAuth } from '../utils/storage';
import { ROUTES } from '../utils/constants';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setTokenState] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  // Initialize auth state from localStorage
  useEffect(() => {
    const initializeAuth = async () => {
      const storedToken = getToken();
      const storedUser = getStoredUser();

      if (storedToken && storedUser) {
        setTokenState(storedToken);
        setUser(storedUser);
        
        // Optionally verify token validity with backend
        try {
          // You could add a /auth/me endpoint to verify token
          // const userData = await authApi.getMe();
          // setUser(userData);
        } catch (error) {
          // Token invalid, clear auth
          clearAuth();
          setTokenState(null);
          setUser(null);
        }
      }
      
      setIsLoading(false);
    };

    initializeAuth();
  }, []);

  const login = async (credentials: LoginCredentials) => {
    try {
      const response = await authApi.login(credentials);
      const { access_token } = response;
      
      // Store token
      setToken(access_token);
      setTokenState(access_token);
      
      // Decode user info from token or fetch user data
      // For now, we'll create a simple user object
      // In production, you might want to decode the JWT or fetch user info
      const userData: User = {
        id: 1, // This should come from token or API
        username: credentials.username,
        email: '', // This should come from API
        created_at: new Date().toISOString(),
      };
      
      setStoredUser(userData);
      setUser(userData);
      
      // Navigate to private todos
      navigate(ROUTES.PRIVATE_TODOS);
    } catch (error) {
      clearAuth();
      throw error;
    }
  };

  const register = async (data: RegisterData) => {
    try {
      const userData = await authApi.register(data);
      // After registration, redirect to login
      navigate(ROUTES.LOGIN);
    } catch (error) {
      throw error;
    }
  };

  const logout = () => {
    clearAuth();
    setUser(null);
    setTokenState(null);
    navigate(ROUTES.HOME);
  };

  const value: AuthContextType = {
    user,
    token,
    isAuthenticated: !!token,
    isLoading,
    login,
    register,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};