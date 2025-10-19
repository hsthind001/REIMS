import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Brain, 
  FileText, 
  MessageSquare, 
  TrendingUp, 
  AlertTriangle,
  Sparkles,
  BarChart3,
  MapPin,
  Users,
  Zap
} from 'lucide-react';

// AI Chat Component
export function AIChatInterface() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('/api/ai/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ query: input })
      });

      const data = await response.json();
      
      if (data.response) {
        setMessages(prev => [...prev, { role: 'assistant', content: data.response }]);
      }
    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'Sorry, I encountered an error. Please try again.' 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="h-[600px] flex flex-col border rounded-lg bg-white">
      <div className="p-4 bg-gradient-to-r from-purple-600 to-blue-600 text-white border-b">
        <div className="flex items-center gap-2">
          <Brain className="w-5 h-5" />
          <span className="font-semibold">REIMS AI Assistant</span>
          <div className="ml-auto flex items-center gap-1 text-sm">
            <div className="w-2 h-2 bg-green-400 rounded-full"></div>
            <span>Online</span>
          </div>
        </div>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 py-8">
            <Brain className="w-12 h-12 mx-auto mb-4 text-gray-300" />
            <p>Ask me anything about your properties, market analysis, or real estate insights!</p>
          </div>
        )}
        
        {messages.map((msg, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div className={`max-w-[80%] p-3 rounded-lg ${
              msg.role === 'user' 
                ? 'bg-blue-600 text-white ml-12' 
                : 'bg-gray-100 text-gray-900 mr-12'
            }`}>
              <p className="whitespace-pre-wrap">{msg.content}</p>
            </div>
          </motion.div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 p-3 rounded-lg mr-12">
              <div className="flex items-center gap-2">
                <div className="animate-spin w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full"></div>
                <span>AI is thinking...</span>
              </div>
            </div>
          </div>
        )}
      </div>
      
      <div className="p-4 border-t">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
            placeholder="Ask about properties, market trends, or get recommendations..."
            className="flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={isLoading}
          />
          <button
            onClick={sendMessage}
            disabled={!input.trim() || isLoading}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}

