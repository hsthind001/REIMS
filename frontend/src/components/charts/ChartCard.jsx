import React from 'react';
import { Card, CardHeader, CardContent, IconButton } from '@mui/material';
import { Download } from 'lucide-react';

export default function ChartCard({ title, subtitle, children, onExport }) {
  return (
    <Card sx={{ 
      height: '100%', 
      display: 'flex', 
      flexDirection: 'column',
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
      <CardHeader
        title={title}
        subheader={subtitle}
        sx={{
          background: 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)',
          borderBottom: '1px solid rgba(0,0,0,0.05)',
          '& .MuiCardHeader-title': {
            fontSize: '1.25rem',
            fontWeight: 700,
            color: '#1e293b'
          },
          '& .MuiCardHeader-subheader': {
            fontSize: '0.875rem',
            color: '#64748b',
            fontWeight: 500
          }
        }}
        action={
          onExport && (
            <IconButton 
              onClick={onExport}
              sx={{
                background: 'rgba(0,0,0,0.05)',
                '&:hover': {
                  background: 'rgba(0,0,0,0.1)'
                }
              }}
            >
              <Download size={20} />
            </IconButton>
          )
        }
      />
      <CardContent sx={{ 
        flexGrow: 1, 
        pt: 2,
        pb: 3,
        px: 3
      }}>
        {children}
      </CardContent>
    </Card>
  );
}
