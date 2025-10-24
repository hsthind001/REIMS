import React from 'react';

const YearSelector = ({ 
  years = [], 
  selectedYear, 
  onYearChange, 
  className = "" 
}) => {
  if (!years || years.length === 0) {
    return (
      <div className={`year-selector ${className}`}>
        <div className="text-sm text-gray-500">No year data available</div>
      </div>
    );
  }

  return (
    <div className={`year-selector ${className}`}>
      <div className="flex items-center space-x-2">
        <span className="text-sm font-medium text-gray-700">Viewing Year:</span>
        <select
          value={selectedYear || ''}
          onChange={(e) => onYearChange(parseInt(e.target.value))}
          className="px-3 py-1 border border-gray-300 rounded-md text-sm font-medium bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          {years.map((year) => (
            <option key={year.year} value={year.year}>
              {year.label}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
};

export default YearSelector;
