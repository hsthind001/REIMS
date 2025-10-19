import React, { useState } from "react";
import { Toaster } from "react-hot-toast";

// Simple test app to verify React is working
function SimpleApp() {
  const [currentView, setCurrentView] = useState('dashboard');

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <Toaster position="top-right" />
      
      {/* Header */}
      <header className="bg-white/10 backdrop-blur-md border-b border-white/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-white">
                🏢 REIMS Executive
              </h1>
            </div>
            <nav className="flex space-x-4">
              {['dashboard', 'properties', 'analytics', 'documents', 'upload'].map((view) => (
                <button
                  key={view}
                  onClick={() => setCurrentView(view)}
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    currentView === view
                      ? 'bg-white/20 text-white'
                      : 'text-gray-300 hover:text-white hover:bg-white/10'
                  }`}
                >
                  {view.charAt(0).toUpperCase() + view.slice(1)}
                </button>
              ))}
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="bg-white/10 backdrop-blur-md rounded-lg p-8 border border-white/20">
            <h2 className="text-3xl font-bold text-white mb-4">
              {currentView.charAt(0).toUpperCase() + currentView.slice(1)} View
            </h2>
            
            {currentView === 'dashboard' && (
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="bg-gradient-to-r from-blue-500 to-cyan-500 p-6 rounded-lg">
                    <h3 className="text-white text-lg font-semibold">Total Properties</h3>
                    <p className="text-white text-3xl font-bold">184</p>
                  </div>
                  <div className="bg-gradient-to-r from-emerald-500 to-teal-500 p-6 rounded-lg">
                    <h3 className="text-white text-lg font-semibold">Portfolio Value</h3>
                    <p className="text-white text-3xl font-bold">$47.8M</p>
                  </div>
                  <div className="bg-gradient-to-r from-purple-500 to-pink-500 p-6 rounded-lg">
                    <h3 className="text-white text-lg font-semibold">Occupancy Rate</h3>
                    <p className="text-white text-3xl font-bold">94.2%</p>
                  </div>
                </div>
                <div className="text-white">
                  <h4 className="text-xl font-semibold mb-2">✅ System Status</h4>
                  <p>Backend: Connected to http://localhost:8001</p>
                  <p>Frontend: React 18.2.0 with Vite</p>
                  <p>Time: {new Date().toLocaleString()}</p>
                </div>
              </div>
            )}
            
            {currentView !== 'dashboard' && (
              <div className="text-center text-white">
                <p className="text-xl mb-4">
                  🚧 {currentView.charAt(0).toUpperCase() + currentView.slice(1)} section coming soon!
                </p>
                <p className="text-gray-300">
                  This view will contain the executive {currentView} interface.
                </p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

export default SimpleApp;