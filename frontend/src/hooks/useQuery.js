import { useState, useEffect, useCallback, useRef } from 'react';

/**
 * Custom React Hook for Data Fetching
 * 
 * Features:
 * - Loading/error/success states
 * - Automatic refetching at intervals
 * - Manual refetch function
 * - Caching with localStorage (5 minute default)
 * - Retry logic (1 retry on failure)
 * - Refetch on window focus
 * 
 * @param {string} queryKey - Unique identifier for the query
 * @param {Function} queryFn - Async function that fetches the data
 * @param {Object} options - Configuration options
 * @param {number} options.refetchInterval - Auto-refetch interval in ms (default: null)
 * @param {number} options.staleTime - Cache time in ms (default: 300000 = 5 minutes)
 * @param {boolean} options.enabled - Enable/disable the query (default: true)
 * @param {boolean} options.refetchOnWindowFocus - Refetch when window gains focus (default: true)
 * @param {number} options.retry - Number of retries on failure (default: 1)
 * @param {boolean} options.cacheEnabled - Enable/disable caching (default: true)
 * 
 * @returns {Object} Query state and methods
 */
export const useQuery = (
  queryKey,
  queryFn,
  options = {}
) => {
  // Default options
  const {
    refetchInterval = null,
    staleTime = 5 * 60 * 1000, // 5 minutes
    enabled = true,
    refetchOnWindowFocus = true,
    retry = 1,
    cacheEnabled = true,
  } = options;

  // State management
  const [data, setData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isFetching, setIsFetching] = useState(false);
  const [error, setError] = useState(null);
  const [isError, setIsError] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);

  // Refs to track intervals and prevent multiple fetches
  const intervalRef = useRef(null);
  const isFetchingRef = useRef(false);
  const retryCountRef = useRef(0);
  const mountedRef = useRef(true);

  // Generate cache key
  const cacheKey = `query_cache_${queryKey}`;
  const cacheTimestampKey = `query_cache_timestamp_${queryKey}`;

  /**
   * Check if cached data is still valid
   */
  const isCacheValid = useCallback(() => {
    if (!cacheEnabled) return false;

    try {
      const cachedTimestamp = localStorage.getItem(cacheTimestampKey);
      if (!cachedTimestamp) return false;

      const age = Date.now() - parseInt(cachedTimestamp, 10);
      return age < staleTime;
    } catch (error) {
      console.warn('Cache validation error:', error);
      return false;
    }
  }, [cacheEnabled, cacheTimestampKey, staleTime]);

  /**
   * Get data from cache
   */
  const getFromCache = useCallback(() => {
    if (!cacheEnabled) return null;

    try {
      const cachedData = localStorage.getItem(cacheKey);
      if (!cachedData) return null;

      return JSON.parse(cachedData);
    } catch (error) {
      console.warn('Cache read error:', error);
      return null;
    }
  }, [cacheEnabled, cacheKey]);

  /**
   * Save data to cache
   */
  const saveToCache = useCallback(
    (data) => {
      if (!cacheEnabled) return;

      try {
        localStorage.setItem(cacheKey, JSON.stringify(data));
        localStorage.setItem(cacheTimestampKey, Date.now().toString());
      } catch (error) {
        console.warn('Cache write error:', error);
        // If localStorage is full or unavailable, continue without caching
      }
    },
    [cacheEnabled, cacheKey, cacheTimestampKey]
  );

  /**
   * Clear cache for this query
   */
  const clearCache = useCallback(() => {
    try {
      localStorage.removeItem(cacheKey);
      localStorage.removeItem(cacheTimestampKey);
    } catch (error) {
      console.warn('Cache clear error:', error);
    }
  }, [cacheKey, cacheTimestampKey]);

  /**
   * Execute the query with retry logic
   */
  const executeQuery = useCallback(
    async (isBackgroundRefetch = false) => {
      // Prevent concurrent fetches
      if (isFetchingRef.current) {
        return;
      }

      isFetchingRef.current = true;
      setIsFetching(true);

      // Only show loading state on initial fetch, not on background refetch
      if (!isBackgroundRefetch && !data) {
        setIsLoading(true);
      }

      setError(null);
      setIsError(false);

      try {
        // Execute the query function
        const result = await queryFn();

        // Only update state if component is still mounted
        if (mountedRef.current) {
          setData(result);
          setIsSuccess(true);
          setIsError(false);
          setError(null);

          // Save to cache
          saveToCache(result);

          // Reset retry count on success
          retryCountRef.current = 0;
        }

        return result;
      } catch (err) {
        console.error(`Query error [${queryKey}]:`, err);

        // Retry logic
        if (retryCountRef.current < retry) {
          retryCountRef.current += 1;
          console.log(`Retrying query [${queryKey}] (attempt ${retryCountRef.current}/${retry})`);

          // Wait a bit before retrying (exponential backoff)
          await new Promise((resolve) => setTimeout(resolve, 1000 * retryCountRef.current));

          // Retry
          isFetchingRef.current = false;
          return executeQuery(isBackgroundRefetch);
        }

        // If all retries failed, update error state
        if (mountedRef.current) {
          setError(err);
          setIsError(true);
          setIsSuccess(false);
        }

        throw err;
      } finally {
        if (mountedRef.current) {
          setIsLoading(false);
          setIsFetching(false);
        }
        isFetchingRef.current = false;
      }
    },
    [queryFn, queryKey, retry, data, saveToCache]
  );

  /**
   * Manual refetch function
   */
  const refetch = useCallback(async () => {
    // Clear cache before refetching
    clearCache();
    return executeQuery(false);
  }, [executeQuery, clearCache]);

  /**
   * Initial data fetch
   */
  useEffect(() => {
    if (!enabled) return;

    // Check cache first
    if (isCacheValid()) {
      const cachedData = getFromCache();
      if (cachedData) {
        setData(cachedData);
        setIsSuccess(true);
        setIsLoading(false);
        // Still fetch in background to update data
        executeQuery(true);
        return;
      }
    }

    // No valid cache, fetch normally
    executeQuery(false);
  }, [queryKey, enabled]); // Only depend on queryKey and enabled

  /**
   * Setup automatic refetch interval
   */
  useEffect(() => {
    if (!enabled || !refetchInterval) return;

    intervalRef.current = setInterval(() => {
      executeQuery(true);
    }, refetchInterval);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [enabled, refetchInterval, executeQuery]);

  /**
   * Setup refetch on window focus
   */
  useEffect(() => {
    if (!enabled || !refetchOnWindowFocus) return;

    const handleFocus = () => {
      // Check if cache is stale before refetching
      if (!isCacheValid()) {
        executeQuery(true);
      }
    };

    window.addEventListener('focus', handleFocus);

    return () => {
      window.removeEventListener('focus', handleFocus);
    };
  }, [enabled, refetchOnWindowFocus, executeQuery, isCacheValid]);

  /**
   * Cleanup on unmount
   */
  useEffect(() => {
    return () => {
      mountedRef.current = false;
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  // Return query state and methods
  return {
    data,
    isLoading,
    isFetching,
    error,
    isError,
    isSuccess,
    refetch,
  };
};

/**
 * Hook for mutations (POST, PUT, DELETE operations)
 * 
 * @param {Function} mutationFn - Async function that performs the mutation
 * @param {Object} options - Configuration options
 * @param {Function} options.onSuccess - Callback on successful mutation
 * @param {Function} options.onError - Callback on failed mutation
 * @param {Function} options.onSettled - Callback after mutation completes (success or error)
 * 
 * @returns {Object} Mutation state and methods
 */
export const useMutation = (mutationFn, options = {}) => {
  const { onSuccess, onError, onSettled } = options;

  const [data, setData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isError, setIsError] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);

  const mountedRef = useRef(true);

  useEffect(() => {
    return () => {
      mountedRef.current = false;
    };
  }, []);

  const mutate = useCallback(
    async (variables) => {
      setIsLoading(true);
      setError(null);
      setIsError(false);
      setIsSuccess(false);

      try {
        const result = await mutationFn(variables);

        if (mountedRef.current) {
          setData(result);
          setIsSuccess(true);
          setIsError(false);
        }

        // Call success callback
        if (onSuccess) {
          onSuccess(result, variables);
        }

        return result;
      } catch (err) {
        console.error('Mutation error:', err);

        if (mountedRef.current) {
          setError(err);
          setIsError(true);
          setIsSuccess(false);
        }

        // Call error callback
        if (onError) {
          onError(err, variables);
        }

        throw err;
      } finally {
        if (mountedRef.current) {
          setIsLoading(false);
        }

        // Call settled callback
        if (onSettled) {
          onSettled(data, error, variables);
        }
      }
    },
    [mutationFn, onSuccess, onError, onSettled, data, error]
  );

  const reset = useCallback(() => {
    setData(null);
    setError(null);
    setIsError(false);
    setIsSuccess(false);
    setIsLoading(false);
  }, []);

  return {
    mutate,
    data,
    isLoading,
    error,
    isError,
    isSuccess,
    reset,
  };
};

/**
 * Clear all query cache
 */
export const clearAllQueryCache = () => {
  try {
    const keys = Object.keys(localStorage);
    keys.forEach((key) => {
      if (key.startsWith('query_cache_')) {
        localStorage.removeItem(key);
      }
    });
  } catch (error) {
    console.warn('Error clearing query cache:', error);
  }
};

/**
 * Clear specific query cache
 */
export const clearQueryCache = (queryKey) => {
  try {
    localStorage.removeItem(`query_cache_${queryKey}`);
    localStorage.removeItem(`query_cache_timestamp_${queryKey}`);
  } catch (error) {
    console.warn('Error clearing query cache:', error);
  }
};

export default useQuery;

