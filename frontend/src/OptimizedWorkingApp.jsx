import React, { useState, useEffect, useCallback, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Toaster, toast } from "react-hot-toast";
import { 
  API_CONFIG, 
  apiGet, 
  apiUpload, 
  checkBackendHealth, 
  preloadCriticalData 
} from "./config/api";

// Import our modern components
import { Navigation } from "./components/Navigation";
import { ModernHeader } from "./components/ModernHeader";
import { LoadingSpinner } from "./components/LoadingSpinner";

// Performance optimized WorkingApp component
function WorkingApp() {
  // State management with performance considerations
  const [currentView, setCurrentView] = useState('dashboard');
  const [isLoading, setIsLoading] = useState(true);
  const [backendStatus, setBackendStatus] = useState('checking');
  const [documents, setDocuments] = useState([]);
  const [uploadFile, setUploadFile] = useState(null);
  const [propertyId, setPropertyId] = useState('');
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  
  // Computed stats with memoization
  const stats = useMemo(() => {
    const totalDocs = documents.length;
    const processedDocs = documents.filter(doc => 
      doc.status === 'processed' || doc.processing_status === 'completed'
    ).length;
    
    return {
      totalDocuments: totalDocs,
      aiProcessed: processedDocs,
      totalProperties: 15, // Mock data
      pendingAnalysis: totalDocs - processedDocs
    };
  }, [documents]);

  // Optimized file size formatter
  const formatFileSize = useCallback((bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }, []);

  // Optimized upload handler with progress
  const handleUpload = useCallback(async () => {
    if (!uploadFile || !propertyId.trim()) {
      toast.error('Please select a file and enter a property ID');
      return;
    }

    setUploading(true);
    setUploadProgress(0);
    
    try {
      const formData = new FormData();
      formData.append('file', uploadFile);
      formData.append('property_id', propertyId);

      const response = await apiUpload(
        API_CONFIG.ENDPOINTS.DOCUMENTS_UPLOAD,
        formData,
        (progress) => setUploadProgress(progress)
      );

      // Add new document to state
      const newDoc = {
        document_id: response.data.document_id,
        original_filename: response.data.filename,
        property_id: response.data.property_id,
        file_size: response.data.file_size,
        upload_timestamp: new Date().toISOString(),
        status: 'uploaded',
        processing_status: 'pending'
      };

      setDocuments(prev => [newDoc, ...prev]);
      
      // Reset form
      setUploadFile(null);
      setPropertyId('');
      setUploadProgress(0);
      
      toast.success(`File uploaded successfully! (${formatFileSize(response.data.file_size)})`);
      
    } catch (error) {
      console.error('Upload failed:', error);
      toast.error(`Upload failed: ${error.message}`);
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  }, [uploadFile, propertyId, formatFileSize]);

  // Optimized document fetcher
  const fetchDocuments = useCallback(async () => {
    try {
      const response = await apiGet(API_CONFIG.ENDPOINTS.DOCUMENTS_LIST, {
        limit: 50,
        offset: 0
      });
      
      if (response.data.documents) {
        setDocuments(response.data.documents);
      }
    } catch (error) {
      console.error('Failed to fetch documents:', error);
      toast.error('Failed to load documents');
    }
  }, []);

  // Backend health checker
  const checkHealth = useCallback(async () => {
    try {
      const health = await checkBackendHealth();
      
      if (health.healthy) {
        setBackendStatus('connected');
        return true;
      } else {
        setBackendStatus('disconnected');
        return false;
      }
    } catch (error) {
      console.error('Health check failed:', error);
      setBackendStatus('error');
      return false;
    }
  }, []);

  // Optimized initialization
  useEffect(() => {
    const initializeApp = async () => {
      setIsLoading(true);
      
      try {
        // Check backend health first
        const isHealthy = await checkHealth();
        
        if (isHealthy) {
          // Preload critical data
          await preloadCriticalData();
          
          // Fetch documents
          await fetchDocuments();
        }
        
      } catch (error) {
        console.error('App initialization failed:', error);
        toast.error('Failed to initialize application');
      } finally {
        setIsLoading(false);
      }
    };

    initializeApp();
  }, [checkHealth, fetchDocuments]);

  // Periodic health checks
  useEffect(() => {
    const healthCheckInterval = setInterval(checkHealth, 30000); // Every 30 seconds
    return () => clearInterval(healthCheckInterval);
  }, [checkHealth]);

  // Render performance indicator
  const renderPerformanceInfo = () => (
    <div className="fixed bottom-4 right-4 text-xs text-gray-400 bg-black/20 px-2 py-1 rounded">
      {backendStatus === 'connected' ? '🟢' : backendStatus === 'disconnected' ? '🟡' : '🔴'} 
      {backendStatus} | {documents.length} docs | React {React.version}
    </div>
  );

  // Main dashboard view
  const renderDashboard = () => (
    <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6 p-6">
      {/* Stats Cards */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="col-span-full grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6"
      >
        {[
          { label: 'Total Documents', value: stats.totalDocuments, color: 'blue' },
          { label: 'AI Processed', value: stats.aiProcessed, color: 'green' },
          { label: 'Properties', value: stats.totalProperties, color: 'purple' },
          { label: 'Pending Analysis', value: stats.pendingAnalysis, color: 'orange' }
        ].map((stat, index) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.1 }}
            className={`bg-gradient-to-r from-${stat.color}-500 to-${stat.color}-600 text-white p-6 rounded-xl shadow-lg`}
          >
            <div className="text-2xl font-bold">{stat.value}</div>
            <div className="text-sm opacity-90">{stat.label}</div>
          </motion.div>
        ))}
      </motion.div>

      {/* Upload Section */}
      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        className="lg:col-span-1 xl:col-span-1"
      >
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h3 className="text-xl font-bold text-gray-800 mb-4">📄 Upload Document</h3>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Property ID
              </label>
              <input
                type="text"
                value={propertyId}
                onChange={(e) => setPropertyId(e.target.value)}
                placeholder="Enter property ID"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select File
              </label>
              <input
                type="file"
                accept=".pdf,.xlsx,.xls,.csv"
                onChange={(e) => setUploadFile(e.target.files[0])}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              />
              {uploadFile && (
                <div className="mt-2 text-sm text-gray-600">
                  Selected: {uploadFile.name} ({formatFileSize(uploadFile.size)})
                </div>
              )}
            </div>

            {uploading && (
              <div>
                <div className="flex justify-between text-sm text-gray-600 mb-1">
                  <span>Uploading...</span>
                  <span>{Math.round(uploadProgress)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${uploadProgress}%` }}
                  ></div>
                </div>
              </div>
            )}

            <button
              onClick={handleUpload}
              disabled={!uploadFile || !propertyId.trim() || uploading}
              className={`w-full py-2 px-4 rounded-lg font-medium transition-all ${
                !uploadFile || !propertyId.trim() || uploading
                  ? 'bg-gray-200 text-gray-500 cursor-not-allowed'
                  : 'bg-blue-600 text-white hover:bg-blue-700 hover:shadow-lg transform hover:scale-[1.02]'
              }`}
            >
              {uploading ? 'Uploading...' : 'Upload Document'}
            </button>
          </div>
        </div>
      </motion.div>

      {/* Recent Documents */}
      <motion.div
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        className="lg:col-span-1 xl:col-span-2"
      >
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-xl font-bold text-gray-800">📋 Recent Documents</h3>
            <button
              onClick={fetchDocuments}
              className="text-blue-600 hover:text-blue-800 text-sm font-medium"
            >
              Refresh
            </button>
          </div>

          <div className="space-y-3 max-h-96 overflow-y-auto">
            <AnimatePresence>
              {documents.slice(0, 10).map((doc, index) => (
                <motion.div
                  key={doc.document_id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  transition={{ delay: index * 0.05 }}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-gray-900 truncate">
                      {doc.original_filename}
                    </div>
                    <div className="text-sm text-gray-500">
                      {doc.property_id} • {formatFileSize(doc.file_size)}
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      doc.status === 'processed' 
                        ? 'bg-green-100 text-green-800'
                        : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {doc.status}
                    </span>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>

            {documents.length === 0 && (
              <div className="text-center text-gray-500 py-8">
                No documents uploaded yet
              </div>
            )}
          </div>
        </div>
      </motion.div>
    </div>
  );

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <LoadingSpinner message="Initializing REIMS..." />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#363636',
            color: '#fff',
          },
        }}
      />

      <ModernHeader 
        backendStatus={backendStatus}
        documentCount={documents.length}
      />

      <Navigation 
        currentView={currentView} 
        onViewChange={setCurrentView}
      />

      <main className="container mx-auto">
        <AnimatePresence mode="wait">
          {currentView === 'dashboard' && (
            <motion.div
              key="dashboard"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              {renderDashboard()}
            </motion.div>
          )}
          
          {currentView === 'documents' && (
            <motion.div
              key="documents"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="p-6"
            >
              <div className="bg-white rounded-xl shadow-lg p-6">
                <h2 className="text-2xl font-bold text-gray-800 mb-4">Document Management</h2>
                <p className="text-gray-600">Full document management interface coming soon...</p>
              </div>
            </motion.div>
          )}

          {currentView === 'analytics' && (
            <motion.div
              key="analytics"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="p-6"
            >
              <div className="bg-white rounded-xl shadow-lg p-6">
                <h2 className="text-2xl font-bold text-gray-800 mb-4">Analytics Dashboard</h2>
                <p className="text-gray-600">Advanced analytics interface coming soon...</p>
              </div>
            </motion.div>
          )}

          {currentView === 'properties' && (
            <motion.div
              key="properties"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="p-6"
            >
              <div className="bg-white rounded-xl shadow-lg p-6">
                <h2 className="text-2xl font-bold text-gray-800 mb-4">Property Management</h2>
                <p className="text-gray-600">Property management interface coming soon...</p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {renderPerformanceInfo()}
    </div>
  );
}

export default React.memo(WorkingApp);