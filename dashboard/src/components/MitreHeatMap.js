import React from 'react';
import './MitreHeatMap.css';

const MitreHeatMap = ({ techniques, mappedTechniques }) => {
  // MITRE ATT&CK Tactics in order
  const tactics = [
    'Initial Access',
    'Execution',
    'Defense Evasion',
    'Credential Access',
    'Lateral Movement',
    'Command and Control',
    'Exfiltration',
    'Impact',
  ];

  // Group techniques by tactic
  const techniquesByTactic = tactics.reduce((acc, tactic) => {
    acc[tactic] = techniques.filter(
      (t) => t.tactic.toLowerCase() === tactic.toLowerCase()
    );
    return acc;
  }, {});

  // Check if a technique is mapped (detected in alerts)
  const isMapped = (techniqueId) => {
    return mappedTechniques.some((t) => t.technique_id === techniqueId);
  };

  // Count mapped techniques per tactic
  const getMappedCount = (tactic) => {
    const tacticTechniques = techniquesByTactic[tactic] || [];
    return tacticTechniques.filter((t) => isMapped(t.technique_id)).length;
  };

  return (
    <div className="mitre-heatmap-container">
      <div className="heatmap-header">
        <h2>🗺️ MITRE ATT&CK Coverage</h2>
        <div className="legend">
          <span className="legend-item">
            <span className="legend-color detected"></span> Detected
          </span>
          <span className="legend-item">
            <span className="legend-color not-detected"></span> Not Detected
          </span>
        </div>
      </div>

      <div className="heatmap-grid">
        {tactics.map((tactic) => (
          <div key={tactic} className="tactic-column">
            <div className="tactic-header">
              <span className="tactic-name">{tactic}</span>
              <span className="tactic-count">
                {getMappedCount(tactic)}/{(techniquesByTactic[tactic] || []).length}
              </span>
            </div>
            <div className="techniques-list">
              {(techniquesByTactic[tactic] || []).map((technique) => (
                <div
                  key={technique.technique_id}
                  className={`technique-cell ${isMapped(technique.technique_id) ? 'detected' : ''}`}
                  title={`${technique.technique_id}: ${technique.name}\n${technique.description || ''}`}
                >
                  <span className="technique-id">{technique.technique_id}</span>
                  <span className="technique-name">{technique.name}</span>
                </div>
              ))}
              {(techniquesByTactic[tactic] || []).length === 0 && (
                <div className="no-techniques">No techniques</div>
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="heatmap-summary">
        <div className="summary-item">
          <span className="summary-value">
            {mappedTechniques.length}
          </span>
          <span className="summary-label">Techniques Detected</span>
        </div>
        <div className="summary-item">
          <span className="summary-value">
            {techniques.length}
          </span>
          <span className="summary-label">Total Techniques</span>
        </div>
        <div className="summary-item">
          <span className="summary-value">
            {techniques.length > 0 
              ? Math.round((mappedTechniques.length / techniques.length) * 100) 
              : 0}%
          </span>
          <span className="summary-label">Coverage</span>
        </div>
      </div>
    </div>
  );
};

export default MitreHeatMap;