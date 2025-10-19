import React, { useState, useRef } from 'react';
import { useDocumentUpload, useDocumentStatus } from '../hooks/useDocumentUpload';

/**
 * Document Upload Component
 * 
 * Features:
 * - Drag & drop file upload
 * - File type validation (PDF, Excel, CSV)
 * - File size validation (50MB max)
 * - Upload progress tracking
 * - Processing status polling
 * - Success/error notifications
 */
export default function DocumentUpload({ propertyId, onUploadComplete }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [documentType, setDocumentType] = useState('offering_memo');
  const fileInputRef = useRef(null);

  // Upload hook
  const {
    uploadDocument,
    isUploading,
    uploadProgress,
    uploadError,
    documentId,
    status: uploadStatus,
    resetUpload,
  } = useDocumentUpload({
    onSuccess: (data) => {
      console.log('Upload successful:', data);
      // Start polling for processing status
      if (data?.data?.document_id) {
        startPolling();
      }
    },
    onError: (error) => {
      console.error('Upload failed:', error);
    },
    onProgress: (progress) => {
      console.log('Upload progress:', progress);
    },
  });

  // Status polling hook
  const {
    status: processingStatus,
    isProcessing,
    isProcessed,
    isFailed,
    metrics,
    error: processingError,
    startPolling,
    stopPolling,
  } = useDocumentStatus(documentId, {
    pollInterval: 2000, // 2 seconds
    onStatusChange: (status) => {
      console.log('Processing status:', status);
    },
    onComplete: (data) => {
      console.log('Processing complete:', data);
      if (onUploadComplete) {
        onUploadComplete(data);
      }
    },
    onError: (error) => {
      console.error('Processing failed:', error);
    },
  });

  // File selection handlers
  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const handleDrop = (event) => {
    event.preventDefault();
    setIsDragging(false);

    const file = event.dataTransfer.files[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const handleDragOver = (event) => {
    event.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleUpload = () => {
    if (!selectedFile || !propertyId) return;

    uploadDocument({
      file: selectedFile,
      propertyId,
      documentType,
    });
  };

  const handleReset = () => {
    setSelectedFile(null);
    resetUpload();
    stopPolling();
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const openFileDialog = () => {
    fileInputRef.current?.click();
  };

  // Get file icon based on type
  const getFileIcon = (file) => {
    if (!file) return null;

    if (file.type === 'application/pdf') {
      return (
        <svg className="w-12 h-12 text-red-500" fill="currentColor" viewBox="0 0 20 20">
          <path d="M4 18h12V6h-4V2H4v16zm-2 1V0h12l4 4v16H2v-1z" />
        </svg>
      );
    }

    if (file.type.includes('spreadsheet') || file.type.includes('excel') || file.type === 'text/csv') {
      return (
        <svg className="w-12 h-12 text-green-500" fill="currentColor" viewBox="0 0 20 20">
          <path d="M4 18h12V6h-4V2H4v16zm-2 1V0h12l4 4v16H2v-1z" />
        </svg>
      );
    }

    return (
      <svg className="w-12 h-12 text-gray-500" fill="currentColor" viewBox="0 0 20 20">
        <path d="M4 18h12V6h-4V2H4v16zm-2 1V0h12l4 4v16H2v-1z" />
      </svg>
    );
  };

  // Format file size
  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 max-w-2xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Upload Document
        </h2>
        <p className="text-sm text-gray-600">
          Upload financial documents (PDF, Excel, CSV). Max file size: 50MB
        </p>
      </div>

      {/* Document Type Selection */}
      {!documentId && (
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Document Type
          </label>
          <select
            value={documentType}
            onChange={(e) => setDocumentType(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={isUploading || isProcessing}
          >
            <option value="offering_memo">Offering Memorandum</option>
            <option value="rent_roll">Rent Roll</option>
            <option value="financial_statement">Financial Statement</option>
            <option value="operating_statement">Operating Statement</option>
            <option value="lease_agreement">Lease Agreement</option>
            <option value="other">Other</option>
          </select>
        </div>
      )}

      {/* Upload Area */}
      {!documentId && (
        <div>
          {/* Drag & Drop Zone */}
          <div
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            className={`
              relative border-2 border-dashed rounded-lg p-8 text-center transition-all
              ${isDragging
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-300 hover:border-gray-400'
              }
              ${selectedFile ? 'bg-gray-50' : ''}
            `}
          >
            {selectedFile ? (
              /* Selected File Display */
              <div className="space-y-4">
                <div className="flex items-center justify-center">
                  {getFileIcon(selectedFile)}
                </div>
                <div>
                  <p className="font-medium text-gray-900">{selectedFile.name}</p>
                  <p className="text-sm text-gray-500">
                    {formatFileSize(selectedFile.size)}
                  </p>
                </div>
                <button
                  onClick={() => setSelectedFile(null)}
                  className="text-sm text-red-600 hover:text-red-700 font-medium"
                >
                  Remove file
                </button>
              </div>
            ) : (
              /* Upload Instructions */
              <div className="space-y-4">
                <svg
                  className="mx-auto h-12 w-12 text-gray-400"
                  stroke="currentColor"
                  fill="none"
                  viewBox="0 0 48 48"
                >
                  <path
                    d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                    strokeWidth={2}
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
                <div>
                  <p className="text-gray-700 font-medium">
                    Drop your file here, or{' '}
                    <button
                      onClick={openFileDialog}
                      className="text-blue-600 hover:text-blue-700 font-semibold"
                    >
                      browse
                    </button>
                  </p>
                  <p className="text-sm text-gray-500 mt-1">
                    PDF, Excel (.xlsx), or CSV files up to 50MB
                  </p>
                </div>
              </div>
            )}

            {/* Hidden File Input */}
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.xlsx,.xls,.csv"
              onChange={handleFileSelect}
              className="hidden"
            />
          </div>

          {/* Upload Error */}
          {uploadError && (
            <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-3">
              <p className="text-sm text-red-700">{uploadError.message || uploadError}</p>
            </div>
          )}

          {/* Upload Button */}
          <div className="mt-6 flex gap-3">
            <button
              onClick={handleUpload}
              disabled={!selectedFile || !propertyId || isUploading}
              className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
            >
              {isUploading ? 'Uploading...' : 'Upload Document'}
            </button>

            {selectedFile && !isUploading && (
              <button
                onClick={() => setSelectedFile(null)}
                className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg font-medium hover:bg-gray-300 transition-colors"
              >
                Cancel
              </button>
            )}
          </div>

          {/* Upload Progress */}
          {isUploading && (
            <div className="mt-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">
                  Uploading...
                </span>
                <span className="text-sm font-medium text-gray-700">
                  {uploadProgress}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                ></div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Processing Status */}
      {documentId && (
        <DocumentProcessingStatus
          documentId={documentId}
          status={processingStatus}
          isProcessing={isProcessing}
          isProcessed={isProcessed}
          isFailed={isFailed}
          metrics={metrics}
          error={processingError}
          onReset={handleReset}
        />
      )}
    </div>
  );
}

/**
 * Document Processing Status Component
 */
function DocumentProcessingStatus({
  documentId,
  status,
  isProcessing,
  isProcessed,
  isFailed,
  metrics,
  error,
  onReset,
}) {
  return (
    <div className="space-y-4">
      {/* Status Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">
          Processing Status
        </h3>
        <span
          className={`
            px-3 py-1 rounded-full text-sm font-medium
            ${status === 'queued' ? 'bg-gray-100 text-gray-700' : ''}
            ${isProcessing ? 'bg-blue-100 text-blue-700' : ''}
            ${isProcessed ? 'bg-green-100 text-green-700' : ''}
            ${isFailed ? 'bg-red-100 text-red-700' : ''}
          `}
        >
          {status.toUpperCase()}
        </span>
      </div>

      {/* Document ID */}
      <div className="bg-gray-50 rounded-lg p-3">
        <p className="text-xs text-gray-500 mb-1">Document ID</p>
        <p className="text-sm font-mono text-gray-900">{documentId}</p>
      </div>

      {/* Processing Steps */}
      <div className="space-y-3">
        <ProcessingStep
          label="Upload to Storage"
          status="completed"
          icon="check"
        />
        <ProcessingStep
          label="Extract Text"
          status={isProcessing || isProcessed ? 'completed' : 'pending'}
          icon={isProcessing || isProcessed ? 'check' : 'pending'}
        />
        <ProcessingStep
          label="Extract Metrics"
          status={isProcessed ? 'completed' : isProcessing ? 'processing' : 'pending'}
          icon={isProcessed ? 'check' : isProcessing ? 'processing' : 'pending'}
        />
      </div>

      {/* Processing Spinner */}
      {isProcessing && (
        <div className="flex items-center justify-center py-4">
          <div className="animate-spin rounded-full h-8 w-8 border-4 border-blue-500 border-t-transparent"></div>
        </div>
      )}

      {/* Success Message */}
      {isProcessed && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <svg className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            <div>
              <h4 className="font-medium text-green-900">Processing Complete!</h4>
              <p className="text-sm text-green-700 mt-1">
                Document has been successfully processed and metrics have been extracted.
              </p>
            </div>
          </div>

          {/* Extracted Metrics */}
          {metrics && (
            <div className="mt-4 pt-4 border-t border-green-200">
              <h5 className="text-sm font-medium text-green-900 mb-2">
                Extracted Metrics
              </h5>
              <div className="grid grid-cols-2 gap-2">
                {Object.entries(metrics).map(([key, value]) => (
                  <div key={key} className="text-sm">
                    <span className="text-green-700">{key}:</span>{' '}
                    <span className="font-medium text-green-900">{value}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Error Message */}
      {isFailed && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <svg className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            <div>
              <h4 className="font-medium text-red-900">Processing Failed</h4>
              <p className="text-sm text-red-700 mt-1">
                {error || 'An error occurred during processing. Please try again.'}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex gap-3 pt-4">
        {isProcessed && (
          <button
            onClick={onReset}
            className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
          >
            Upload Another Document
          </button>
        )}

        {isFailed && (
          <button
            onClick={onReset}
            className="flex-1 px-6 py-3 bg-red-600 text-white rounded-lg font-medium hover:bg-red-700 transition-colors"
          >
            Try Again
          </button>
        )}
      </div>
    </div>
  );
}

/**
 * Processing Step Component
 */
function ProcessingStep({ label, status, icon }) {
  const getIcon = () => {
    if (icon === 'check') {
      return (
        <svg className="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
        </svg>
      );
    }

    if (icon === 'processing') {
      return (
        <div className="animate-spin rounded-full h-5 w-5 border-2 border-blue-600 border-t-transparent"></div>
      );
    }

    return (
      <div className="w-5 h-5 rounded-full border-2 border-gray-300"></div>
    );
  };

  return (
    <div className="flex items-center gap-3">
      {getIcon()}
      <span
        className={`
          text-sm font-medium
          ${status === 'completed' ? 'text-gray-900' : 'text-gray-500'}
        `}
      >
        {label}
      </span>
    </div>
  );
}
