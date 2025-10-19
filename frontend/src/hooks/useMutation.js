import { useState, useCallback, useRef } from 'react';
import { clearQueryCache } from './useQuery';

/**
 * Enhanced Mutation Hook for API Mutations
 * 
 * Handles POST, PUT, DELETE requests with:
 * - Loading/error/success states
 * - Optimistic updates
 * - Automatic cache invalidation
 * - Error recovery
 * - Retry with exponential backoff
 * 
 * @param {Function} mutationFn - Async function that performs the mutation
 * @param {Object} options - Configuration options
 * @param {Function} options.onSuccess - Callback on successful mutation
 * @param {Function} options.onError - Callback on failed mutation
 * @param {Function} options.onSettled - Callback after mutation completes
 * @param {Function} options.onMutate - Callback before mutation starts (for optimistic updates)
 * @param {Array<string>} options.invalidateQueries - Query keys to invalidate on success
 * @param {number} options.retry - Number of retries on failure (default: 2)
 * @param {number} options.retryDelay - Initial retry delay in ms (default: 1000)
 * @param {boolean} options.throwOnError - Whether to throw errors (default: false)
 * 
 * @returns {Object} Mutation state and methods
 */
export const useMutation = (mutationFn, options = {}) => {
  const {
    onSuccess,
    onError,
    onSettled,
    onMutate,
    invalidateQueries = [],
    retry = 2,
    retryDelay = 1000,
    throwOnError = false,
  } = options;

  // State management
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isError, setIsError] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [status, setStatus] = useState('idle'); // 'idle' | 'loading' | 'error' | 'success'

  // Refs for cleanup and state management
  const mountedRef = useRef(true);
  const retryCountRef = useRef(0);
  const optimisticDataRef = useRef(null);

  /**
   * Execute mutation with retry logic
   */
  const executeMutation = useCallback(
    async (variables, currentRetryCount = 0) => {
      try {
        const result = await mutationFn(variables);
        return result;
      } catch (err) {
        // Retry logic
        if (currentRetryCount < retry) {
          const delay = retryDelay * Math.pow(2, currentRetryCount); // Exponential backoff
          console.log(
            `Mutation failed, retrying in ${delay}ms (attempt ${currentRetryCount + 1}/${retry})`
          );

          await new Promise((resolve) => setTimeout(resolve, delay));
          return executeMutation(variables, currentRetryCount + 1);
        }

        throw err;
      }
    },
    [mutationFn, retry, retryDelay]
  );

  /**
   * Main mutate function
   */
  const mutate = useCallback(
    async (variables) => {
      // Reset state
      setIsLoading(true);
      setIsError(false);
      setIsSuccess(false);
      setError(null);
      setStatus('loading');
      retryCountRef.current = 0;

      // Store optimistic data snapshot
      let optimisticRollback = null;

      try {
        // Execute onMutate for optimistic updates
        if (onMutate) {
          optimisticRollback = await onMutate(variables);
          optimisticDataRef.current = optimisticRollback;
        }

        // Execute the mutation
        const result = await executeMutation(variables);

        // Only update state if component is still mounted
        if (mountedRef.current) {
          setData(result);
          setIsSuccess(true);
          setIsError(false);
          setError(null);
          setStatus('success');
        }

        // Invalidate queries on success
        if (invalidateQueries.length > 0) {
          invalidateQueries.forEach((queryKey) => {
            clearQueryCache(queryKey);
          });
        }

        // Call success callback
        if (onSuccess) {
          await onSuccess(result, variables);
        }

        return result;
      } catch (err) {
        console.error('Mutation error:', err);

        // Rollback optimistic updates
        if (optimisticRollback && onError) {
          console.log('Rolling back optimistic updates');
        }

        // Only update state if component is still mounted
        if (mountedRef.current) {
          setError(err);
          setIsError(true);
          setIsSuccess(false);
          setStatus('error');
        }

        // Call error callback
        if (onError) {
          await onError(err, variables, optimisticRollback);
        }

        // Throw error if requested
        if (throwOnError) {
          throw err;
        }
      } finally {
        if (mountedRef.current) {
          setIsLoading(false);
        }

        // Call settled callback
        if (onSettled) {
          await onSettled(data, error, variables);
        }

        // Clear optimistic data
        optimisticDataRef.current = null;
      }
    },
    [
      executeMutation,
      onMutate,
      onSuccess,
      onError,
      onSettled,
      invalidateQueries,
      throwOnError,
      data,
      error,
    ]
  );

  /**
   * Async version that returns a promise
   */
  const mutateAsync = useCallback(
    async (variables) => {
      return mutate(variables);
    },
    [mutate]
  );

  /**
   * Reset mutation state
   */
  const reset = useCallback(() => {
    setData(null);
    setError(null);
    setIsLoading(false);
    setIsError(false);
    setIsSuccess(false);
    setStatus('idle');
    retryCountRef.current = 0;
    optimisticDataRef.current = null;
  }, []);

  /**
   * Cleanup on unmount
   */
  useCallback(() => {
    return () => {
      mountedRef.current = false;
    };
  }, [])();

  return {
    mutate,
    mutateAsync,
    data,
    error,
    isLoading,
    isError,
    isSuccess,
    status,
    reset,
  };
};

