import React from "react";
import { motion } from "framer-motion";
import { 
  HomeIcon, 
  CloudArrowUpIcon, 
  DocumentTextIcon, 
  ChartBarIcon, 
  BuildingOfficeIcon 
} from "@heroicons/react/24/outline";
import { 
  HomeIcon as HomeIconSolid, 
  CloudArrowUpIcon as CloudArrowUpIconSolid, 
  DocumentTextIcon as DocumentTextIconSolid, 
  ChartBarIcon as ChartBarIconSolid, 
  BuildingOfficeIcon as BuildingOfficeIconSolid 
} from "@heroicons/react/24/solid";

export function Navigation({ currentView, onViewChange }) {
  const navItems = [
    { 
      id: 'dashboard', 
      label: 'Dashboard', 
      icon: HomeIcon, 
      iconSolid: HomeIconSolid,
      gradient: 'from-blue-500 to-purple-600',
      description: 'Overview & insights'
    },
    { 
      id: 'upload', 
      label: 'Upload', 
      icon: CloudArrowUpIcon, 
      iconSolid: CloudArrowUpIconSolid,
      gradient: 'from-green-500 to-blue-500',
      description: 'Document upload'
    },
    { 
      id: 'documents', 
      label: 'Documents', 
      icon: DocumentTextIcon, 
      iconSolid: DocumentTextIconSolid,
      gradient: 'from-purple-500 to-pink-500',
      description: 'Document library'
    },
    { 
      id: 'analytics', 
      label: 'Analytics', 
      icon: ChartBarIcon, 
      iconSolid: ChartBarIconSolid,
      gradient: 'from-indigo-500 to-purple-500',
      description: 'Data insights'
    },
    { 
      id: 'properties', 
      label: 'Properties', 
      icon: BuildingOfficeIcon, 
      iconSolid: BuildingOfficeIconSolid,
      gradient: 'from-orange-500 to-red-500',
      description: 'Property management'
    }
  ];

  return (
    <motion.nav 
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ delay: 0.3, duration: 0.5 }}
      className="sticky top-0 z-50 bg-white/80 backdrop-blur-lg border-b border-white/20 shadow-lg"
    >
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex justify-center lg:justify-start">
          <div className="flex space-x-1 lg:space-x-2 py-4 overflow-x-auto">
            {navItems.map((item, index) => {
              const isActive = currentView === item.id;
              const Icon = isActive ? item.iconSolid : item.icon;
              
              return (
                <motion.button
                  key={item.id}
                  onClick={() => onViewChange(item.id)}
                  className="relative group"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 * index, duration: 0.3 }}
                >
                  {/* Active background */}
                  {isActive && (
                    <motion.div
                      className={`absolute inset-0 bg-gradient-to-r ${item.gradient} rounded-xl opacity-10`}
                      layoutId="activeBackground"
                      transition={{ type: "spring", stiffness: 300, damping: 30 }}
                    />
                  )}
                  
                  {/* Button content */}
                  <div className={`relative flex flex-col items-center px-4 py-3 rounded-xl transition-all duration-200 ${
                    isActive 
                      ? 'text-gray-800' 
                      : 'text-gray-500 hover:text-gray-700'
                  }`}>
                    {/* Icon with gradient background */}
                    <div className={`relative p-2 rounded-lg transition-all duration-200 ${
                      isActive 
                        ? `bg-gradient-to-r ${item.gradient} shadow-lg` 
                        : 'bg-gray-100 group-hover:bg-gray-200'
                    }`}>
                      <Icon className={`w-5 h-5 ${isActive ? 'text-white' : 'text-gray-600'}`} />
                      
                      {/* Glow effect for active item */}
                      {isActive && (
                        <motion.div
                          className={`absolute inset-0 bg-gradient-to-r ${item.gradient} rounded-lg blur-lg opacity-30`}
                          animate={{ scale: [1, 1.2, 1] }}
                          transition={{ duration: 2, repeat: Infinity }}
                        />
                      )}
                    </div>
                    
                    {/* Label */}
                    <span className={`mt-2 text-xs font-medium transition-all duration-200 ${
                      isActive ? 'text-gray-800' : 'text-gray-500 group-hover:text-gray-700'
                    }`}>
                      {item.label}
                    </span>
                    
                    {/* Description for larger screens */}
                    <span className="hidden xl:block text-xs text-gray-400 mt-1">
                      {item.description}
                    </span>
                  </div>
                  
                  {/* Active indicator */}
                  {isActive && (
                    <motion.div
                      className={`absolute -bottom-1 left-1/2 w-12 h-1 bg-gradient-to-r ${item.gradient} rounded-full`}
                      layoutId="activeIndicator"
                      transition={{ type: "spring", stiffness: 300, damping: 30 }}
                      style={{ transform: 'translateX(-50%)' }}
                    />
                  )}
                  
                  {/* Hover effect */}
                  <motion.div
                    className="absolute inset-0 rounded-xl bg-gradient-to-r from-gray-100 to-gray-50 opacity-0 group-hover:opacity-100 transition-opacity duration-200"
                    style={{ zIndex: -1 }}
                  />
                </motion.button>
              );
            })}
          </div>
        </div>
        
        {/* Mobile indicator */}
        <div className="lg:hidden pb-2">
          <div className="flex justify-center">
            <div className="flex space-x-2">
              {navItems.map((item) => (
                <div
                  key={item.id}
                  className={`w-2 h-2 rounded-full transition-all duration-200 ${
                    currentView === item.id
                      ? `bg-gradient-to-r ${item.gradient}`
                      : 'bg-gray-300'
                  }`}
                />
              ))}
            </div>
          </div>
        </div>
      </div>
    </motion.nav>
  );
}