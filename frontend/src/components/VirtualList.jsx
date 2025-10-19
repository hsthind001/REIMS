import { useVirtualizer } from '@tanstack/react-virtual'
import { useRef } from 'react'

/**
 * Virtual List Component
 * Renders only visible items for optimal performance with large datasets
 * 
 * @param {Array} items - Array of items to render
 * @param {Function} renderItem - Function to render each item
 * @param {Number} estimateSize - Estimated height of each item in pixels
 * @param {Number} overscan - Number of items to render outside viewport
 */
export function VirtualList({ 
  items, 
  renderItem, 
  estimateSize = 80,
  overscan = 5,
  className = ""
}) {
  const parentRef = useRef(null)

  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => estimateSize,
    overscan: overscan,
  })

  const virtualItems = virtualizer.getVirtualItems()

  return (
    <div
      ref={parentRef}
      className={`overflow-auto ${className}`}
      style={{ height: '100%', width: '100%' }}
    >
      <div
        style={{
          height: `${virtualizer.getTotalSize()}px`,
          width: '100%',
          position: 'relative',
        }}
      >
        {virtualItems.map((virtualRow) => {
          const item = items[virtualRow.index]
          return (
            <div
              key={virtualRow.key}
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                height: `${virtualRow.size}px`,
                transform: `translateY(${virtualRow.start}px)`,
              }}
            >
              {renderItem(item, virtualRow.index)}
            </div>
          )
        })}
      </div>
    </div>
  )
}

/**
 * Example usage:
 * 
 * <VirtualList
 *   items={documents}
 *   estimateSize={100}
 *   renderItem={(doc, index) => (
 *     <div className="p-4 border-b">
 *       <h3>{doc.name}</h3>
 *       <p>{doc.description}</p>
 *     </div>
 *   )}
 *   className="h-[600px]"
 * />
 */

export default VirtualList

















