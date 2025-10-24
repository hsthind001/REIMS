import { useState, useEffect } from 'react';

const API_BASE_URL = 'http://localhost:8001';

export const usePropertyFinancials = (propertyId, options = {}) => {
  const {
    year = null, // Auto-select latest if null
    compareYears = null,
    refetchInterval = 5 * 60 * 1000 // 5 minutes
  } = options;

  const [financials, setFinancials] = useState(null);
  const [comparison, setComparison] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch financial data for a specific year
  const fetchFinancials = async (propertyId, year) => {
    try {
      setLoading(true);
      setError(null);
      
      const url = new URL(`${API_BASE_URL}/api/properties/${propertyId}/financials`);
      if (year) {
        url.searchParams.append('year', year);
      }
      
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setFinancials(data);
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Fetch comparison data for multiple years
  const fetchComparison = async (propertyId, years) => {
    try {
      setLoading(true);
      setError(null);
      
      const yearsParam = Array.isArray(years) ? years.join(',') : years;
      const url = `${API_BASE_URL}/api/properties/${propertyId}/financials/compare?years=${yearsParam}`;
      
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setComparison(data);
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Auto-fetch financials when propertyId or year changes
  useEffect(() => {
    if (propertyId) {
      fetchFinancials(propertyId, year);
    }
  }, [propertyId, year]);

  // Auto-fetch comparison when compareYears changes
  useEffect(() => {
    if (propertyId && compareYears && compareYears.length > 1) {
      fetchComparison(propertyId, compareYears);
    }
  }, [propertyId, compareYears]);

  // Manual refresh function
  const refresh = () => {
    if (propertyId) {
      fetchFinancials(propertyId, year);
      if (compareYears && compareYears.length > 1) {
        fetchComparison(propertyId, compareYears);
      }
    }
  };

  // Change year function
  const changeYear = (newYear) => {
    if (propertyId) {
      fetchFinancials(propertyId, newYear);
    }
  };

  // Enable comparison mode
  const enableComparison = (years) => {
    if (propertyId && years && years.length > 1) {
      fetchComparison(propertyId, years);
    }
  };

  // Disable comparison mode
  const disableComparison = () => {
    setComparison(null);
  };

  return {
    // Data
    financials,
    comparison,
    
    // State
    loading,
    error,
    
    // Actions
    refresh,
    changeYear,
    enableComparison,
    disableComparison,
    
    // Computed properties
    selectedYear: financials?.selected_year,
    availableYears: financials?.available_years || [],
    isPartialYear: financials?.is_partial_year,
    metrics: financials?.metrics,
    completeness: financials?.completeness,
    
    // Comparison data
    comparisonData: comparison?.comparison_data || [],
    yearsCompared: comparison?.years_compared || [],
    propertyName: comparison?.property_name
  };
};

export default usePropertyFinancials;
