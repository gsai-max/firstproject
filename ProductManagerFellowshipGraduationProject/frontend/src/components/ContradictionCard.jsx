import React from 'react';
import { GitCompare, AlertTriangle, Lightbulb, CheckCircle2 } from 'lucide-react';

export default function ContradictionCard({ contradictionData }) {
  const fallbackContradictions = {
    contradictions: [
      {
        contradiction_id: "ct_001",
        stated_desire: "Users express wanting more product discovery and exciting new SKUs on the home screen",
        observed_behavior: "95% of purchases are completed via the 'Reorder Past Items' row in under 30 seconds",
        underlying_paradox: "Users desire category discovery in theory, but refuse to invest cognitive effort or time to actively browse",
        product_insight: "Discovery must be integrated effortlessly into reorder flows without requiring manual catalog navigation",
        confidence_score: 0.94,
        evidence_count: 18400
      },
      {
        contradiction_id: "ct_002",
        stated_desire: "Users demand wider non-grocery product selection and variety",
        observed_behavior: "When presented with 50+ new non-grocery options, category conversion rates drop due to decision fatigue",
        underlying_paradox: "Wider selection increases uncertainty; users need curated top-3 options rather than endless listings",
        product_insight: "Limit initial cross-category discovery ribbons to 3 pre-vetted 'Best Seller' SKUs with 100% Quality Seals",
        confidence_score: 0.91,
        evidence_count: 12100
      }
    ]
  };

  const data = contradictionData && contradictionData.contradictions ? contradictionData : fallbackContradictions;
  const list = data.contradictions || [];

  return (
    <div className="glass-card animate-fade-in" style={{ padding: '24px', marginBottom: '32px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <GitCompare size={22} style={{ color: '#eab308' }} />
            <h2 className="gradient-heading" style={{ fontSize: '1.4rem', fontWeight: 700 }}>
              Agent 6: Stated vs. Actual Contradiction Detector
            </h2>
          </div>
          <p style={{ fontSize: '0.86rem', color: '#94a3b8' }}>
            Uncovering counter-intuitive paradoxes between stated user desires vs. actual purchasing habits
          </p>
        </div>
        <span className="glass-pill" style={{ color: '#fde047' }}>
          Behavioral Paradox Engine
        </span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        {list.map(item => (
          <div
            key={item.contradiction_id}
            style={{
              background: 'rgba(15,23,42,0.75)',
              borderRadius: '12px',
              padding: '20px',
              border: '1px solid rgba(234,179,8,0.3)',
              boxShadow: '0 4px 20px rgba(0,0,0,0.2)'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px', flexWrap: 'wrap', gap: '8px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.95rem', fontWeight: 700, color: '#fde047' }}>
                <AlertTriangle size={16} /> Behavior Paradox ({item.contradiction_id})
              </div>
              <div style={{ display: 'flex', gap: '8px' }}>
                <span className="glass-pill" style={{ color: '#34d399', fontSize: '0.72rem' }}>
                  Confidence: {Math.round(item.confidence_score * 100)}%
                </span>
                <span className="glass-pill" style={{ color: '#94a3b8', fontSize: '0.72rem' }}>
                  {item.evidence_count.toLocaleString()} Evidence Reviews
                </span>
              </div>
            </div>

            {/* Comparison Split Row */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '14px', marginBottom: '14px' }}>
              {/* Stated Desire */}
              <div style={{ background: 'rgba(59,130,246,0.1)', padding: '14px', borderRadius: '8px', border: '1px solid rgba(59,130,246,0.2)' }}>
                <div style={{ fontSize: '0.72rem', fontWeight: 700, color: '#60a5fa', textTransform: 'uppercase', marginBottom: '4px' }}>
                  🗣️ Stated User Desire
                </div>
                <div style={{ fontSize: '0.88rem', color: '#e2e8f0', fontWeight: 600, lineHeight: 1.4 }}>
                  "{item.stated_desire}"
                </div>
              </div>

              {/* Observed Behavior */}
              <div style={{ background: 'rgba(239,68,68,0.1)', padding: '14px', borderRadius: '8px', border: '1px solid rgba(239,68,68,0.2)' }}>
                <div style={{ fontSize: '0.72rem', fontWeight: 700, color: '#f87171', textTransform: 'uppercase', marginBottom: '4px' }}>
                  📊 Observed Purchase Behavior
                </div>
                <div style={{ fontSize: '0.88rem', color: '#e2e8f0', fontWeight: 600, lineHeight: 1.4 }}>
                  "{item.observed_behavior}"
                </div>
              </div>
            </div>

            {/* Underlying Paradox */}
            <div style={{ background: 'rgba(234,179,8,0.08)', padding: '12px', borderRadius: '8px', border: '1px solid rgba(234,179,8,0.2)', marginBottom: '14px' }}>
              <div style={{ fontSize: '0.74rem', fontWeight: 700, color: '#fde047', textTransform: 'uppercase', marginBottom: '4px' }}>
                💡 Underlying Psychological Paradox:
              </div>
              <div style={{ fontSize: '0.86rem', color: '#f8fafc', fontWeight: 600 }}>
                {item.underlying_paradox}
              </div>
            </div>

            {/* Actionable Product Strategy */}
            <div style={{ background: 'rgba(16,185,129,0.1)', padding: '12px', borderRadius: '8px', border: '1px solid rgba(16,185,129,0.2)', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <CheckCircle2 size={16} style={{ color: '#34d399', flexShrink: 0 }} />
              <div>
                <span style={{ fontSize: '0.74rem', fontWeight: 700, color: '#34d399', textTransform: 'uppercase' }}>PM Strategic Insight: </span>
                <span style={{ fontSize: '0.84rem', color: '#e2e8f0', fontWeight: 600 }}>{item.product_insight}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
