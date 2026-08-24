// Centralized API Base URL helper supporting Vite Environment Variables
export const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000').replace(/\/+$/, '');

// WebSocket Base URL derived from API_BASE_URL (or VITE_WS_BASE_URL if explicitly set)
export const WS_BASE_URL = (
  import.meta.env.VITE_WS_BASE_URL || 
  API_BASE_URL.replace(/^http/, 'ws')
).replace(/\/+$/, '');
