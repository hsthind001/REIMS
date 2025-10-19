import React, { useState, useEffect } from "react";

function ExecutiveApp() {
  const [currentTime, setCurrentTime] = useState(new Date());
  const [isLoading, setIsLoading] = useState(true);
  const [activeSection, setActiveSection] = useState('dashboard');

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    setTimeout(() => setIsLoading(false), 1000);
    return () => clearInterval(timer);
  }, []);

  const handleSectionChange = (section) => {
    setActiveSection(section);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900 flex items-center justify-center">
        <div className="text-white text-2xl font-bold">Loading REIMS Executive Dashboard...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900">
      <header className="bg-white/10 backdrop-blur-md border-b border-white/20 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-10 h-10 bg-gradient-to-r from-blue-400 to-purple-500 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-xl">R</span>
            </div>
            <div>
              <h1 className="text-white text-xl font-bold">REIMS Executive</h1>
              <p className="text-blue-200 text-sm">Real Estate Intelligence & Management</p>
            </div>
          </div>
          <div className="text-white text-sm">
            {currentTime.toLocaleString()}
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        {activeSection === 'dashboard' && (
          <div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <MetricCard title="Total Portfolio Value" value="$45.2M" change="+12.3%" positive={true} icon="💰" />
              <MetricCard title="Active Properties" value="127" change="+5" positive={true} icon="🏢" />
              <MetricCard title="Monthly Revenue" value="$892K" change="+8.1%" positive={true} icon="📈" />
              <MetricCard title="Occupancy Rate" value="94.2%" change="-1.2%" positive={false} icon="🏠" />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <ActionCard 
                title="Property Management"
                description="View and manage your property portfolio"
                icon="🏢"
                color="blue"
                onClick={() => handleSectionChange('properties')}
              />
              <ActionCard 
                title="Analytics Dashboard"
                description="Deep insights and performance metrics"
                icon="📊"
                color="purple"
                onClick={() => handleSectionChange('analytics')}
              />
              <ActionCard 
                title="Document Center"
                description="AI-powered document management"
                icon="📄"
                color="green"
                onClick={() => handleSectionChange('documents')}
              />
            </div>

            <div className="mt-8">
              <div className="bg-white/10 backdrop-blur-md rounded-xl border border-white/20 p-6">
                <h3 className="text-white text-xl font-bold mb-4">Recent Activity</h3>
                <div className="space-y-3">
                  <ActivityItem text="New lease agreement signed for Property #127" time="2 hours ago" type="success" />
                  <ActivityItem text="Monthly report generated for October 2025" time="4 hours ago" type="info" />
                  <ActivityItem text="Maintenance request completed at Sunset Plaza" time="6 hours ago" type="success" />
                </div>
              </div>
            </div>
          </div>
        )}

        {activeSection === 'properties' && <PropertySection onBack={() => handleSectionChange('dashboard')} />}
        {activeSection === 'analytics' && <AnalyticsSection onBack={() => handleSectionChange('dashboard')} />}
        {activeSection === 'documents' && <DocumentSection onBack={() => handleSectionChange('dashboard')} />}
      </main>
    </div>
  );
}

function MetricCard({ title, value, change, positive, icon }) {
  return (
    <div className="bg-white/10 backdrop-blur-md rounded-xl border border-white/20 p-6 hover:bg-white/15 transition-all duration-300">
      <div className="flex items-center justify-between mb-2">
        <span className="text-2xl">{icon}</span>
        <span className={`text-sm font-medium px-2 py-1 rounded-full ${
          positive ? 'bg-green-500/20 text-green-300' : 'bg-red-500/20 text-red-300'
        }`}>
          {change}
        </span>
      </div>
      <h3 className="text-white/80 text-sm font-medium">{title}</h3>
      <p className="text-white text-2xl font-bold">{value}</p>
    </div>
  );
}

function ActionCard({ title, description, icon, color, onClick }) {
  const colorClasses = {
    blue: 'from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700',
    purple: 'from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700',
    green: 'from-green-500 to-green-600 hover:from-green-600 hover:to-green-700'
  };

  return (
    <div 
      onClick={onClick}
      className={`bg-gradient-to-r ${colorClasses[color]} rounded-xl p-6 cursor-pointer transform hover:scale-105 transition-all duration-300 shadow-lg hover:shadow-xl`}
    >
      <div className="text-3xl mb-3">{icon}</div>
      <h3 className="text-white text-lg font-bold mb-2">{title}</h3>
      <p className="text-white/90 text-sm">{description}</p>
    </div>
  );
}

