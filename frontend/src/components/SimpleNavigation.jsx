import React from "react";

export function SimpleNavigation({ currentView, onViewChange }) {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard' },
    { id: 'upload', label: 'Upload' },
    { id: 'documents', label: 'Documents' },
    { id: 'analytics', label: 'Analytics' },
    { id: 'properties', label: 'Properties' }
  ];

  return (
    <nav className="bg-white/80 backdrop-blur-lg border-b border-white/20 shadow-lg">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex justify-center lg:justify-start">
          <div className="flex space-x-1 lg:space-x-2 py-4">
            {navItems.map((item) => (
              <button
                key={item.id}
                onClick={() => onViewChange(item.id)}
                className={`px-4 py-2 rounded-xl transition-all duration-200 ${
                  currentView === item.id
                    ? 'bg-blue-500 text-white'
                    : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                }`}
              >
                {item.label}
              </button>
            ))}
          </div>
        </div>
      </div>
    </nav>
  );
}