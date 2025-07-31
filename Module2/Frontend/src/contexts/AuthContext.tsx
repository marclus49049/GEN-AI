/**
 * Authentication context providing global auth state management.
 * 
 * Features:
 * - Persistent authentication via localStorage
 * - Automatic token validation on app startup
 * - Centralized auth state for the entire app
 * - Navigation side effects (redirect after login/logout)
 * 
 * Design decisions:
 * - Uses localStorage for token persistence across browser sessions
 * - Implements optimistic user creation (creates User object from login credentials)
 * - Loading state prevents flash of unauthenticated content during initialization
 * - Separates login/register flows (register doesn't auto-login for security)
 */
import React, { createContext, ReactNode, useContext, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authApi } from '../api/auth';
import { LoginCredentials, RegisterData, User } from '../types';
import { ROUTES } from '../utils/constants';
import { clearAuth, getStoredUser, getToken, setStoredUser, setToken } from '../utils/storage';

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

  /**
   * Initialize authentication state from localStorage on app startup.
   * 
   * This handles browser refresh/reload scenarios where we need to restore
   * the user's authentication state. The loading state prevents flash of
   * unauthenticated content while we check localStorage.
   * 
   * Future enhancement: Add token validation against backend to handle
   * expired tokens gracefully.
   */
  useEffect(() => {
    const initializeAuth = async () => {
      const storedToken = getToken();
      const storedUser = getStoredUser();

      if (storedToken && storedUser) {
        setTokenState(storedToken);
        setUser(storedUser);
        
        // Future enhancement: Verify token validity with backend
        try {
          // Could add a /auth/me endpoint to verify token and get fresh user data
          // const userData = await authApi.getMe();
          // setUser(userData);
        } catch (error) {
          // Token invalid or expired, clear auth state
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
    /**
     * Authenticate user and establish session.
     * 
     * Flow:
     * 1. Send login request to backend
     * 2. Store JWT token in localStorage and state
     * 3. Create optimistic user object (production should fetch real user data)
     * 4. Navigate to protected route
     * 
     * Error handling: Clears any existing auth state if login fails
     */
    try {
      const response = await authApi.login(credentials);
      const { access_token } = response;
      
      // Store token in localStorage and state
      setToken(access_token);
      setTokenState(access_token);
      
      // Optimistic user creation - production should decode JWT or fetch user data
      // This approach avoids extra API call but limits available user info
      const userData: User = {
        id: 1, // Should decode from JWT token or fetch from API
        username: credentials.username,
        email: '', // Should come from user profile API
        created_at: new Date().toISOString(),
      };
      
      setStoredUser(userData);
      setUser(userData);
      
      // Navigation side effect: redirect to protected area
      navigate(ROUTES.PRIVATE_TODOS);
    } catch (error) {
      // Ensure clean state on login failure
      clearAuth();
      throw error;
    }
  };

  const register = async (data: RegisterData) => {
    /**
     * Register new user account.
     * 
     * Security design: Does NOT auto-login after registration.
     * This forces explicit authentication step and prevents
     * account takeover via registration endpoints.
     */
    try {
      const userData = await authApi.register(data);
      // Redirect to login - user must explicitly authenticate
      navigate(ROUTES.LOGIN);
    } catch (error) {
      throw error;
    }
  };

  const logout = () => {
    /**
     * Clear authentication state and return to public area.
     * 
     * Handles both localStorage cleanup and component state.
     * Navigation side effect ensures user sees public content.
     */
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