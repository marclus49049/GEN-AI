import { axiosInstance } from './axiosConfig';
import { Todo, CreateTodoDto, UpdateTodoDto, PublicTodo, PublicTodoDto, PaginationParams } from '../types';
import { API_ENDPOINTS } from '../utils/constants';

// Private Todo API
export const todosApi = {
  // Get user's private todos
  getAll: async (params?: PaginationParams): Promise<Todo[]> => {
    const response = await axiosInstance.get<Todo[]>(API_ENDPOINTS.TODOS.LIST, {
      params,
    });
    return response.data;
  },

  // Get single private todo
  getById: async (id: number): Promise<Todo> => {
    const response = await axiosInstance.get<Todo>(API_ENDPOINTS.TODOS.DETAIL(id));
    return response.data;
  },

  // Create private todo
  create: async (data: CreateTodoDto): Promise<Todo> => {
    const response = await axiosInstance.post<Todo>(API_ENDPOINTS.TODOS.LIST, data);
    return response.data;
  },

  // Update private todo
  update: async (id: number, data: UpdateTodoDto): Promise<Todo> => {
    const response = await axiosInstance.put<Todo>(
      API_ENDPOINTS.TODOS.DETAIL(id),
      data
    );
    return response.data;
  },

  // Delete private todo
  delete: async (id: number): Promise<void> => {
    await axiosInstance.delete(API_ENDPOINTS.TODOS.DETAIL(id));
  },
};

// Public Todo API
export const publicTodosApi = {
  // Get all public todos
  getAll: async (params?: PaginationParams): Promise<PublicTodo[]> => {
    const response = await axiosInstance.get<PublicTodo[]>(
      API_ENDPOINTS.PUBLIC_TODOS.LIST,
      { params }
    );
    return response.data;
  },

  // Get single public todo
  getById: async (id: number): Promise<PublicTodo> => {
    const response = await axiosInstance.get<PublicTodo>(
      API_ENDPOINTS.PUBLIC_TODOS.DETAIL(id)
    );
    return response.data;
  },

  // Create public todo (auth optional - will be logged as owner if logged in)
  create: async (data: PublicTodoDto): Promise<PublicTodo> => {
    const response = await axiosInstance.post<PublicTodo>(
      API_ENDPOINTS.PUBLIC_TODOS.LIST,
      data
    );
    return response.data;
  },

  // Update public todo
  update: async (id: number, data: UpdateTodoDto): Promise<PublicTodo> => {
    const response = await axiosInstance.put<PublicTodo>(
      API_ENDPOINTS.PUBLIC_TODOS.DETAIL(id),
      data
    );
    return response.data;
  },

  // Delete public todo
  delete: async (id: number): Promise<void> => {
    await axiosInstance.delete(API_ENDPOINTS.PUBLIC_TODOS.DETAIL(id));
  },
};