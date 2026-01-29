import React, { useState, useEffect, useCallback } from 'react';
import './App.css';
import MetricsCards from './components/MetricsCards';
import AlertsTable from './components/AlertsTable';
import MitreHeatMap from './components/MitreHeatMap';
import CreateAlertForm from './components/CreateAlertForm';
import {
  getAlerts,
  createAlert,
  enrichAlert,
  runPlaybooks,
  deleteAlert,
  getDashboardStats,
  getMitreTechniques,
  mapAlertToMitre,
} from './services/api';

function App() {
  const [alerts, setAlerts] = useState([]);
  const [stats, setStats] = useState(null);
  const [techniques, setTechniques] = useState([]);
  const [mappedTechniques, setMappedTechniques] = useState([]);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async () => {
    try {
      setError(null);
      const [alertsData, statsData, techniquesData] = await Promise.all([
        getAlerts(),
        getDashboardStats(),
        getMitreTechniques(),
      ]);
      setAlerts(alertsData);
      setStats(statsData);
      setTechniques(techniquesData);
    } catch (err) {
      console.error('Error fetching data:', err);
      setError('Failed to connect to SOAREngine API. Make sure the server is running.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleCreateAlert = async (alertData) => {
    const newAlert = await createAlert(alertData);
    await fetchData();
    return newAlert;
  };

  const handleEnrichAlert = async (alertId) => {
    await enrichAlert(alertId);
    await fetchData();
  };

  const handleRunPlaybooks = async (alertId) => {
    try {
      await runPlaybooks(alertId);
    } catch (err) {
      // Playbooks might return 404 if no matching playbooks
      console.log('Playbook result:', err.response?.data?.detail || 'Completed');
    }
    await fetchData();
  };

  const handleMapMitre = async (alertId) => {
    const mapping = await mapAlertToMitre(alertId);
    if (mapping.techniques && mapping.techniques.length > 0) {
      setMappedTechniques((prev) => {
        const newTechniques = [...prev];
        mapping.techniques.forEach((t) => {
          if (!newTechniques.some((existing) => existing.technique_id === t.technique_id)) {
            newTechniques.push(t);
          }
        });
        return newTechniques;
      });
    }
    return mapping;
  };

  const handleDeleteAlert = async (alertId) => {
    await deleteAlert(alertId);
    await fetchData();
  };

  if (loading) {
    return (
      <div className="app">
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading SOAREngine Dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>🛡️ SOAREngine</h1>
          <p>Security Orchestration, Automation & Response</p>
        </div>
        <button className="create-alert-btn" onClick={() => setShowCreateForm(true)}>
          + New Alert
        </button>
      </header>

      <main className="app-main">
        {error && (
          <div className="error-banner">
            ⚠️ {error}
          </div>
        )}

        <MetricsCards stats={stats} />

        <AlertsTable
          alerts={alerts}
          onEnrich={handleEnrichAlert}
          onRunPlaybooks={handleRunPlaybooks}
          onMapMitre={handleMapMitre}
          onDelete={handleDeleteAlert}
          onRefresh={fetchData}
        />

        <MitreHeatMap
          techniques={techniques}
          mappedTechniques={mappedTechniques}
        />
      </main>

      <footer className="app-footer">
        <p>SOAREngine Dashboard • Connected to API at http://127.0.0.1:8000</p>
      </footer>

      {showCreateForm && (
        <CreateAlertForm
          onCreateAlert={handleCreateAlert}
          onClose={() => setShowCreateForm(false)}
        />
      )}
    </div>
  );
}

export default App;