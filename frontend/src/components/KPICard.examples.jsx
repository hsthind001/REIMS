/**
 * KPICard Component - Usage Examples
 * 
 * Demonstrates various use cases for the KPI Card component
 */

import React from 'react';
import KPICard, { KPICardGrid, KPICardSkeleton } from './KPICard';

// Example icons (using Heroicons)
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

// ============================================================================
// Example 1: Basic KPI Cards
// ============================================================================

export function BasicKPICards() {
  return (
    <div className="p-6 space-y-6">
      <h2 className="text-2xl font-bold text-gray-900">Basic KPI Cards</h2>
      
      <KPICardGrid columns={4}>
        <KPICard
          title="Total Portfolio Value"
          value={47800000}
          unit="$"
          trend={8.2}
          trendUp={true}
          icon={DollarIcon}
          color="blue"
          subtitle="vs last month"
        />

        <KPICard
          title="Total Properties"
          value={184}
          trend={12}
          trendUp={true}
          icon={BuildingIcon}
          color="green"
          subtitle="12 new this month"
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
        />

        <KPICard
          title="Active Tenants"
          value={1247}
          trend={-3.2}
          trendUp={false}
          icon={UsersIcon}
          color="orange"
          subtitle="3 vacancies"
        />
      </KPICardGrid>
    </div>
  );
}

// ============================================================================
// Example 2: Different Number Formats
// ============================================================================

export function NumberFormats() {
  return (
    <div className="p-6 space-y-6">
      <h2 className="text-2xl font-bold text-gray-900">Number Formats</h2>
      
      <KPICardGrid columns={3}>
        {/* Large currency */}
        <KPICard
          title="Annual Revenue"
          value={125000000}
          unit="$"
          trend={15.3}
          color="green"
          subtitle="$125M"
        />

        {/* Medium currency */}
        <KPICard
          title="Monthly NOI"
          value={3750000}
          unit="$"
          trend={5.7}
          color="blue"
          subtitle="$3.8M"
        />

        {/* Small currency */}
        <KPICard
          title="Average Rent"
          value={2850}
          unit="$"
          trend={-1.2}
          color="purple"
          subtitle="per unit"
        />

        {/* Percentage */}
        <KPICard
          title="Cap Rate"
          value={7.2}
          unit="%"
          trend={0.3}
          color="indigo"
        />

        {/* Large count */}
        <KPICard
          title="Square Footage"
          value={2500000}
          trend={8.1}
          color="orange"
          subtitle="total sqft"
        />

        {/* Regular count */}
        <KPICard
          title="Units"
          value={842}
          trend={4.5}
          color="red"
          subtitle="residential units"
        />
      </KPICardGrid>
    </div>
  );
}

// ============================================================================
// Example 3: With and Without Trends
// ============================================================================

export function TrendsVariations() {
  return (
    <div className="p-6 space-y-6">
      <h2 className="text-2xl font-bold text-gray-900">Trends Variations</h2>
      
      <KPICardGrid columns={2}>
        {/* Positive trend */}
        <KPICard
          title="Revenue Growth"
          value={23.5}
          unit="%"
          trend={5.2}
          trendUp={true}
          color="green"
        />

        {/* Negative trend */}
        <KPICard
          title="Vacancy Rate"
          value={5.4}
          unit="%"
          trend={-2.1}
          trendUp={true} // Negative trend is good for vacancy
          color="green"
          subtitle="improvement"
        />

        {/* No trend */}
        <KPICard
          title="Total Assets"
          value={89500000}
          unit="$"
          color="blue"
          subtitle="as of today"
        />

        {/* Zero trend */}
        <KPICard
          title="Maintenance Requests"
          value={42}
          trend={0}
          color="orange"
          subtitle="unchanged"
        />
      </KPICardGrid>
    </div>
  );
}

// ============================================================================
// Example 4: Different Colors
// ============================================================================

export function ColorVariations() {
  return (
    <div className="p-6 space-y-6">
      <h2 className="text-2xl font-bold text-gray-900">Color Variations</h2>
      
      <KPICardGrid columns={3}>
        <KPICard
          title="Blue Card"
          value={1234}
          trend={5.6}
          color="blue"
          icon={ChartIcon}
        />

        <KPICard
          title="Green Card"
          value={5678}
          trend={8.2}
          color="green"
          icon={DollarIcon}
        />

        <KPICard
          title="Purple Card"
          value={9012}
          trend={3.4}
          color="purple"
          icon={BuildingIcon}
        />

        <KPICard
          title="Orange Card"
          value={3456}
          trend={-2.1}
          color="orange"
          icon={UsersIcon}
        />

        <KPICard
          title="Red Card"
          value={7890}
          trend={-5.3}
          color="red"
          icon={ChartIcon}
        />

        <KPICard
          title="Indigo Card"
          value={2468}
          trend={12.7}
          color="indigo"
          icon={DollarIcon}
        />
      </KPICardGrid>
    </div>
  );
}

// ============================================================================
// Example 5: Loading State
// ============================================================================

