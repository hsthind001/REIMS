import React from 'react';
import { Card, CardContent, Typography, Box, Chip } from '@mui/material';
import { TrendingUp, TrendingDown } from 'lucide-react';

export default function MetricCard({ title, value, trend, trendValue, icon, color }) {
  return (
    <Card sx={{ 
      height: '100%',
      background: 'white',
      borderRadius: 3,
      boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
      border: '1px solid rgba(0,0,0,0.05)',
      transition: 'all 0.3s ease',
      '&:hover': {
        boxShadow: '0 8px 30px rgba(0,0,0,0.12)',
        transform: 'translateY(-2px)'
      }
    }}>
      <CardContent sx={{ p: 3 }}>
        <Box sx={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          mb: 3 
        }}>
          <Typography variant="overline" sx={{ 
            color: 'text.secondary',
            fontWeight: 600,
            fontSize: '0.75rem',
            letterSpacing: '0.1em'
          }}>
            {title}
          </Typography>
          <Box sx={{
            p: 1.5,
            borderRadius: 2,
            background: `${color}15`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            {icon}
          </Box>
        </Box>
        <Typography variant="h3" sx={{ 
          color, 
          fontWeight: 800, 
          mb: 2,
          fontSize: '2.5rem',
          lineHeight: 1.2
        }}>
          {value}
        </Typography>
        {trend && (
          <Chip 
            label={`${trend} ${trendValue}`}
            size="small"
            color={trend === 'up' ? 'success' : 'error'}
            icon={trend === 'up' ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
            sx={{
              fontWeight: 600,
              fontSize: '0.75rem'
            }}
          />
        )}
      </CardContent>
    </Card>
  );
}
