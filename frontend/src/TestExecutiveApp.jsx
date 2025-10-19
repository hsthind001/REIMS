import React from "react";
import ExecutiveDashboard from "./components/ExecutiveDashboard.jsx";
import { Toaster } from "react-hot-toast";

function TestExecutiveApp() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <Toaster position="top-right" />
      
      <div className="p-4">
        <h1 className="text-white text-2xl mb-4">Testing Executive Dashboard</h1>
        <ExecutiveDashboard />
      </div>
    </div>
  );
}

export default TestExecutiveApp;