/**
 * React Query client with performance-optimized configuration.
 * 
 * Configuration rationale:
 * 
 * Query settings:
 * - retry: 1 - Single retry prevents excessive requests for permanent failures
 * - refetchOnWindowFocus: false - Prevents unnecessary refetches during development/multitasking
 * - staleTime: 5 minutes - Data considered fresh for 5 min, reduces redundant requests
 * - gcTime: 10 minutes - Cache persists 10 min after last usage for faster navigation
 * 
 * Mutation settings:
 * - retry: 0 - No retries for mutations to prevent duplicate actions (POST, PUT, DELETE)
 * 
 * Performance benefits:
 * - Reduced server load through intelligent caching
 * - Faster navigation with background cache
 * - Prevents duplicate mutations
 * - Balances data freshness with performance
 */
import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,                    // Single retry for network errors
      refetchOnWindowFocus: false, // Disable focus refetching for better UX
      staleTime: 5 * 60 * 1000,   // 5 minutes fresh data window
      gcTime: 10 * 60 * 1000,     // 10 minutes garbage collection delay
    },
    mutations: {
      retry: 0, // Never retry mutations to prevent duplicate actions
    },
  },
});