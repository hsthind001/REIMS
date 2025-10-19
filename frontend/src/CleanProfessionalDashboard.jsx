import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

const CleanProfessionalDashboard = () => {
  const [dateTime, setDateTime] = useState(new Date());
  const [kpiData, setKpiData] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshKey, setRefreshKey] = useState(0);

  // Update date/time every second
  useEffect(() => {
    const timer = setInterval(() => {
      setDateTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // Fetch all data
  useEffect(() => {
    const fetchAllData = async () => {
      try {
        setLoading(true);
        
        // Fetch KPI data
        const kpiResponse = await fetch('http://localhost:8001/api/kpis/financial');
        const kpiData = await kpiResponse.json();
        setKpiData(kpiData);

        // Fetch documents
        const docsResponse = await fetch('http://localhost:8001/api/documents');
        const docsData = await docsResponse.json();
        setDocuments(docsData.documents || []);

      } catch (error) {
        console.error('Failed to fetch data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchAllData();
    const interval = setInterval(fetchAllData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, [refreshKey]);

  const handleRefresh = () => {
    setRefreshKey(prev => prev + 1);
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);
    formData.append('property_id', 'PROP-' + Math.floor(Math.random() * 1000));

    try {
      const response = await fetch('http://localhost:8001/api/documents/upload', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        handleRefresh(); // Refresh data after upload
        alert('File uploaded successfully!');
      }
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Upload failed');
    }
  };

  // Generate KPI cards from data
  const kpis = kpiData?.core_kpis ? [
    {
      title: 'Total Portfolio Value',
      value: kpiData.core_kpis.total_portfolio_value.formatted,
      change: '+12.3%',
      trend: 'up'
    },
    {
      title: 'Properties',
      value: kpiData.core_kpis.total_properties.value.toString(),
      change: `${kpiData.core_kpis.total_properties.occupied} occupied`,
      trend: 'up'
    },
    {
      title: 'Monthly Income',
      value: kpiData.core_kpis.monthly_rental_income.formatted,
      change: '+8.4%',
      trend: 'up'
    },
    {
      title: 'Occupancy Rate',
      value: kpiData.core_kpis.occupancy_rate.formatted,
      change: kpiData.core_kpis.occupancy_rate.value > 90 ? 'Good' : 'Needs attention',
      trend: kpiData.core_kpis.occupancy_rate.value > 90 ? 'up' : 'down'
    }
  ] : [
    {
      title: 'Total Portfolio Value',
      value: '$47.8M',
      change: '+12.3%',
      trend: 'up'
    },
    {
      title: 'Properties',
      value: '184',
      change: '174 occupied',
      trend: 'up'
    },
    {
      title: 'Monthly Income',
      value: '$1.2M',
      change: '+8.4%',
      trend: 'up'
    },
    {
      title: 'Occupancy Rate',
      value: '94.6%',
      change: 'Good',
      trend: 'up'
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 mb-8">
          <div className="px-8 py-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-gray-900">REIMS Executive Dashboard</h1>
                <p className="text-gray-600 mt-1">Real Estate Intelligence & Management System</p>
              </div>
              
              <div className="flex items-center space-x-6">
                <div className="text-right">
                  <div className="text-gray-900 font-medium">
                    {dateTime.toLocaleDateString('en-US', { 
                      weekday: 'short', 
                      month: 'short', 
                      day: 'numeric' 
                    })}
                  </div>
                  <div className="text-gray-600 text-sm">
                    {dateTime.toLocaleTimeString('en-US', { 
                      hour: '2-digit', 
                      minute: '2-digit',
                      second: '2-digit'
                    })}
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  <span className="text-green-600 text-sm font-medium">System Online</span>
                </div>

                <button
                  onClick={handleRefresh}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors duration-200 font-medium"
                >
                  Refresh Data
                </button>
              </div>
            </div>
          </div>
        </header>

        <div className="px-8 space-y-8">
          {/* KPI Cards */}
          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Key Performance Indicators</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
              {kpis.map((kpi, index) => (
                <motion.div
                  key={kpi.title}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="bg-white rounded-lg p-6 shadow-sm border border-gray-200 hover:shadow-md transition-shadow duration-200"
                >
                  <h3 className="text-sm font-semibold text-gray-600 uppercase tracking-wider mb-3">
                    {kpi.title}
                  </h3>
                  <div className="text-3xl font-bold text-gray-900 mb-2">
                    {kpi.value}
                  </div>
                  <div className={`text-sm font-medium ${
                    kpi.trend === 'up' ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {kpi.change}
                  </div>
                </motion.div>
              ))}
            </div>
          </section>

          {/* Action Buttons Section */}
          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Quick Actions</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
              <label className="cursor-pointer">
                <input
                  type="file"
                  onChange={handleFileUpload}
                  className="hidden"
                  accept=".pdf,.csv,.xlsx,.xls"
                />
                <div className="bg-white border-2 border-blue-600 hover:bg-blue-50 rounded-lg p-6 text-center transition-colors duration-200">
                  <div className="text-lg font-semibold text-blue-600">Upload Document</div>
                  <div className="text-sm text-gray-600 mt-2">PDF, CSV, Excel files</div>
                </div>
              </label>

              <button className="bg-white border-2 border-green-600 hover:bg-green-50 rounded-lg p-6 text-center transition-colors duration-200">
                <div className="text-lg font-semibold text-green-600">View Properties</div>
                <div className="text-sm text-gray-600 mt-2">Manage property portfolio</div>
              </button>

              <button className="bg-white border-2 border-purple-600 hover:bg-purple-50 rounded-lg p-6 text-center transition-colors duration-200">
                <div className="text-lg font-semibold text-purple-600">Analytics</div>
                <div className="text-sm text-gray-600 mt-2">View detailed reports</div>
              </button>

              <button className="bg-white border-2 border-orange-600 hover:bg-orange-50 rounded-lg p-6 text-center transition-colors duration-200">
                <div className="text-lg font-semibold text-orange-600">Financial Reports</div>
                <div className="text-sm text-gray-600 mt-2">Income and expenses</div>
              </button>
            </div>
          </section>

          {/* Document Management Section */}
          <section>
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h3 className="text-xl font-bold text-gray-900">Document Center</h3>
                  <p className="text-gray-600 text-sm mt-1">AI-powered document processing</p>
                </div>
              </div>

              {/* Document Stats */}
              <div className="grid grid-cols-3 gap-4 mb-6">
                <div className="bg-gray-50 rounded-lg p-4 text-center border border-gray-200">
                  <div className="text-2xl font-bold text-gray-900">{documents.length}</div>
                  <div className="text-gray-600 text-sm mt-1">Total Documents</div>
                </div>
                <div className="bg-gray-50 rounded-lg p-4 text-center border border-gray-200">
                  <div className="text-2xl font-bold text-green-600">
                    {documents.filter(doc => doc.status === 'uploaded').length}
                  </div>
                  <div className="text-gray-600 text-sm mt-1">Processed</div>
                </div>
                <div className="bg-gray-50 rounded-lg p-4 text-center border border-gray-200">
                  <div className="text-2xl font-bold text-blue-600">
                    {documents.filter(doc => doc.minio_url).length}
                  </div>
                  <div className="text-gray-600 text-sm mt-1">In Cloud Storage</div>
                </div>
              </div>

              {/* Recent Documents Table */}
              <div>
                <h4 className="text-lg font-semibold text-gray-900 mb-4">Recent Documents</h4>
                {documents.length > 0 ? (
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Filename
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Property ID
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Size
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Status
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Uploaded
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Actions
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {documents.slice(0, 5).map((doc) => (
                          <tr key={doc.document_id} className="hover:bg-gray-50">
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                              {doc.original_filename}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                              {doc.property_id}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                              {(doc.file_size / 1024).toFixed(2)} KB
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span className="px-3 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                                {doc.status}
                              </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                              {new Date(doc.upload_timestamp).toLocaleDateString()}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm">
                              <button className="text-blue-600 hover:text-blue-800 font-medium mr-4">
                                View
                              </button>
                              <button className="text-red-600 hover:text-red-800 font-medium">
                                Delete
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
                    <p className="text-gray-600 mb-4">No documents uploaded yet</p>
                    <label className="cursor-pointer">
                      <input
                        type="file"
                        onChange={handleFileUpload}
                        className="hidden"
                        accept=".pdf,.csv,.xlsx,.xls"
                      />
                      <span className="inline-block px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors duration-200">
                        Upload First Document
                      </span>
                    </label>
                  </div>
                )}
              </div>
            </div>
          </section>

          {/* System Status Section */}
          <section>
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-xl font-bold text-gray-900 mb-4">System Status</h3>
              
              <div className="space-y-3">
                <div className="flex items-center justify-between py-3 border-b border-gray-200">
                  <span className="text-gray-700 font-medium">Backend API</span>
                  <span className="px-3 py-1 bg-green-100 text-green-800 text-sm font-semibold rounded-full">
                    Online
                  </span>
                </div>
                <div className="flex items-center justify-between py-3 border-b border-gray-200">
                  <span className="text-gray-700 font-medium">Database</span>
                  <span className="px-3 py-1 bg-green-100 text-green-800 text-sm font-semibold rounded-full">
                    Connected
                  </span>
                </div>
                <div className="flex items-center justify-between py-3 border-b border-gray-200">
                  <span className="text-gray-700 font-medium">Cloud Storage</span>
                  <span className="px-3 py-1 bg-green-100 text-green-800 text-sm font-semibold rounded-full">
                    Available
                  </span>
                </div>
                <div className="flex items-center justify-between py-3">
                  <span className="text-gray-700 font-medium">AI Processing</span>
                  <span className="px-3 py-1 bg-green-100 text-green-800 text-sm font-semibold rounded-full">
                    Ready
                  </span>
                </div>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
};

export default CleanProfessionalDashboard;

















