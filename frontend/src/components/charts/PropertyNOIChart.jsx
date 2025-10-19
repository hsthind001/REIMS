import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function PropertyNOIChart({ propertyData }) {
  console.log('📈 PropertyNOIChart received data:', propertyData);
  
  // Generate realistic NOI data based on property's annual NOI
  const generateNOIData = () => {
    const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const data = [];
    const annualNOI = propertyData?.noi || 0;
    const avgMonthlyNOI = annualNOI / 12;
    
    // Use property ID as seed for consistent data
    const propertyId = propertyData?.id || 1;
    
    // Create realistic monthly variations for ALL 12 months
    for (let i = 0; i < 12; i++) {
      // Seasonal factors
      let seasonalFactor = 1.0;
      if (i >= 9) seasonalFactor = 1.08; // Q4 boost
      else if (i >= 0 && i <= 2) seasonalFactor = 0.95; // Q1 dip
      else if (i >= 6 && i <= 8) seasonalFactor = 1.02; // Q3 slight increase
      
      // Deterministic variation based on property ID and month
      const seed = (propertyId * 1000) + (i * 100);
      const deterministicVariation = 1 + (Math.sin(seed) * 0.08); // Reduced variation for more realistic data
      const monthlyNOI = avgMonthlyNOI * seasonalFactor * deterministicVariation;
      
      data.push({
        month: monthNames[i],
        noi: Math.round(monthlyNOI),
        target: Math.round(avgMonthlyNOI * 1.05) // More realistic target
      });
    }
    return data;
  };

  const data = generateNOIData();

  return (
    <ResponsiveContainer width="100%" height={350}>
      <LineChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
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
            name === 'noi' ? 'Actual NOI' : 'Target NOI'
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
        <Line 
          type="monotone" 
          dataKey="noi" 
          stroke="#667eea" 
          strokeWidth={3}
          dot={{ fill: '#667eea', strokeWidth: 2, r: 5 }}
          activeDot={{ r: 7, stroke: '#667eea', strokeWidth: 3, fill: 'white' }}
        />
        <Line 
          type="monotone" 
          dataKey="target" 
          stroke="#10b981" 
          strokeWidth={2}
          strokeDasharray="5 5"
          dot={false}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
