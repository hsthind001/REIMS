import React, { useState, useCallback, useEffect } from 'react';
import { useMutation } from './useMutation';
import api from '../api';

/**
 * Custom hook for uploading documents with progress tracking
 * 
 * @param {Object} options - Hook configuration options
 * @param {Function} options.onSuccess - Callback on successful upload
 * @param {Function} options.onError - Callback on upload error
 * @param {Function} options.onProgress - Callback for upload progress (0-100)
 * 
 * @returns {Object} Upload state and functions
 */
export function useDocumentUpload(options = {}) {
  const {
    onSuccess,
    onError,
    onProgress,
  } = options;

  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadedFile, setUploadedFile] = useState(null);

  // Upload mutation
  const {
    mutate: uploadDocument,
    isLoading: isUploading,
    error: uploadError,
    data: uploadResponse,
    reset,
  } = useMutation(
    async ({ file, propertyId, documentType }) => {
      // Validate file
      if (!file) {
        throw new Error('No file selected');
      }

      // Validate file type
      const allowedTypes = [
        'application/pdf',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'text/csv',
      ];

      if (!allowedTypes.includes(file.type)) {
        throw new Error('Invalid file type. Only PDF, Excel, and CSV files are allowed.');
      }

      // Validate file size (50MB max)
      const maxSize = 50 * 1024 * 1024; // 50MB
      if (file.size > maxSize) {
        throw new Error('File size exceeds 50MB limit');
      }

      // Create FormData
      const formData = new FormData();
      formData.append('file', file);
      formData.append('property_id', propertyId);
      if (documentType) {
        formData.append('document_type', documentType);
      }

      // Upload with progress tracking
      try {
        const response = await uploadWithProgress(
          '/api/documents/upload',
          formData,
          (progress) => {
            setUploadProgress(progress);
            if (onProgress) {
              onProgress(progress);
            }
          }
        );

        setUploadedFile(file);
        return response;
      } catch (error) {
        setUploadProgress(0);
        throw error;
      }
    },
    {
      onSuccess: (data) => {
        setUploadProgress(100);
        if (onSuccess) {
          onSuccess(data, uploadedFile);
        }
      },
      onError: (error) => {
        setUploadProgress(0);
        if (onError) {
          onError(error);
        }
      },
    }
  );

  // Reset upload state
  const resetUpload = useCallback(() => {
    setUploadProgress(0);
    setUploadedFile(null);
    reset();
  }, [reset]);

  return {
    uploadDocument,
    isUploading,
    uploadProgress,
    uploadError,
    uploadResponse,
    uploadedFile,
    documentId: uploadResponse?.data?.document_id,
    status: uploadResponse?.data?.status,
    resetUpload,
  };
}

/**
 * Upload file with progress tracking
 */
async function uploadWithProgress(url, formData, onProgress) {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();

    // Track upload progress
    xhr.upload.addEventListener('progress', (event) => {
      if (event.lengthComputable) {
        const percentComplete = Math.round((event.loaded / event.total) * 100);
        onProgress(percentComplete);
      }
    });

    // Handle completion
    xhr.addEventListener('load', () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          const response = JSON.parse(xhr.responseText);
          resolve(response);
        } catch (error) {
          reject(new Error('Invalid response format'));
        }
      } else {
        try {
          const error = JSON.parse(xhr.responseText);
          reject(new Error(error.message || 'Upload failed'));
        } catch {
          reject(new Error(`Upload failed with status ${xhr.status}`));
        }
      }
    });

    // Handle errors
    xhr.addEventListener('error', () => {
      reject(new Error('Network error during upload'));
    });

    xhr.addEventListener('abort', () => {
      reject(new Error('Upload cancelled'));
    });

    // Send request
    const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8001';
    xhr.open('POST', `${baseURL}${url}`);
    
    // Add auth token if available
    const token = localStorage.getItem('auth_token');
    if (token) {
      xhr.setRequestHeader('Authorization', `Bearer ${token}`);
    }

    xhr.send(formData);
  });
}

/**
 * Hook for tracking document processing status with polling
 * 
 * @param {string} documentId - Document ID to track
 * @param {Object} options - Hook configuration options
 * @param {number} options.pollInterval - Polling interval in ms (default: 2000)
 * @param {Function} options.onStatusChange - Callback when status changes
 * @param {Function} options.onComplete - Callback when processing completes
 * @param {Function} options.onError - Callback on processing error
 * 
 * @returns {Object} Status tracking state
 */
