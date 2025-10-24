import React from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function PropertyRevenueChart({ propertyData }) {
  // Generate realistic revenue/expense data for ALL 12 months
  const generateRevenueData = () => {
    const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const data = [];
    const monthlyRent = propertyData?.monthly_rent || 0;
    const avgMonthlyExpenses = monthlyRent * 0.6; // Assume 60% expense ratio
    
    // Use property ID as seed for consistent data
    const propertyId = propertyData?.id || 1;
    
    // Generate data for ALL 12 months
    for (let i = 0; i < 12; i++) {
      // Seasonal revenue variations
      let seasonalRevenueFactor = 1.0;
      if (i >= 9) seasonalRevenueFactor = 1.05; // Q4 boost
      else if (i >= 0 && i <= 2) seasonalRevenueFactor = 0.97; // Q1 dip
      
      // Deterministic variations based on property ID and month
      const revenueSeed = (propertyId * 1000) + (i * 50);
      const revenueVariation = 1 + (Math.sin(revenueSeed) * 0.05); // Reduced variation
      const monthlyRevenue = monthlyRent * seasonalRevenueFactor * revenueVariation;
      
      const expenseSeed = (propertyId * 1000) + (i * 75);
      const expenseVariation = 1 + (Math.sin(expenseSeed) * 0.08); // Reduced variation
      const monthlyExpenses = avgMonthlyExpenses * expenseVariation;
      
      data.push({
        month: monthNames[i],
        revenue: Math.round(monthlyRevenue),
        expenses: Math.round(monthlyExpenses),
        profit: Math.round(monthlyRevenue - monthlyExpenses)
      });
    }
    return data;
  };

  const data = generateRevenueData();

  return (
    <div>
      <div style={{
        fontSize: '12px',
        color: '#9ca3af',
        marginBottom: '8px',
        fontStyle: 'italic'
      }}>
        * Projected data based on monthly rent with estimated expense ratios
      </div>
      <ResponsiveContainer width="100%" height={350}>
        <AreaChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis 
          dataKey="month" 
          tick={{ fontSize: 12, fill: '#64748b' }}
          axisLine={{ stroke: '#e0e0e0' }}
          tickLine={{ stroke: '#e0e0e0' }}
          interval={0}
          angle={-45}
          textAnchor="end"
          height={60}
        />
        <YAxis 
          tick={{ fontSize: 12, fill: '#64748b' }}
          axisLine={{ stroke: '#e0e0e0' }}
          tickLine={{ stroke: '#e0e0e0' }}
          tickFormatter={(value) => `$${(value / 1000).toFixed(0)}K`}
        />
        <Tooltip 
          formatter={(value, name) => [
            `$${value.toLocaleString()}`, 
            name === 'revenue' ? 'Revenue' : name === 'expenses' ? 'Expenses' : 'Profit'
          ]}
          labelStyle={{ color: '#1e293b', fontWeight: 600 }}
          contentStyle={{ 
            backgroundColor: 'white', 
            border: '1px solid #e0e0e0',
            borderRadius: '12px',
            boxShadow: '0 8px 25px rgba(0,0,0,0.15)',
            padding: '12px 16px'
          }}
        />
        <Area 
          type="monotone" 
          dataKey="revenue" 
          stackId="1"
          stroke="#10b981" 
          fill="#10b981"
          fillOpacity={0.8}
          strokeWidth={2}
        />
        <Area 
          type="monotone" 
          dataKey="expenses" 
          stackId="2"
          stroke="#ef4444" 
          fill="#ef4444"
          fillOpacity={0.8}
          strokeWidth={2}
        />
      </AreaChart>
    </ResponsiveContainer>
    </div>
  );
}
