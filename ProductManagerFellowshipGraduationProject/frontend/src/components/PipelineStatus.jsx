import React, { useState } from 'react';
import { Activity, RefreshCw, CheckCircle, Clock, Server } from 'lucide-react';

export default function PipelineStatus({ statusData, onTriggerRun }) {
  const [isRunning, setIsRunning] = useState(false);
  const [message, setMessage] = useState('');

  const handleRun = async () => {
    setIsRunning(true);
    setMessage('Triggering pipeline run...');
    try {
      if (onTriggerRun) {
        await onTriggerRun();
      }
      setMessage('Pipeline execution complete and cache refreshed!');
    } catch (err) {
      setMessage('Pipeline trigger error: ' + err.message);
    } finally {
      setIsRunning(false);
      setTimeout(() => setMessage(''), 4000);
    }
  };

  const lastRun = statusData?.last_run_timestamp 
    ? new Date(statusData.last_run_timestamp).toLocaleString()
    : new Date().toLocaleString();

  return (
    <div className="glass-card" style={{ padding: '24px', marginBottom: '32px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ width: '40px', height: '40px', borderRadius: '12px', background: 'rgba(16,185,129,0.15)', border: '1px solid rgba(16,185,129,0.3)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#10b981' }}>
            <Activity size={20} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#f8fafc' }}>
                Discovery Engine Pipeline Health
              </h3>
              <span className="glass-pill" style={{ color: '#34d399', background: 'rgba(16,185,129,0.15)', borderColor: 'rgba(16,185,129,0.3)' }}>
                <CheckCircle size={12} /> ONLINE
              </span>
            </div>
            <p style={{ fontSize: '0.82rem', color: '#94a3b8', display: 'flex', alignItems: 'center', gap: '6px', marginTop: '4px' }}>
              <Clock size={12} /> Last updated: {lastRun}
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <button 
            onClick={handleRun} 
            disabled={isRunning}
            className="btn-primary"
            style={{ opacity: isRunning ? 0.7 : 1, cursor: isRunning ? 'not-allowed' : 'pointer' }}
          >
            <RefreshCw size={16} className={isRunning ? 'animate-spin' : ''} />
            {isRunning ? 'Running Pipeline...' : 'Run Fresh Pipeline'}
          </button>
        </div>
      </div>

      {message && (
        <div style={{ marginTop: '14px', padding: '10px 14px', background: 'rgba(6,182,212,0.1)', border: '1px solid rgba(6,182,212,0.3)', borderRadius: '8px', color: '#22d3ee', fontSize: '0.85rem' }}>
          {message}
        </div>
      )}
    </div>
  );
}
