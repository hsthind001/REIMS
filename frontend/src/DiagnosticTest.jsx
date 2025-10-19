import React from "react";

function DiagnosticTest() {
  return (
    <div style={{
      padding: '40px',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      minHeight: '100vh',
      color: 'white',
      fontFamily: 'Arial, sans-serif'
    }}>
      <h1>🚀 REIMS React Diagnostic Test</h1>
      <div style={{
        background: 'rgba(255, 255, 255, 0.1)',
        padding: '20px',
        borderRadius: '10px',
        margin: '20px 0'
      }}>
        <h2>✅ React is Working!</h2>
        <p>Current time: {new Date().toLocaleString()}</p>
        <p>React version: {React.version}</p>
        <p>URL: {window.location.href}</p>
      </div>
      
      <button 
        onClick={() => alert('React is working!')}
        style={{
          background: 'linear-gradient(45deg, #ff6b6b, #ee5a24)',
          border: 'none',
          padding: '15px 30px',
          borderRadius: '10px',
          color: 'white',
          cursor: 'pointer',
          fontSize: '1.1rem'
        }}
      >
        Test React Interactivity
      </button>
    </div>
  );
}

export default DiagnosticTest;