import React from 'react';

function SimpleTest() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-600 to-purple-700 flex items-center justify-center">
      <div className="text-center text-white">
        <h1 className="text-6xl font-bold mb-4">REIMS Executive</h1>
        <p className="text-2xl mb-8">Real Estate Intelligence & Management System</p>
        <div className="bg-white/10 backdrop-blur-md rounded-2xl p-8 border border-white/20">
          <h2 className="text-3xl font-semibold mb-6">System Status</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-center space-x-3">
              <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
              <span className="text-lg">Frontend: Running</span>
            </div>
            <div className="flex items-center justify-center space-x-3">
              <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
              <span className="text-lg">React: Loaded</span>
            </div>
            <div className="flex items-center justify-center space-x-3">
              <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
              <span className="text-lg">Tailwind: Active</span>
            </div>
          </div>
          <button 
            className="mt-6 px-6 py-3 bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700 rounded-lg font-semibold transition-all duration-200"
            onClick={() => alert('React is working!')}
          >
            Test Interaction
          </button>
        </div>
      </div>
    </div>
  );
}

export default SimpleTest;