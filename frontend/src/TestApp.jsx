import React, { useState } from "react";

function TestApp() {
  const [currentView, setCurrentView] = useState('dashboard');

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-gray-800 mb-8 text-center">
          REIMS - Testing Components
        </h1>
        
        <div className="bg-white/70 backdrop-blur-lg rounded-xl p-8 border border-white/20 shadow-lg">
          <h2 className="text-2xl font-semibold text-gray-700 mb-4">Component Test</h2>
          <p className="text-gray-600 mb-4">
            Testing REIMS components step by step...
          </p>
          
          <div className="space-y-4">
            <div>
              <p className="text-lg">Current View: <span className="font-bold text-blue-600">{currentView}</span></p>
              <div className="flex space-x-2 mt-2">
                <button 
                  onClick={() => setCurrentView('dashboard')}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Dashboard
                </button>
                <button 
                  onClick={() => setCurrentView('upload')}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                >
                  Upload
                </button>
              </div>
            </div>
            
            <div className="pt-4 border-t">
              <p className="text-sm text-gray-500">
                ✅ React is working<br/>
                ✅ Tailwind CSS is working<br/>
                ✅ State management is working<br/>
                ✅ Basic interactions are working
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default TestApp;