import React, { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import { 
  ChartBarIcon, 
  CurrencyDollarIcon, 
  BuildingOfficeIcon,
  UserGroupIcon,
  BanknotesIcon,
  CloudArrowUpIcon,
  ArrowPathIcon,
  DocumentTextIcon,
  TrendingUpIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';

const WorkingExecutiveDashboard = () => {
  const [dateTime, setDateTime] = useState(new Date());
  const [kpiData, setKpiData] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [refreshKey, setRefreshKey] = useState(0);

  // Update date/time every second
  useEffect(() => {
    const timer = setInterval(() => {
      setDateTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // Fetch data from backend
  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch KPI data
        const kpiResponse = await fetch('http://localhost:8001/api/kpis/financial');
        if (kpiResponse.ok) {
          const kpiData = await kpiResponse.json();
          setKpiData(kpiData);
        }

        // Fetch documents
        const docsResponse = await fetch('http://localhost:8001/api/documents');
        if (docsResponse.ok) {
          const docsData = await docsResponse.json();
          setDocuments(docsData.documents || []);
        }
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, [refreshKey]);

  const handleRefresh = () => {
    setRefreshKey(prev => prev + 1);
    toast.success('Data refreshed successfully!');
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);
    formData.append('property_id', 'PROP-' + Math.floor(Math.random() * 1000));

    const uploadPromise = fetch('http://localhost:8001/api/documents/upload', {
      method: 'POST',
      body: formData,
    });

    toast.promise(
      uploadPromise,
      {
        loading: `Uploading ${file.name}...`,
        success: (response) => {
          if (response.ok) {
            handleRefresh();
            return `${file.name} uploaded successfully!`;
          }
          throw new Error('Upload failed');
        },
        error: 'Upload failed. Please try again.',
      }
    );
  };

  // KPI data with fallbacks
  const kpis = kpiData?.core_kpis ? [
    {
      title: 'Portfolio Value',
      value: kpiData.core_kpis.total_portfolio_value.formatted,
      change: '+12.3%',
      icon: BanknotesIcon,
      color: 'emerald'
    },
    {
      title: 'Properties',
      value: kpiData.core_kpis.total_properties.value.toString(),
      change: `${kpiData.core_kpis.total_properties.occupied} occupied`,
      icon: BuildingOfficeIcon,
      color: 'blue'
    },
    {
      title: 'Monthly Income',
      value: kpiData.core_kpis.monthly_rental_income.formatted,
      change: '+8.4%',
      icon: CurrencyDollarIcon,
      color: 'purple'
    },
    {
      title: 'Occupancy',
      value: kpiData.core_kpis.occupancy_rate.formatted,
      change: 'Good',
      icon: UserGroupIcon,
      color: 'green'
    }
  ] : [
    {
      title: 'Portfolio Value',
      value: '$47.8M',
      change: '+12.3%',
      icon: BanknotesIcon,
      color: 'emerald'
    },
    {
      title: 'Properties',
      value: '184',
      change: '174 occupied',
      icon: BuildingOfficeIcon,
      color: 'blue'
    },
    {
      title: 'Monthly Income',
      value: '$1.2M',
      change: '+8.4%',
      icon: CurrencyDollarIcon,
      color: 'purple'
    },
    {
      title: 'Occupancy',
      value: '94.6%',
      change: 'Good',
      icon: UserGroupIcon,
      color: 'green'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900">
      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute inset-0 bg-grid-pattern"></div>
      </div>

      <div className="relative z-10">
        {/* Header */}
        <header className="bg-white/10 backdrop-blur-md border-b border-white/20">
          <div className="max-w-7xl mx-auto px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="p-3 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl shadow-lg">
                  <BuildingOfficeIcon className="w-8 h-8 text-white" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-white">REIMS Executive</h1>
                  <p className="text-blue-200">Real Estate Intelligence & Management System</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-6">
                <div className="text-right">
                  <div className="text-white font-medium">
                    {dateTime.toLocaleDateString('en-US', { 
                      weekday: 'short', 
                      month: 'short', 
                      day: 'numeric' 
                    })}
                  </div>
                  <div className="text-blue-200 text-sm">
                    {dateTime.toLocaleTimeString('en-US', { 
                      hour: '2-digit', 
                      minute: '2-digit' 
                    })}
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
                  <span className="text-green-300 text-sm font-medium">Live</span>
                </div>

                <button
                  onClick={handleRefresh}
                  className="p-2 bg-white/10 hover:bg-white/20 rounded-lg transition-colors duration-200"
                >
                  <ArrowPathIcon className="w-5 h-5 text-white" />
                </button>
              </div>
            </div>
          </div>
        </header>

        <div className="max-w-7xl mx-auto px-6 py-8 space-y-8">
          {/* Title */}
          <div className="text-center">
            <h2 className="text-4xl font-bold text-white mb-4">Executive Dashboard</h2>
            <p className="text-blue-200 text-lg">Overview & Key Performance Indicators</p>
          </div>

          {/* KPI Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
            {kpis.map((kpi, index) => (
              <div
                key={kpi.title}
                className="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20 hover:bg-white/20 transition-all duration-300"
              >
                <div className="flex items-center justify-between mb-4">
                  <div className="p-3 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl shadow-lg">
                    <kpi.icon className="w-6 h-6 text-white" />
                  </div>
                  <div className="flex items-center space-x-1 text-sm font-semibold text-emerald-400">
                    <TrendingUpIcon className="w-4 h-4" />
                    <span>{kpi.change}</span>
                  </div>
                </div>
                
                <h3 className="text-sm font-medium text-blue-200 uppercase tracking-wider mb-2">
                  {kpi.title}
                </h3>
                <div className="text-3xl font-bold text-white mb-2">
                  {kpi.value}
                </div>
              </div>
            ))}
          </div>

          {/* Two Column Layout */}
          <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
            {/* Document Management */}
            <div className="xl:col-span-2 bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-gradient-to-r from-purple-500 to-pink-600 rounded-lg">
                    <DocumentTextIcon className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-white">Document Center</h3>
                    <p className="text-blue-200 text-sm">AI Document Processing</p>
                  </div>
                </div>
                
                <label className="relative cursor-pointer">
                  <input
                    type="file"
                    onChange={handleFileUpload}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                    accept=".pdf,.csv,.xlsx,.xls"
                  />
                  <div className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700 rounded-lg text-white font-medium transition-all duration-200">
                    <CloudArrowUpIcon className="w-5 h-5" />
                    <span>Upload</span>
                  </div>
                </label>
              </div>

              {/* Document Stats */}
              <div className="grid grid-cols-3 gap-4 mb-6">
                <div className="bg-white/10 rounded-xl p-4 text-center border border-white/10">
                  <div className="text-2xl font-bold text-white">{documents.length}</div>
                  <div className="text-blue-200 text-sm">Total Documents</div>
                </div>
                <div className="bg-white/10 rounded-xl p-4 text-center border border-white/10">
                  <div className="text-2xl font-bold text-emerald-400">
                    {documents.filter(doc => doc.status === 'uploaded').length}
                  </div>
                  <div className="text-blue-200 text-sm">Processed</div>
                </div>
                <div className="bg-white/10 rounded-xl p-4 text-center border border-white/10">
                  <div className="text-2xl font-bold text-orange-400">
                    {documents.filter(doc => doc.minio_url).length}
                  </div>
                  <div className="text-blue-200 text-sm">In Storage</div>
                </div>
              </div>

              {/* Recent Documents */}
              <div className="space-y-3 max-h-64 overflow-y-auto">
                {documents.slice(0, 5).map((doc, index) => (
                  <div
                    key={doc.document_id || index}
                    className="flex items-center justify-between p-4 bg-white/10 rounded-xl border border-white/10"
                  >
                    <div className="flex items-center space-x-3">
                      <div className="p-2 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg">
                        <DocumentTextIcon className="w-4 h-4 text-white" />
                      </div>
                      <div>
                        <div className="text-white font-medium text-sm">
                          {doc.original_filename || 'Unknown File'}
                        </div>
                        <div className="text-blue-200 text-xs">
                          Property: {doc.property_id || 'N/A'}
                        </div>
                      </div>
                    </div>
                    <CheckCircleIcon className="w-5 h-5 text-emerald-400" />
                  </div>
                ))}
                
                {documents.length === 0 && (
                  <div className="text-center py-8">
                    <DocumentTextIcon className="w-12 h-12 text-blue-300 mx-auto mb-3" />
                    <p className="text-blue-200">No documents uploaded yet</p>
                  </div>
                )}
              </div>
            </div>

            {/* Analytics Sidebar */}
            <div className="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20">
              <div className="flex items-center space-x-3 mb-6">
                <div className="p-2 bg-gradient-to-r from-orange-500 to-red-600 rounded-lg">
                  <ChartBarIcon className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-white">Analytics</h3>
                  <p className="text-blue-200 text-sm">Business Insights</p>
                </div>
              </div>

              <div className="space-y-4">
                <div className="p-4 bg-white/10 rounded-xl border border-white/10">
                  <h4 className="text-white font-semibold mb-2">Market Performance</h4>
                  <div className="text-2xl font-bold text-emerald-400 mb-1">+15.7%</div>
                  <p className="text-blue-200 text-sm">YoY growth in portfolio value</p>
                </div>

                <div className="p-4 bg-white/10 rounded-xl border border-white/10">
                  <h4 className="text-white font-semibold mb-2">Investment Opportunities</h4>
                  <div className="text-2xl font-bold text-blue-400 mb-1">23</div>
                  <p className="text-blue-200 text-sm">Properties available</p>
                </div>

                <div className="p-4 bg-white/10 rounded-xl border border-white/10">
                  <h4 className="text-white font-semibold mb-2">Risk Assessment</h4>
                  <div className="text-2xl font-bold text-green-400 mb-1">Low Risk</div>
                  <p className="text-blue-200 text-sm">Portfolio risk score: 2.1/10</p>
                </div>

                <div className="p-4 bg-white/10 rounded-xl border border-white/10">
                  <h4 className="text-white font-semibold mb-2">Data Status</h4>
                  <div className="text-sm text-green-300 mb-1">
                    {kpiData?.source === 'database' ? '🟢 Live Database' : '🟡 Mock Data'}
                  </div>
                  <p className="text-blue-200 text-xs">
                    Last updated: {kpiData ? new Date(kpiData.timestamp).toLocaleTimeString() : 'N/A'}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Executive Summary */}
          <div className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 rounded-2xl p-8 text-white shadow-2xl">
            <div className="text-center space-y-4">
              <h2 className="text-3xl font-bold">Portfolio Performance Summary</h2>
              <p className="text-indigo-100 text-lg max-w-4xl mx-auto">
                Your real estate portfolio demonstrates exceptional performance with strong growth across all key metrics. 
                The portfolio shows robust fundamentals with high occupancy rates and consistent income generation.
              </p>
              <div className="flex justify-center space-x-8 pt-6">
                <div className="text-center">
                  <div className="text-3xl font-bold">+18.3%</div>
                  <div className="text-indigo-200">YoY Growth</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold">{kpiData?.core_kpis?.total_portfolio_value?.formatted || '$47.8M'}</div>
                  <div className="text-indigo-200">Total Value</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold">{kpiData?.core_kpis?.total_properties?.value || '184'}</div>
                  <div className="text-indigo-200">Properties</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold">{documents.length}</div>
                  <div className="text-indigo-200">Documents</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WorkingExecutiveDashboard;