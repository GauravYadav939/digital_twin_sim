/**
 * API Service
 * Handles all communication with backend FastAPI server
 */

import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ============================================================
// SIMULATOR API ENDPOINTS
// ============================================================

export const simulatorAPI = {
  /**
   * Health check
   */
  healthCheck: async () => {
    const response = await api.get('/');
    return response.data;
  },

  /**
   * Get simulator status
   */
  getStatus: async () => {
    const response = await api.get('/api/status');
    return response.data;
  },

  /**
   * Initialize simulator at idle
   */
  initialize: async (altitude_m = 0, T_ambient_C = 15) => {
    const response = await api.post('/api/simulator/init', {
      altitude_m,
      T_ambient_C,
    });
    return response.data;
  },

  /**
   * Start simulation with configuration
   */
  start: async (config) => {
    const response = await api.post('/api/simulator/start', config);
    return response.data;
  },

  /**
   * Execute single simulation step
   */
  step: async (inputs) => {
    const response = await api.post('/api/simulator/step', inputs);
    return response.data;
  },

  /**
   * Get current telemetry
   */
  getTelemetry: async () => {
    const response = await api.get('/api/simulator/telemetry');
    return response.data;
  },

  /**
   * Get telemetry history
   */
  getHistory: async (limit = 100) => {
    const response = await api.get(`/api/simulator/history?limit=${limit}`);
    return response.data;
  },

  /**
   * Stop simulation
   */
  stop: async () => {
    const response = await api.post('/api/simulator/stop');
    return response.data;
  },

  /**
   * Reset simulator
   */
  reset: async () => {
    const response = await api.post('/api/simulator/reset');
    return response.data;
  },

  /**
   * Get configuration
   */
  getConfig: async () => {
    const response = await api.get('/api/simulator/config');
    return response.data;
  },
};

export default api;