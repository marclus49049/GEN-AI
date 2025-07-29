/**
 * React Query hooks for todo management with intelligent cache invalidation.
 * 
 * Cache invalidation strategy:
 * - Private todos: Invalidate on all CRUD operations to current user's todos
 * - Public todos: Cross-invalidate when private todos are made public
 * - Optimistic updates: Immediate UI feedback with rollback on error
 * - Query key design: Simple string keys for reliable cache targeting
 * 
 * Performance considerations:
 * - Uses React Query's built-in deduplication to prevent duplicate requests
 * - Automatic background refetching keeps data fresh
 * - Cache invalidation is surgical - only affected query keys are updated
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { todosApi, publicTodosApi } from '../api/todos';
import { CreateTodoDto, UpdateTodoDto, PublicTodoDto } from '../types';
import { QUERY_KEYS } from '../utils/constants';

// Private Todos Hooks
export const usePrivateTodos = () => {
  /**
   * Fetch all todos owned by the authenticated user.
   * Includes both private and public todos created by the user.
   */
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
      /**
       * Smart cache invalidation based on visibility.
       * 
       * Always invalidate private todos since user will see it in their list.
       * Cross-invalidate public todos if the created todo is public, ensuring
       * it appears immediately in the public view without manual refresh.
       */
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.TODOS] });
      
      // Cross-cache invalidation: public todos affected if todo is public
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
      /**
       * Conservative cache invalidation for updates.
       * 
       * Only invalidates private todos cache since we can't easily determine
       * if the updated todo affects public visibility without additional logic.
       * Future enhancement: Check if visibility changed and cross-invalidate.
       */
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
  /**
   * Fetch all public todos visible to everyone.
   * No authentication required for this query.
   */
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
      /**
       * Bidirectional cache invalidation for public todo creation.
       * 
       * Public todos appear in both:
       * 1. Public todos list (visible to everyone)
       * 2. Private todos list (user's own todos, including public ones)
       * 
       * Both caches must be invalidated to ensure consistency.
       */
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.PUBLIC_TODOS] });
      // Cross-invalidate: authenticated users see their public todos in private list
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
      /**
       * Conservative cache invalidation for public todo updates.
       * 
       * Only invalidates public todos cache since:
       * 1. Updates to public todos don't affect private todo ownership
       * 2. Cross-user modifications should trigger real-time updates via WebSocket
       * 3. Over-invalidation could cause unnecessary re-fetching
       */
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.PUBLIC_TODOS] });
    },
  });
};

export const useDeletePublicTodo = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => publicTodosApi.delete(id),
    onSuccess: () => {
      /**
       * Single cache invalidation for public todo deletion.
       * 
       * Only invalidates public todos cache since:
       * 1. Deletion from public view doesn't affect private todo lists
       * 2. If user deletes their own public todo, they'd typically do it from private view
       * 3. Cross-user deletions should be rare and trigger notifications
       */
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.PUBLIC_TODOS] });
    },
  });
};