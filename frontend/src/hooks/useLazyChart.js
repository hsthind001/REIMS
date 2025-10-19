import { useState, useEffect, useRef } from 'react'

/**
 * Lazy Load Charts Hook
 * Only loads chart when tab/component becomes visible
 * Improves initial page load performance
 * 
 * @param {Boolean} isVisible - Whether the chart should be loaded
 * @returns {Boolean} shouldRender - Whether to render the chart
 */
export function useLazyChart(isVisible = true) {
  const [shouldRender, setShouldRender] = useState(false)
  const hasRendered = useRef(false)

  useEffect(() => {
    if (isVisible && !hasRendered.current) {
      // Delay rendering to not block main thread
      const timer = setTimeout(() => {
        setShouldRender(true)
        hasRendered.current = true
      }, 100)

      return () => clearTimeout(timer)
    }
  }, [isVisible])

  return shouldRender || hasRendered.current
}

/**
 * Intersection Observer Hook for Lazy Loading
 * Loads content when it becomes visible in viewport
 */
export function useInViewport(options = {}) {
  const [isVisible, setIsVisible] = useState(false)
  const [hasBeenVisible, setHasBeenVisible] = useState(false)
  const ref = useRef(null)

  useEffect(() => {
    const element = ref.current
    if (!element) return

    const observer = new IntersectionObserver(
      ([entry]) => {
        const visible = entry.isIntersecting
        setIsVisible(visible)
        
        if (visible && !hasBeenVisible) {
          setHasBeenVisible(true)
        }
      },
      {
        threshold: 0.1,
        rootMargin: '50px',
        ...options,
      }
    )

    observer.observe(element)

    return () => {
      observer.disconnect()
    }
  }, [hasBeenVisible, options])

  return { ref, isVisible, hasBeenVisible }
}

/**
 * Example usage:
 * 
 * function ChartComponent() {
 *   const { ref, hasBeenVisible } = useInViewport()
 *   const shouldRender = useLazyChart(hasBeenVisible)
 *   
 *   return (
 *     <div ref={ref}>
 *       {shouldRender ? (
 *         <LineChart data={data} />
 *       ) : (
 *         <div className="h-64 bg-gray-100 animate-pulse" />
 *       )}
 *     </div>
 *   )
 * }
 */

