export function LoadingState() {
  return (
    <div className="p-6 space-y-6">
      <h2 className="text-2xl font-bold text-gray-900">Loading State</h2>
      
      <KPICardGrid columns={4}>
        <KPICard
          title="Total Value"
          value={47800000}
          unit="$"
          loading={true}
          color="blue"
        />

        <KPICard
          title="Properties"
          value={184}
          loading={true}
          color="green"
        />

        <KPICardSkeleton color="purple" />
        <KPICardSkeleton color="orange" />
      </KPICardGrid>
    </div>
  );
}

// ============================================================================
// Example 6: Clickable Cards
// ============================================================================

export function ClickableCards() {
  const handleClick = (cardTitle) => {
    alert(`Clicked: ${cardTitle}`);
  };

  return (
    <div className="p-6 space-y-6">
      <h2 className="text-2xl font-bold text-gray-900">Clickable Cards</h2>
      
      <KPICardGrid columns={4}>
        <KPICard
          title="View Properties"
          value={184}
          trend={12}
          icon={BuildingIcon}
          color="blue"
          onClick={() => handleClick('Properties')}
          subtitle="Click to view details"
        />

        <KPICard
          title="Revenue Report"
          value={47800000}
          unit="$"
          trend={8.2}
          icon={DollarIcon}
          color="green"
          onClick={() => handleClick('Revenue')}
          subtitle="Click for breakdown"
        />

        <KPICard
          title="Occupancy Details"
          value={94.6}
          unit="%"
          trend={2.4}
          icon={ChartIcon}
          color="purple"
          onClick={() => handleClick('Occupancy')}
          subtitle="Click for analysis"
        />

        <KPICard
          title="Tenant List"
          value={1247}
          trend={-3.2}
          icon={UsersIcon}
          color="orange"
          onClick={() => handleClick('Tenants')}
          subtitle="Click to manage"
        />
      </KPICardGrid>
    </div>
  );
}

// ============================================================================
// Example 7: Real-World Dashboard
// ============================================================================

export function RealWorldDashboard() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Real Estate Portfolio Dashboard
          </h1>
          <p className="text-gray-600">
            Overview of your property portfolio performance
          </p>
        </div>

        {/* Primary KPIs */}
        <div>
          <h2 className="text-lg font-semibold text-gray-700 mb-4">
            Primary Metrics
          </h2>
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
            />

            <KPICard
              title="Total Properties"
              value={184}
              trend={12}
              trendUp={true}
              icon={BuildingIcon}
              color="green"
              subtitle="12 new acquisitions"
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
            />

            <KPICard
              title="Monthly NOI"
              value={3750000}
              unit="$"
              trend={5.7}
              trendUp={true}
              icon={DollarIcon}
              color="indigo"
              subtitle="net operating income"
            />
          </KPICardGrid>
        </div>

        {/* Secondary KPIs */}
        <div>
          <h2 className="text-lg font-semibold text-gray-700 mb-4">
            Operational Metrics
          </h2>
          <KPICardGrid columns={3}>
            <KPICard
              title="Active Tenants"
              value={1247}
              trend={-3.2}
              trendUp={false}
              icon={UsersIcon}
              color="orange"
              subtitle="3 vacancies this month"
            />

            <KPICard
              title="Maintenance Requests"
              value={42}
              trend={-15.2}
              trendUp={true}
              color="green"
              subtitle="faster resolution"
            />

            <KPICard
              title="Lease Renewals"
              value={87.3}
              unit="%"
              trend={4.1}
              trendUp={true}
              color="blue"
              subtitle="retention rate"
            />
          </KPICardGrid>
        </div>

        {/* Financial KPIs */}
        <div>
          <h2 className="text-lg font-semibold text-gray-700 mb-4">
            Financial Performance
          </h2>
          <KPICardGrid columns={4}>
            <KPICard
              title="Annual Revenue"
              value={125000000}
              unit="$"
              trend={15.3}
              color="green"
              subtitle="year over year"
            />

            <KPICard
              title="Operating Expenses"
              value={35000000}
              unit="$"
              trend={-8.1}
              trendUp={true}
              color="green"
              subtitle="cost reduction"
            />

            <KPICard
              title="Cap Rate"
              value={7.2}
              unit="%"
              trend={0.3}
              color="purple"
              subtitle="portfolio average"
            />

            <KPICard
              title="Debt-to-Equity"
              value={0.65}
              trend={-5.2}
              trendUp={true}
              color="blue"
              subtitle="improved ratio"
            />
          </KPICardGrid>
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// Example 8: Compact Grid
// ============================================================================

export function CompactGrid() {
  return (
    <div className="p-6 space-y-6">
      <h2 className="text-2xl font-bold text-gray-900">Compact Grid (6 columns)</h2>
      
      <KPICardGrid columns={6}>
        <KPICard title="Revenue" value={12500000} unit="$" trend={8.2} color="green" />
        <KPICard title="Properties" value={184} trend={12} color="blue" />
        <KPICard title="Occupancy" value={94.6} unit="%" trend={2.4} color="purple" />
        <KPICard title="Tenants" value={1247} trend={-3.2} color="orange" />
        <KPICard title="NOI" value={3750000} unit="$" trend={5.7} color="indigo" />
        <KPICard title="Cap Rate" value={7.2} unit="%" trend={0.3} color="blue" />
      </KPICardGrid>
    </div>
  );
}

