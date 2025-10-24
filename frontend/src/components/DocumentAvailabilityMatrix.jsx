import React from 'react';

const DocumentAvailabilityMatrix = ({ 
  propertyId,
  years = [],
  className = "" 
}) => {
  if (!years || years.length === 0) {
    return (
      <div className={`document-matrix ${className}`}>
        <div className="text-sm text-gray-500">No document data available</div>
      </div>
    );
  }

  const documentTypes = [
    'Balance Sheet',
    'Income Statement', 
    'Cash Flow Statement',
    'Rent Roll'
  ];

  const getDocumentStatus = (year, docType) => {
    // This would be populated from the API response
    // For now, return mock data based on year
    if (year === 2025) {
      return docType === 'Rent Roll' ? 'available' : 'pending';
    } else {
      return ['Balance Sheet', 'Income Statement', 'Cash Flow Statement'].includes(docType) 
        ? 'available' 
        : 'not_applicable';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'available':
        return '✅';
      case 'pending':
        return '⏳';
      case 'not_applicable':
        return '➖';
      default:
        return '❌';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'available':
        return 'text-green-600';
      case 'pending':
        return 'text-yellow-600';
      case 'not_applicable':
        return 'text-gray-400';
      default:
        return 'text-red-600';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'available':
        return 'Available';
      case 'pending':
        return 'Pending';
      case 'not_applicable':
        return 'N/A';
      default:
        return 'Missing';
    }
  };

  return (
    <div className={`document-matrix ${className}`}>
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
          <h3 className="text-lg font-semibold text-gray-900">Document Availability by Year</h3>
          <p className="text-sm text-gray-600 mt-1">Track which financial documents are available for each year</p>
        </div>
        
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Document Type
                </th>
                {years.map((year) => (
                  <th key={year.year} className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {year.year}
                    {year.is_complete ? (
                      <span className="ml-1 text-green-600">✓</span>
                    ) : (
                      <span className="ml-1 text-yellow-600">⏳</span>
                    )}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {documentTypes.map((docType) => (
                <tr key={docType} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {docType}
                  </td>
                  {years.map((year) => {
                    const status = getDocumentStatus(year.year, docType);
                    return (
                      <td key={year.year} className="px-6 py-4 whitespace-nowrap text-center">
                        <div className="flex flex-col items-center">
                          <span className="text-lg">{getStatusIcon(status)}</span>
                          <span className={`text-xs ${getStatusColor(status)}`}>
                            {getStatusText(status)}
                          </span>
                        </div>
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200">
          <div className="flex items-center justify-between text-xs text-gray-500">
            <div className="flex items-center space-x-4">
              <div className="flex items-center">
                <span className="mr-1">✅</span>
                <span>Available</span>
              </div>
              <div className="flex items-center">
                <span className="mr-1">⏳</span>
                <span>Pending</span>
              </div>
              <div className="flex items-center">
                <span className="mr-1">➖</span>
                <span>N/A</span>
              </div>
            </div>
            <div className="text-right">
              <span className="text-green-600">✓</span> = Complete Year
              <span className="ml-2 text-yellow-600">⏳</span> = Partial Year
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DocumentAvailabilityMatrix;
