import React, { useState } from 'react';
import KPICard, { KPICardGrid, KPICardSkeleton } from './KPICard';

/**
 * Interactive Demo for KPICard Component
 * Showcases all features and variations
 */
export default function KPICardDemo() {
  const [loading, setLoading] = useState(false);
  const [clickedCard, setClickedCard] = useState(null);

  // Sample icons
  const DollarIcon = (props) => (
    <svg {...props} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  );

  const BuildingIcon = (props) => (
    <svg {...props} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
    </svg>
  );

  const ChartIcon = (props) => (
    <svg {...props} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
    </svg>
  );

  const UsersIcon = (props) => (
    <svg {...props} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
    </svg>
  );

  const handleCardClick = (cardName) => {
    setClickedCard(cardName);
    setTimeout(() => setClickedCard(null), 2000);
  };

  const toggleLoading = () => {
    setLoading(!loading);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-6">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl p-8 shadow-xl">
          <h1 className="text-4xl font-bold mb-3">KPICard Component Demo</h1>
          <p className="text-blue-100 text-lg mb-4">
            Interactive showcase of the reusable KPI Card component
          </p>
          <div className="flex gap-4">
            <button
              onClick={toggleLoading}
              className="px-4 py-2 bg-white/20 hover:bg-white/30 rounded-lg font-medium transition-colors backdrop-blur"
            >
              {loading ? 'Hide' : 'Show'} Loading State
            </button>
          </div>
          {clickedCard && (
            <div className="mt-4 px-4 py-2 bg-green-500 rounded-lg inline-block animate-bounce">
              Clicked: {clickedCard}
            </div>
          )}
        </div>

        {/* Section 1: Basic KPI Cards */}
        <section>
          <div className="mb-4">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              1. Primary KPI Cards
            </h2>
            <p className="text-gray-600">
              Basic cards with values, trends, icons, and different colors
            </p>
          </div>

          <KPICardGrid columns={4}>
            <KPICard
              title="Total Portfolio Value"
              value={47800000}
              unit="$"
              trend={8.2}
              trendUp={true}
              icon={DollarIcon}
              color="blue"
              subtitle="vs last quarter"
              loading={loading}
            />

            <KPICard
              title="Total Properties"
              value={184}
              trend={12}
              trendUp={true}
              icon={BuildingIcon}
              color="green"
              subtitle="12 new this month"
              loading={loading}
            />

            <KPICard
              title="Average Occupancy"
              value={94.6}
              unit="%"
              trend={2.4}
              trendUp={true}
              icon={ChartIcon}
              color="purple"
              subtitle="across all properties"
              loading={loading}
            />

            <KPICard
              title="Active Tenants"
              value={1247}
              trend={-3.2}
              trendUp={false}
              icon={UsersIcon}
              color="orange"
              subtitle="3 vacancies"
              loading={loading}
            />
          </KPICardGrid>
        </section>

        {/* Section 2: Number Formats */}
        <section>
          <div className="mb-4">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              2. Number Formatting
            </h2>
            <p className="text-gray-600">
              Automatic formatting for different number types and magnitudes
            </p>
          </div>

          <KPICardGrid columns={3}>
            {/* Large currency */}
            <KPICard
              title="Annual Revenue"
              value={125000000}
              unit="$"
              trend={15.3}
              color="green"
              subtitle="$125M formatted"
            />

            {/* Medium currency */}
            <KPICard
              title="Monthly NOI"
              value={3750000}
              unit="$"
              trend={5.7}
              color="blue"
              subtitle="$3.8M formatted"
            />

            {/* Small currency */}
            <KPICard
              title="Average Rent"
              value={2850}
              unit="$"
              trend={-1.2}
              color="purple"
              subtitle="$2,850 formatted"
            />

            {/* Percentage */}
            <KPICard
              title="Cap Rate"
              value={7.2}
              unit="%"
              trend={0.3}
              color="indigo"
              subtitle="percentage format"
            />

            {/* Large count */}
            <KPICard
              title="Square Footage"
              value={2500000}
              trend={8.1}
              color="orange"
              subtitle="2.5M formatted"
            />

            {/* Regular count */}
            <KPICard
              title="Units"
              value={842}
              trend={4.5}
              color="red"
              subtitle="standard count"
            />
          </KPICardGrid>
        </section>

        {/* Section 3: Color Variations */}
        <section>
          <div className="mb-4">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              3. Color Variations
            </h2>
            <p className="text-gray-600">
              6 gradient color themes available
            </p>
          </div>

          <KPICardGrid columns={6}>
            <KPICard
              title="Blue"
              value={1234}
              trend={5.6}
              color="blue"
              icon={ChartIcon}
            />

            <KPICard
              title="Green"
              value={5678}
              trend={8.2}
              color="green"
              icon={DollarIcon}
            />

            <KPICard
              title="Purple"
              value={9012}
              trend={3.4}
              color="purple"
              icon={BuildingIcon}
            />

            <KPICard
              title="Orange"
              value={3456}
              trend={-2.1}
              color="orange"
              icon={UsersIcon}
            />

            <KPICard
              title="Red"
              value={7890}
              trend={-5.3}
              color="red"
              icon={ChartIcon}
            />

            <KPICard
              title="Indigo"
              value={2468}
              trend={12.7}
              color="indigo"
              icon={DollarIcon}
            />
          </KPICardGrid>
        </section>

        {/* Section 4: Trend Variations */}
        <section>
          <div className="mb-4">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              4. Trend Variations
            </h2>
            <p className="text-gray-600">
              Positive, negative, no trend, and manual override
            </p>
          </div>

          <KPICardGrid columns={4}>
            {/* Positive trend */}
            <KPICard
              title="Revenue Growth"
              value={23.5}
              unit="%"
              trend={5.2}
              trendUp={true}
              color="green"
              subtitle="positive trend"
            />

            {/* Negative trend (bad) */}
            <KPICard
              title="Operating Costs"
              value={15.8}
              unit="%"
              trend={-3.2}
              trendUp={false}
              color="red"
              subtitle="negative trend"
            />

            {/* Negative trend (good) */}
            <KPICard
              title="Vacancy Rate"
              value={5.4}
              unit="%"
              trend={-2.1}
              trendUp={true}
              color="green"
              subtitle="improvement"
            />

            {/* No trend */}
            <KPICard
              title="Total Assets"
              value={89500000}
              unit="$"
              color="blue"
              subtitle="no trend data"
            />
          </KPICardGrid>
        </section>

        {/* Section 5: Clickable Cards */}
        <section>
          <div className="mb-4">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              5. Clickable Cards
            </h2>
            <p className="text-gray-600">
              Cards with onClick handlers (try clicking them!)
            </p>
          </div>

          <KPICardGrid columns={4}>
            <KPICard
              title="View Properties"
              value={184}
              trend={12}
              icon={BuildingIcon}
              color="blue"
              onClick={() => handleCardClick('Properties')}
              subtitle="Click to view details"
            />

            <KPICard
              title="Revenue Report"
              value={47800000}
              unit="$"
              trend={8.2}
              icon={DollarIcon}
              color="green"
              onClick={() => handleCardClick('Revenue')}
              subtitle="Click for breakdown"
            />

            <KPICard
              title="Occupancy Details"
              value={94.6}
              unit="%"
              trend={2.4}
              icon={ChartIcon}
              color="purple"
              onClick={() => handleCardClick('Occupancy')}
              subtitle="Click for analysis"
            />

            <KPICard
              title="Tenant List"
              value={1247}
              trend={-3.2}
              icon={UsersIcon}
              color="orange"
              onClick={() => handleCardClick('Tenants')}
              subtitle="Click to manage"
            />
          </KPICardGrid>
        </section>

        {/* Section 6: Loading State */}
        {loading && (
          <section>
            <div className="mb-4">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                6. Loading State
              </h2>
              <p className="text-gray-600">
                Skeleton loaders while data is fetching
              </p>
            </div>

            <KPICardGrid columns={4}>
              <KPICardSkeleton color="blue" />
              <KPICardSkeleton color="green" />
              <KPICardSkeleton color="purple" />
              <KPICardSkeleton color="orange" />
            </KPICardGrid>
          </section>
        )}

        {/* Features List */}
        <section className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            ✨ Features Demonstrated
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            <div className="flex items-start gap-2">
              <span className="text-green-600 font-bold text-lg">✓</span>
              <span className="text-gray-700">Animated number count-up</span>
            </div>
            <div className="flex items-start gap-2">
              <span className="text-green-600 font-bold text-lg">✓</span>
              <span className="text-gray-700">Trend indicators with arrows</span>
            </div>
            <div className="flex items-start gap-2">
              <span className="text-green-600 font-bold text-lg">✓</span>
              <span className="text-gray-700">Color-coded backgrounds</span>
            </div>
            <div className="flex items-start gap-2">
              <span className="text-green-600 font-bold text-lg">✓</span>
              <span className="text-gray-700">Hover effects with elevation</span>
            </div>
            <div className="flex items-start gap-2">
              <span className="text-green-600 font-bold text-lg">✓</span>
              <span className="text-gray-700">Auto number formatting</span>
            </div>
            <div className="flex items-start gap-2">
              <span className="text-green-600 font-bold text-lg">✓</span>
              <span className="text-gray-700">Optional icons</span>
            </div>
            <div className="flex items-start gap-2">
              <span className="text-green-600 font-bold text-lg">✓</span>
              <span className="text-gray-700">Loading skeleton</span>
            </div>
            <div className="flex items-start gap-2">
              <span className="text-green-600 font-bold text-lg">✓</span>
              <span className="text-gray-700">Clickable cards</span>
            </div>
            <div className="flex items-start gap-2">
              <span className="text-green-600 font-bold text-lg">✓</span>
              <span className="text-gray-700">Fully responsive</span>
            </div>
          </div>
        </section>

        {/* Usage Example */}
        <section className="bg-white rounded-xl p-6 border border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            📝 Quick Start
          </h2>
          <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
            <code>{`import KPICard, { KPICardGrid } from '@/components/KPICard';

function Dashboard() {
  return (
    <KPICardGrid columns={4}>
      <KPICard
        title="Total Revenue"
        value={47800000}
        unit="$"
        trend={8.2}
        color="blue"
        subtitle="vs last month"
      />
      
      <KPICard
        title="Properties"
        value={184}
        trend={12}
        color="green"
      />
      
      {/* More cards... */}
    </KPICardGrid>
  );
}`}</code>
          </pre>
        </section>
      </div>
    </div>
  );
}

