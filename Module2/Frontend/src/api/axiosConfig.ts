/**
 * Centralized Axios configuration with automatic JWT token management.
 * 
 * Features:
 * - Request interceptor: Automatically adds Bearer token to all requests
 * - Response interceptor: Handles 401 errors with automatic logout/redirect
 * - Environment-based API URL configuration
 * - TypeScript integration with proper error typing
 * 
 * Design rationale:
 * - Single axios instance ensures consistent behavior across all API calls
 * - Interceptors eliminate need for manual token handling in each API function
 * - Automatic 401 handling provides seamless auth error recovery
 * - Prevents redirect loops by checking current path before redirecting
 */
import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import { getToken, removeToken } from '../utils/storage';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// Create configured axios instance with base URL and default headers
export const axiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Request interceptor: Automatically inject JWT Bearer token
 * 
 * Runs before every request to add the Authorization header if a token exists.
 * This eliminates the need to manually handle tokens in individual API calls.
 * Only adds token when headers object exists to prevent runtime errors.
 */
axiosInstance.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = getToken();
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

/**
 * Response interceptor: Handle authentication failures globally
 * 
 * Intercepts all HTTP responses to detect 401 Unauthorized errors.
 * When detected:
 * 1. Removes invalid token from localStorage
 * 2. Redirects to login page (unless already on auth pages)
 * 3. Prevents redirect loops by checking current path
 * 
 * This provides automatic recovery from token expiration or invalidation
 * without requiring error handling in every component.
 */
axiosInstance.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Token expired, invalid, or missing - clear localStorage
      removeToken();
      
      // Prevent redirect loops: only redirect if not already on auth pages
      const currentPath = window.location.pathname;
      if (!currentPath.includes('/login') && !currentPath.includes('/register')) {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);