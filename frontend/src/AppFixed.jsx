import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Toaster } from "react-hot-toast";
import { Navigation } from "./components/Navigation";
import ExecutiveDashboard from "./components/ExecutiveDashboard";
import PropertyManagementExecutive from "./components/PropertyManagementExecutive";
import ExecutiveAnalytics from "./components/ExecutiveAnalytics";
import ExecutiveDocumentCenter from "./components/ExecutiveDocumentCenter";
import { DocumentUpload } from "./components/DocumentUpload";
import { ModernHeader } from "./components/ModernHeader";

function App() {
  const [currentView, setCurrentView] = useState('dashboard');
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [systemStats, setSystemStats] = useState({ status: 'healthy' });

  // Quick health check without loading delay
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await fetch('http://localhost:8001/health');
        const health = await response.json();
        setSystemStats({
          status: health.status,
          timestamp: new Date().toISOString()
        });
      } catch (error) {
        console.warn('Backend not available:', error);
        setSystemStats({
          status: 'disconnected',
          timestamp: new Date().toISOString()
        });
      }
    };

    checkHealth();
  }, []);

  const handleUploadSuccess = () => {
    setRefreshTrigger(prev => prev + 1);
    setCurrentView('documents');
  };

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

  const renderContent = () => {
    const components = {
      dashboard: (
        <motion.section 
          key="dashboard"
          initial="initial"
          animate="in"
          exit="out"
          variants={pageVariants}
          transition={pageTransition}
        >
          <ExecutiveDashboard />
        </motion.section>
      ),
      
      upload: (
        <motion.section 
          key="upload"
          initial="initial"
          animate="in"
          exit="out"
          variants={pageVariants}
          transition={pageTransition}
        >
          <div className="text-center space-y-4 mb-8">
            <h1 className="text-5xl font-bold bg-gradient-to-r from-emerald-600 via-teal-600 to-blue-600 bg-clip-text text-transparent">
              Smart Document Upload
            </h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              AI-powered document processing with intelligent data extraction and executive insights
            </p>
          </div>
          <DocumentUpload onUploadSuccess={handleUploadSuccess} />
        </motion.section>
      ),
      
      documents: (
        <motion.section 
          key="documents"
          initial="initial"
          animate="in"
          exit="out"
          variants={pageVariants}
          transition={pageTransition}
        >
          <ExecutiveDocumentCenter />
        </motion.section>
      ),
      
      analytics: (
        <motion.section 
          key="analytics"
          initial="initial"
          animate="in"
          exit="out"
          variants={pageVariants}
          transition={pageTransition}
        >
          <ExecutiveAnalytics />
        </motion.section>
      ),
      
      properties: (
        <motion.section 
          key="properties"
          initial="initial"
          animate="in"
          exit="out"
          variants={pageVariants}
          transition={pageTransition}
        >
          <PropertyManagementExecutive />
        </motion.section>
      )
    };

    return components[currentView] || components.dashboard;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 relative overflow-hidden">
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 0.1, scale: 1 }}
          transition={{ duration: 2 }}
          className="absolute -top-40 -right-40 w-80 h-80 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full blur-3xl"
        />
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 0.1, scale: 1 }}
          transition={{ duration: 2, delay: 0.5 }}
          className="absolute -bottom-40 -left-40 w-80 h-80 bg-gradient-to-r from-emerald-500 to-teal-600 rounded-full blur-3xl"
        />
      </div>

      {/* Toast Notifications */}
      <Toaster 
        position="top-right" 
        toastOptions={{
          className: 'glass-card',
          style: {
            background: 'rgba(255, 255, 255, 0.1)',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(255, 255, 255, 0.2)',
            color: 'white'
          }
        }}
      />

      {/* Modern Header */}
      <ModernHeader 
        currentView={currentView}
        onViewChange={setCurrentView}
        systemStats={systemStats}
      />

      {/* Main Content Area */}
      <main className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <AnimatePresence mode="wait">
          {renderContent()}
        </AnimatePresence>
      </main>

      {/* Enhanced Navigation */}
      <Navigation 
        currentView={currentView}
        onViewChange={setCurrentView}
      />
    </div>
  );
}

export default App;