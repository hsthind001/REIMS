import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  TrendingUp, 
  RefreshCw, 
  DollarSign, 
  BarChart3,
  Calculator,
  Target,
  AlertTriangle,
  CheckCircle,
  XCircle,
  ArrowUp,
  ArrowDown,
  Minus
} from 'lucide-react';

// Main Exit Strategy Dashboard
export function ExitStrategyDashboard({ propertyId }) {
  const [analysis, setAnalysis] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const runAnalysis = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`/api/exit-strategy/analyze/${propertyId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Analysis failed');
      }
      
      const data = await response.json();
      setAnalysis(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (propertyId) {
      runAnalysis();
    }
  }, [propertyId]);

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full"></div>
        <span className="ml-3">Analyzing exit strategies...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="flex items-center gap-2 text-red-800">
          <AlertTriangle className="w-5 h-5" />
          <span className="font-semibold">Analysis Error</span>
        </div>
        <p className="text-red-700 mt-2">{error}</p>
        <button
          onClick={runAnalysis}
          className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
        >
          Retry Analysis
        </button>
      </div>
    );
  }

  if (!analysis) {
    return (
      <div className="text-center py-8">
        <Calculator className="w-12 h-12 mx-auto mb-4 text-gray-400" />
        <p className="text-gray-600">No exit strategy analysis available</p>
        <button
          onClick={runAnalysis}
          className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Run Exit Strategy Analysis
        </button>
      </div>
    );
  }

  const { scenarios, recommendation } = analysis;

  return (
    <div className="space-y-6">
      {/* Recommendation Banner */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className={`border-l-4 p-6 rounded-lg ${
          recommendation.recommended_strategy === 'hold' ? 'border-green-500 bg-green-50' :
          recommendation.recommended_strategy === 'refinance' ? 'border-blue-500 bg-blue-50' :
          'border-purple-500 bg-purple-50'
        }`}
      >
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Recommended Strategy: {recommendation.recommended_strategy.toUpperCase()}
            </h2>
            <p className="text-gray-700 mb-2">
              Confidence: {Math.round(recommendation.confidence * 100)}%
            </p>
            <p className="text-sm text-gray-600">
              {recommendation.rationale}
            </p>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold text-gray-900">
              {Math.round(recommendation.confidence * 100)}%
            </div>
            <div className="text-sm text-gray-600">Confidence</div>
          </div>
        </div>
      </motion.div>

      {/* Scenario Comparison */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <ScenarioCard
          icon={<TrendingUp className="w-6 h-6" />}
          title="Hold"
          scenario={scenarios.hold}
          isRecommended={recommendation.recommended_strategy === 'hold'}
        />
        <ScenarioCard
          icon={<RefreshCw className="w-6 h-6" />}
          title="Refinance"
          scenario={scenarios.refinance}
          isRecommended={recommendation.recommended_strategy === 'refinance'}
        />
        <ScenarioCard
          icon={<DollarSign className="w-6 h-6" />}
          title="Sell"
          scenario={scenarios.sale}
          isRecommended={recommendation.recommended_strategy === 'sale'}
        />
      </div>

      {/* Analysis Details */}
      <AnalysisDetails analysis={analysis} />
    </div>
  );
}

// Scenario Card Component
function ScenarioCard({ icon, title, scenario, isRecommended }) {
  const getStatusIcon = () => {
    if (isRecommended) return <CheckCircle className="w-5 h-5 text-green-600" />;
    return <Minus className="w-5 h-5 text-gray-400" />;
  };

  const getStatusColor = () => {
    if (isRecommended) return 'ring-2 ring-green-500 bg-green-50';
    return 'bg-white';
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`border rounded-lg p-6 ${getStatusColor()}`}
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          {icon}
          <h3 className="font-bold text-lg">{title}</h3>
        </div>
        <div className="flex items-center gap-2">
          {getStatusIcon()}
          {isRecommended && (
            <span className="text-xs bg-green-600 text-white px-2 py-1 rounded">
              RECOMMENDED
            </span>
          )}
        </div>
      </div>

      <div className="space-y-4">
        {/* Key Metrics */}
        {scenario.irr && (
          <MetricRow
            label="IRR"
            value={`${(scenario.irr * 100).toFixed(1)}%`}
            trend={scenario.irr > 0.1 ? 'up' : scenario.irr > 0.05 ? 'neutral' : 'down'}
          />
        )}
        
        {scenario.net_proceeds && (
          <MetricRow
            label="Net Proceeds"
            value={`$${(scenario.net_proceeds / 1000000).toFixed(2)}M`}
            trend="up"
          />
        )}
        
        {scenario.monthly_savings && (
          <MetricRow
            label="Monthly Savings"
            value={`$${scenario.monthly_savings.toLocaleString()}`}
            trend={scenario.monthly_savings > 0 ? 'up' : 'down'}
          />
        )}

        {scenario.cash_out && (
          <MetricRow
            label="Cash Out"
            value={`$${scenario.cash_out.toLocaleString()}`}
            trend="up"
          />
        )}

        {/* Pros and Cons */}
        <div className="grid grid-cols-1 gap-4">
          <div>
            <div className="text-sm font-semibold text-green-700 mb-1">Pros:</div>
            <ul className="text-xs space-y-1">
              {scenario.pros?.map((pro, i) => (
                <li key={i} className="flex items-start gap-1">
                  <CheckCircle className="w-3 h-3 text-green-600 mt-0.5 flex-shrink-0" />
                  <span>{pro}</span>
                </li>
              ))}
            </ul>
          </div>
          
          <div>
            <div className="text-sm font-semibold text-red-700 mb-1">Cons:</div>
            <ul className="text-xs space-y-1">
              {scenario.cons?.map((con, i) => (
                <li key={i} className="flex items-start gap-1">
                  <XCircle className="w-3 h-3 text-red-600 mt-0.5 flex-shrink-0" />
                  <span>{con}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

// Metric Row Component
function MetricRow({ label, value, trend }) {
  const getTrendIcon = () => {
    switch (trend) {
      case 'up': return <ArrowUp className="w-4 h-4 text-green-600" />;
      case 'down': return <ArrowDown className="w-4 h-4 text-red-600" />;
      default: return <Minus className="w-4 h-4 text-gray-400" />;
    }
  };

  return (
    <div className="flex items-center justify-between">
      <span className="text-sm text-gray-600">{label}</span>
      <div className="flex items-center gap-2">
        <span className="text-lg font-bold">{value}</span>
        {getTrendIcon()}
      </div>
    </div>
  );
}

// Analysis Details Component
function AnalysisDetails({ analysis }) {
  const [activeTab, setActiveTab] = useState('scenarios');

  const tabs = [
    { id: 'scenarios', label: 'Scenarios', icon: <BarChart3 className="w-4 h-4" /> },
    { id: 'metrics', label: 'Metrics', icon: <Calculator className="w-4 h-4" /> },
    { id: 'market', label: 'Market', icon: <TrendingUp className="w-4 h-4" /> }
  ];

  return (
    <div className="bg-white rounded-lg border">
      <div className="border-b">
        <nav className="flex space-x-8 px-6">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      <div className="p-6">
        {activeTab === 'scenarios' && (
          <ScenariosTab analysis={analysis} />
        )}
        {activeTab === 'metrics' && (
          <MetricsTab analysis={analysis} />
        )}
        {activeTab === 'market' && (
          <MarketTab analysis={analysis} />
        )}
      </div>
    </div>
  );
}

// Scenarios Tab
function ScenariosTab({ analysis }) {
  const { scenarios } = analysis;

  return (
    <div className="space-y-6">
      <h3 className="text-lg font-semibold">Detailed Scenario Analysis</h3>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {Object.entries(scenarios).map(([strategy, data]) => (
          <div key={strategy} className="border rounded-lg p-4">
            <h4 className="font-semibold mb-3 capitalize">{strategy} Strategy</h4>
            
            <div className="space-y-3">
              {data.irr && (
                <div>
                  <span className="text-sm text-gray-600">IRR:</span>
                  <span className="ml-2 font-bold">{(data.irr * 100).toFixed(1)}%</span>
                </div>
              )}
              
              {data.net_proceeds && (
                <div>
                  <span className="text-sm text-gray-600">Net Proceeds:</span>
                  <span className="ml-2 font-bold">${(data.net_proceeds / 1000000).toFixed(2)}M</span>
                </div>
              )}
              
              {data.monthly_savings && (
                <div>
                  <span className="text-sm text-gray-600">Monthly Savings:</span>
                  <span className="ml-2 font-bold">${data.monthly_savings.toLocaleString()}</span>
                </div>
              )}
              
              {data.cash_out && (
                <div>
                  <span className="text-sm text-gray-600">Cash Out:</span>
                  <span className="ml-2 font-bold">${data.cash_out.toLocaleString()}</span>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// Metrics Tab
function MetricsTab({ analysis }) {
  const { property_metrics } = analysis;

  return (
    <div className="space-y-6">
      <h3 className="text-lg font-semibold">Property Financial Metrics</h3>
      
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          label="NOI"
          value={`$${property_metrics.noi?.toLocaleString() || 'N/A'}`}
          description="Net Operating Income"
        />
        <MetricCard
          label="Cap Rate"
          value={`${(property_metrics.cap_rate * 100)?.toFixed(1) || 'N/A'}%`}
          description="Capitalization Rate"
        />
        <MetricCard
          label="Occupancy"
          value={`${(property_metrics.occupancy * 100)?.toFixed(1) || 'N/A'}%`}
          description="Occupancy Rate"
        />
        <MetricCard
          label="DSCR"
          value={property_metrics.dscr?.toFixed(2) || 'N/A'}
          description="Debt Service Coverage Ratio"
        />
        <MetricCard
          label="Property Value"
          value={`$${(property_metrics.estimated_value / 1000000)?.toFixed(2) || 'N/A'}M`}
          description="Estimated Market Value"
        />
        <MetricCard
          label="Loan Balance"
          value={`$${(property_metrics.loan_balance / 1000000)?.toFixed(2) || 'N/A'}M`}
          description="Outstanding Loan Balance"
        />
        <MetricCard
          label="Equity"
          value={`$${(property_metrics.equity / 1000000)?.toFixed(2) || 'N/A'}M`}
          description="Owner Equity"
        />
        <MetricCard
          label="Interest Rate"
          value={`${(property_metrics.interest_rate * 100)?.toFixed(2) || 'N/A'}%`}
          description="Current Interest Rate"
        />
      </div>
    </div>
  );
}

// Market Tab
function MarketTab({ analysis }) {
  const { market_conditions } = analysis;

  return (
    <div className="space-y-6">
      <h3 className="text-lg font-semibold">Market Conditions</h3>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-4">
          <h4 className="font-semibold">Market Metrics</h4>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-600">Market Cap Rate:</span>
              <span className="font-semibold">{(market_conditions.market_cap_rate * 100).toFixed(1)}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">NOI Growth Rate:</span>
              <span className="font-semibold">{(market_conditions.noi_growth_rate * 100).toFixed(1)}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Current Mortgage Rate:</span>
              <span className="font-semibold">{(market_conditions.current_mortgage_rate * 100).toFixed(2)}%</span>
            </div>
          </div>
        </div>
        
        <div className="space-y-4">
          <h4 className="font-semibold">Property Adjustments</h4>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-600">Condition Adjustment:</span>
              <span className="font-semibold">{(market_conditions.condition_adjustment * 100).toFixed(0)}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Location Premium:</span>
              <span className="font-semibold">{(market_conditions.location_premium * 100).toFixed(0)}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Market Trends:</span>
              <span className="font-semibold capitalize">{market_conditions.market_trends}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Metric Card Component
function MetricCard({ label, value, description }) {
  return (
    <div className="bg-gray-50 rounded-lg p-4">
      <div className="text-sm text-gray-600 mb-1">{label}</div>
      <div className="text-2xl font-bold text-gray-900 mb-1">{value}</div>
      <div className="text-xs text-gray-500">{description}</div>
    </div>
  );
}

// Portfolio Analysis Component
export function PortfolioExitStrategy({ propertyIds }) {
  const [portfolioAnalysis, setPortfolioAnalysis] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const analyzePortfolio = async () => {
    setIsLoading(true);
    
    try {
      const response = await fetch('/api/exit-strategy/portfolio', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(propertyIds)
      });
      
      const data = await response.json();
      setPortfolioAnalysis(data);
    } catch (error) {
      console.error('Portfolio analysis error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (propertyIds && propertyIds.length > 0) {
      analyzePortfolio();
    }
  }, [propertyIds]);

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full"></div>
        <span className="ml-3">Analyzing portfolio...</span>
      </div>
    );
  }

  if (!portfolioAnalysis) {
    return (
      <div className="text-center py-8">
        <Target className="w-12 h-12 mx-auto mb-4 text-gray-400" />
        <p className="text-gray-600">No portfolio analysis available</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg border p-6">
        <h3 className="text-lg font-semibold mb-4">Portfolio Exit Strategy Summary</h3>
        
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">{portfolioAnalysis.analysis_count}</div>
            <div className="text-sm text-gray-600">Properties Analyzed</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">
              {Math.round(portfolioAnalysis.average_confidence * 100)}%
            </div>
            <div className="text-sm text-gray-600">Avg Confidence</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">
              ${(portfolioAnalysis.total_equity / 1000000).toFixed(1)}M
            </div>
            <div className="text-sm text-gray-600">Total Equity</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-orange-600">
              ${(portfolioAnalysis.total_value / 1000000).toFixed(1)}M
            </div>
            <div className="text-sm text-gray-600">Total Value</div>
          </div>
        </div>

        <div className="space-y-4">
          <h4 className="font-semibold">Strategy Distribution</h4>
          <div className="grid grid-cols-3 gap-4">
            {Object.entries(portfolioAnalysis.strategy_distribution).map(([strategy, count]) => (
              <div key={strategy} className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-gray-900">{count}</div>
                <div className="text-sm text-gray-600 capitalize">{strategy}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