export function useDocumentStatus(documentId, options = {}) {
  const {
    pollInterval = 2000, // 2 seconds
    onStatusChange,
    onComplete,
    onError: onErrorCallback,
  } = options;

  const [status, setStatus] = useState('queued');
  const [isPolling, setIsPolling] = useState(false);
  const [metrics, setMetrics] = useState(null);
  const [error, setError] = useState(null);

  // Start polling
  const startPolling = useCallback(() => {
    if (!documentId || isPolling) return;

    setIsPolling(true);
    setError(null);

    const pollStatus = async () => {
      try {
        const response = await api.get(`/api/documents/${documentId}/status`);
        const data = response.data || response;

        const newStatus = data.status;
        setStatus(newStatus);

        // Call status change callback
        if (onStatusChange) {
          onStatusChange(newStatus, data);
        }

        // Check if processing is complete
        if (newStatus === 'processed' || newStatus === 'completed') {
          setIsPolling(false);
          setMetrics(data.metrics || null);
          
          if (onComplete) {
            onComplete(data);
          }
          return true; // Stop polling
        }

        // Check if processing failed
        if (newStatus === 'failed' || newStatus === 'error') {
          setIsPolling(false);
          const errorMsg = data.error || 'Processing failed';
          setError(errorMsg);
          
          if (onErrorCallback) {
            onErrorCallback(new Error(errorMsg));
          }
          return true; // Stop polling
        }

        return false; // Continue polling
      } catch (err) {
        console.error('Error polling document status:', err);
        setError(err.message || 'Failed to check status');
        setIsPolling(false);
        
        if (onErrorCallback) {
          onErrorCallback(err);
        }
        return true; // Stop polling on error
      }
    };

    // Initial poll
    pollStatus().then((shouldStop) => {
      if (shouldStop) return;

      // Set up interval for subsequent polls
      const intervalId = setInterval(async () => {
        const shouldStop = await pollStatus();
        if (shouldStop) {
          clearInterval(intervalId);
        }
      }, pollInterval);

      // Cleanup on unmount
      return () => clearInterval(intervalId);
    });
  }, [documentId, isPolling, pollInterval, onStatusChange, onComplete, onErrorCallback]);

  // Stop polling
  const stopPolling = useCallback(() => {
    setIsPolling(false);
  }, []);

  // Reset status
  const reset = useCallback(() => {
    setStatus('queued');
    setIsPolling(false);
    setMetrics(null);
    setError(null);
  }, []);

  return {
    status,
    isPolling,
    metrics,
    error,
    isQueued: status === 'queued',
    isProcessing: status === 'processing',
    isProcessed: status === 'processed' || status === 'completed',
    isFailed: status === 'failed' || status === 'error',
    startPolling,
    stopPolling,
    reset,
  };
}

/**
 * Hook for batch document upload
 */
export function useBatchDocumentUpload(options = {}) {
  const [uploads, setUploads] = useState([]);
  const [overallProgress, setOverallProgress] = useState(0);

  const addUpload = useCallback((file, propertyId, documentType) => {
    const uploadId = `upload-${Date.now()}-${Math.random()}`;
    
    setUploads((prev) => [
      ...prev,
      {
        id: uploadId,
        file,
        propertyId,
        documentType,
        status: 'pending',
        progress: 0,
        error: null,
        documentId: null,
      },
    ]);

    return uploadId;
  }, []);

  const updateUpload = useCallback((uploadId, updates) => {
    setUploads((prev) =>
      prev.map((upload) =>
        upload.id === uploadId ? { ...upload, ...updates } : upload
      )
    );
  }, []);

  const removeUpload = useCallback((uploadId) => {
    setUploads((prev) => prev.filter((upload) => upload.id !== uploadId));
  }, []);

  const clearCompleted = useCallback(() => {
    setUploads((prev) =>
      prev.filter((upload) => upload.status !== 'completed' && upload.status !== 'failed')
    );
  }, []);

  // Calculate overall progress
  useEffect(() => {
    if (uploads.length === 0) {
      setOverallProgress(0);
      return;
    }

    const totalProgress = uploads.reduce((sum, upload) => sum + upload.progress, 0);
    setOverallProgress(Math.round(totalProgress / uploads.length));
  }, [uploads]);

  return {
    uploads,
    overallProgress,
    addUpload,
    updateUpload,
    removeUpload,
    clearCompleted,
    totalUploads: uploads.length,
    completedUploads: uploads.filter((u) => u.status === 'completed').length,
    failedUploads: uploads.filter((u) => u.status === 'failed').length,
    pendingUploads: uploads.filter((u) => u.status === 'pending' || u.status === 'uploading').length,
  };
}

export default useDocumentUpload;

