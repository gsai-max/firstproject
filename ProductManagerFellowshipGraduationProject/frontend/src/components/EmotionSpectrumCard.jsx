import React, { useState } from 'react';
import { HeartHandshake, AlertTriangle, ShieldAlert, Quote, ChevronDown, ChevronUp } from 'lucide-react';

export default function EmotionSpectrumCard({ emotionData }) {
  const [expandedEmotionId, setExpandedEmotionId] = useState(null);

  const fallbackEmotions = {
    emotions: [
      {
        emotion_id: "em_001",
        emotion_type: "Risk Perception",
        intensity: 0.88,
        prevalence_percentage: 64.0,
        trigger_context: "Browsing unverified non-grocery categories (personal care, pet supplies, electronics accessories)",
        description: "Users fear financial loss or product quality disappointment when departing from trusted grocery staples.",
        representative_quotes: [
          { record_id: "rd_102", text: "Trying new non-grocery categories on Blinkit feels like gambling my money. What if the product is duplicate or expired?", source: "reddit" },
          { record_id: "ps_405", text: "I stick to milk and bread. Bought shampoo once, received damaged bottle. Never buying personal care again.", source: "play_store" }
        ]
      },
      {
        emotion_id: "em_002",
        emotion_type: "Cognitive Decision Fatigue",
        intensity: 0.76,
        prevalence_percentage: 52.0,
        trigger_context: "Navigating deep multi-tier home screen banners during quick 10-minute emergency orders",
        description: "Users open the app under time pressure and refuse to expend mental effort searching unfamiliar product catalogs.",
        representative_quotes: [
          { record_id: "as_204", text: "I open Blinkit to get items in 10 mins, not to spend 15 mins scrolling through 20 category rows.", source: "app_store" }
        ]
      },
      {
        emotion_id: "em_003",
        emotion_type: "Uncertainty & Verification Anxiety",
        intensity: 0.81,
        prevalence_percentage: 45.0,
        trigger_context: "Lack of brand authenticity seals or explicit return guarantees on niche D2C products",
        description: "Lack of visible trust badges or customer reviews leads users to default back to national brand groceries.",
        representative_quotes: [
          { record_id: "tw_809", text: "Blinkit lists new D2C skin care brands, but zero reviews or quality seals. How do I know it's safe?", source: "twitter" }
        ]
      }
    ]
  };

  const data = emotionData && emotionData.emotions ? emotionData : fallbackEmotions;
  const list = data.emotions || [];

  const getEmotionBadge = (type) => {
    if (type.toLowerCase().includes('risk')) return { color: '#f87171', bg: 'rgba(239,68,68,0.15)', icon: ShieldAlert };
    if (type.toLowerCase().includes('fatigue')) return { color: '#c084fc', bg: 'rgba(168,85,247,0.15)', icon: AlertTriangle };
    return { color: '#38bdf8', bg: 'rgba(56,189,248,0.15)', icon: HeartHandshake };
  };

  return (
    <div className="glass-card animate-fade-in" style={{ padding: '24px', marginBottom: '32px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <ShieldAlert size={22} style={{ color: '#ef4444' }} />
            <h2 className="gradient-heading" style={{ fontSize: '1.4rem', fontWeight: 700 }}>
              Agent 2: Emotional Spectrum Analysis
            </h2>
          </div>
          <p style={{ fontSize: '0.86rem', color: '#94a3b8' }}>
            Psychological & emotional barriers blocking cross-category adoption
          </p>
        </div>
        <span className="glass-pill" style={{ color: '#f87171' }}>
          3 Core Emotional Drivers
        </span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '18px' }}>
        {list.map(item => {
          const badge = getEmotionBadge(item.emotion_type);
          const Icon = badge.icon;
          const isExpanded = expandedEmotionId === item.emotion_id;

          return (
            <div 
              key={item.emotion_id} 
              style={{ 
                background: 'rgba(15,23,42,0.7)', 
                borderRadius: '12px', 
                padding: '20px', 
                border: `1px solid ${isExpanded ? badge.color : 'rgba(255,255,255,0.08)'}`,
                transition: 'all 0.2s ease'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <div style={{ padding: '6px', borderRadius: '8px', background: badge.bg, color: badge.color }}>
                    <Icon size={18} />
                  </div>
                  <h3 style={{ fontSize: '1.02rem', fontWeight: 700, color: '#f8fafc' }}>
                    {item.emotion_type}
                  </h3>
                </div>
                <span className="glass-pill" style={{ color: badge.color, fontSize: '0.75rem' }}>
                  {item.prevalence_percentage}% Users
                </span>
              </div>

              <p style={{ fontSize: '0.84rem', color: '#94a3b8', marginBottom: '14px', lineHeight: 1.5 }}>
                {item.description}
              </p>

              {/* Intensity Progress Meter */}
              <div style={{ marginBottom: '14px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: '#64748b', marginBottom: '4px' }}>
                  <span>Emotional Friction Intensity</span>
                  <span style={{ color: badge.color, fontWeight: 700 }}>{Math.round(item.intensity * 100)}%</span>
                </div>
                <div style={{ width: '100%', height: '6px', background: 'rgba(255,255,255,0.08)', borderRadius: '3px', overflow: 'hidden' }}>
                  <div 
                    style={{ 
                      width: `${item.intensity * 100}%`, 
                      height: '100%', 
                      background: `linear-gradient(90deg, ${badge.color} 0%, #38bdf8 100%)`, 
                      borderRadius: '3px' 
                    }} 
                  />
                </div>
              </div>

              {/* Trigger Context */}
              <div style={{ fontSize: '0.78rem', color: '#cbd5e1', background: 'rgba(10,15,26,0.6)', padding: '8px 12px', borderRadius: '6px', marginBottom: '12px' }}>
                <span style={{ color: '#64748b', fontWeight: 600 }}>Trigger: </span>
                {item.trigger_context}
              </div>

              {/* Quotes Toggle Button */}
              {item.representative_quotes && item.representative_quotes.length > 0 && (
                <div>
                  <button
                    onClick={() => setExpandedEmotionId(isExpanded ? null : item.emotion_id)}
                    style={{
                      background: 'transparent',
                      border: 'none',
                      color: badge.color,
                      fontSize: '0.8rem',
                      fontWeight: 600,
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '4px',
                      padding: 0
                    }}
                  >
                    <Quote size={12} /> {isExpanded ? 'Hide Evidence Quotes' : `View ${item.representative_quotes.length} Grounded Quotes`}
                    {isExpanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                  </button>

                  {isExpanded && (
                    <div style={{ marginTop: '10px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                      {item.representative_quotes.map((q, idx) => (
                        <div key={idx} style={{ background: 'rgba(15,23,42,0.9)', padding: '10px', borderRadius: '6px', borderLeft: `3px solid ${badge.color}`, fontSize: '0.78rem', color: '#e2e8f0', fontStyle: 'italic' }}>
                          "{q.text}"
                          <span style={{ display: 'block', fontSize: '0.7rem', color: '#64748b', fontStyle: 'normal', marginTop: '4px', textAlign: 'right' }}>
                            — {q.source} ({q.record_id})
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
