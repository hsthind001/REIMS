import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  DocumentIcon,
  ChartBarIcon,
  CpuChipIcon,
  ClockIcon,
  ArrowPathIcon,
  EyeIcon,
  PlayIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon
} from "@heroicons/react/24/outline";
import { LoadingSpinner } from "./LoadingSpinner";
import { API_CONFIG, buildApiUrl } from "../config/api";

export function DocumentList() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedDoc, setSelectedDoc] = useState(null);
  const [processedData, setProcessedData] = useState(null);
  const [processingStatus, setProcessingStatus] = useState({});
  const [loadingData, setLoadingData] = useState(false);

  const fetchDocuments = async () => {
    try {
      setLoading(true);
      const response = await fetch(buildApiUrl(API_CONFIG.ENDPOINTS.DOCUMENTS_LIST));
      
      if (!response.ok) {
        throw new Error("Failed to fetch documents");
      }
      
      const data = await response.json();
      setDocuments(data.documents);
      
      // Fetch processing status for each document
      for (const doc of data.documents) {
        fetchProcessingStatus(doc.document_id);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchProcessingStatus = async (documentId) => {
    try {
      const response = await fetch(buildApiUrl(API_CONFIG.ENDPOINTS.AI_PROCESS_STATUS(documentId)));
      
      if (response.ok) {
        const data = await response.json();
        setProcessingStatus(prev => ({
          ...prev,
          [documentId]: data
        }));
      }
    } catch (err) {
      console.log(`Could not fetch processing status for ${documentId}:`, err.message);
    }
  };

  const fetchProcessedData = async (documentId) => {
    try {
      setLoadingData(true);
      setProcessedData(null);
      setSelectedDoc(documentId);
      
      // First try to get AI processed data
      const aiResponse = await fetch(buildApiUrl(API_CONFIG.ENDPOINTS.AI_PROCESSED_DATA(documentId)));
      
      if (aiResponse.ok) {
        const aiData = await aiResponse.json();
        setProcessedData({
          source: "ai",
          ...aiData
        });
        return;
      }
      
      // Fallback to basic processed data
      const basicResponse = await fetch(buildApiUrl(API_CONFIG.ENDPOINTS.DOCUMENTS_PROCESSED(documentId)));
      
      if (basicResponse.ok) {
        const basicData = await basicResponse.json();
        setProcessedData({
          source: "basic",
          ...basicData
        });
      } else {
        setProcessedData({ error: "Processed data not available" });
      }
    } catch (err) {
      setProcessedData({ error: err.message });
    } finally {
      setLoadingData(false);
    }
  };

  const startAIProcessing = async (documentId) => {
    try {
      const response = await fetch(buildApiUrl(`/ai/process/${documentId}`), {
        method: 'POST'
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log("AI processing started:", data);
        
        // Update processing status
        setProcessingStatus(prev => ({
          ...prev,
          [documentId]: {
            status: "processing",
            message: "AI processing started"
          }
        }));
        
        // Poll for updates
        setTimeout(() => fetchProcessingStatus(documentId), 3000);
      }
    } catch (err) {
      console.error("Error starting AI processing:", err);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (isoString) => {
    return new Date(isoString).toLocaleString();
  };

  const getStatusConfig = (doc) => {
    const docId = doc.document_id;
    const aiStatus = processingStatus[docId];
    
    if (aiStatus) {
      switch (aiStatus.status) {
        case 'success': 
          return {
            color: 'from-green-500 to-emerald-500',
            bgColor: 'bg-green-50',
            textColor: 'text-green-700',
            icon: CheckCircleIcon
          };
        case 'processing': 
          return {
            color: 'from-yellow-500 to-orange-500',
            bgColor: 'bg-yellow-50',
            textColor: 'text-yellow-700',
            icon: CpuChipIcon
          };
        case 'error': 
          return {
            color: 'from-red-500 to-pink-500',
            bgColor: 'bg-red-50',
            textColor: 'text-red-700',
            icon: ExclamationTriangleIcon
          };
        default: 
          return {
            color: 'from-gray-500 to-slate-500',
            bgColor: 'bg-gray-50',
            textColor: 'text-gray-700',
            icon: InformationCircleIcon
          };
      }
    }
    
    // Fallback to document status
    switch (doc.status) {
      case 'uploaded': 
        return {
          color: 'from-blue-500 to-cyan-500',
          bgColor: 'bg-blue-50',
          textColor: 'text-blue-700',
          icon: DocumentIcon
        };
      case 'processed': 
        return {
          color: 'from-green-500 to-emerald-500',
          bgColor: 'bg-green-50',
          textColor: 'text-green-700',
          icon: CheckCircleIcon
        };
      default: 
        return {
          color: 'from-gray-500 to-slate-500',
          bgColor: 'bg-gray-50',
          textColor: 'text-gray-700',
          icon: InformationCircleIcon
        };
    }
  };

  const getDisplayStatus = (doc) => {
    const docId = doc.document_id;
    const aiStatus = processingStatus[docId];
    
    if (aiStatus && aiStatus.status !== 'not_processed') {
      return aiStatus.status === 'success' ? 'AI Processed' : 
             aiStatus.status === 'processing' ? 'AI Processing' :
             aiStatus.status === 'error' ? 'AI Error' : aiStatus.status;
    }
    
    return doc.status.charAt(0).toUpperCase() + doc.status.slice(1);
  };

  if (loading) {
    return <LoadingSpinner message="Loading documents..." />;
  }

  if (error) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-card p-8 text-center"
      >
        <ExclamationTriangleIcon className="w-12 h-12 text-red-500 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-red-800 mb-2">Error Loading Documents</h3>
        <p className="text-red-600 mb-4">{error}</p>
        <motion.button 
          onClick={fetchDocuments}
          className="px-6 py-2 bg-red-100 text-red-700 rounded-xl hover:bg-red-200 transition-colors"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <ArrowPathIcon className="w-4 h-4 inline mr-2" />
          Retry
        </motion.button>
      </motion.div>
    );
  }

  return (
    <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
      {/* Document List */}
      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        className="glass-card"
      >
        <div className="p-6 border-b border-white/10">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <DocumentIcon className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-gray-800">Document Library</h3>
                <p className="text-sm text-gray-600">{documents.length} documents uploaded</p>
              </div>
            </div>
            <motion.button 
              onClick={fetchDocuments}
              className="p-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors"
              whileHover={{ scale: 1.05, rotate: 180 }}
              whileTap={{ scale: 0.95 }}
            >
              <ArrowPathIcon className="w-5 h-5" />
            </motion.button>
          </div>
        </div>
        
        {documents.length === 0 ? (
          <div className="p-12 text-center">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2 }}
              className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4"
            >
              <DocumentIcon className="w-10 h-10 text-gray-400" />
            </motion.div>
            <p className="text-gray-500 text-lg">No documents uploaded yet</p>
            <p className="text-gray-400 text-sm mt-2">Upload your first document to get started</p>
          </div>
        ) : (
          <div className="divide-y divide-white/10">
            <AnimatePresence>
              {documents.map((doc, index) => {
                const statusConfig = getStatusConfig(doc);
                const StatusIcon = statusConfig.icon;
                
                return (
                  <motion.div 
                    key={doc.document_id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="p-6 hover:bg-white/5 transition-all duration-200 cursor-pointer"
                    onClick={() => fetchProcessedData(doc.document_id)}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-start space-x-4 flex-1">
                        <div className={`p-3 ${statusConfig.bgColor} rounded-xl`}>
                          <DocumentIcon className={`w-6 h-6 ${statusConfig.textColor}`} />
                        </div>
                        
                        <div className="flex-1 min-w-0">
                          <h4 className="font-semibold text-gray-800 truncate mb-1">
                            {doc.original_filename}
                          </h4>
                          <div className="space-y-1">
                            <div className="flex items-center space-x-4 text-xs text-gray-500">
                              <span className="flex items-center space-x-1">
                                <span className="font-medium">Property:</span>
                                <span>{doc.property_id}</span>
                              </span>
                              <span className="flex items-center space-x-1">
                                <span className="font-medium">Size:</span>
                                <span>{formatFileSize(doc.file_size)}</span>
                              </span>
                            </div>
                            <div className="flex items-center space-x-1 text-xs text-gray-400">
                              <ClockIcon className="w-3 h-3" />
                              <span>{formatDate(doc.upload_timestamp)}</span>
                            </div>
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex flex-col items-end space-y-2 ml-4">
                        <div className="flex items-center space-x-2">
                          <StatusIcon className={`w-4 h-4 ${statusConfig.textColor}`} />
                          <span className={`px-3 py-1 text-xs font-medium rounded-full bg-gradient-to-r ${statusConfig.color} text-white`}>
                            {getDisplayStatus(doc)}
                          </span>
                        </div>
                        
                        <div className="flex space-x-1">
                          <motion.button
                            onClick={(e) => {
                              e.stopPropagation();
                              fetchProcessedData(doc.document_id);
                            }}
                            className="px-3 py-1 text-xs bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors flex items-center space-x-1"
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                          >
                            <EyeIcon className="w-3 h-3" />
                            <span>View</span>
                          </motion.button>
                          
                          {processingStatus[doc.document_id]?.status !== 'success' && 
                           processingStatus[doc.document_id]?.status !== 'processing' && (
                            <motion.button
                              onClick={(e) => {
                                e.stopPropagation();
                                startAIProcessing(doc.document_id);
                              }}
                              className="px-3 py-1 text-xs bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition-colors flex items-center space-x-1"
                              whileHover={{ scale: 1.05 }}
                              whileTap={{ scale: 0.95 }}
                            >
                              <PlayIcon className="w-3 h-3" />
                              <span>AI Process</span>
                            </motion.button>
                          )}
                        </div>
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </AnimatePresence>
          </div>
        )}
      </motion.div>

      {/* Processed Data Panel */}
      <motion.div
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.2 }}
        className="glass-card"
      >
        <div className="p-6 border-b border-white/10">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-pink-600 rounded-lg flex items-center justify-center">
              <ChartBarIcon className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-gray-800">Processed Data</h3>
              <p className="text-sm text-gray-600">
                {selectedDoc ? 'Viewing document analysis' : 'Select a document to view data'}
              </p>
            </div>
          </div>
        </div>
        
        {!selectedDoc ? (
          <div className="p-12 text-center">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.4 }}
              className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4"
            >
              <ChartBarIcon className="w-10 h-10 text-gray-400" />
            </motion.div>
            <p className="text-gray-500 text-lg">No document selected</p>
            <p className="text-gray-400 text-sm mt-2">Click on a document to view its processed data</p>
          </div>
        ) : loadingData ? (
          <LoadingSpinner message="Loading processed data..." />
        ) : processedData?.error ? (
          <div className="p-8 text-center">
            <ExclamationTriangleIcon className="w-12 h-12 text-orange-500 mx-auto mb-4" />
            <p className="text-orange-600 font-medium">{processedData.error}</p>
          </div>
        ) : processedData ? (
          <div className="p-6 max-h-[600px] overflow-y-auto">
            {processedData.source === "ai" ? (
              // AI Processed Data View
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="space-y-6"
              >
                <div className="flex items-center justify-between">
                  <h4 className="text-lg font-bold text-gray-800">AI Analysis Results</h4>
                  <span className="px-3 py-1 text-xs bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-full">
                    AI Processed
                  </span>
                </div>
                
                {processedData.document_type && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-white/50 backdrop-blur-sm rounded-xl p-4 border border-white/20"
                  >
                    <h5 className="font-semibold text-gray-700 mb-2">Document Type</h5>
                    <div className="flex items-center justify-between">
                      <p className="text-gray-800 font-medium">{processedData.document_type}</p>
                      {processedData.confidence_score && (
                        <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full">
                          {Math.round(processedData.confidence_score * 100)}% confidence
                        </span>
                      )}
                    </div>
                  </motion.div>
                )}
                
                {processedData.extracted_data?.financial_metrics && 
                 Object.keys(processedData.extracted_data.financial_metrics).length > 0 && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    className="bg-white/50 backdrop-blur-sm rounded-xl p-4 border border-white/20"
                  >
                    <h5 className="font-semibold text-gray-700 mb-3">Financial Data</h5>
                    <div className="grid grid-cols-1 gap-3">
                      {Object.entries(processedData.extracted_data.financial_metrics).map(([key, value], index) => (
                        <motion.div
                          key={key}
                          initial={{ opacity: 0, x: -10 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: index * 0.05 }}
                          className="flex justify-between items-center py-2 border-b border-gray-200 last:border-b-0"
                        >
                          <span className="text-gray-600 capitalize font-medium">
                            {key.replace('_', ' ')}:
                          </span>
                          <span className="font-bold text-gray-800">
                            {typeof value === 'object' && value.primary_value 
                              ? `$${value.primary_value.toLocaleString()} ${value.currency || ''}`
                              : JSON.stringify(value)
                            }
                          </span>
                        </motion.div>
                      ))}
                    </div>
                  </motion.div>
                )}
                
                {processedData.extracted_data?.property_details && 
                 Object.keys(processedData.extracted_data.property_details).length > 0 && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="bg-white/50 backdrop-blur-sm rounded-xl p-4 border border-white/20"
                  >
                    <h5 className="font-semibold text-gray-700 mb-3">Property Details</h5>
                    <div className="grid grid-cols-1 gap-3">
                      {Object.entries(processedData.extracted_data.property_details).map(([key, value], index) => (
                        <motion.div
                          key={key}
                          initial={{ opacity: 0, x: -10 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: index * 0.05 }}
                          className="flex justify-between items-start py-2 border-b border-gray-200 last:border-b-0"
                        >
                          <span className="text-gray-600 capitalize font-medium">
                            {key.replace('_', ' ')}:
                          </span>
                          <span className="font-medium text-gray-800 text-right max-w-xs truncate">
                            {typeof value === 'object' 
                              ? JSON.stringify(value).substring(0, 50) + (JSON.stringify(value).length > 50 ? '...' : '')
                              : String(value)
                            }
                          </span>
                        </motion.div>
                      ))}
                    </div>
                  </motion.div>
                )}
                
                {processedData.insights?.key_findings && 
                 processedData.insights.key_findings.length > 0 && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 }}
                    className="bg-white/50 backdrop-blur-sm rounded-xl p-4 border border-white/20"
                  >
                    <h5 className="font-semibold text-gray-700 mb-3">Key Insights</h5>
                    <ul className="space-y-2">
                      {processedData.insights.key_findings.map((finding, index) => (
                        <motion.li
                          key={index}
                          initial={{ opacity: 0, x: -10 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: index * 0.1 }}
                          className="flex items-start space-x-2 text-gray-700"
                        >
                          <div className="w-1.5 h-1.5 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                          <span className="text-sm">{finding}</span>
                        </motion.li>
                      ))}
                    </ul>
                  </motion.div>
                )}
                
                {processedData.processing_time_seconds && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.4 }}
                    className="pt-4 border-t border-gray-200 text-center"
                  >
                    <p className="text-xs text-gray-500 flex items-center justify-center space-x-1">
                      <ClockIcon className="w-3 h-3" />
                      <span>Processing time: {processedData.processing_time_seconds.toFixed(2)}s</span>
                    </p>
                  </motion.div>
                )}
              </motion.div>
            ) : (
              // Basic Processed Data View
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="space-y-6"
              >
                {/* Similar structure but with basic data styling */}
                <div className="space-y-4">
                  <div className="bg-white/50 backdrop-blur-sm rounded-xl p-4 border border-white/20">
                    <h4 className="font-semibold text-gray-800 mb-2">Processing Status</h4>
                    <span className="px-3 py-1 text-xs bg-blue-100 text-blue-700 rounded-full">
                      {processedData.status}
                    </span>
                  </div>
                  
                  {processedData.type && (
                    <div className="bg-white/50 backdrop-blur-sm rounded-xl p-4 border border-white/20">
                      <h4 className="font-semibold text-gray-800 mb-2">File Type</h4>
                      <p className="text-gray-700 font-medium">{processedData.type.toUpperCase()}</p>
                    </div>
                  )}
                  
                  {processedData.analysis && (
                    <div className="bg-white/50 backdrop-blur-sm rounded-xl p-4 border border-white/20">
                      <h4 className="font-semibold text-gray-800 mb-3">Analysis Summary</h4>
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        {processedData.analysis.row_count && (
                          <div className="flex justify-between">
                            <span className="text-gray-600">Rows:</span>
                            <span className="font-medium">{processedData.analysis.row_count}</span>
                          </div>
                        )}
                        {processedData.analysis.column_count && (
                          <div className="flex justify-between">
                            <span className="text-gray-600">Columns:</span>
                            <span className="font-medium">{processedData.analysis.column_count}</span>
                          </div>
                        )}
                        {processedData.analysis.page_count && (
                          <div className="flex justify-between">
                            <span className="text-gray-600">Pages:</span>
                            <span className="font-medium">{processedData.analysis.page_count}</span>
                          </div>
                        )}
                        {processedData.analysis.total_words && (
                          <div className="flex justify-between">
                            <span className="text-gray-600">Words:</span>
                            <span className="font-medium">{processedData.analysis.total_words}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                  
                  {processedData.sample_data && (
                    <div className="bg-white/50 backdrop-blur-sm rounded-xl p-4 border border-white/20">
                      <h4 className="font-semibold text-gray-800 mb-3">Sample Data</h4>
                      <div className="bg-gray-50 rounded-lg p-3 max-h-40 overflow-auto">
                        <pre className="text-xs text-gray-600 whitespace-pre-wrap">
                          {JSON.stringify(processedData.sample_data, null, 2)}
                        </pre>
                      </div>
                    </div>
                  )}
                </div>
              </motion.div>
            )}
          </div>
        ) : null}
      </motion.div>
    </div>
  );
}