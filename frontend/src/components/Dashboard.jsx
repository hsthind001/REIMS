import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { 
  DocumentIcon,
  ChartBarIcon,
  CloudArrowUpIcon,
  BuildingOfficeIcon,
  CpuChipIcon,
  ClockIcon,
  TrendingUpIcon,
  TrendingDownIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon
} from "@heroicons/react/24/outline";

export function Dashboard() {
  const [stats, setStats] = useState({
    totalDocuments: 0,
    aiProcessed: 0,
    totalProperties: 0,
    recentUploads: []
  });
  const [loading, setLoading] = useState(true);
  const [systemStatus, setSystemStatus] = useState([]);

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      // Fetch documents
      const docsResponse = await fetch("http://localhost:8001/api/documents");
      if (docsResponse.ok) {
        const docsData = await docsResponse.json();
        const documents = docsData.documents || [];
        
        // Count AI processed documents
        let aiProcessedCount = 0;
        for (const doc of documents) {
          try {
            const statusResponse = await fetch(`http://localhost:8001/ai/process/${doc.document_id}/status`);
            if (statusResponse.ok) {
              const statusData = await statusResponse.json();
              if (statusData.status === 'success') {
                aiProcessedCount++;
              }
            }
          } catch (err) {
            // Ignore errors for individual status checks
          }
        }

        // Get recent uploads (last 5)
        const recentUploads = documents
          .sort((a, b) => new Date(b.upload_timestamp) - new Date(a.upload_timestamp))
          .slice(0, 5);

        setStats({
          totalDocuments: documents.length,
          aiProcessed: aiProcessedCount,
          totalProperties: new Set(documents.map(doc => doc.property_id)).size,
          recentUploads
        });
      }

      // Check system status
      const statusChecks = [
        { name: "Backend API", url: "http://localhost:8001/health", timeout: 5000 },
        { name: "Document Processing", url: "http://localhost:8001/api/documents", timeout: 5000 },
        { name: "AI Services", url: "http://localhost:8001/ai/health", timeout: 5000 }
      ];

      const statusResults = await Promise.allSettled(
        statusChecks.map(async (check) => {
          try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), check.timeout);
            
            const response = await fetch(check.url, {
              signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            
            return {
              name: check.name,
              status: response.ok ? 'online' : 'error',
              responseTime: response.ok ? '< 1s' : 'N/A'
            };
          } catch (err) {
            return {
              name: check.name,
              status: 'offline',
              responseTime: 'N/A'
            };
          }
        })
      );

      setSystemStatus(statusResults.map(result => result.value || result.reason));
      setLoading(false);
    } catch (err) {
      console.error("Error fetching dashboard data:", err);
      setLoading(false);
    }
  };

  const formatDate = (isoString) => {
    return new Date(isoString).toLocaleDateString();
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const StatCard = ({ icon: Icon, title, value, subtitle, gradient, delay = 0 }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.5 }}
      className="glass-card p-6 relative overflow-hidden group hover:scale-105 transition-transform duration-200"
    >
      {/* Background gradient */}
      <div className={`absolute inset-0 bg-gradient-to-br ${gradient} opacity-5 group-hover:opacity-10 transition-opacity duration-200`} />
      
      <div className="relative z-10">
        <div className="flex items-center justify-between mb-4">
          <div className={`p-3 bg-gradient-to-r ${gradient} rounded-xl`}>
            <Icon className="w-6 h-6 text-white" />
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold text-gray-800">{value}</div>
            <div className="text-sm text-gray-600">{title}</div>
          </div>
        </div>
        {subtitle && (
          <div className="text-xs text-gray-500">{subtitle}</div>
        )}
      </div>
    </motion.div>
  );

  const SystemStatusCard = ({ name, status, responseTime, delay = 0 }) => {
    const getStatusConfig = () => {
      switch (status) {
        case 'online':
          return {
            color: 'text-green-600',
            bgColor: 'bg-green-100',
            icon: CheckCircleIcon
          };
        case 'offline':
          return {
            color: 'text-red-600',
            bgColor: 'bg-red-100',
            icon: ExclamationTriangleIcon
          };
        default:
          return {
            color: 'text-yellow-600',
            bgColor: 'bg-yellow-100',
            icon: ExclamationTriangleIcon
          };
      }
    };

    const config = getStatusConfig();
    const StatusIcon = config.icon;

    return (
      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay, duration: 0.3 }}
        className="flex items-center justify-between p-3 bg-white/50 backdrop-blur-sm rounded-lg border border-white/20"
      >
        <div className="flex items-center space-x-3">
          <div className={`p-2 ${config.bgColor} rounded-lg`}>
            <StatusIcon className={`w-4 h-4 ${config.color}`} />
          </div>
          <span className="font-medium text-gray-800">{name}</span>
        </div>
        <div className="text-right">
          <div className={`text-sm font-semibold ${config.color} capitalize`}>{status}</div>
          <div className="text-xs text-gray-500">{responseTime}</div>
        </div>
      </motion.div>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          className="w-12 h-12 border-4 border-blue-200 border-t-blue-600 rounded-full"
        />
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="space-y-8"
    >
      {/* Welcome Section */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-8"
      >
        <h1 className="text-4xl font-bold text-gray-800 mb-2">
          Welcome to <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">REIMS</span>
        </h1>
        <p className="text-gray-600 text-lg">Real Estate Intelligence Management System</p>
      </motion.div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          icon={DocumentIcon}
          title="Total Documents"
          value={stats.totalDocuments}
          subtitle="Files uploaded to system"
          gradient="from-blue-500 to-cyan-500"
          delay={0.1}
        />
        <StatCard
          icon={CpuChipIcon}
          title="AI Processed"
          value={stats.aiProcessed}
          subtitle="Documents analyzed by AI"
          gradient="from-purple-500 to-pink-500"
          delay={0.2}
        />
        <StatCard
          icon={BuildingOfficeIcon}
          title="Properties"
          value={stats.totalProperties}
          subtitle="Unique property IDs"
          gradient="from-green-500 to-emerald-500"
          delay={0.3}
        />
        <StatCard
          icon={ChartBarIcon}
          title="Processing Rate"
          value={stats.totalDocuments > 0 ? `${Math.round((stats.aiProcessed / stats.totalDocuments) * 100)}%` : "0%"}
          subtitle="AI analysis completion"
          gradient="from-orange-500 to-red-500"
          delay={0.4}
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
        {/* Recent Uploads */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.5 }}
          className="xl:col-span-2 glass-card"
        >
          <div className="p-6 border-b border-white/10">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <CloudArrowUpIcon className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-gray-800">Recent Uploads</h3>
                <p className="text-sm text-gray-600">Latest document activity</p>
              </div>
            </div>
          </div>
          
          <div className="p-6">
            {stats.recentUploads.length === 0 ? (
              <div className="text-center py-8">
                <DocumentIcon className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                <p className="text-gray-500">No documents uploaded yet</p>
              </div>
            ) : (
              <div className="space-y-4">
                {stats.recentUploads.map((doc, index) => (
                  <motion.div
                    key={doc.document_id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.6 + index * 0.1 }}
                    className="flex items-center justify-between p-4 bg-white/30 backdrop-blur-sm rounded-lg border border-white/20"
                  >
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                        <DocumentIcon className="w-5 h-5 text-blue-600" />
                      </div>
                      <div>
                        <p className="font-medium text-gray-800 truncate max-w-xs">
                          {doc.original_filename}
                        </p>
                        <p className="text-sm text-gray-600">
                          Property: {doc.property_id}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium text-gray-700">
                        {formatFileSize(doc.file_size)}
                      </p>
                      <p className="text-xs text-gray-500">
                        {formatDate(doc.upload_timestamp)}
                      </p>
                    </div>
                  </motion.div>
                ))}
              </div>
            )}
          </div>
        </motion.div>

        {/* System Status */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.6 }}
          className="glass-card"
        >
          <div className="p-6 border-b border-white/10">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-green-500 to-emerald-600 rounded-lg flex items-center justify-center">
                <CheckCircleIcon className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-gray-800">System Status</h3>
                <p className="text-sm text-gray-600">Service health overview</p>
              </div>
            </div>
          </div>
          
          <div className="p-6 space-y-3">
            {systemStatus.map((service, index) => (
              <SystemStatusCard
                key={service.name}
                name={service.name}
                status={service.status}
                responseTime={service.responseTime}
                delay={0.7 + index * 0.1}
              />
            ))}
          </div>
        </motion.div>
      </div>

      {/* Quick Actions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.8 }}
        className="glass-card p-6"
      >
        <h3 className="text-xl font-bold text-gray-800 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[
            { title: "Upload Document", icon: CloudArrowUpIcon, gradient: "from-blue-500 to-cyan-500" },
            { title: "View Analytics", icon: ChartBarIcon, gradient: "from-purple-500 to-pink-500" },
            { title: "Manage Properties", icon: BuildingOfficeIcon, gradient: "from-green-500 to-emerald-500" },
            { title: "AI Processing", icon: CpuChipIcon, gradient: "from-orange-500 to-red-500" }
          ].map((action, index) => (
            <motion.button
              key={action.title}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.9 + index * 0.1 }}
              className="p-4 bg-white/30 backdrop-blur-sm rounded-xl border border-white/20 hover:bg-white/40 transition-all duration-200 group"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <div className={`w-12 h-12 bg-gradient-to-r ${action.gradient} rounded-lg flex items-center justify-center mx-auto mb-3 group-hover:scale-110 transition-transform duration-200`}>
                <action.icon className="w-6 h-6 text-white" />
              </div>
              <p className="text-sm font-medium text-gray-800">{action.title}</p>
            </motion.button>
          ))}
        </div>
      </motion.div>
    </motion.div>
  );
}