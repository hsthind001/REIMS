import React from "react";

function MinimalApp() {
  return (
    <div style={{
      padding: '20px',
      fontFamily: 'Arial, sans-serif',
      backgroundColor: '#f0f0f0',
      minHeight: '100vh'
    }}>
      <h1 style={{color: '#333'}}>🚀 REIMS Minimal Test</h1>
      <div style={{
        background: 'white',
        padding: '20px',
        borderRadius: '8px',
        boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
        margin: '20px 0'
      }}>
        <h2>✅ React is Working!</h2>
        <p>Current time: {new Date().toLocaleString()}</p>
        <p>This is a minimal React component to test basic functionality.</p>
        <button 
          onClick={() => alert('React is working!')}
          style={{
            background: '#007bff',
            color: 'white',
            border: 'none',
            padding: '10px 20px',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Test Click
        </button>
      </div>
    </div>
  );
}

export default MinimalApp;