function ActivityItem({ text, time, type }) {
  const typeClasses = {
    success: 'bg-green-500',
    info: 'bg-blue-500',
    warning: 'bg-yellow-500'
  };

  return (
    <div className="flex items-center space-x-3">
      <div className={`w-3 h-3 rounded-full ${typeClasses[type]}`}></div>
      <div className="flex-1">
        <p className="text-white text-sm">{text}</p>
        <p className="text-white/60 text-xs">{time}</p>
      </div>
    </div>
  );
}

function PropertySection({ onBack }) {
  return (
    <div>
      <div className="flex items-center mb-6">
        <button 
          onClick={onBack}
          className="bg-white/10 backdrop-blur-md border border-white/20 text-white px-4 py-2 rounded-lg hover:bg-white/20 transition-all mr-4"
        >
          ← Back to Dashboard
        </button>
        <h2 className="text-white text-2xl font-bold">Property Management</h2>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white/10 backdrop-blur-md rounded-xl border border-white/20 p-6">
          <h3 className="text-white text-xl font-bold mb-4">🏢 Sunset Plaza</h3>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-white/80">Property Value:</span>
              <span className="text-white font-semibold">$12.5M</span>
            </div>
            <div className="flex justify-between">
              <span className="text-white/80">Occupancy Rate:</span>
              <span className="text-white font-semibold">95%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-white/80">Monthly Income:</span>
              <span className="text-white font-semibold">$125K</span>
            </div>
          </div>
          <button className="w-full mt-4 bg-gradient-to-r from-blue-500 to-purple-600 text-white py-2 rounded-lg hover:from-blue-600 hover:to-purple-700 transition-all">
            View Details
          </button>
        </div>
        
        <div className="bg-white/10 backdrop-blur-md rounded-xl border border-white/20 p-6">
          <h3 className="text-white text-xl font-bold mb-4">🏢 Harbor View Towers</h3>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-white/80">Property Value:</span>
              <span className="text-white font-semibold">$18.2M</span>
            </div>
            <div className="flex justify-between">
              <span className="text-white/80">Occupancy Rate:</span>
              <span className="text-white font-semibold">88%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-white/80">Monthly Income:</span>
              <span className="text-white font-semibold">$180K</span>
            </div>
          </div>
          <button className="w-full mt-4 bg-gradient-to-r from-blue-500 to-purple-600 text-white py-2 rounded-lg hover:from-blue-600 hover:to-purple-700 transition-all">
            View Details
          </button>
        </div>
      </div>
    </div>
  );
}

