import React from 'react';
import { Target, ArrowRight, Lightbulb, CheckCircle } from 'lucide-react';

export default function JTBDMatrix({ jtbdData }) {
  const fallbackJTBD = {
    jtbd_items: [
      {
        jtbd_id: "jtbd_001",
        underlying_need: "Look presentable for an impromptu morning meeting in 20 minutes",
        context: "Short notice morning routine; discovered missing grooming product",
        legacy_category: "Personal Care",
        solution_opportunity: "20-Minute Emergency Grooming Kit with guaranteed fast delivery tag",
        prevalence: "high"
      },
      {
        jtbd_id: "jtbd_002",
        underlying_need: "Instant stress relief and cognitive reset during intense work hours",
        context: "Late afternoon work fatigue / mid-shift energy slump",
        legacy_category: "Snacks & Beverages",
        solution_opportunity: "Curated 'Focus & Energy Break' sample bundles with zero decision overhead",
        prevalence: "high"
      },
      {
        jtbd_id: "jtbd_003",
        underlying_need: "Immediate pet relief without leaving house during rain/work",
        context: "Sudden pet food/treat exhaustion during bad weather",
        legacy_category: "Pet Supplies",
        solution_opportunity: "'Paws & Treat Express' sample add-ons at grocery checkout",
        prevalence: "medium"
      }
    ]
  };

  const data = jtbdData && jtbdData.jtbd_items ? jtbdData : fallbackJTBD;
  const items = data.jtbd_items || [];

  return (
    <div className="glass-card animate-fade-in" style={{ padding: '24px', marginBottom: '32px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <Target size={22} style={{ color: '#38bdf8' }} />
            <h2 className="gradient-heading" style={{ fontSize: '1.4rem', fontWeight: 700 }}>
              Agent 4: Jobs-To-Be-Done (JTBD) Matrix
            </h2>
          </div>
          <p style={{ fontSize: '0.86rem', color: '#94a3b8' }}>
            Understanding fundamental human needs vs. static app categories
          </p>
        </div>
        <span className="glass-pill" style={{ color: '#38bdf8' }}>
          Human Need Mapping
        </span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '18px' }}>
        {items.map(item => (
          <div
            key={item.jtbd_id}
            style={{
              background: 'rgba(15,23,42,0.7)',
              borderRadius: '12px',
              padding: '20px',
              border: '1px solid rgba(56,189,248,0.25)',
              display: 'flex',
              flexDirection: 'column',
              justify: 'space-between'
            }}
          >
            <div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
                <span className="glass-pill" style={{ color: '#94a3b8', fontSize: '0.72rem' }}>
                  Category: <strong style={{ color: '#f8fafc' }}>{item.legacy_category}</strong>
                </span>
                <span className="glass-pill" style={{ color: '#38bdf8', fontSize: '0.7rem', textTransform: 'uppercase' }}>
                  {item.prevalence} Demand
                </span>
              </div>

              <div style={{ marginBottom: '14px' }}>
                <div style={{ fontSize: '0.74rem', color: '#64748b', fontWeight: 700, textTransform: 'uppercase', marginBottom: '4px' }}>
                  True Customer Job To Be Done:
                </div>
                <div style={{ fontSize: '0.98rem', fontWeight: 700, color: '#38bdf8', lineHeight: 1.4 }}>
                  "{item.underlying_need}"
                </div>
              </div>

              <div style={{ fontSize: '0.82rem', color: '#94a3b8', marginBottom: '14px', background: 'rgba(10,15,26,0.5)', padding: '10px', borderRadius: '6px' }}>
                <strong style={{ color: '#cbd5e1' }}>Context Trigger: </strong> {item.context}
              </div>
            </div>

            <div style={{ background: 'rgba(16,185,129,0.1)', padding: '12px', borderRadius: '8px', border: '1px solid rgba(16,185,129,0.2)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.75rem', fontWeight: 700, color: '#34d399', marginBottom: '4px' }}>
                <Lightbulb size={14} /> Product Solution Opportunity:
              </div>
              <div style={{ fontSize: '0.84rem', color: '#e2e8f0', fontWeight: 600 }}>
                {item.solution_opportunity}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
