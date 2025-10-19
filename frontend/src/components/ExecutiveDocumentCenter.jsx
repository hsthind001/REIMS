import React, { useState, useEffect, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  DocumentTextIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  CloudArrowUpIcon,
  EyeIcon,
  ArrowDownTrayIcon,
  ShareIcon,
  TrashIcon,
  FolderIcon,
  TagIcon,
  CalendarIcon,
  UserIcon,
  DocumentDuplicateIcon,
  ChartBarIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ClockIcon,
  StarIcon,
  PlusIcon
} from '@heroicons/react/24/outline';
import { 
  DocumentTextIcon as DocumentTextIconSolid,
  StarIcon as StarIconSolid
} from '@heroicons/react/24/solid';

const ExecutiveDocumentCenter = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedFilter, setSelectedFilter] = useState('all');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [viewMode, setViewMode] = useState('grid');
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [showUpload, setShowUpload] = useState(false);
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch real documents from API
  useEffect(() => {
    const fetchDocuments = async () => {
      try {
        setLoading(true);
        const response = await fetch('http://localhost:8001/api/documents/list');
        if (!response.ok) {
          throw new Error('Failed to fetch documents');
        }
        const data = await response.json();
        
        // Map API data to component format
        const mappedDocs = data.documents.map((doc, index) => ({
          id: index + 1,
          name: doc.original_filename,
          type: doc.content_type.includes('pdf') ? 'financial' : 'other',
          category: 'reports',
          status: doc.status || 'processed',
          priority: 'high',
          size: `${(doc.file_size / 1024 / 1024).toFixed(2)} MB`,
          format: doc.content_type.includes('pdf') ? 'PDF' : 'Unknown',
          uploadDate: new Date(doc.upload_timestamp).toLocaleDateString(),
          lastModified: new Date(doc.upload_timestamp).toLocaleDateString(),
          uploadedBy: 'System User',
          propertyId: doc.property_id || '1',
          propertyName: doc.property_name || 'Empire State Plaza',
          tags: ['financial', '2024', 'ESP'],
          summary: `Financial document for ${doc.property_name || 'ESP'}`,
          insights: ['Processed successfully'],
          rating: 4.8,
          views: 0,
          downloads: 0,
          shares: 0,
          thumbnail: '/api/placeholder/300/400'
        }));
        
        setDocuments(mappedDocs);
      } catch (err) {
        console.error('Error fetching documents:', err);
        setError(err.message);
        setDocuments([]);
      } finally {
        setLoading(false);
      }
    };

    fetchDocuments();
  }, []);

  // Mock document data (fallback/example)
  const mockDocuments = [
    {
      id: 1,
      name: 'Q3 Financial Report 2024',
      type: 'financial',
      category: 'reports',
      status: 'processed',
      priority: 'high',
      size: '2.4 MB',
      format: 'PDF',
      uploadDate: '2024-09-15',
      lastModified: '2024-09-20',
      uploadedBy: 'Sarah Johnson, CFO',
      propertyId: 'all',
      propertyName: 'Portfolio Overview',
      tags: ['financial', 'quarterly', 'revenue', 'performance'],
      summary: 'Comprehensive financial analysis showing 13.8% revenue growth and strategic recommendations for Q4.',
      insights: ['Revenue up 13.8%', 'Occupancy at 94.6%', 'ROI increased to 12.3%'],
      rating: 4.9,
      views: 47,
      downloads: 12,
      shares: 8,
      thumbnail: '/api/placeholder/300/400'
    },
    {
      id: 2,
      name: 'Skyline Tower Lease Agreement',
      type: 'legal',
      category: 'contracts',
      status: 'processed',
      priority: 'high',
      size: '1.8 MB',
      format: 'PDF',
      uploadDate: '2024-09-10',
      lastModified: '2024-09-12',
      uploadedBy: 'Mike Chen, Legal',
      propertyId: 'skyline-tower',
      propertyName: 'Skyline Tower',
      tags: ['lease', 'contract', 'commercial', '5-year'],
      summary: 'Major commercial lease renewal for Tech Corp Inc. with favorable terms and 5-year commitment.',
      insights: ['$35K monthly rent', '5-year term', '3% annual increase'],
      rating: 4.7,
      views: 23,
      downloads: 8,
      shares: 5,
      thumbnail: '/api/placeholder/300/400'
    },
    {
      id: 3,
      name: 'Market Analysis Downtown District',
      type: 'analysis',
      category: 'research',
      status: 'processing',
      priority: 'medium',
      size: '5.2 MB',
      format: 'PDF',
      uploadDate: '2024-09-18',
      lastModified: '2024-09-18',
      uploadedBy: 'David Rodriguez, Research',
      propertyId: 'potential',
      propertyName: 'Expansion Opportunity',
      tags: ['market', 'analysis', 'downtown', 'expansion'],
      summary: 'Comprehensive market study for potential expansion into downtown district with ROI projections.',
      insights: ['8-12% ROI potential', 'High demand area', 'Competition analysis'],
      rating: 4.5,
      views: 15,
      downloads: 3,
      shares: 2,
      thumbnail: '/api/placeholder/300/400'
    },
    {
      id: 4,
      name: 'Insurance Policy Renewal',
      type: 'insurance',
      category: 'policies',
      status: 'pending',
      priority: 'urgent',
      size: '0.9 MB',
      format: 'PDF',
      uploadDate: '2024-09-22',
      lastModified: '2024-09-22',
      uploadedBy: 'Emily Watson, Operations',
      propertyId: 'all',
      propertyName: 'Portfolio Coverage',
      tags: ['insurance', 'renewal', 'coverage', 'liability'],
      summary: 'Annual insurance policy renewal with updated coverage terms and premium adjustments.',
      insights: ['Premium increase 5%', 'Enhanced coverage', 'Renewal due Oct 1'],
      rating: 4.2,
      views: 8,
      downloads: 1,
      shares: 0,
      thumbnail: '/api/placeholder/300/400'
    },
    {
      id: 5,
      name: 'Maintenance Report September',
      type: 'maintenance',
      category: 'reports',
      status: 'processed',
      priority: 'medium',
      size: '3.1 MB',
      format: 'PDF',
      uploadDate: '2024-09-25',
      lastModified: '2024-09-25',
      uploadedBy: 'Maintenance Team',
      propertyId: 'industrial-park',
      propertyName: 'Industrial Park A',
      tags: ['maintenance', 'repair', 'inspection', 'costs'],
      summary: 'Monthly maintenance activities and cost analysis with recommendations for preventive measures.',
      insights: ['Costs up 15%', '3 urgent repairs', 'Preventive plan needed'],
      rating: 4.0,
      views: 12,
      downloads: 4,
      shares: 1,
      thumbnail: '/api/placeholder/300/400'
    },
    {
      id: 6,
      name: 'Tenant Satisfaction Survey',
      type: 'survey',
      category: 'research',
      status: 'processed',
      priority: 'low',
      size: '1.5 MB',
      format: 'PDF',
      uploadDate: '2024-09-20',
      lastModified: '2024-09-21',
      uploadedBy: 'Customer Relations',
      propertyId: 'all',
      propertyName: 'All Properties',
      tags: ['tenant', 'satisfaction', 'survey', 'feedback'],
      summary: 'Annual tenant satisfaction survey results with actionable insights for service improvements.',
      insights: ['4.7/5 rating', '89% retention', 'Service improvements needed'],
      rating: 4.6,
      views: 19,
      downloads: 6,
      shares: 3,
      thumbnail: '/api/placeholder/300/400'
    }
  ];

  // Document statistics
  const documentStats = useMemo(() => {
    const total = documents.length;
    const processed = documents.filter(doc => doc.status === 'processed').length;
    const pending = documents.filter(doc => doc.status === 'pending').length;
    const processing = documents.filter(doc => doc.status === 'processing').length;
    const urgent = documents.filter(doc => doc.priority === 'urgent').length;
    const totalSize = documents.reduce((sum, doc) => sum + parseFloat(doc.size), 0);
    const avgRating = documents.reduce((sum, doc) => sum + doc.rating, 0) / total;

    return {
      total,
      processed,
      pending,
      processing,
      urgent,
      totalSize: totalSize.toFixed(1),
      avgRating: avgRating.toFixed(1)
    };
  }, []);

  // Filter documents
  const filteredDocuments = useMemo(() => {
    return documents.filter(doc => {
      const matchesSearch = doc.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          doc.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
      const matchesFilter = selectedFilter === 'all' || doc.status === selectedFilter;
      const matchesCategory = selectedCategory === 'all' || doc.category === selectedCategory;
      return matchesSearch && matchesFilter && matchesCategory;
    });
  }, [searchTerm, selectedFilter, selectedCategory]);

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.2
      }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        type: "spring",
        stiffness: 100,
        damping: 12
      }
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'processed': return 'text-emerald-600 bg-emerald-50 border-emerald-200';
      case 'processing': return 'text-blue-600 bg-blue-50 border-blue-200';
      case 'pending': return 'text-orange-600 bg-orange-50 border-orange-200';
      case 'failed': return 'text-red-600 bg-red-50 border-red-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'urgent': return 'text-red-600 bg-red-50 border-red-200';
      case 'high': return 'text-orange-600 bg-orange-50 border-orange-200';
      case 'medium': return 'text-blue-600 bg-blue-50 border-blue-200';
      case 'low': return 'text-gray-600 bg-gray-50 border-gray-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getTypeIcon = (type) => {
    switch (type) {
      case 'financial': return ChartBarIcon;
      case 'legal': return DocumentTextIcon;
      case 'analysis': return DocumentDuplicateIcon;
      case 'insurance': return FolderIcon;
      case 'maintenance': return ExclamationTriangleIcon;
      case 'survey': return UserIcon;
      default: return DocumentTextIcon;
    }
  };

  const DocumentCard = ({ document, index }) => {
    const TypeIcon = getTypeIcon(document.type);

    return (
      <motion.div
        key={document.id}
        variants={itemVariants}
        className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden group border border-white/20"
        whileHover={{ 
          scale: 1.02,
          y: -5,
          transition: { type: "spring", stiffness: 400, damping: 25 }
        }}
      >
        {/* Document Preview */}
        <div className="relative h-40 bg-gradient-to-br from-indigo-100 to-purple-100 overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-indigo-600/20 to-purple-600/20" />
          
          {/* Status and Priority Badges */}
          <div className="absolute top-3 left-3 flex flex-col space-y-2">
            <div className={`px-2 py-1 rounded-full text-xs font-semibold border ${getStatusColor(document.status)}`}>
              {document.status.charAt(0).toUpperCase() + document.status.slice(1)}
            </div>
            <div className={`px-2 py-1 rounded-full text-xs font-semibold border ${getPriorityColor(document.priority)}`}>
              {document.priority.charAt(0).toUpperCase() + document.priority.slice(1)}
            </div>
          </div>

          {/* Rating */}
          <div className="absolute top-3 right-3 flex items-center space-x-1 bg-white/20 backdrop-blur-sm rounded-lg px-2 py-1">
            <StarIcon className="w-3 h-3 text-yellow-400 fill-current" />
            <span className="text-white text-xs font-semibold">{document.rating}</span>
          </div>

          {/* Document Type Icon */}
          <div className="absolute inset-0 flex items-center justify-center">
            <TypeIcon className="w-12 h-12 text-white/30" />
          </div>
        </div>

        {/* Document Details */}
        <div className="p-5">
          <div className="mb-3">
            <h3 className="text-lg font-bold text-gray-900 mb-1 group-hover:text-indigo-600 transition-colors duration-200 line-clamp-2">
              {document.name}
            </h3>
            <p className="text-sm text-gray-600 line-clamp-2">{document.summary}</p>
          </div>

          {/* Property and Upload Info */}
          <div className="space-y-2 mb-4">
            <div className="flex items-center text-xs text-gray-500">
              <FolderIcon className="w-3 h-3 mr-1" />
              {document.propertyName}
            </div>
            <div className="flex items-center text-xs text-gray-500">
              <UserIcon className="w-3 h-3 mr-1" />
              {document.uploadedBy}
            </div>
            <div className="flex items-center text-xs text-gray-500">
              <CalendarIcon className="w-3 h-3 mr-1" />
              {new Date(document.uploadDate).toLocaleDateString()}
            </div>
          </div>

          {/* Key Insights */}
          <div className="mb-4">
            <h4 className="text-xs font-semibold text-gray-700 mb-2">Key Insights:</h4>
            <div className="space-y-1">
              {document.insights.slice(0, 2).map((insight, idx) => (
                <div key={idx} className="text-xs text-gray-600 flex items-center">
                  <div className="w-1 h-1 bg-indigo-400 rounded-full mr-2"></div>
                  {insight}
                </div>
              ))}
            </div>
          </div>

          {/* Tags */}
          <div className="flex flex-wrap gap-1 mb-4">
            {document.tags.slice(0, 3).map((tag) => (
              <span 
                key={tag}
                className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-md"
              >
                {tag}
              </span>
            ))}
            {document.tags.length > 3 && (
              <span className="px-2 py-1 bg-gray-100 text-gray-500 text-xs rounded-md">
                +{document.tags.length - 3}
              </span>
            )}
          </div>

          {/* Engagement Stats */}
          <div className="flex justify-between text-xs text-gray-500 mb-4">
            <div className="flex items-center space-x-1">
              <EyeIcon className="w-3 h-3" />
              <span>{document.views}</span>
            </div>
            <div className="flex items-center space-x-1">
              <ArrowDownTrayIcon className="w-3 h-3" />
              <span>{document.downloads}</span>
            </div>
            <div className="flex items-center space-x-1">
              <ShareIcon className="w-3 h-3" />
              <span>{document.shares}</span>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex space-x-2">
            <motion.button
              onClick={() => setSelectedDocument(document)}
              className="flex-1 flex items-center justify-center space-x-1 px-3 py-2 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-lg text-xs font-medium hover:from-indigo-600 hover:to-purple-700 transition-all duration-200"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <EyeIcon className="w-3 h-3" />
              <span>View</span>
            </motion.button>
            <motion.button
              className="p-2 text-gray-600 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-all duration-200"
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
            >
              <ArrowDownTrayIcon className="w-3 h-3" />
            </motion.button>
            <motion.button
              className="p-2 text-gray-600 hover:text-green-600 hover:bg-green-50 rounded-lg transition-all duration-200"
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
            >
              <ShareIcon className="w-3 h-3" />
            </motion.button>
          </div>
        </div>
      </motion.div>
    );
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-8"
    >
      {/* Document Center Header */}
      <motion.div variants={itemVariants} className="text-center space-y-4">
        <h1 className="text-5xl font-bold bg-gradient-to-r from-indigo-600 via-purple-600 to-blue-600 bg-clip-text text-transparent">
          Executive Document Center
        </h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          Centralized document management with AI-powered insights and executive-level analytics
        </p>
      </motion.div>

      {/* Document Statistics */}
      <motion.div variants={itemVariants} className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
        <div className="bg-gradient-to-br from-emerald-500 to-teal-600 p-4 rounded-xl text-white text-center">
          <div className="text-2xl font-bold">{documentStats.total}</div>
          <div className="text-xs text-emerald-100">Total Documents</div>
        </div>
        <div className="bg-gradient-to-br from-blue-500 to-indigo-600 p-4 rounded-xl text-white text-center">
          <div className="text-2xl font-bold">{documentStats.processed}</div>
          <div className="text-xs text-blue-100">Processed</div>
        </div>
        <div className="bg-gradient-to-br from-orange-500 to-red-600 p-4 rounded-xl text-white text-center">
          <div className="text-2xl font-bold">{documentStats.pending}</div>
          <div className="text-xs text-orange-100">Pending</div>
        </div>
        <div className="bg-gradient-to-br from-purple-500 to-pink-600 p-4 rounded-xl text-white text-center">
          <div className="text-2xl font-bold">{documentStats.urgent}</div>
          <div className="text-xs text-purple-100">Urgent</div>
        </div>
        <div className="bg-gradient-to-br from-gray-500 to-slate-600 p-4 rounded-xl text-white text-center">
          <div className="text-2xl font-bold">{documentStats.totalSize}</div>
          <div className="text-xs text-gray-100">MB Total</div>
        </div>
        <div className="bg-gradient-to-br from-yellow-500 to-orange-600 p-4 rounded-xl text-white text-center">
          <div className="text-2xl font-bold">{documentStats.avgRating}</div>
          <div className="text-xs text-yellow-100">Avg Rating</div>
        </div>
        <div className="bg-gradient-to-br from-cyan-500 to-blue-600 p-4 rounded-xl text-white text-center">
          <div className="text-2xl font-bold">{documents.reduce((sum, doc) => sum + doc.views, 0)}</div>
          <div className="text-xs text-cyan-100">Total Views</div>
        </div>
      </motion.div>

      {/* Search and Filter Controls */}
      <motion.div variants={itemVariants} className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-white/20">
        <div className="flex flex-col lg:flex-row lg:items-center gap-4">
          {/* Search */}
          <div className="relative flex-1">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search documents, tags, or insights..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white/50 backdrop-blur-sm"
            />
          </div>

          {/* Filters */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <FunnelIcon className="w-5 h-5 text-gray-500" />
              <select
                value={selectedFilter}
                onChange={(e) => setSelectedFilter(e.target.value)}
                className="border border-gray-300 rounded-lg px-3 py-3 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white/50 backdrop-blur-sm"
              >
                <option value="all">All Status</option>
                <option value="processed">Processed</option>
                <option value="processing">Processing</option>
                <option value="pending">Pending</option>
              </select>
            </div>

            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-3 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white/50 backdrop-blur-sm"
            >
              <option value="all">All Categories</option>
              <option value="reports">Reports</option>
              <option value="contracts">Contracts</option>
              <option value="research">Research</option>
              <option value="policies">Policies</option>
            </select>

            <motion.button
              onClick={() => setShowUpload(true)}
              className="flex items-center space-x-2 px-6 py-3 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-lg hover:from-indigo-600 hover:to-purple-700 transition-all duration-200 shadow-lg"
              whileHover={{ scale: 1.02, y: -1 }}
              whileTap={{ scale: 0.98 }}
            >
              <CloudArrowUpIcon className="w-5 h-5" />
              <span className="font-medium">Upload Document</span>
            </motion.button>
          </div>
        </div>
      </motion.div>

      {/* Documents Grid */}
      <motion.div 
        variants={containerVariants}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6"
      >
        {filteredDocuments.map((document, index) => (
          <DocumentCard key={document.id} document={document} index={index} />
        ))}
      </motion.div>

      {/* Empty State */}
      {filteredDocuments.length === 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center py-12"
        >
          <DocumentTextIcon className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-600 mb-2">No documents found</h3>
          <p className="text-gray-500">Try adjusting your search or filter criteria</p>
        </motion.div>
      )}

      {/* Document Detail Modal */}
      <AnimatePresence>
        {selectedDocument && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setSelectedDocument(null)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0, y: 20 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              exit={{ scale: 0.9, opacity: 0, y: 20 }}
              className="bg-white rounded-2xl p-8 max-w-4xl max-h-[90vh] overflow-y-auto shadow-2xl"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex justify-between items-start mb-6">
                <div>
                  <h2 className="text-3xl font-bold text-gray-900 mb-2">{selectedDocument.name}</h2>
                  <p className="text-gray-600">{selectedDocument.summary}</p>
                </div>
                <button
                  onClick={() => setSelectedDocument(null)}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors duration-200"
                >
                  <svg className="w-6 h-6 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              {/* Document details would go here */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div className="space-y-4">
                  <h3 className="text-xl font-semibold text-gray-900">Document Information</h3>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Type:</span>
                      <span className="font-medium capitalize">{selectedDocument.type}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Category:</span>
                      <span className="font-medium capitalize">{selectedDocument.category}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Status:</span>
                      <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getStatusColor(selectedDocument.status)}`}>
                        {selectedDocument.status}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Priority:</span>
                      <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getPriorityColor(selectedDocument.priority)}`}>
                        {selectedDocument.priority}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <h3 className="text-xl font-semibold text-gray-900">Key Insights</h3>
                  <div className="space-y-2">
                    {selectedDocument.insights.map((insight, index) => (
                      <div key={index} className="flex items-center p-3 bg-gray-50 rounded-lg">
                        <CheckCircleIcon className="w-5 h-5 text-emerald-500 mr-3" />
                        <span className="text-gray-700">{insight}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

export default ExecutiveDocumentCenter;