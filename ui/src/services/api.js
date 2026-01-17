import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export default {
  // Chat
  async sendMessage(message, context = 'general') {
    const response = await api.post('/api/chat', { message, context })
    return response.data
  },

  // Command execution
  async executeCommand(command, dryRun = false) {
    const response = await api.post('/api/execute', { command, dry_run: dryRun })
    return response.data
  },

  // System
  async getSystemStatus() {
    const response = await api.get('/api/system/status')
    return response.data
  },

  // Apps
  async getApps() {
    const response = await api.get('/api/apps')
    return response.data
  },

  // Services
  async getServices() {
    const response = await api.get('/api/services')
    return response.data
  },

  // Backups
  async getBackups() {
    const response = await api.get('/api/backups')
    return response.data
  },

  // Changes
  async getChanges() {
    const response = await api.get('/api/changes')
    return response.data
  },

  // Stats
  async getStats() {
    const response = await api.get('/api/stats')
    return response.data
  },

  // Preferences
  async getPreferences() {
    const response = await api.get('/api/preferences')
    return response.data
  },

  async updatePreference(key, value) {
    const response = await api.post('/api/preferences', null, {
      params: { key, value }
    })
    return response.data
  },
}