function AnalyticsSection({ onBack }) {
  return (
    <div>
      <div className="flex items-center mb-6">
        <button 
          onClick={onBack}
          className="bg-white/10 backdrop-blur-md border border-white/20 text-white px-4 py-2 rounded-lg hover:bg-white/20 transition-all mr-4"
        >
          ← Back to Dashboard
        </button>
        <h2 className="text-white text-2xl font-bold">Analytics Dashboard</h2>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white/10 backdrop-blur-md rounded-xl border border-white/20 p-6">
          <h3 className="text-white text-xl font-bold mb-4">📈 Revenue Performance</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-white/80">Q1 2025</span>
              <span className="text-white">$2.4M</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-white/80">Q2 2025</span>
              <span className="text-white">$2.7M</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-white/80">Q3 2025</span>
              <span className="text-white">$3.1M</span>
            </div>
          </div>
        </div>

        <div className="bg-white/10 backdrop-blur-md rounded-xl border border-white/20 p-6">
          <h3 className="text-white text-xl font-bold mb-4">🎯 Market Insights</h3>
          <div className="space-y-4">
            <div className="flex items-center p-3 bg-green-500/20 rounded-lg">
              <span className="text-2xl mr-3">📊</span>
              <div>
                <p className="text-green-300 font-semibold">Market Growth</p>
                <p className="text-white/80 text-sm">Property values up 15% YoY</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function DocumentSection({ onBack }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [documents, setDocuments] = useState([
    { name: "Q3 2025 Financial Report", type: "PDF", size: "2.4 MB", date: "Oct 5, 2025", status: "processed" },
    { name: "Lease Agreement - Sunset Plaza", type: "PDF", size: "1.8 MB", date: "Oct 3, 2025", status: "processed" },
    { name: "Property Inspection - Harbor View", type: "PDF", size: "3.1 MB", date: "Oct 1, 2025", status: "processing" },
    { name: "Insurance Policy Updates", type: "DOCX", size: "890 KB", date: "Sep 28, 2025", status: "processed" },
  ]);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    setSelectedFile(file);
    setUploadStatus(null);
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setUploadStatus({ type: 'error', message: 'Please select a file first' });
      return;
    }

    setUploading(true);
    setUploadStatus(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('property_id', 'default-property');

      const response = await fetch('http://localhost:8001/api/documents/upload', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        setUploadStatus({ type: 'success', message: `File "${selectedFile.name}" uploaded successfully!` });
        
        // Add the uploaded document to the list
        const newDoc = {
          name: selectedFile.name,
          type: selectedFile.name.split('.').pop().toUpperCase(),
          size: `${(selectedFile.size / 1024 / 1024).toFixed(1)} MB`,
          date: new Date().toLocaleDateString(),
          status: "processing"
        };
        setDocuments([newDoc, ...documents]);
        setSelectedFile(null);
        
        // Reset file input
        const fileInput = document.getElementById('file-upload');
        if (fileInput) fileInput.value = '';
      } else {
        const error = await response.json();
        setUploadStatus({ type: 'error', message: error.detail || 'Upload failed' });
      }
    } catch (error) {
      console.error('Upload error:', error);
      setUploadStatus({ type: 'error', message: 'Upload failed. Please check your connection.' });
    } finally {
      setUploading(false);
    }
  };

  return (
    <div>
      <div className="flex items-center mb-6">
        <button 
          onClick={onBack}
          className="bg-white/10 backdrop-blur-md border border-white/20 text-white px-4 py-2 rounded-lg hover:bg-white/20 transition-all mr-4"
        >
          ← Back to Dashboard
        </button>
        <h2 className="text-white text-2xl font-bold">Document Center</h2>
      </div>
      
      <div className="bg-gradient-to-r from-green-500 to-teal-600 rounded-xl p-6 mb-6">
        <h3 className="text-white text-xl font-bold mb-4">📄 AI-Powered Document Processing</h3>
        <p className="text-white/90 mb-4">Upload documents for automatic analysis and insights</p>
        
        {/* File Upload Section */}
        <div className="space-y-4">
          <div className="flex items-center space-x-4">
            <input
              id="file-upload"
              type="file"
              onChange={handleFileSelect}
              accept=".pdf,.doc,.docx,.txt,.csv,.xlsx"
              className="hidden"
            />
            <label
              htmlFor="file-upload"
              className="bg-white/20 backdrop-blur-md text-white px-4 py-2 rounded-lg hover:bg-white/30 transition-all cursor-pointer flex items-center space-x-2"
            >
              <span>📁</span>
              <span>Choose File</span>
            </label>
            
            {selectedFile && (
              <span className="text-white/90 text-sm">
                Selected: {selectedFile.name} ({(selectedFile.size / 1024 / 1024).toFixed(1)} MB)
              </span>
            )}
          </div>

          <button
            onClick={handleUpload}
            disabled={!selectedFile || uploading}
            className={`px-6 py-2 rounded-lg transition-all flex items-center space-x-2 ${
              selectedFile && !uploading
                ? 'bg-white/20 backdrop-blur-md text-white hover:bg-white/30'
                : 'bg-white/10 text-white/50 cursor-not-allowed'
            }`}
          >
            {uploading ? (
              <>
                <span className="animate-spin">⏳</span>
                <span>Uploading...</span>
              </>
            ) : (
              <>
                <span>⬆️</span>
                <span>Upload Document</span>
              </>
            )}
          </button>

          {/* Upload Status */}
          {uploadStatus && (
            <div className={`p-3 rounded-lg ${
              uploadStatus.type === 'success' 
                ? 'bg-green-500/20 text-green-300' 
                : 'bg-red-500/20 text-red-300'
            }`}>
              {uploadStatus.message}
            </div>
          )}
        </div>
      </div>

      {/* Documents List */}
      <div className="bg-white/10 backdrop-blur-md rounded-xl border border-white/20 p-6">
        <h3 className="text-white text-xl font-bold mb-4">Recent Documents</h3>
        <div className="space-y-3">
          {documents.map((doc, index) => (
            <div key={index} className="flex items-center justify-between p-4 bg-white/5 rounded-lg hover:bg-white/10 transition-all">
              <div className="flex items-center">
                <span className="text-2xl mr-4">📄</span>
                <div>
                  <p className="text-white font-semibold">{doc.name}</p>
                  <p className="text-white/60 text-sm">{doc.type} • {doc.size} • {doc.date}</p>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                  doc.status === 'processed' ? 'bg-green-500/20 text-green-300' : 'bg-yellow-500/20 text-yellow-300'
                }`}>
                  {doc.status === 'processed' ? '✅ Processed' : '⏳ Processing'}
                </span>
                <button className="text-blue-300 hover:text-blue-200 transition-all">
                  View
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default ExecutiveApp;