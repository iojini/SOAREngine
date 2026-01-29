import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000';
const API_KEY = 'test-secret-key-12345';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': API_KEY,
  },
});

// Alerts API
export const getAlerts = async () => {
  const response = await api.get('/alerts/');
  return response.data;
};

export const createAlert = async (alertData) => {
  const response = await api.post('/alerts/', alertData);
  return response.data;
};

export const enrichAlert = async (alertId) => {
  const response = await api.post(`/alerts/${alertId}/enrich`);
  return response.data;
};

export const runPlaybooks = async (alertId) => {
  const response = await api.post(`/alerts/${alertId}/run-playbooks`);
  return response.data;
};

export const deleteAlert = async (alertId) => {
  const response = await api.delete(`/alerts/${alertId}`);
  return response.data;
};

// Statistics API
export const getDashboardStats = async () => {
  const response = await api.get('/statistics/dashboard');
  return response.data;
};

export const getAlertStats = async () => {
  const response = await api.get('/statistics/alerts');
  return response.data;
};

export const getTopSourceIps = async () => {
  const response = await api.get('/statistics/top-source-ips');
  return response.data;
};

// MITRE ATT&CK API
export const getMitreTechniques = async () => {
  const response = await api.get('/mitre/techniques');
  return response.data;
};

export const mapAlertToMitre = async (alertId) => {
  const response = await api.post(`/mitre/alerts/${alertId}/map`);
  return response.data;
};

// Playbooks API
export const getPlaybooks = async () => {
  const response = await api.get('/playbooks/');
  return response.data;
};

export default api;