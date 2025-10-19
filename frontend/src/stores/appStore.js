import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'

/**
 * Main Application Store using Zustand
 * Example store for global state management
 */
const useAppStore = create(
  devtools(
    persist(
      (set, get) => ({
        // User state
        user: null,
        isAuthenticated: false,
        
        // UI state
        sidebarOpen: true,
        theme: 'light',
        
        // Document state
        documents: [],
        selectedDocument: null,
        
        // Property state
        properties: [],
        selectedProperty: null,
        
        // Actions
        setUser: (user) => set({ user, isAuthenticated: !!user }),
        logout: () => set({ user: null, isAuthenticated: false }),
        
        toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
        setTheme: (theme) => set({ theme }),
        
        setDocuments: (documents) => set({ documents }),
        setSelectedDocument: (document) => set({ selectedDocument: document }),
        addDocument: (document) =>
          set((state) => ({ documents: [...state.documents, document] })),
        
        setProperties: (properties) => set({ properties }),
        setSelectedProperty: (property) => set({ selectedProperty: property }),
        addProperty: (property) =>
          set((state) => ({ properties: [...state.properties, property] })),
        
        // Reset store
        reset: () =>
          set({
            user: null,
            isAuthenticated: false,
            sidebarOpen: true,
            theme: 'light',
            documents: [],
            selectedDocument: null,
            properties: [],
            selectedProperty: null,
          }),
      }),
      {
        name: 'reims-storage', // LocalStorage key
        partialize: (state) => ({
          // Only persist these fields
          theme: state.theme,
          sidebarOpen: state.sidebarOpen,
        }),
      }
    ),
    { name: 'AppStore' } // DevTools name
  )
)

export default useAppStore

















