import React from 'react';
import { Users, TrendingUp, ShieldAlert, Sparkles, Target } from 'lucide-react';

export default function ArchetypeSegmentGrid({ archetypeData }) {
  const fallbackArchetypes = {
    archetypes: [
      {
        archetype_id: "arch_001",
        name: "Routine Grocery Buyers",
        description: "95% repeat grocery purchases; heavy reliance on previous order rows with extreme habit persistence.",
        size_percentage: 65.0,
        key_drivers: ["Speed of checkout", "Frictionless 10-min delivery", "Quality grocery consistency"],
        primary_barriers: ["Perceived risk in non-grocery categories", "Habitual grocery tunnel vision"],
        experimentation_propensity: "Low",
        recommended_strategy: "Zero-friction cart cross-sell prompts during checkout for instant sample kits"
      },
      {
        archetype_id: "arch_002",
        name: "Category Explorers",
        description: "Frequently browse new categories and try fresh SKUs when incentivized by quality tags or sample bundles.",
        size_percentage: 15.0,
        key_drivers: ["Novelty discovery", "Curated brand variety", "Exclusive quick-commerce launches"],
        primary_barriers: ["Limited category discovery UI visibility on homepage"],
        experimentation_propensity: "High",
        recommended_strategy: "Personalized 'New Arrivals Ribbon' and exclusive D2C category spotlights"
      },
      {
        archetype_id: "arch_003",
        name: "Value & Discount Seekers",
        description: "Price-sensitive shoppers who cross-compare handling fees and promos across Blinkit, Zepto, and Instamart.",
        size_percentage: 12.0,
        key_drivers: ["Bundle discounts", "Free delivery threshold deals", "Handling fee waivers"],
        primary_barriers: ["Handling fee friction", "Perceived premium markup on non-grocery SKUs"],
        experimentation_propensity: "Medium",
        recommended_strategy: "Cross-category trial bundles (e.g. 'Buy Groceries + Get 30% Off Personal Care')"
      },
      {
        archetype_id: "arch_004",
        name: "Emergency Convenience Users",
        description: "High-income urban professionals buying high-urgency items (electronics accessories, baby items, medicine) on short notice.",
        size_percentage: 8.0,
        key_drivers: ["Ultra-fast 10-min delivery", "Guaranteed genuine products"],
        primary_barriers: ["Stock availability in non-grocery categories"],
        experimentation_propensity: "High",
        recommended_strategy: "'Instant Emergency Replacement' badges with guaranteed stock availability tags"
      }
    ]
  };

  const data = archetypeData && archetypeData.archetypes ? archetypeData : fallbackArchetypes;
  const list = data.archetypes || [];

  const getPropensityStyle = (prop) => {
    switch (prop.toLowerCase()) {
      case 'high': return { color: '#34d399', bg: 'rgba(16,185,129,0.15)' };
      case 'medium': return { color: '#fde047', bg: 'rgba(234,179,8,0.15)' };
      default: return { color: '#f87171', bg: 'rgba(239,68,68,0.15)' };
    }
  };

  return (
    <div className="glass-card animate-fade-in" style={{ padding: '24px', marginBottom: '32px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <Users size={22} style={{ color: '#a855f7' }} />
            <h2 className="gradient-heading" style={{ fontSize: '1.4rem', fontWeight: 700 }}>
              Agent 5: Consumer Archetypes & Segmentation Matrix
            </h2>
          </div>
          <p style={{ fontSize: '0.86rem', color: '#94a3b8' }}>
            Emergent consumer archetypes and category experimentation propensities
          </p>
        </div>
        <span className="glass-pill" style={{ color: '#c084fc' }}>
          4 Key Archetypes
        </span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '18px' }}>
        {list.map(arch => {
          const propStyle = getPropensityStyle(arch.experimentation_propensity);
          return (
            <div
              key={arch.archetype_id}
              style={{
                background: 'rgba(15,23,42,0.7)',
                borderRadius: '12px',
                padding: '20px',
                border: '1px solid rgba(168,85,247,0.25)',
                display: 'flex',
                flexDirection: 'column',
                justify: 'space-between'
              }}
            >
              <div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
                  <span style={{ fontSize: '1.1rem', fontWeight: 700, color: '#f8fafc' }}>
                    {arch.name}
                  </span>
                  <span className="glass-pill" style={{ color: '#c084fc', fontSize: '0.78rem', fontWeight: 700 }}>
                    {arch.size_percentage}% Cohort
                  </span>
                </div>

                <p style={{ fontSize: '0.84rem', color: '#94a3b8', marginBottom: '14px', lineHeight: 1.5 }}>
                  {arch.description}
                </p>

                {/* Experimentation Propensity */}
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 12px', borderRadius: '6px', background: 'rgba(10,15,26,0.6)', marginBottom: '14px' }}>
                  <span style={{ fontSize: '0.78rem', color: '#cbd5e1' }}>Experimentation Propensity:</span>
                  <span style={{ fontSize: '0.75rem', fontWeight: 700, padding: '2px 8px', borderRadius: '4px', background: propStyle.bg, color: propStyle.color }}>
                    {arch.experimentation_propensity} Trial Risk
                  </span>
                </div>

                {/* Drivers & Barriers */}
                <div style={{ fontSize: '0.78rem', color: '#94a3b8', marginBottom: '14px' }}>
                  <div style={{ marginBottom: '6px', color: '#34d399' }}>
                    <strong>Key Drivers: </strong> {arch.key_drivers.join(' • ')}
                  </div>
                  <div style={{ color: '#f87171' }}>
                    <strong>Primary Barriers: </strong> {arch.primary_barriers.join(' • ')}
                  </div>
                </div>
              </div>

              {/* Recommended PM Strategy */}
              <div style={{ background: 'rgba(168,85,247,0.1)', padding: '12px', borderRadius: '8px', border: '1px solid rgba(168,85,247,0.2)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.75rem', fontWeight: 700, color: '#c084fc', marginBottom: '4px' }}>
                  <Target size={14} /> Recommended Growth Strategy:
                </div>
                <div style={{ fontSize: '0.82rem', color: '#e2e8f0', fontWeight: 600 }}>
                  {arch.recommended_strategy}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
