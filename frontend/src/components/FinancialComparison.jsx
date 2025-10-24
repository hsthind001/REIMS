import React from 'react';

const FinancialComparison = ({ 
  comparisonData = [], 
  className = "" 
}) => {
  if (!comparisonData || comparisonData.length === 0) {
    return (
      <div className={`financial-comparison ${className}`}>
        <div className="text-sm text-gray-500">No comparison data available</div>
      </div>
    );
  }

  const formatCurrency = (value) => {
    if (value === null || value === undefined) return 'N/A';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  };

  const formatPercentage = (value) => {
    if (value === null || value === undefined) return 'N/A';
    return `${(value * 100).toFixed(1)}%`;
  };

  const getChangeIcon = (change) => {
    if (!change || change.percentage_change === 0) return '➡️';
    return change.percentage_change > 0 ? '📈' : '📉';
  };

  const getChangeColor = (change) => {
    if (!change || change.percentage_change === 0) return 'text-gray-500';
    return change.percentage_change > 0 ? 'text-green-600' : 'text-red-600';
  };

  return (
    <div className={`financial-comparison ${className}`}>
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
          <h3 className="text-lg font-semibold text-gray-900">Year-over-Year Comparison</h3>
        </div>
        
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Year
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Market Value
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Monthly Rent
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Annual NOI
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Occupancy Rate
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {comparisonData.map((yearData, index) => (
                <tr key={yearData.year} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <span className="text-sm font-medium text-gray-900">
                        {yearData.year}
                      </span>
                      {yearData.is_partial_year && (
                        <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-yellow-100 text-yellow-800">
                          YTD
                        </span>
                      )}
                    </div>
                  </td>
                  
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      {formatCurrency(yearData.current_market_value)}
                    </div>
                    {yearData.changes.current_market_value && (
                      <div className={`text-xs ${getChangeColor(yearData.changes.current_market_value)}`}>
                        {getChangeIcon(yearData.changes.current_market_value)} 
                        {yearData.changes.current_market_value.percentage_change > 0 ? '+' : ''}
                        {yearData.changes.current_market_value.percentage_change.toFixed(1)}%
                      </div>
                    )}
                  </td>
                  
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      {formatCurrency(yearData.monthly_rent)}
                    </div>
                    {yearData.changes.monthly_rent && (
                      <div className={`text-xs ${getChangeColor(yearData.changes.monthly_rent)}`}>
                        {getChangeIcon(yearData.changes.monthly_rent)} 
                        {yearData.changes.monthly_rent.percentage_change > 0 ? '+' : ''}
                        {yearData.changes.monthly_rent.percentage_change.toFixed(1)}%
                      </div>
                    )}
                  </td>
                  
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      {formatCurrency(yearData.annual_noi)}
                    </div>
                    {yearData.changes.annual_noi && (
                      <div className={`text-xs ${getChangeColor(yearData.changes.annual_noi)}`}>
                        {getChangeIcon(yearData.changes.annual_noi)} 
                        {yearData.changes.annual_noi.percentage_change > 0 ? '+' : ''}
                        {yearData.changes.annual_noi.percentage_change.toFixed(1)}%
                      </div>
                    )}
                  </td>
                  
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      {formatPercentage(yearData.occupancy_rate)}
                    </div>
                    {yearData.changes.occupancy_rate && (
                      <div className={`text-xs ${getChangeColor(yearData.changes.occupancy_rate)}`}>
                        {getChangeIcon(yearData.changes.occupancy_rate)} 
                        {yearData.changes.occupancy_rate.percentage_change > 0 ? '+' : ''}
                        {yearData.changes.occupancy_rate.percentage_change.toFixed(1)}%
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default FinancialComparison;
