import React from 'react'
import { motion } from 'framer-motion'

/**
 * ContentWrapper Component
 * Simple wrapper for page content that matches Portfolio/KPI style
 * Does NOT include header - works within existing navigation
 */

const ContentWrapper = ({ children }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      style={{
        background: 'rgba(255, 255, 255, 0.95)',
        backdropFilter: 'blur(16px)',
        borderRadius: '16px',
        padding: '24px',
        boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
        border: '1px solid rgba(255, 255, 255, 0.2)',
        minHeight: 'calc(100vh - 200px)',
        overflow: 'auto',
        display: 'flex',
        flexDirection: 'column'
      }}
    >
      {children}
    </motion.div>
  )
}

export default ContentWrapper
