/**
 * Query Client for managing query cache
 * Provides methods to invalidate and update queries
 */
export const createQueryClient = () => {
  return {
    /**
     * Invalidate one or more queries
     */
    invalidateQueries: (queryKeys) => {
      const keys = Array.isArray(queryKeys) ? queryKeys : [queryKeys];
      keys.forEach((key) => {
        clearQueryCache(key);
      });
    },

    /**
     * Set query data in cache
     */
    setQueryData: (queryKey, updater) => {
      try {
        const cacheKey = `query_cache_${queryKey}`;
        const existingData = localStorage.getItem(cacheKey);
        const data = existingData ? JSON.parse(existingData) : null;

        const newData = typeof updater === 'function' ? updater(data) : updater;

        localStorage.setItem(cacheKey, JSON.stringify(newData));
        localStorage.setItem(
          `query_cache_timestamp_${queryKey}`,
          Date.now().toString()
        );
      } catch (error) {
        console.warn('Error setting query data:', error);
      }
    },

    /**
     * Get query data from cache
     */
    getQueryData: (queryKey) => {
      try {
        const cacheKey = `query_cache_${queryKey}`;
        const cachedData = localStorage.getItem(cacheKey);
        return cachedData ? JSON.parse(cachedData) : null;
      } catch (error) {
        console.warn('Error getting query data:', error);
        return null;
      }
    },

    /**
     * Clear all cache
     */
    clear: () => {
      try {
        const keys = Object.keys(localStorage);
        keys.forEach((key) => {
          if (key.startsWith('query_cache_')) {
            localStorage.removeItem(key);
          }
        });
      } catch (error) {
        console.warn('Error clearing cache:', error);
      }
    },
  };
};

// Singleton query client instance
export const queryClient = createQueryClient();

/**
 * Helper hook to use the query client
 */
export const useQueryClient = () => {
  return queryClient;
};

/**
 * Optimistic update helper
 * Returns a function to update query cache optimistically and a rollback function
 */
export const useOptimisticUpdate = (queryKey) => {
  const client = useQueryClient();

  const updateOptimistically = useCallback(
    (updater) => {
      // Get current data
      const previousData = client.getQueryData(queryKey);

      // Update cache with new data
      client.setQueryData(queryKey, updater);

      // Return rollback function
      return () => {
        client.setQueryData(queryKey, previousData);
      };
    },
    [queryKey, client]
  );

  return updateOptimistically;
};

/**
 * Create a mutation with automatic optimistic updates
 */
export const useOptimisticMutation = (
  mutationFn,
  queryKey,
  optimisticUpdater,
  options = {}
) => {
  const client = useQueryClient();

  return useMutation(mutationFn, {
    ...options,
    onMutate: async (variables) => {
      // Cancel outgoing refetches
      const previousData = client.getQueryData(queryKey);

      // Optimistically update cache
      if (optimisticUpdater) {
        client.setQueryData(queryKey, (old) => optimisticUpdater(old, variables));
      }

      // Call user's onMutate if provided
      if (options.onMutate) {
        await options.onMutate(variables);
      }

      // Return rollback function
      return () => {
        client.setQueryData(queryKey, previousData);
      };
    },
    onError: async (error, variables, rollback) => {
      // Rollback on error
      if (rollback) {
        rollback();
      }

      // Call user's onError if provided
      if (options.onError) {
        await options.onError(error, variables, rollback);
      }
    },
    onSuccess: async (data, variables) => {
      // Invalidate query to refetch
      client.invalidateQueries(queryKey);

      // Call user's onSuccess if provided
      if (options.onSuccess) {
        await options.onSuccess(data, variables);
      }
    },
  });
};

/**
 * Batch mutations - execute multiple mutations in sequence
 */
export const useBatchMutation = (mutations) => {
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState([]);
  const [results, setResults] = useState([]);

  const executeBatch = useCallback(
    async (variablesArray) => {
      setIsLoading(true);
      setErrors([]);
      setResults([]);

      const batchResults = [];
      const batchErrors = [];

      for (let i = 0; i < mutations.length; i++) {
        try {
          const result = await mutations[i](variablesArray[i]);
          batchResults.push(result);
        } catch (error) {
          batchErrors.push({ index: i, error });
        }
      }

      setResults(batchResults);
      setErrors(batchErrors);
      setIsLoading(false);

      return { results: batchResults, errors: batchErrors };
    },
    [mutations]
  );

  return {
    executeBatch,
    isLoading,
    errors,
    results,
  };
};

export default useMutation;

