import React from 'react';

const YearBadge = ({ 
  year, 
  isComplete = true, 
  dataThroughDate = null,
  className = "" 
}) => {
  const getBadgeColor = () => {
    if (isComplete) {
      return "bg-green-100 text-green-800 border-green-200";
    } else {
      return "bg-yellow-100 text-yellow-800 border-yellow-200";
    }
  };

  const getIcon = () => {
    if (isComplete) {
      return "✅";
    } else {
      return "⏳";
    }
  };

  const getLabel = () => {
    if (isComplete) {
      return "Full Year";
    } else {
      return dataThroughDate ? `Through ${dataThroughDate}` : "YTD";
    }
  };

  return (
    <div className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getBadgeColor()} ${className}`}>
      <span className="mr-1">{getIcon()}</span>
      <span>{year} ({getLabel()})</span>
    </div>
  );
};

export default YearBadge;
