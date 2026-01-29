import React, { useState } from 'react';
import './AlertsTable.css';

const AlertsTable = ({ alerts, onEnrich, onRunPlaybooks, onMapMitre, onDelete, onRefresh }) => {
  const [loading, setLoading] = useState({});

  const handleAction = async (action, alertId, actionName) => {
    setLoading({ ...loading, [`${alertId}-${actionName}`]: true });
    try {
      await action(alertId);
      onRefresh();
    } catch (error) {
      console.error(`Error executing ${actionName}:`, error);
      alert(`Failed to ${actionName}`);
    }
    setLoading({ ...loading, [`${alertId}-${actionName}`]: false });
  };

  const getSeverityBadge = (severity) => {
    const colors = {
      critical: '#e74c3c',
      high: '#e67e22',
      medium: '#f39c12',
      low: '#27ae60',
    };
    return (
      <span
        className="severity-badge"
        style={{ backgroundColor: colors[severity] || '#95a5a6' }}
      >
        {severity?.toUpperCase()}
      </span>
    );
  };

  const getStatusBadge = (status) => {
    const colors = {
      pending: '#f39c12',
      processing: '#3498db',
      enriched: '#27ae60',
      completed: '#2ecc71',
      failed: '#e74c3c',
    };
    return (
      <span
        className="status-badge"
        style={{ backgroundColor: colors[status] || '#95a5a6' }}
      >
        {status}
      </span>
    );
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  return (
    <div className="alerts-table-container">
      <div className="table-header">
        <h2>📋 Recent Alerts</h2>
        <button className="refresh-btn" onClick={onRefresh}>
          🔄 Refresh
        </button>
      </div>
      
      <table className="alerts-table">
        <thead>
          <tr>
            <th>Title</th>
            <th>Severity</th>
            <th>Source</th>
            <th>Status</th>
            <th>Source IP</th>
            <th>Created</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {alerts.length === 0 ? (
            <tr>
              <td colSpan="7" className="no-data">
                No alerts found. Create one to get started!
              </td>
            </tr>
          ) : (
            alerts.map((alert) => (
              <tr key={alert.id}>
                <td className="alert-title">{alert.title}</td>
                <td>{getSeverityBadge(alert.severity)}</td>
                <td>{alert.source}</td>
                <td>{getStatusBadge(alert.status)}</td>
                <td className="ip-address">{alert.source_ip || '-'}</td>
                <td className="date">{formatDate(alert.created_at)}</td>
                <td className="actions">
                  <button
                    className="action-btn enrich"
                    onClick={() => handleAction(onEnrich, alert.id, 'enrich')}
                    disabled={loading[`${alert.id}-enrich`] || alert.status === 'enriched'}
                    title="Enrich with threat intel"
                  >
                    {loading[`${alert.id}-enrich`] ? '...' : '🔍'}
                  </button>
                  <button
                    className="action-btn playbook"
                    onClick={() => handleAction(onRunPlaybooks, alert.id, 'playbook')}
                    disabled={loading[`${alert.id}-playbook`]}
                    title="Run playbooks"
                  >
                    {loading[`${alert.id}-playbook`] ? '...' : '▶️'}
                  </button>
                  <button
                    className="action-btn mitre"
                    onClick={() => handleAction(onMapMitre, alert.id, 'mitre')}
                    disabled={loading[`${alert.id}-mitre`]}
                    title="Map to MITRE ATT&CK"
                  >
                    {loading[`${alert.id}-mitre`] ? '...' : '🗺️'}
                  </button>
                  <button
                    className="action-btn delete"
                    onClick={() => handleAction(onDelete, alert.id, 'delete')}
                    disabled={loading[`${alert.id}-delete`]}
                    title="Delete alert"
                  >
                    {loading[`${alert.id}-delete`] ? '...' : '🗑️'}
                  </button>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
};

export default AlertsTable;