// Document Summarization Component
export function DocumentSummarization({ documentId, onSummaryGenerated }) {
  const [isSummarizing, setIsSummarizing] = useState(false);
  const [summary, setSummary] = useState(null);
  const [documentType, setDocumentType] = useState('lease');

  const generateSummary = async () => {
    setIsSummarizing(true);
    
    try {
      const response = await fetch(`/api/ai/summarize/${documentId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: `document_type=${documentType}`
      });

      const data = await response.json();
      
      if (data.summary) {
        setSummary(data);
        onSummaryGenerated?.(data);
      }
    } catch (error) {
      console.error('Summarization error:', error);
    } finally {
      setIsSummarizing(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-4">
        <select
          value={documentType}
          onChange={(e) => setDocumentType(e.target.value)}
          className="px-3 py-2 border rounded-lg"
        >
          <option value="lease">Lease Document</option>
          <option value="offering_memorandum">Offering Memorandum</option>
          <option value="financial_statement">Financial Statement</option>
        </select>
        
        <button
          onClick={generateSummary}
          disabled={isSummarizing}
          className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 flex items-center gap-2"
        >
          <Sparkles className="w-4 h-4" />
          {isSummarizing ? 'Generating Summary...' : 'Generate AI Summary'}
        </button>
      </div>

      {summary && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="border rounded-lg p-6 bg-gradient-to-r from-purple-50 to-blue-50"
        >
          <div className="flex items-center gap-2 mb-4">
            <Brain className="w-5 h-5 text-purple-600" />
            <span className="font-semibold text-purple-900">
              AI-Generated Summary (Confidence: {Math.round(summary.confidence * 100)}%)
            </span>
          </div>
          
          <div className="prose prose-sm max-w-none">
            {summary.summary.split('\n').map((line, i) => (
              <p key={i} className="mb-2">{line}</p>
            ))}
          </div>
          
          <div className="mt-4 text-xs text-gray-500 border-t pt-2">
            ⚠️ Machine-generated content. Verify critical details. | Model: {summary.model} | Generated: {new Date(summary.generated_at).toLocaleString()}
          </div>
        </motion.div>
      )}
    </div>
  );
}

// Market Intelligence Component
export function MarketIntelligence({ propertyId }) {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const [location, setLocation] = useState({ address: '', city: '', state: '' });

  const runAnalysis = async () => {
    setIsAnalyzing(true);
    
    try {
      const response = await fetch('/api/market/analyze-location', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          address: location.address,
          city: location.city,
          state: location.state,
          property_type: 'commercial'
        })
      });

      const data = await response.json();
      setAnalysis(data);
    } catch (error) {
      console.error('Analysis error:', error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg p-6 border">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <MapPin className="w-5 h-5 text-blue-600" />
          Market Intelligence Analysis
        </h3>
        
        <div className="grid grid-cols-3 gap-4 mb-4">
          <input
            type="text"
            placeholder="Address"
            value={location.address}
            onChange={(e) => setLocation({...location, address: e.target.value})}
            className="px-3 py-2 border rounded-lg"
          />
          <input
            type="text"
            placeholder="City"
            value={location.city}
            onChange={(e) => setLocation({...location, city: e.target.value})}
            className="px-3 py-2 border rounded-lg"
          />
          <input
            type="text"
            placeholder="State"
            value={location.state}
            onChange={(e) => setLocation({...location, state: e.target.value})}
            className="px-3 py-2 border rounded-lg"
          />
        </div>
        
        <button
          onClick={runAnalysis}
          disabled={isAnalyzing || !location.address || !location.city || !location.state}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
        >
          <TrendingUp className="w-4 h-4" />
          {isAnalyzing ? 'Analyzing...' : 'Run Market Analysis'}
        </button>
      </div>

      {analysis && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-4"
        >
          <div className="bg-white rounded-lg p-6 border">
            <h4 className="font-semibold mb-2">Market Analysis</h4>
            <div className="prose prose-sm max-w-none">
              {analysis.analysis.split('\n').map((line, i) => (
                <p key={i} className="mb-2">{line}</p>
              ))}
            </div>
          </div>
          
          {analysis.market_data && Object.keys(analysis.market_data).length > 0 && (
            <div className="bg-white rounded-lg p-6 border">
              <h4 className="font-semibold mb-2">Market Data</h4>
              <div className="space-y-2">
                {Object.entries(analysis.market_data).map(([key, value]) => (
                  <div key={key} className="text-sm">
                    <span className="font-medium">{key}:</span>
                    <span className="ml-2 text-gray-600">{value.length} results</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </motion.div>
      )}
    </div>
  );
}

// Tenant Recommendations Component
export function TenantRecommendations({ propertyId }) {
  const [recommendations, setRecommendations] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [availableSqft, setAvailableSqft] = useState('');
  const [currentTenants, setCurrentTenants] = useState('');

  const generateRecommendations = async () => {
    setIsGenerating(true);
    
    try {
      const response = await fetch('/api/market/recommend-tenants', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          property_id: propertyId,
          available_sqft: parseFloat(availableSqft),
          current_tenants: currentTenants.split(',').map(t => t.trim()).filter(t => t)
        })
      });

      const data = await response.json();
      setRecommendations(data);
    } catch (error) {
      console.error('Recommendations error:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg p-6 border">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Users className="w-5 h-5 text-green-600" />
          AI Tenant Recommendations
        </h3>
        
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium mb-2">Available Square Footage</label>
            <input
              type="number"
              value={availableSqft}
              onChange={(e) => setAvailableSqft(e.target.value)}
              placeholder="e.g., 5000"
              className="w-full px-3 py-2 border rounded-lg"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Current Tenants (comma-separated)</label>
            <input
              type="text"
              value={currentTenants}
              onChange={(e) => setCurrentTenants(e.target.value)}
              placeholder="e.g., Starbucks, Bank of America"
              className="w-full px-3 py-2 border rounded-lg"
            />
          </div>
        </div>
        
        <button
          onClick={generateRecommendations}
          disabled={isGenerating || !availableSqft}
          className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 flex items-center gap-2"
        >
          <Brain className="w-4 h-4" />
          {isGenerating ? 'Generating...' : 'Get AI Recommendations'}
        </button>
      </div>

      {recommendations && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-4"
        >
          <div className="bg-white rounded-lg p-6 border">
            <h4 className="font-semibold mb-4">Recommended Tenants</h4>
            <div className="space-y-4">
              {recommendations.recommendations.map((rec, i) => (
                <div key={i} className="border rounded-lg p-4 bg-gray-50">
                  <div className="flex items-start justify-between mb-2">
                    <h5 className="font-medium text-lg">{rec.business_type}</h5>
                    <span className="text-sm text-gray-500">#{rec.rank}</span>
                  </div>
                  <p className="text-gray-700 mb-2">{rec.rationale}</p>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="font-medium">Rent Range:</span> {rec.rent_range}
                    </div>
                    <div>
                      <span className="font-medium">Confidence:</span> {Math.round(rec.confidence * 100)}%
                    </div>
                  </div>
                  <div className="mt-2 text-sm">
                    <span className="font-medium">Synergies:</span> {rec.synergies}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
}

// Anomaly Detection Dashboard
export function AnomalyDetectionDashboard({ propertyId }) {
  const [anomalies, setAnomalies] = useState([]);
  const [statistics, setStatistics] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchAnomalies();
    fetchStatistics();
  }, [propertyId]);

  const fetchAnomalies = async () => {
    try {
      const response = await fetch(`/api/market/anomalies/${propertyId}?days_back=30`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const data = await response.json();
      setAnomalies(data);
    } catch (error) {
      console.error('Error fetching anomalies:', error);
    }
  };

  const fetchStatistics = async () => {
    try {
      const response = await fetch(`/api/market/anomalies/statistics?property_id=${propertyId}&days_back=30`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const data = await response.json();
      setStatistics(data);
    } catch (error) {
      console.error('Error fetching statistics:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return <div className="flex justify-center p-8">Loading anomaly data...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg p-6 border">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 text-orange-600" />
          Anomaly Detection Dashboard
        </h3>
        
        {statistics && (
          <div className="grid grid-cols-4 gap-4 mb-6">
            <div className="text-center p-4 bg-red-50 rounded-lg">
              <div className="text-2xl font-bold text-red-600">{statistics.total_anomalies}</div>
              <div className="text-sm text-red-700">Total Anomalies</div>
            </div>
            <div className="text-center p-4 bg-orange-50 rounded-lg">
              <div className="text-2xl font-bold text-orange-600">{statistics.by_confidence.high}</div>
              <div className="text-sm text-orange-700">High Confidence</div>
            </div>
            <div className="text-center p-4 bg-yellow-50 rounded-lg">
              <div className="text-2xl font-bold text-yellow-600">{statistics.by_confidence.medium}</div>
              <div className="text-sm text-yellow-700">Medium Confidence</div>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="text-2xl font-bold text-green-600">{statistics.by_confidence.low}</div>
              <div className="text-sm text-green-700">Low Confidence</div>
            </div>
          </div>
        )}
        
        <div className="space-y-4">
          {anomalies.map((anomaly, i) => (
            <div key={i} className="border rounded-lg p-4 bg-gray-50">
              <div className="flex items-center justify-between mb-2">
                <h5 className="font-medium">{anomaly.metric_name}</h5>
                <span className={`px-2 py-1 rounded text-xs ${
                  anomaly.confidence >= 0.8 ? 'bg-red-100 text-red-800' :
                  anomaly.confidence >= 0.6 ? 'bg-orange-100 text-orange-800' :
                  'bg-yellow-100 text-yellow-800'
                }`}>
                  {Math.round(anomaly.confidence * 100)}% confidence
                </span>
              </div>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="font-medium">Value:</span> {anomaly.value}
                </div>
                <div>
                  <span className="font-medium">Method:</span> {anomaly.detection_method}
                </div>
                {anomaly.z_score && (
                  <div>
                    <span className="font-medium">Z-Score:</span> {anomaly.z_score.toFixed(2)}
                  </div>
                )}
                {anomaly.trend_direction && (
                  <div>
                    <span className="font-medium">Trend:</span> {anomaly.trend_direction}
                  </div>
                )}
              </div>
              <div className="mt-2 text-xs text-gray-500">
                Detected: {new Date(anomaly.timestamp).toLocaleString()}
              </div>
            </div>
          ))}
          
          {anomalies.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              <AlertTriangle className="w-12 h-12 mx-auto mb-4 text-gray-300" />
              <p>No anomalies detected in the last 30 days</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
