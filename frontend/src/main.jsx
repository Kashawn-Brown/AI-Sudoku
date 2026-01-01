import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import './index.css'
import App from './App.jsx'

// Create a QueryClient instance for React Query
// This manages the state of all queries (caching, refetching, etc.)
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Don't refetch on window focus (prevents unnecessary API calls)
      refetchOnWindowFocus: false,
      // Retry failed requests once
      retry: 1,
    },
  },
})

// Render the app with React Query provider
// The QueryClientProvider makes the queryClient available to all child components
createRoot(document.getElementById('root')).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </StrictMode>,
)
