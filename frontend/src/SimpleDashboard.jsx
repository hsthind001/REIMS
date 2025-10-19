import React, { useState, useEffect } from 'react';

const ExecutiveDashboard = () => {
  const [dateTime, setDateTime] = useState(new Date());
  const [kpiData, setKpiData] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [notification, setNotification] = useState(null);

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
        const kpiResponse = await fetch('http://localhost:8001/api/kpis/financial');
        if (kpiResponse.ok) {
          const kpiData = await kpiResponse.json();
          setKpiData(kpiData);
        }

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
  }, []);

  // Show notification helper
  const showNotification = (message, type = 'success') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 3000);
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setIsUploading(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('property_id', 'PROP-' + Math.floor(Math.random() * 1000));

    try {
      const response = await fetch('http://localhost:8001/api/documents/upload', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        showNotification('✓ Document uploaded successfully!', 'success');
        // Refresh documents
        const docsResponse = await fetch('http://localhost:8001/api/documents');
        if (docsResponse.ok) {
          const docsData = await docsResponse.json();
          setDocuments(docsData.documents || []);
        }
      } else {
        showNotification('⚠ Upload failed. Please try again.', 'error');
      }
    } catch (error) {
      console.error('Upload failed:', error);
      showNotification('⚠ Upload failed. Please try again.', 'error');
    } finally {
      setIsUploading(false);
      event.target.value = '';
    }
  };

  // KPI data with fallbacks
  const kpis = kpiData?.core_kpis ? [
    {
      title: 'Portfolio Value',
      value: kpiData.core_kpis.total_portfolio_value.formatted,
      change: '+12.3%',
      trend: 'up',
      gradient: 'from-emerald-500 via-teal-500 to-cyan-500',
      icon: 'M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1'
    },
    {
      title: 'Properties',
      value: kpiData.core_kpis.total_properties.value.toString(),
      change: `${kpiData.core_kpis.total_properties.occupied} occupied`,
      trend: 'stable',
      gradient: 'from-blue-500 via-indigo-500 to-purple-500',
      icon: 'M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4'
    },
    {
      title: 'Monthly Income',
      value: kpiData.core_kpis.monthly_rental_income.formatted,
      change: '+8.4%',
      trend: 'up',
      gradient: 'from-purple-500 via-pink-500 to-red-500',
      icon: 'M13 7h8m0 0v8m0-8l-8 8-4-4-6 6'
    },
    {
      title: 'Occupancy',
      value: kpiData.core_kpis.occupancy_rate.formatted,
      change: 'Excellent',
      trend: 'up',
      gradient: 'from-green-500 via-emerald-500 to-teal-500',
      icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z'
    }
  ] : [
    {
      title: 'Portfolio Value',
      value: '$47.8M',
      change: '+12.3%',
      trend: 'up',
      gradient: 'from-emerald-500 via-teal-500 to-cyan-500',
      icon: 'M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1'
    },
    {
      title: 'Properties',
      value: '184',
      change: '174 occupied',
      trend: 'stable',
      gradient: 'from-blue-500 via-indigo-500 to-purple-500',
      icon: 'M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4'
    },
    {
      title: 'Monthly Income',
      value: '$1.2M',
      change: '+8.4%',
      trend: 'up',
      gradient: 'from-purple-500 via-pink-500 to-red-500',
      icon: 'M13 7h8m0 0v8m0-8l-8 8-4-4-6 6'
    },
    {
      title: 'Occupancy',
      value: '94.6%',
      change: 'Excellent',
      trend: 'up',
      gradient: 'from-green-500 via-emerald-500 to-teal-500',
      icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-indigo-900 relative overflow-hidden">
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-cyan-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse" style={{animationDelay: '2s'}}></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-pink-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse" style={{animationDelay: '4s'}}></div>
      </div>

      {/* Notification Toast */}
      {notification && (
        <div className={`fixed top-4 right-4 z-50 px-6 py-4 rounded-xl shadow-2xl border backdrop-blur-md transform transition-all duration-500 ${
          notification.type === 'success' 
            ? 'bg-emerald-500/90 border-emerald-400 text-white' 
            : 'bg-red-500/90 border-red-400 text-white'
        }`}>
          <div className="flex items-center space-x-3">
            <div className="text-2xl">{notification.type === 'success' ? '✓' : '⚠'}</div>
            <div className="font-medium">{notification.message}</div>
          </div>
        </div>
      )}

      {/* Header */}
      <header className="relative bg-gradient-to-r from-white/10 via-white/5 to-white/10 backdrop-blur-xl border-b border-white/20 shadow-2xl">
        <div className="max-w-7xl mx-auto px-6 py-5">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="relative p-3 bg-gradient-to-br from-cyan-400 via-blue-500 to-purple-600 rounded-2xl shadow-2xl transform hover:scale-105 transition-transform duration-300">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
                <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-400 rounded-full animate-ping"></div>
                <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-400 rounded-full"></div>
              </div>
              <div>
                <h1 className="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-400">
                  REIMS Executive
                </h1>
                <p className="text-cyan-200 font-medium">Real Estate Intelligence & Management System</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-6">
              <div className="text-right bg-white/10 backdrop-blur-sm px-4 py-2 rounded-xl border border-white/20">
                <div className="text-white font-bold text-lg">
                  {dateTime.toLocaleDateString('en-US', { 
                    weekday: 'short', 
                    month: 'short', 
                    day: 'numeric' 
                  })}
                </div>
                <div className="text-cyan-300 text-sm font-semibold">
                  {dateTime.toLocaleTimeString('en-US', { 
                    hour: '2-digit', 
                    minute: '2-digit',
                    second: '2-digit'
                  })}
                </div>
              </div>
              
              <div className="flex items-center space-x-2 bg-green-500/20 backdrop-blur-sm px-4 py-2 rounded-xl border border-green-400/30">
                <div className="relative">
                  <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
                  <div className="absolute inset-0 w-3 h-3 bg-green-400 rounded-full animate-ping"></div>
                </div>
                <span className="text-green-300 text-sm font-bold">LIVE</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="relative max-w-7xl mx-auto px-6 py-8 space-y-8">
        {/* Title */}
        <div className="text-center space-y-2 animate-fade-in-up">
          <h2 className="text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400">
            Executive Dashboard
          </h2>
          <p className="text-cyan-200 text-xl font-medium">Real-Time Portfolio Intelligence</p>
        </div>

        {/* KPI Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
          {kpis.map((kpi, index) => (
            <div
              key={kpi.title}
              className="group relative bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-xl rounded-3xl p-6 border border-white/20 hover:border-white/40 transition-all duration-500 hover:scale-105 hover:shadow-2xl overflow-hidden"
              style={{animationDelay: `${index * 100}ms`}}
            >
              {/* Animated gradient background on hover */}
              <div className={`absolute inset-0 bg-gradient-to-br ${kpi.gradient} opacity-0 group-hover:opacity-10 transition-opacity duration-500`}></div>
              
              <div className="relative z-10">
                <div className="flex items-center justify-between mb-4">
                  <div className={`p-3 bg-gradient-to-br ${kpi.gradient} rounded-2xl shadow-lg transform group-hover:scale-110 group-hover:rotate-3 transition-transform duration-300`}>
                    <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d={kpi.icon} />
                    </svg>
                  </div>
                  <div className={`flex items-center space-x-1 text-sm font-bold px-3 py-1 rounded-full ${
                    kpi.trend === 'up' ? 'bg-emerald-500/20 text-emerald-300' : 'bg-blue-500/20 text-blue-300'
                  }`}>
                    {kpi.trend === 'up' && (
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                      </svg>
                    )}
                    <span>{kpi.change}</span>
                  </div>
                </div>
                
                <h3 className="text-xs font-bold text-cyan-300 uppercase tracking-widest mb-3">
                  {kpi.title}
                </h3>
                <div className="text-4xl font-black text-white mb-2 group-hover:scale-105 transition-transform duration-300">
                  {kpi.value}
                </div>
                
                {/* Progress bar indicator */}
                <div className="w-full h-1 bg-white/10 rounded-full overflow-hidden mt-4">
                  <div className={`h-full bg-gradient-to-r ${kpi.gradient} rounded-full animate-pulse`} style={{width: '75%'}}></div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Two Column Layout */}
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
          {/* Document Management */}
          <div className="xl:col-span-2 group bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-xl rounded-3xl p-8 border border-white/20 hover:border-purple-400/50 transition-all duration-500 shadow-xl hover:shadow-2xl">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center space-x-4">
                <div className="relative p-3 bg-gradient-to-br from-purple-500 via-pink-500 to-red-500 rounded-2xl shadow-2xl transform group-hover:scale-110 group-hover:rotate-3 transition-all duration-300">
                  <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <div className="absolute -top-1 -right-1 w-4 h-4 bg-pink-400 rounded-full animate-bounce"></div>
                </div>
                <div>
                  <h3 className="text-2xl font-black text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400">
                    Document Center
                  </h3>
                  <p className="text-purple-200 text-sm font-semibold">🤖 AI-Powered Processing</p>
                </div>
              </div>
              
              <label className="relative cursor-pointer group/upload">
                <input
                  type="file"
                  onChange={handleFileUpload}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                  accept=".pdf,.csv,.xlsx,.xls"
                  disabled={isUploading}
                />
                <div className={`flex items-center space-x-3 px-6 py-3 bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-500 hover:from-emerald-600 hover:via-teal-600 hover:to-cyan-600 rounded-2xl text-white font-bold shadow-lg hover:shadow-2xl transform hover:scale-105 transition-all duration-300 ${isUploading ? 'opacity-50 cursor-not-allowed' : ''}`}>
                  {isUploading ? (
                    <>
                      <svg className="w-5 h-5 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                      </svg>
                      <span>Uploading...</span>
                    </>
                  ) : (
                    <>
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                      </svg>
                      <span>Upload Document</span>
                    </>
                  )}
                </div>
              </label>
            </div>

            {/* Document Stats */}
            <div className="grid grid-cols-3 gap-5 mb-8">
              <div className="group/stat relative bg-gradient-to-br from-blue-500/20 to-cyan-500/20 rounded-2xl p-5 text-center border border-blue-400/30 hover:border-cyan-400/60 transition-all duration-300 hover:scale-105 cursor-pointer">
                <div className="absolute inset-0 bg-gradient-to-br from-blue-500 to-cyan-500 opacity-0 group-hover/stat:opacity-10 rounded-2xl transition-opacity duration-300"></div>
                <div className="relative">
                  <div className="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-cyan-400">{documents.length}</div>
                  <div className="text-cyan-200 text-xs font-bold uppercase tracking-wider">Total Docs</div>
                </div>
              </div>
              <div className="group/stat relative bg-gradient-to-br from-emerald-500/20 to-teal-500/20 rounded-2xl p-5 text-center border border-emerald-400/30 hover:border-teal-400/60 transition-all duration-300 hover:scale-105 cursor-pointer">
                <div className="absolute inset-0 bg-gradient-to-br from-emerald-500 to-teal-500 opacity-0 group-hover/stat:opacity-10 rounded-2xl transition-opacity duration-300"></div>
                <div className="relative">
                  <div className="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-teal-400">
                    {documents.filter(doc => doc.status === 'uploaded').length}
                  </div>
                  <div className="text-emerald-200 text-xs font-bold uppercase tracking-wider">Processed</div>
                </div>
              </div>
              <div className="group/stat relative bg-gradient-to-br from-orange-500/20 to-pink-500/20 rounded-2xl p-5 text-center border border-orange-400/30 hover:border-pink-400/60 transition-all duration-300 hover:scale-105 cursor-pointer">
                <div className="absolute inset-0 bg-gradient-to-br from-orange-500 to-pink-500 opacity-0 group-hover/stat:opacity-10 rounded-2xl transition-opacity duration-300"></div>
                <div className="relative">
                  <div className="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-orange-400 to-pink-400">
                    {documents.filter(doc => doc.minio_url).length}
                  </div>
                  <div className="text-orange-200 text-xs font-bold uppercase tracking-wider">In Storage</div>
                </div>
              </div>
            </div>

            {/* Recent Documents */}
            <div>
              <h4 className="text-sm font-bold text-purple-300 uppercase tracking-widest mb-4">📄 Recent Activity</h4>
              <div className="space-y-3 max-h-80 overflow-y-auto pr-2 custom-scrollbar">
                {documents.slice(0, 5).map((doc, index) => (
                  <div
                    key={doc.document_id || index}
                    className="group/doc flex items-center justify-between p-4 bg-gradient-to-r from-white/10 to-white/5 hover:from-purple-500/20 hover:to-pink-500/20 rounded-2xl border border-white/10 hover:border-purple-400/50 transition-all duration-300 hover:scale-102 cursor-pointer"
                    style={{animationDelay: `${index * 50}ms`}}
                  >
                    <div className="flex items-center space-x-4">
                      <div className="relative p-3 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl shadow-lg group-hover/doc:scale-110 group-hover/doc:rotate-6 transition-all duration-300">
                        <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                      </div>
                      <div>
                        <div className="text-white font-bold text-sm">
                          {doc.original_filename || 'Unknown File'}
                        </div>
                        <div className="text-purple-200 text-xs font-medium">
                          🏢 Property: {doc.property_id || 'N/A'}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="px-3 py-1 bg-emerald-500/20 rounded-full">
                        <svg className="w-5 h-5 text-emerald-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                      </div>
                    </div>
                  </div>
                ))}
                
                {documents.length === 0 && (
                  <div className="text-center py-12">
                    <div className="inline-block p-6 bg-gradient-to-br from-purple-500/10 to-pink-500/10 rounded-3xl mb-4">
                      <svg className="w-16 h-16 text-purple-300 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                    </div>
                    <p className="text-purple-200 font-semibold text-lg">No documents uploaded yet</p>
                    <p className="text-purple-300 text-sm mt-2">Upload your first document to get started!</p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Analytics Sidebar */}
          <div className="group bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-xl rounded-3xl p-6 border border-white/20 hover:border-orange-400/50 transition-all duration-500 shadow-xl hover:shadow-2xl">
            <div className="flex items-center space-x-4 mb-6">
              <div className="relative p-3 bg-gradient-to-br from-orange-500 via-red-500 to-pink-600 rounded-2xl shadow-2xl transform group-hover:scale-110 group-hover:rotate-3 transition-all duration-300">
                <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                <div className="absolute -top-1 -right-1 w-4 h-4 bg-yellow-400 rounded-full animate-pulse"></div>
              </div>
              <div>
                <h3 className="text-2xl font-black text-transparent bg-clip-text bg-gradient-to-r from-orange-400 to-red-400">
                  Analytics
                </h3>
                <p className="text-orange-200 text-sm font-semibold">📊 Business Insights</p>
              </div>
            </div>

            <div className="space-y-4">
              <div className="group/card relative p-5 bg-gradient-to-br from-emerald-500/20 to-teal-500/20 hover:from-emerald-500/30 hover:to-teal-500/30 rounded-2xl border border-emerald-400/30 hover:border-emerald-400/60 transition-all duration-300 cursor-pointer overflow-hidden">
                <div className="absolute top-0 right-0 w-20 h-20 bg-emerald-400/10 rounded-full blur-2xl group-hover/card:scale-150 transition-transform duration-500"></div>
                <h4 className="text-emerald-300 font-bold mb-2 text-sm uppercase tracking-wider">📈 Market Performance</h4>
                <div className="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-teal-400 mb-1">+15.7%</div>
                <p className="text-emerald-200 text-xs font-medium">YoY growth in portfolio value</p>
                <div className="w-full h-1 bg-emerald-900/30 rounded-full overflow-hidden mt-3">
                  <div className="h-full bg-gradient-to-r from-emerald-500 to-teal-500 rounded-full animate-pulse" style={{width: '85%'}}></div>
                </div>
              </div>

              <div className="group/card relative p-5 bg-gradient-to-br from-blue-500/20 to-indigo-500/20 hover:from-blue-500/30 hover:to-indigo-500/30 rounded-2xl border border-blue-400/30 hover:border-blue-400/60 transition-all duration-300 cursor-pointer overflow-hidden">
                <div className="absolute top-0 right-0 w-20 h-20 bg-blue-400/10 rounded-full blur-2xl group-hover/card:scale-150 transition-transform duration-500"></div>
                <h4 className="text-blue-300 font-bold mb-2 text-sm uppercase tracking-wider">💎 Investment Opportunities</h4>
                <div className="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-400 mb-1">23</div>
                <p className="text-blue-200 text-xs font-medium">Properties available for acquisition</p>
                <div className="w-full h-1 bg-blue-900/30 rounded-full overflow-hidden mt-3">
                  <div className="h-full bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full animate-pulse" style={{width: '60%'}}></div>
                </div>
              </div>

              <div className="group/card relative p-5 bg-gradient-to-br from-green-500/20 to-lime-500/20 hover:from-green-500/30 hover:to-lime-500/30 rounded-2xl border border-green-400/30 hover:border-green-400/60 transition-all duration-300 cursor-pointer overflow-hidden">
                <div className="absolute top-0 right-0 w-20 h-20 bg-green-400/10 rounded-full blur-2xl group-hover/card:scale-150 transition-transform duration-500"></div>
                <h4 className="text-green-300 font-bold mb-2 text-sm uppercase tracking-wider">🛡️ Risk Assessment</h4>
                <div className="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-lime-400 mb-1">Low Risk</div>
                <p className="text-green-200 text-xs font-medium">Portfolio risk score: 2.1/10</p>
                <div className="w-full h-1 bg-green-900/30 rounded-full overflow-hidden mt-3">
                  <div className="h-full bg-gradient-to-r from-green-500 to-lime-500 rounded-full animate-pulse" style={{width: '21%'}}></div>
                </div>
              </div>

              <div className="group/card relative p-5 bg-gradient-to-br from-cyan-500/20 to-blue-500/20 hover:from-cyan-500/30 hover:to-blue-500/30 rounded-2xl border border-cyan-400/30 hover:border-cyan-400/60 transition-all duration-300 cursor-pointer overflow-hidden">
                <div className="absolute top-0 right-0 w-20 h-20 bg-cyan-400/10 rounded-full blur-2xl group-hover/card:scale-150 transition-transform duration-500"></div>
                <h4 className="text-cyan-300 font-bold mb-2 text-sm uppercase tracking-wider">💻 Data Status</h4>
                <div className="text-lg font-black text-cyan-300 mb-1 flex items-center space-x-2">
                  <div className={`w-3 h-3 rounded-full ${kpiData?.source === 'database' ? 'bg-green-400 animate-pulse' : 'bg-yellow-400'}`}></div>
                  <span>{kpiData?.source === 'database' ? 'Live Database' : 'Mock Data'}</span>
                </div>
                <p className="text-cyan-200 text-xs font-medium">
                  Last updated: {kpiData ? new Date(kpiData.timestamp).toLocaleTimeString() : 'N/A'}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Executive Summary */}
        <div className="relative group bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 rounded-3xl p-10 text-white shadow-2xl overflow-hidden hover:shadow-3xl transition-all duration-500">
          {/* Animated background pattern */}
          <div className="absolute inset-0 opacity-10">
            <div className="absolute top-0 left-0 w-72 h-72 bg-white rounded-full blur-3xl animate-pulse"></div>
            <div className="absolute bottom-0 right-0 w-96 h-96 bg-pink-300 rounded-full blur-3xl animate-pulse" style={{animationDelay: '1s'}}></div>
          </div>
          
          <div className="relative z-10 text-center space-y-6">
            <div className="inline-block">
              <h2 className="text-4xl md:text-5xl font-black mb-2">🎯 Portfolio Performance Summary</h2>
              <div className="w-32 h-1 bg-white/50 rounded-full mx-auto"></div>
            </div>
            
            <p className="text-indigo-100 text-lg md:text-xl max-w-4xl mx-auto font-medium leading-relaxed">
              Your real estate portfolio demonstrates <span className="font-black text-white">exceptional performance</span> with strong growth across all key metrics. 
              The portfolio shows robust fundamentals with high occupancy rates and consistent income generation.
            </p>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 pt-8">
              <div className="group/summary bg-white/10 backdrop-blur-sm rounded-2xl p-6 hover:bg-white/20 transition-all duration-300 hover:scale-105 cursor-pointer border border-white/20">
                <div className="text-4xl font-black mb-2 group-hover/summary:scale-110 transition-transform duration-300">+18.3%</div>
                <div className="text-indigo-100 font-semibold uppercase tracking-wider text-sm">YoY Growth</div>
              </div>
              <div className="group/summary bg-white/10 backdrop-blur-sm rounded-2xl p-6 hover:bg-white/20 transition-all duration-300 hover:scale-105 cursor-pointer border border-white/20">
                <div className="text-4xl font-black mb-2 group-hover/summary:scale-110 transition-transform duration-300">
                  {kpiData?.core_kpis?.total_portfolio_value?.formatted || '$47.8M'}
                </div>
                <div className="text-indigo-100 font-semibold uppercase tracking-wider text-sm">Total Value</div>
              </div>
              <div className="group/summary bg-white/10 backdrop-blur-sm rounded-2xl p-6 hover:bg-white/20 transition-all duration-300 hover:scale-105 cursor-pointer border border-white/20">
                <div className="text-4xl font-black mb-2 group-hover/summary:scale-110 transition-transform duration-300">
                  {kpiData?.core_kpis?.total_properties?.value || '184'}
                </div>
                <div className="text-indigo-100 font-semibold uppercase tracking-wider text-sm">Properties</div>
              </div>
              <div className="group/summary bg-white/10 backdrop-blur-sm rounded-2xl p-6 hover:bg-white/20 transition-all duration-300 hover:scale-105 cursor-pointer border border-white/20">
                <div className="text-4xl font-black mb-2 group-hover/summary:scale-110 transition-transform duration-300">{documents.length}</div>
                <div className="text-indigo-100 font-semibold uppercase tracking-wider text-sm">Documents</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="relative mt-12 py-6 text-center text-white/60 text-sm">
        <div className="max-w-7xl mx-auto px-6">
          <p className="font-medium">
            Powered by <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-400 font-bold">REIMS AI</span> © 2024
          </p>
        </div>
      </footer>
    </div>
  );
};

export default ExecutiveDashboard;