import React from 'react';
import './MetricsCards.css';

const MetricsCards = ({ stats }) => {
  const cards = [
    {
      title: 'Total Alerts',
      value: stats?.total_alerts || 0,
      icon: '📊',
      color: '#3498db',
    },
    {
      title: 'Critical',
      value: stats?.critical_alerts || 0,
      icon: '🔴',
      color: '#e74c3c',
    },
    {
      title: 'High',
      value: stats?.high_alerts || 0,
      icon: '🟠',
      color: '#e67e22',
    },
    {
      title: 'Pending',
      value: stats?.pending_alerts || 0,
      icon: '⏳',
      color: '#f39c12',
    },
    {
      title: 'Enriched',
      value: stats?.enriched_alerts || 0,
      icon: '✅',
      color: '#27ae60',
    },
    {
      title: 'Today',
      value: stats?.alerts_today || 0,
      icon: '📅',
      color: '#9b59b6',
    },
  ];

  return (
    <div className="metrics-cards">
      {cards.map((card, index) => (
        <div
          key={index}
          className="metric-card"
          style={{ borderTopColor: card.color }}
        >
          <div className="metric-icon">{card.icon}</div>
          <div className="metric-value">{card.value}</div>
          <div className="metric-title">{card.title}</div>
        </div>
      ))}
    </div>
  );
};

export default MetricsCards;