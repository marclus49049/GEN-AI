export const APP_NAME = 'Todo App';

export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  REGISTER: '/register',
  PUBLIC_TODOS: '/todos/public',
  PRIVATE_TODOS: '/todos',
  PROFILE: '/profile',
} as const;

export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
  },
  TODOS: {
    LIST: '/todos',
    DETAIL: (id: number) => `/todos/${id}`,
  },
  PUBLIC_TODOS: {
    LIST: '/public/todos',
    DETAIL: (id: number) => `/public/todos/${id}`,
  },
} as const;

export const QUERY_KEYS = {
  TODOS: 'todos',
  PUBLIC_TODOS: 'publicTodos',
  USER: 'user',
} as const;