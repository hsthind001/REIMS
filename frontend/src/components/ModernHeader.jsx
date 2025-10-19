import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  BellIcon, 
  UserCircleIcon, 
  Cog6ToothIcon,
  ChevronDownIcon 
} from '@heroicons/react/24/outline';

export const ModernHeader = ({ systemStats }) => {
  const [currentTime, setCurrentTime] = useState(new Date());
  const [notifications] = useState([
    { id: 1, message: "New document processed", type: "success", time: "2 min ago" },
    { id: 2, message: "Property update required", type: "warning", time: "5 min ago" },
    { id: 3, message: "System backup completed", type: "info", time: "10 min ago" }
  ]);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const formatTime = (date) => {
    return date.toLocaleTimeString('en-US', {
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  const formatDate = (date) => {
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  return (
    <motion.header 
      initial={{ y: -100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
      className="relative bg-white/10 backdrop-blur-lg border-b border-white/20 shadow-lg"
    >
      {/* Background gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-r from-blue-600/20 via-purple-600/20 to-pink-600/20" />
      
      <div className="relative z-10 max-w-7xl mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Logo and title section */}
          <motion.div 
            className="flex items-center space-x-4"
            initial={{ x: -50, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ delay: 0.2, duration: 0.5 }}
          >
            <div className="relative">
              <motion.div
                className="w-12 h-12 bg-gradient-primary rounded-xl flex items-center justify-center shadow-lg"
                whileHover={{ scale: 1.1, rotate: 5 }}
                whileTap={{ scale: 0.95 }}
              >
                <svg className="w-7 h-7 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z" />
                </svg>
              </motion.div>
              {systemStats?.status === 'healthy' && (
                <motion.div
                  className="absolute -top-1 -right-1 w-4 h-4 bg-green-400 rounded-full border-2 border-white"
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 2, repeat: Infinity }}
                />
              )}
            </div>
            
            <div>
              <motion.h1 
                className="text-2xl font-bold bg-gradient-to-r from-gray-800 to-gray-600 bg-clip-text text-transparent"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.3 }}
              >
                REIMS
              </motion.h1>
              <motion.p 
                className="text-sm text-gray-600 font-medium"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.4 }}
              >
                Real Estate Intelligence
              </motion.p>
            </div>
          </motion.div>

          {/* Center section - Date and Time */}
          <motion.div 
            className="hidden md:flex items-center space-x-6"
            initial={{ y: -20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.3, duration: 0.5 }}
          >
            <div className="text-center">
              <div className="text-sm text-gray-500 font-medium">
                {formatDate(currentTime)}
              </div>
              <div className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                {formatTime(currentTime)}
              </div>
            </div>
          </motion.div>

          {/* Right section - Actions */}
          <motion.div 
            className="flex items-center space-x-4"
            initial={{ x: 50, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ delay: 0.4, duration: 0.5 }}
          >
            {/* System status */}
            <div className="hidden sm:flex items-center space-x-2 px-3 py-2 bg-white/20 backdrop-blur-sm rounded-lg border border-white/30">
              <div className={`w-2 h-2 rounded-full ${systemStats?.status === 'healthy' ? 'bg-green-400' : 'bg-red-400'} animate-pulse`} />
              <span className="text-sm font-medium text-gray-700">
                {systemStats?.status === 'healthy' ? 'Online' : 'Offline'}
              </span>
            </div>

            {/* Notifications */}
            <motion.div 
              className="relative"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <button className="p-2 bg-white/20 backdrop-blur-sm rounded-lg border border-white/30 hover:bg-white/30 transition-all duration-200">
                <BellIcon className="w-5 h-5 text-gray-700" />
                {notifications.length > 0 && (
                  <motion.span
                    className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center font-bold"
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ type: "spring", stiffness: 500, damping: 30 }}
                  >
                    {notifications.length}
                  </motion.span>
                )}
              </button>
            </motion.div>

            {/* Settings */}
            <motion.button 
              className="p-2 bg-white/20 backdrop-blur-sm rounded-lg border border-white/30 hover:bg-white/30 transition-all duration-200"
              whileHover={{ scale: 1.05, rotate: 90 }}
              whileTap={{ scale: 0.95 }}
            >
              <Cog6ToothIcon className="w-5 h-5 text-gray-700" />
            </motion.button>

            {/* User menu */}
            <motion.div 
              className="flex items-center space-x-2 px-3 py-2 bg-white/20 backdrop-blur-sm rounded-lg border border-white/30 hover:bg-white/30 transition-all duration-200 cursor-pointer"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <UserCircleIcon className="w-6 h-6 text-gray-700" />
              <span className="hidden sm:block text-sm font-medium text-gray-700">Admin</span>
              <ChevronDownIcon className="w-4 h-4 text-gray-500" />
            </motion.div>
          </motion.div>
        </div>

        {/* Quick stats bar */}
        <motion.div 
          className="mt-4 flex items-center justify-between text-sm"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5, duration: 0.5 }}
        >
          <div className="flex items-center space-x-6">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
              <span className="text-gray-600">All Systems Operational</span>
            </div>
            <div className="hidden md:flex items-center space-x-4 text-gray-500">
              <span>Last backup: 2 hours ago</span>
              <span>•</span>
              <span>Uptime: 99.9%</span>
            </div>
          </div>
          
          <div className="hidden lg:flex items-center space-x-4 text-gray-500">
            <span>Version 2.1.0</span>
            <span>•</span>
            <span>API Response: 45ms</span>
          </div>
        </motion.div>
      </div>
    </motion.header>
  );
};