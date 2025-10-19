import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Toaster, toast } from "react-hot-toast";
import { API_CONFIG, buildApiUrl } from "./config/api";

// Import our modern components
import { Navigation } from "./components/Navigation";
import { ModernHeader } from "./components/ModernHeader";
import { LoadingSpinner } from "./components/LoadingSpinner";

function WorkingApp() {
  const [currentView, setCurrentView] = useState('dashboard');
  const [isLoading, setIsLoading] = useState(true);
  const [activeView, setActiveView] = useState('dashboard');
  const [backendStatus, setBackendStatus] = useState('checking');
  const [stats, setStats] = useState({
    totalDocuments: 42,
    aiProcessed: 38,
    totalProperties: 15,
    pendingAnalysis: 4
  });
  const [uploadFile, setUploadFile] = useState(null);
  const [propertyId, setPropertyId] = useState('');
  const [uploading, setUploading] = useState(false);
  const [documents, setDocuments] = useState([]);

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const handleUpload = async () => {
    if (!uploadFile || !propertyId.trim()) {
      toast.error('Please select a file and enter a property ID');
      return;
    }

    setUploading(true);
    
    try {
      const formData = new FormData();
      formData.append('file', uploadFile);
      formData.append('property_id', propertyId);

      const response = await fetch(buildApiUrl(API_CONFIG.ENDPOINTS.DOCUMENTS_UPLOAD), {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        toast.success('File uploaded successfully!');
        setUploadFile(null);
        setPropertyId('');
        // Refresh stats and documents
        fetchStats();
        fetchDocuments();
      } else {
        const error = await response.json();
        toast.error(`Upload failed: ${error.detail || 'Unknown error'}`);
      }
    } catch (error) {
      toast.error(`Upload failed: ${error.message}`);
    } finally {
      setUploading(false);
    }
  };

  const fetchStats = async () => {
    try {
      // Try to get documents count
      const docsResponse = await fetch(buildApiUrl(API_CONFIG.ENDPOINTS.DOCUMENTS_LIST));
      if (docsResponse.ok) {
        const docsData = await docsResponse.json();
        const totalDocs = docsData.count || 0;
        const processedDocs = docsData.documents?.filter(doc => 
          doc.status === 'processed' || doc.job_status === 'completed'
        ).length || 0;
        
        setStats(prevStats => ({
          ...prevStats,
          totalDocuments: totalDocs,
          aiProcessed: processedDocs,
          totalProperties: new Set(docsData.documents?.map(doc => doc.property_id)).size || 0,
          pendingAnalysis: totalDocs - processedDocs
        }));
      }
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  const fetchDocuments = async () => {
    try {
      const response = await fetch(buildApiUrl(API_CONFIG.ENDPOINTS.DOCUMENTS_LIST));
      if (response.ok) {
        const data = await response.json();
        setDocuments(data.documents || []);
      }
    } catch (error) {
      console.error('Failed to fetch documents:', error);
    }
  };
  const [systemStats, setSystemStats] = useState({
    totalDocuments: 0,
    aiProcessed: 0,
    totalProperties: 0,
    recentUploads: []
  });

  // Initialize app and check backend connectivity
  useEffect(() => {
    const initializeApp = async () => {
      try {
        // Check backend connectivity
        const healthResponse = await fetch(buildApiUrl(API_CONFIG.ENDPOINTS.HEALTH));
        if (healthResponse.ok) {
          setBackendStatus('connected');
          
          // Fetch system statistics
          try {
            const docsResponse = await fetch(buildApiUrl(API_CONFIG.ENDPOINTS.DOCUMENTS_LIST));
            if (docsResponse.ok) {
              const docsData = await docsResponse.json();
              const documents = docsData.documents || [];
              const totalDocs = documents.length;
              const processedDocs = documents.filter(doc => 
                doc.status === 'processed' || doc.job_status === 'completed'
              ).length;
              const totalProps = new Set(documents.map(doc => doc.property_id)).size;
              
              setSystemStats({
                totalDocuments: totalDocs,
                aiProcessed: processedDocs,
                totalProperties: totalProps,
                recentUploads: documents.slice(-3)
              });

              setStats({
                totalDocuments: totalDocs,
                aiProcessed: processedDocs,
                totalProperties: totalProps,
                pendingAnalysis: totalDocs - processedDocs
              });

              setDocuments(documents);
            }
          } catch (err) {
            console.log('Could not fetch documents:', err);
          }
        } else {
          setBackendStatus('disconnected');
        }
      } catch (error) {
        setBackendStatus('disconnected');
      }
      
      setTimeout(() => {
        setIsLoading(false);
      }, 1500);
    };
    
    initializeApp();
  }, []);

  // Refresh data when changing to certain views
  useEffect(() => {
    if (activeView === 'documents') {
      fetchDocuments();
    } else if (activeView === 'dashboard') {
      fetchStats();
    }
  }, [activeView]);

  // Render different views based on currentView
  const renderContent = () => {
    const pageVariants = {
      initial: { opacity: 0, y: 20, scale: 0.95 },
      in: { opacity: 1, y: 0, scale: 1 },
      out: { opacity: 0, y: -20, scale: 0.95 }
    };

    const pageTransition = {
      type: 'tween',
      ease: 'anticipate',
      duration: 0.5
    };

    switch (currentView) {
      case 'dashboard':
        return (
          <motion.div
            key="dashboard"
            initial="initial"
            animate="in"
            exit="out"
            variants={pageVariants}
            transition={pageTransition}
            className="space-y-8"
          >
            {/* Welcome Section */}
            <div className="text-center mb-8">
              <motion.h1 
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-4xl font-bold text-gray-800 mb-2"
              >
                Welcome to <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">REIMS</span>
              </motion.h1>
              <p className="text-gray-600 text-lg">Real Estate Intelligence Management System</p>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {[
                { 
                  title: "Total Documents", 
                  value: systemStats.totalDocuments, 
                  subtitle: "Files uploaded",
                  gradient: "from-blue-500 to-cyan-500",
                  icon: "📄"
                },
                { 
                  title: "AI Processed", 
                  value: systemStats.aiProcessed, 
                  subtitle: "Documents analyzed",
                  gradient: "from-purple-500 to-pink-500",
                  icon: "🤖"
                },
                { 
                  title: "Properties", 
                  value: systemStats.totalProperties, 
                  subtitle: "Unique properties",
                  gradient: "from-green-500 to-emerald-500",
                  icon: "🏢"
                },
                { 
                  title: "Success Rate", 
                  value: systemStats.totalDocuments > 0 ? `${Math.round((systemStats.aiProcessed / systemStats.totalDocuments) * 100)}%` : "100%", 
                  subtitle: "Processing success",
                  gradient: "from-orange-500 to-red-500",
                  icon: "📊"
                }
              ].map((stat, index) => (
                <motion.div
                  key={stat.title}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="glass-card p-6 hover:scale-105 transition-transform duration-200"
                >
                  <div className={`absolute inset-0 bg-gradient-to-br ${stat.gradient} opacity-5 rounded-xl`} />
                  <div className="relative z-10">
                    <div className="flex items-center justify-between mb-4">
                      <span className="text-2xl">{stat.icon}</span>
                      <div className="text-right">
                        <div className="text-2xl font-bold text-gray-800">{stat.value}</div>
                        <div className="text-sm text-gray-600">{stat.title}</div>
                      </div>
                    </div>
                    <div className="text-xs text-gray-500">{stat.subtitle}</div>
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Recent Activity & Quick Actions */}
            <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.5 }}
                className="glass-card p-6"
              >
                <h3 className="text-xl font-bold text-gray-800 mb-4">Recent Activity</h3>
                {systemStats.recentUploads.length === 0 ? (
                  <div className="text-center py-8">
                    <div className="text-4xl mb-2">📂</div>
                    <p className="text-gray-500">No recent uploads</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {systemStats.recentUploads.map((doc, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-white/30 rounded-lg">
                        <div>
                          <p className="font-medium text-gray-800">{doc.original_filename}</p>
                          <p className="text-sm text-gray-600">Property: {doc.property_id}</p>
                        </div>
                        <span className="text-xs text-gray-500">{formatFileSize(doc.file_size)}</span>
                      </div>
                    ))}
                  </div>
                )}
              </motion.div>

              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.6 }}
                className="glass-card p-6"
              >
                <h3 className="text-xl font-bold text-gray-800 mb-4">Quick Actions</h3>
                <div className="grid grid-cols-2 gap-4">
                  {[
                    { title: "Upload", icon: "📤", view: "upload", gradient: "from-blue-500 to-cyan-500" },
                    { title: "Analytics", icon: "📊", view: "analytics", gradient: "from-purple-500 to-pink-500" },
                    { title: "Documents", icon: "📚", view: "documents", gradient: "from-green-500 to-emerald-500" },
                    { title: "Properties", icon: "🏠", view: "properties", gradient: "from-orange-500 to-red-500" }
                  ].map((action, index) => (
                    <motion.button
                      key={action.title}
                      onClick={() => setCurrentView(action.view)}
                      className="p-4 bg-white/30 rounded-lg hover:bg-white/40 transition-all duration-200 group"
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.7 + index * 0.1 }}
                    >
                      <div className={`text-2xl mb-2 group-hover:scale-110 transition-transform duration-200`}>
                        {action.icon}
                      </div>
                      <p className="text-sm font-medium text-gray-800">{action.title}</p>
                    </motion.button>
                  ))}
                </div>
              </motion.div>
            </div>
          </motion.div>
        );
      
      case 'upload':
        return (
          <motion.div
            key="upload"
            initial="initial"
            animate="in"
            exit="out"
            variants={pageVariants}
            transition={pageTransition}
          >
            <div className="mb-8">
              <h2 className="text-3xl font-bold bg-gradient-to-r from-green-600 to-blue-600 bg-clip-text text-transparent mb-2">
                Document Upload
              </h2>
              <p className="text-gray-600">Upload and process your documents with AI-powered extraction</p>
            </div>
            
            <div className="glass-card p-8">
              <div className="mb-6">
                <label htmlFor="propertyId" className="block text-sm font-semibold text-gray-700 mb-2">
                  Property ID
                </label>
                <input
                  id="propertyId"
                  type="text"
                  value={propertyId}
                  onChange={(e) => setPropertyId(e.target.value)}
                  placeholder="Enter property ID (e.g., PROP_001)"
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                />
              </div>

              <div className="border-2 border-dashed border-gray-300 rounded-xl p-12 text-center mb-6 hover:border-gray-400 transition-colors relative">
                <input
                  type="file"
                  accept=".pdf,.xlsx,.xls,.csv"
                  onChange={(e) => setUploadFile(e.target.files[0])}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                />
                
                {uploadFile ? (
                  <div className="space-y-4">
                    <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto">
                      <span className="text-2xl">📄</span>
                    </div>
                    <div>
                      <p className="font-semibold text-gray-800">{uploadFile.name}</p>
                      <p className="text-sm text-gray-600">{formatFileSize(uploadFile.size)}</p>
                    </div>
                    <button
                      onClick={() => setUploadFile(null)}
                      className="text-red-500 hover:text-red-700 text-sm"
                    >
                      Remove file
                    </button>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto">
                      <span className="text-2xl">📤</span>
                    </div>
                    <div>
                      <p className="text-lg font-semibold text-gray-700 mb-2">
                        Drag & drop your file here
                      </p>
                      <p className="text-gray-500">or click to browse</p>
                      <p className="text-xs text-gray-400 mt-2">
                        Supported: PDF, Excel (.xlsx, .xls), CSV • Max 10MB
                      </p>
                    </div>
                  </div>
                )}
              </div>

              <motion.button
                onClick={handleUpload}
                disabled={!uploadFile || !propertyId.trim() || uploading}
                className={`w-full py-3 px-6 rounded-xl font-semibold transition-all duration-200 ${
                  !uploadFile || !propertyId.trim() || uploading
                    ? "bg-gray-200 text-gray-500 cursor-not-allowed"
                    : "bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:from-blue-700 hover:to-purple-700 shadow-lg hover:shadow-xl transform hover:scale-[1.02]"
                }`}
                whileHover={!uploading && uploadFile && propertyId.trim() ? { scale: 1.02 } : {}}
                whileTap={!uploading && uploadFile && propertyId.trim() ? { scale: 0.98 } : {}}
              >
                {uploading ? (
                  <div className="flex items-center justify-center space-x-2">
                    <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    <span>Uploading...</span>
                  </div>
                ) : (
                  "Upload Document"
                )}
              </motion.button>
            </div>
          </motion.div>
        );
      
      case 'documents':
        return (
          <motion.div
            key="documents"
            initial="initial"
            animate="in"
            exit="out"
            variants={pageVariants}
            transition={pageTransition}
          >
            <div className="mb-8 flex items-center justify-between">
              <div>
                <h2 className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent mb-2">
                  Document Library
                </h2>
                <p className="text-gray-600">Manage and analyze your uploaded documents</p>
              </div>
              <button
                onClick={() => {fetchDocuments(); setActiveView('documents');}}
                className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
              >
                Refresh
              </button>
            </div>
            
            <div className="space-y-4">
              {documents.length > 0 ? (
                documents.map((doc) => (
                  <motion.div
                    key={doc.document_id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="glass-card p-6"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                          {doc.content_type?.includes('pdf') ? (
                            <span className="text-xl">📄</span>
                          ) : doc.content_type?.includes('csv') ? (
                            <span className="text-xl">📊</span>
                          ) : (
                            <span className="text-xl">📋</span>
                          )}
                        </div>
                        <div>
                          <h3 className="font-semibold text-gray-800">{doc.original_filename}</h3>
                          <p className="text-sm text-gray-500">
                            Property: {doc.property_id} • {formatFileSize(doc.file_size)}
                          </p>
                          <p className="text-xs text-gray-400">
                            Uploaded: {new Date(doc.upload_timestamp).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                      <div className="flex space-x-2">
                        <span className={`px-3 py-1 text-xs rounded-full ${
                          doc.status === 'processed' || doc.job_status === 'completed'
                            ? 'bg-green-100 text-green-700'
                            : doc.status === 'processing' || doc.job_status === 'processing'
                            ? 'bg-yellow-100 text-yellow-700'
                            : 'bg-gray-100 text-gray-700'
                        }`}>
                          {doc.status === 'processed' || doc.job_status === 'completed'
                            ? 'Processed'
                            : doc.status === 'processing' || doc.job_status === 'processing'
                            ? 'Processing'
                            : 'Queued'}
                        </span>
                        <button className="px-3 py-1 text-xs bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors">
                          View
                        </button>
                      </div>
                    </div>
                  </motion.div>
                ))
              ) : (
                <div className="text-center py-12">
                  <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <span className="text-2xl">📚</span>
                  </div>
                  <h3 className="text-lg font-semibold text-gray-800 mb-2">No Documents Yet</h3>
                  <p className="text-gray-500 mb-4">Upload your first document to get started!</p>
                  <button 
                    onClick={() => setActiveView('upload')}
                    className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                  >
                    Upload Document
                  </button>
                </div>
              )}
            </div>
          </motion.div>
        );
      
      case 'analytics':
        return (
          <motion.div
            key="analytics"
            initial="initial"
            animate="in"
            exit="out"
            variants={pageVariants}
            transition={pageTransition}
          >
            <div className="mb-8">
              <h2 className="text-3xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent mb-2">
                Analytics Dashboard
              </h2>
              <p className="text-gray-600">Insights and analytics from your data</p>
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="glass-card p-6">
                <h3 className="font-semibold text-gray-800 mb-4">Document Processing</h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Total Documents</span>
                    <span className="font-medium">{stats.totalDocuments}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">AI Processed</span>
                    <span className="font-medium">{stats.aiProcessed}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Success Rate</span>
                    <span className="font-medium text-green-600">
                      {stats.totalDocuments > 0 
                        ? Math.round((stats.aiProcessed / stats.totalDocuments) * 100)
                        : 100}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Pending Analysis</span>
                    <span className="font-medium text-orange-600">{stats.pendingAnalysis}</span>
                  </div>
                </div>
              </div>
              
              <div className="glass-card p-6">
                <h3 className="font-semibold text-gray-800 mb-4">System Performance</h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Backend Status</span>
                    <span className={`font-medium ${
                      backendStatus === 'connected' ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {backendStatus === 'connected' ? 'Connected' : 'Disconnected'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Total Properties</span>
                    <span className="font-medium">{stats.totalProperties}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Storage Used</span>
                    <span className="font-medium text-blue-600">
                      {formatFileSize(documents.reduce((total, doc) => total + (doc.file_size || 0), 0))}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Last Updated</span>
                    <span className="font-medium text-gray-600">{new Date().toLocaleTimeString()}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Recent Activity */}
            <div className="mt-8">
              <div className="glass-card p-6">
                <h3 className="font-semibold text-gray-800 mb-4">Recent Activity</h3>
                <div className="space-y-3">
                  {documents.slice(0, 5).map((doc, index) => (
                    <div key={doc.document_id} className="flex items-center justify-between p-3 bg-white/30 rounded-lg">
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                          <span className="text-sm">📄</span>
                        </div>
                        <div>
                          <p className="font-medium text-gray-800">{doc.original_filename}</p>
                          <p className="text-sm text-gray-500">Property: {doc.property_id}</p>
                        </div>
                      </div>
                      <span className="text-sm text-gray-400">
                        {new Date(doc.upload_timestamp).toLocaleDateString()}
                      </span>
                    </div>
                  ))}
                  {documents.length === 0 && (
                    <p className="text-gray-500 text-center py-4">No recent activity</p>
                  )}
                </div>
              </div>
            </div>
          </motion.div>
        );
      
      case 'properties':
        return (
          <motion.div
            key="properties"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="glass-card p-8"
          >
            <h2 className="text-3xl font-bold bg-gradient-to-r from-orange-600 to-red-600 bg-clip-text text-transparent mb-4">
              Property Management
            </h2>
            <p className="text-gray-600 mb-6">Manage your real estate portfolio</p>
            
            <div className="text-center py-12">
              <div className="w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-gray-800 mb-2">No Properties Yet</h3>
              <p className="text-gray-500 mb-4">Start by uploading documents to automatically detect and manage properties</p>
              <button className="px-6 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors">
                Add Property
              </button>
            </div>
          </motion.div>
        );
        return (
          <motion.div
            key={currentView}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="glass-card p-8"
          >
            <h2 className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent mb-4">
              {currentView.charAt(0).toUpperCase() + currentView.slice(1)}
            </h2>
            <p className="text-gray-600">This section is under development.</p>
          </motion.div>
        );
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      {/* Animated Background Elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <motion.div
          className="absolute -top-40 -right-40 w-80 h-80 bg-gradient-to-r from-blue-400/20 to-purple-400/20 rounded-full blur-3xl"
          animate={{
            scale: [1, 1.2, 1],
            rotate: [0, 180, 360],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            ease: "linear"
          }}
        />
        <motion.div
          className="absolute -bottom-40 -left-40 w-80 h-80 bg-gradient-to-r from-green-400/20 to-blue-400/20 rounded-full blur-3xl"
          animate={{
            scale: [1.2, 1, 1.2],
            rotate: [360, 180, 0],
          }}
          transition={{
            duration: 25,
            repeat: Infinity,
            ease: "linear"
          }}
        />
      </div>

      {/* Header */}
      <motion.header
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="relative z-10 bg-white/10 backdrop-blur-lg border-b border-white/20"
      >
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">R</span>
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-800">REIMS</h1>
                <p className="text-xs text-gray-600">Real Estate Intelligence</p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-600">
                Backend: 
                <span className={`font-medium ml-1 ${
                  backendStatus === 'connected' ? 'text-green-600' : 
                  backendStatus === 'disconnected' ? 'text-red-600' : 
                  'text-yellow-600'
                }`}>
                  {backendStatus === 'connected' ? 'Connected' : 
                   backendStatus === 'disconnected' ? 'Disconnected' : 
                   'Checking...'}
                </span>
              </p>
            </div>
          </div>
        </div>
      </motion.header>
      
      {/* Navigation */}
      <SimpleNavigation currentView={currentView} onViewChange={setCurrentView} />
      
      {/* Main Content */}
      <motion.main 
        className="relative z-10 max-w-7xl mx-auto px-4 py-8"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2, duration: 0.8 }}
      >
        <AnimatePresence mode="wait">
          {renderContent()}
        </AnimatePresence>
      </motion.main>

      {/* Toast Notifications */}
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(255, 255, 255, 0.2)',
            borderRadius: '12px',
            color: '#374151',
            boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
          },
          success: {
            iconTheme: {
              primary: '#10B981',
              secondary: '#FFFFFF',
            },
          },
          error: {
            iconTheme: {
              primary: '#EF4444',
              secondary: '#FFFFFF',
            },
          },
        }}
      />
    </div>
  );
}

export default WorkingApp;