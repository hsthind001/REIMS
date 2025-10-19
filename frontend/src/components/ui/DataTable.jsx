import { useState, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { cn } from '@/lib/utils'
import { 
  ChevronUp, 
  ChevronDown, 
  ChevronsUpDown,
  Search,
  Filter,
  Download
} from 'lucide-react'

/**
 * REIMS Data Table Component
 * Feature-rich table with sorting, filtering, and beautiful styling
 */

export function DataTable({
  data = [],
  columns = [],
  sortable = true,
  filterable = true,
  searchable = true,
  exportable = false,
  pageSize = 10,
  className,
  onRowClick,
}) {
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' })
  const [searchTerm, setSearchTerm] = useState('')
  const [currentPage, setCurrentPage] = useState(1)
  const [filterColumn, setFilterColumn] = useState(null)

  // Sorting
  const sortedData = useMemo(() => {
    if (!sortConfig.key) return data

    return [...data].sort((a, b) => {
      const aValue = a[sortConfig.key]
      const bValue = b[sortConfig.key]

      if (aValue < bValue) return sortConfig.direction === 'asc' ? -1 : 1
      if (aValue > bValue) return sortConfig.direction === 'asc' ? 1 : -1
      return 0
    })
  }, [data, sortConfig])

  // Searching
  const searchedData = useMemo(() => {
    if (!searchTerm) return sortedData

    return sortedData.filter(row =>
      Object.values(row).some(value =>
        String(value).toLowerCase().includes(searchTerm.toLowerCase())
      )
    )
  }, [sortedData, searchTerm])

  // Pagination
  const paginatedData = useMemo(() => {
    const startIndex = (currentPage - 1) * pageSize
    return searchedData.slice(startIndex, startIndex + pageSize)
  }, [searchedData, currentPage, pageSize])

  const totalPages = Math.ceil(searchedData.length / pageSize)

  const handleSort = (key) => {
    if (!sortable) return

    setSortConfig(prev => ({
      key,
      direction: prev.key === key && prev.direction === 'asc' ? 'desc' : 'asc'
    }))
  }

  const handleExport = () => {
    const csv = [
      columns.map(col => col.header).join(','),
      ...data.map(row => columns.map(col => row[col.key]).join(','))
    ].join('\n')

    const blob = new Blob([csv], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'data-export.csv'
    a.click()
  }

  return (
    <div className={cn('space-y-4', className)}>
      {/* Toolbar */}
      {(searchable || exportable) && (
        <div className="flex items-center justify-between gap-4 p-4 bg-neutral-slate-50 dark:bg-dark-bg-secondary rounded-lg border border-neutral-slate-200 dark:border-dark-border-primary">
          {searchable && (
            <div className="flex-1 max-w-md relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-neutral-slate-400" />
              <input
                type="text"
                placeholder="Search..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 rounded-lg border border-neutral-slate-300 dark:border-dark-border-primary bg-white dark:bg-dark-bg-primary text-neutral-slate-900 dark:text-dark-text-primary focus:ring-2 focus:ring-brand-blue-500 focus:border-transparent transition-all"
              />
            </div>
          )}

          <div className="flex items-center gap-2">
            {filterable && (
              <button className="flex items-center gap-2 px-4 py-2 rounded-lg border border-neutral-slate-300 dark:border-dark-border-primary hover:bg-white dark:hover:bg-dark-bg-tertiary transition-colors">
                <Filter className="w-4 h-4" />
                <span className="text-sm font-medium">Filter</span>
              </button>
            )}
            
            {exportable && (
              <button
                onClick={handleExport}
                className="flex items-center gap-2 px-4 py-2 rounded-lg bg-brand-blue-500 hover:bg-brand-blue-600 text-white transition-colors"
              >
                <Download className="w-4 h-4" />
                <span className="text-sm font-medium">Export</span>
              </button>
            )}
          </div>
        </div>
      )}

      {/* Table */}
      <div className="overflow-hidden rounded-xl border border-neutral-slate-200 dark:border-dark-border-primary shadow-lg">
        <div className="overflow-x-auto">
          <table className="w-full">
            {/* Header */}
            <thead className="bg-gradient-to-r from-brand-blue-500 to-brand-teal-500 text-white">
              <tr>
                {columns.map((column) => (
                  <th
                    key={column.key}
                    onClick={() => column.sortable !== false && handleSort(column.key)}
                    className={cn(
                      'px-6 py-4 text-left text-sm font-bold uppercase tracking-wider',
                      column.sortable !== false && sortable && 'cursor-pointer hover:bg-white/10 transition-colors'
                    )}
                  >
                    <div className="flex items-center gap-2">
                      <span>{column.header}</span>
                      {column.sortable !== false && sortable && (
                        <span className="text-white/60">
                          {sortConfig.key === column.key ? (
                            sortConfig.direction === 'asc' ? (
                              <ChevronUp className="w-4 h-4" />
                            ) : (
                              <ChevronDown className="w-4 h-4" />
                            )
                          ) : (
                            <ChevronsUpDown className="w-4 h-4" />
                          )}
                        </span>
                      )}
                    </div>
                  </th>
                ))}
              </tr>
            </thead>

            {/* Body */}
            <tbody className="bg-white dark:bg-dark-bg-secondary divide-y divide-neutral-slate-200 dark:divide-dark-border-subtle">
              <AnimatePresence mode="popLayout">
                {paginatedData.map((row, rowIndex) => (
                  <motion.tr
                    key={rowIndex}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ delay: rowIndex * 0.05 }}
                    onClick={() => onRowClick?.(row)}
                    className={cn(
                      'hover:bg-brand-blue-50 dark:hover:bg-brand-blue-900/20 transition-colors',
                      onRowClick && 'cursor-pointer'
                    )}
                  >
                    {columns.map((column) => (
                      <td
                        key={column.key}
                        className="px-6 py-4 text-sm text-neutral-slate-900 dark:text-dark-text-primary"
                      >
                        {column.render ? column.render(row[column.key], row) : row[column.key]}
                      </td>
                    ))}
                  </motion.tr>
                ))}
              </AnimatePresence>
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between px-6 py-4 bg-neutral-slate-50 dark:bg-dark-bg-tertiary border-t border-neutral-slate-200 dark:border-dark-border-primary">
            <div className="text-sm text-neutral-slate-600 dark:text-dark-text-secondary">
              Showing {((currentPage - 1) * pageSize) + 1} to {Math.min(currentPage * pageSize, searchedData.length)} of {searchedData.length} results
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                disabled={currentPage === 1}
                className="px-3 py-1 rounded-lg border border-neutral-slate-300 dark:border-dark-border-primary disabled:opacity-50 disabled:cursor-not-allowed hover:bg-white dark:hover:bg-dark-bg-secondary transition-colors"
              >
                Previous
              </button>
              {Array.from({ length: totalPages }, (_, i) => i + 1).map(page => (
                <button
                  key={page}
                  onClick={() => setCurrentPage(page)}
                  className={cn(
                    'px-3 py-1 rounded-lg border transition-colors',
                    page === currentPage
                      ? 'bg-brand-blue-500 text-white border-brand-blue-500'
                      : 'border-neutral-slate-300 dark:border-dark-border-primary hover:bg-white dark:hover:bg-dark-bg-secondary'
                  )}
                >
                  {page}
                </button>
              ))}
              <button
                onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                disabled={currentPage === totalPages}
                className="px-3 py-1 rounded-lg border border-neutral-slate-300 dark:border-dark-border-primary disabled:opacity-50 disabled:cursor-not-allowed hover:bg-white dark:hover:bg-dark-bg-secondary transition-colors"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

















