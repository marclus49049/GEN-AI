import { AuthToken, LoginCredentials, RegisterData, User } from '../types';
import { API_ENDPOINTS } from '../utils/constants';
import { axiosInstance } from './axiosConfig';

export const authApi = {
  login: async (credentials: LoginCredentials): Promise<AuthToken> => {
    // Backend expects form data for OAuth2PasswordRequestForm
    const formData = new URLSearchParams();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);
    
    const response = await axiosInstance.post<AuthToken>(
      API_ENDPOINTS.AUTH.LOGIN,
      formData,
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      }
    );
    
    return response.data;
  },

  register: async (data: RegisterData): Promise<User> => {
    const response = await axiosInstance.post<User>(
      API_ENDPOINTS.AUTH.REGISTER,
      data
    );
    return response.data;
  },

  // Optional: Add a getMe endpoint if your backend supports it
  getMe: async (): Promise<User> => {
    const response = await axiosInstance.get<User>('/auth/me');
    return response.data;
  },
};