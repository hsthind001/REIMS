import { motion } from 'framer-motion'

/**
 * Color Showcase Component
 * Demonstrates the REIMS color palette
 * Use this as a reference or style guide page
 */
export default function ColorShowcase() {
  const colors = {
    primary: [
      { name: 'Brand Blue', class: 'bg-brand-blue', hex: '#2563EB' },
      { name: 'Dark Blue', class: 'bg-brand-dark-blue', hex: '#1E40AF' },
      { name: 'Light Blue', class: 'bg-brand-light-blue', hex: '#DBEAFE', dark: true },
    ],
    semantic: [
      { name: 'Success Green', class: 'bg-semantic-success', hex: '#10B981' },
      { name: 'Warning Yellow', class: 'bg-semantic-warning', hex: '#F59E0B' },
      { name: 'Critical Red', class: 'bg-semantic-critical', hex: '#EF4444' },
      { name: 'Info Blue', class: 'bg-semantic-info', hex: '#3B82F6' },
    ],
    neutral: [
      { name: 'Dark', class: 'bg-neutral-dark', hex: '#0F172A' },
      { name: 'Light', class: 'bg-neutral-light', hex: '#F8FAFC', dark: true },
      { name: 'Gray', class: 'bg-neutral-gray', hex: '#64748B' },
    ],
  }

  const buttonExamples = [
    { label: 'Primary', class: 'bg-brand-blue hover:bg-brand-dark-blue text-white' },
    { label: 'Success', class: 'bg-semantic-success hover:bg-green-600 text-white' },
    { label: 'Warning', class: 'bg-semantic-warning hover:bg-yellow-600 text-white' },
    { label: 'Danger', class: 'bg-semantic-critical hover:bg-red-600 text-white' },
    { label: 'Secondary', class: 'bg-neutral-light hover:bg-gray-100 text-neutral-dark border border-neutral-gray' },
  ]

  const badgeExamples = [
    { label: 'Active', class: 'bg-semantic-success/10 text-semantic-success' },
    { label: 'Pending', class: 'bg-semantic-warning/10 text-semantic-warning' },
    { label: 'Failed', class: 'bg-semantic-critical/10 text-semantic-critical' },
    { label: 'Info', class: 'bg-semantic-info/10 text-semantic-info' },
  ]

  return (
    <div className="min-h-screen bg-neutral-light p-8">
      <div className="max-w-7xl mx-auto space-y-12">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center"
        >
          <h1 className="text-5xl font-bold text-neutral-dark mb-4">
            REIMS Color Palette
          </h1>
          <p className="text-neutral-gray text-xl">
            Professional color system for data-driven interfaces
          </p>
        </motion.div>

        {/* Primary Colors */}
        <section>
          <h2 className="text-3xl font-bold text-neutral-dark mb-6">Primary Colors</h2>
          <div className="grid grid-cols-3 gap-6">
            {colors.primary.map((color, index) => (
              <motion.div
                key={color.name}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="bg-white rounded-lg shadow-lg overflow-hidden"
              >
                <div className={`${color.class} h-32`} />
                <div className="p-4">
                  <h3 className="font-bold text-neutral-dark mb-1">{color.name}</h3>
                  <p className="text-neutral-gray text-sm font-mono">{color.hex}</p>
                  <code className="text-xs text-brand-blue bg-brand-light-blue px-2 py-1 rounded mt-2 inline-block">
                    {color.class}
                  </code>
                </div>
              </motion.div>
            ))}
          </div>
        </section>

        {/* Semantic Colors */}
        <section>
          <h2 className="text-3xl font-bold text-neutral-dark mb-6">Semantic Colors</h2>
          <div className="grid grid-cols-4 gap-6">
            {colors.semantic.map((color, index) => (
              <motion.div
                key={color.name}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="bg-white rounded-lg shadow-lg overflow-hidden"
              >
                <div className={`${color.class} h-24`} />
                <div className="p-4">
                  <h3 className="font-bold text-neutral-dark text-sm mb-1">{color.name}</h3>
                  <p className="text-neutral-gray text-xs font-mono">{color.hex}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </section>

        {/* Neutral Colors */}
        <section>
          <h2 className="text-3xl font-bold text-neutral-dark mb-6">Neutral Colors</h2>
          <div className="grid grid-cols-3 gap-6">
            {colors.neutral.map((color, index) => (
              <motion.div
                key={color.name}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="bg-white rounded-lg shadow-lg overflow-hidden"
              >
                <div className={`${color.class} h-24 ${color.dark ? 'border border-neutral-gray/20' : ''}`} />
                <div className="p-4">
                  <h3 className="font-bold text-neutral-dark mb-1">{color.name}</h3>
                  <p className="text-neutral-gray text-sm font-mono">{color.hex}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </section>

        {/* Button Examples */}
        <section>
          <h2 className="text-3xl font-bold text-neutral-dark mb-6">Button Examples</h2>
          <div className="bg-white rounded-lg shadow-lg p-8">
            <div className="flex flex-wrap gap-4">
              {buttonExamples.map((button, index) => (
                <motion.button
                  key={button.label}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: index * 0.1 }}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className={`${button.class} px-6 py-3 rounded-lg font-semibold transition-all duration-200 shadow-md hover:shadow-lg`}
                >
                  {button.label}
                </motion.button>
              ))}
            </div>
          </div>
        </section>

        {/* Badge Examples */}
        <section>
          <h2 className="text-3xl font-bold text-neutral-dark mb-6">Badge Examples</h2>
          <div className="bg-white rounded-lg shadow-lg p-8">
            <div className="flex flex-wrap gap-4">
              {badgeExamples.map((badge, index) => (
                <motion.span
                  key={badge.label}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: index * 0.1 }}
                  className={`${badge.class} px-4 py-2 rounded-full text-sm font-semibold`}
                >
                  {badge.label}
                </motion.span>
              ))}
            </div>
          </div>
        </section>

        {/* Card Example */}
        <section>
          <h2 className="text-3xl font-bold text-neutral-dark mb-6">Card Example</h2>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-neutral-light border border-neutral-gray/20 rounded-lg p-6 hover:shadow-lg transition-shadow"
          >
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="text-2xl font-bold text-neutral-dark mb-2">Dashboard Card</h3>
                <p className="text-neutral-gray">
                  This is an example of a card using the REIMS color palette.
                </p>
              </div>
              <span className="bg-semantic-success/10 text-semantic-success px-3 py-1 rounded-full text-sm font-semibold">
                Active
              </span>
            </div>
            
            <div className="grid grid-cols-3 gap-4 mb-4">
              <div className="text-center p-4 bg-white rounded-lg">
                <div className="text-3xl font-bold text-brand-blue">184</div>
                <div className="text-sm text-neutral-gray">Properties</div>
              </div>
              <div className="text-center p-4 bg-white rounded-lg">
                <div className="text-3xl font-bold text-semantic-success">94.6%</div>
                <div className="text-sm text-neutral-gray">Occupancy</div>
              </div>
              <div className="text-center p-4 bg-white rounded-lg">
                <div className="text-3xl font-bold text-semantic-info">$1.2M</div>
                <div className="text-sm text-neutral-gray">Revenue</div>
              </div>
            </div>
            
            <button className="w-full bg-brand-blue hover:bg-brand-dark-blue text-white px-4 py-3 rounded-lg font-semibold transition-colors">
              View Details
            </button>
          </motion.div>
        </section>

        {/* Alert Examples */}
        <section>
          <h2 className="text-3xl font-bold text-neutral-dark mb-6">Alert Examples</h2>
          <div className="space-y-4">
            <div className="bg-semantic-success/10 border-l-4 border-semantic-success p-4 rounded">
              <p className="text-semantic-success font-semibold">
                ✓ Success! Your changes have been saved successfully.
              </p>
            </div>
            <div className="bg-semantic-warning/10 border-l-4 border-semantic-warning p-4 rounded">
              <p className="text-semantic-warning font-semibold">
                ⚠ Warning: Please review your input before proceeding.
              </p>
            </div>
            <div className="bg-semantic-critical/10 border-l-4 border-semantic-critical p-4 rounded">
              <p className="text-semantic-critical font-semibold">
                ✕ Error: Something went wrong. Please try again.
              </p>
            </div>
            <div className="bg-semantic-info/10 border-l-4 border-semantic-info p-4 rounded">
              <p className="text-semantic-info font-semibold">
                ℹ Info: New features are available in this update.
              </p>
            </div>
          </div>
        </section>
      </div>
    </div>
  )
}

















