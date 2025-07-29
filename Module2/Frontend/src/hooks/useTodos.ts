import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { todosApi, publicTodosApi } from '../api/todos';
import { CreateTodoDto, UpdateTodoDto, PublicTodoDto } from '../types';
import { QUERY_KEYS } from '../utils/constants';

// Private Todos Hooks
export const usePrivateTodos = () => {
  return useQuery({
    queryKey: [QUERY_KEYS.TODOS],
    queryFn: () => todosApi.getAll(),
  });
};

export const useCreatePrivateTodo = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateTodoDto) => todosApi.create(data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.TODOS] });
      
      // If the created todo is public, also invalidate public todos cache
      if (variables.is_public) {
        queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.PUBLIC_TODOS] });
      }
    },
  });
};

export const useUpdatePrivateTodo = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: UpdateTodoDto }) =>
      todosApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.TODOS] });
    },
  });
};

export const useDeletePrivateTodo = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => todosApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.TODOS] });
    },
  });
};

// Public Todos Hooks
export const usePublicTodos = () => {
  return useQuery({
    queryKey: [QUERY_KEYS.PUBLIC_TODOS],
    queryFn: () => publicTodosApi.getAll(),
  });
};

export const useCreatePublicTodo = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: PublicTodoDto) => publicTodosApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.PUBLIC_TODOS] });
      // Also invalidate private todos cache since logged-in users will see their public todos there
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.TODOS] });
    },
  });
};

export const useUpdatePublicTodo = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: UpdateTodoDto }) =>
      publicTodosApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.PUBLIC_TODOS] });
    },
  });
};

export const useDeletePublicTodo = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => publicTodosApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.PUBLIC_TODOS] });
    },
  });
};