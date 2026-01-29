import React, { useState } from 'react';
import './CreateAlertForm.css';

const CreateAlertForm = ({ onCreateAlert, onClose }) => {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    severity: 'medium',
    source: 'siem',
    source_ip: '',
  });
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.title) {
      alert('Title is required');
      return;
    }

    setLoading(true);
    try {
      await onCreateAlert(formData);
      setFormData({
        title: '',
        description: '',
        severity: 'medium',
        source: 'siem',
        source_ip: '',
      });
      onClose();
    } catch (error) {
      console.error('Error creating alert:', error);
      alert('Failed to create alert');
    }
    setLoading(false);
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="modal-header">
          <h2>🚨 Create New Alert</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="title">Title *</label>
            <input
              type="text"
              id="title"
              name="title"
              value={formData.title}
              onChange={handleChange}
              placeholder="e.g., Suspicious login attempt"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="description">Description</label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              placeholder="Detailed description of the security event"
              rows="3"
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="severity">Severity</label>
              <select
                id="severity"
                name="severity"
                value={formData.severity}
                onChange={handleChange}
              >
                <option value="low">🟢 Low</option>
                <option value="medium">🟡 Medium</option>
                <option value="high">🟠 High</option>
                <option value="critical">🔴 Critical</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="source">Source</label>
              <select
                id="source"
                name="source"
                value={formData.source}
                onChange={handleChange}
              >
                <option value="siem">SIEM</option>
                <option value="edr">EDR</option>
                <option value="firewall">Firewall</option>
                <option value="ids">IDS</option>
                <option value="email">Email</option>
                <option value="custom">Custom</option>
              </select>
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="source_ip">Source IP</label>
            <input
              type="text"
              id="source_ip"
              name="source_ip"
              value={formData.source_ip}
              onChange={handleChange}
              placeholder="e.g., 192.168.1.100"
            />
          </div>

          <div className="form-actions">
            <button type="button" className="cancel-btn" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="submit-btn" disabled={loading}>
              {loading ? 'Creating...' : '🚨 Create Alert'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateAlertForm;