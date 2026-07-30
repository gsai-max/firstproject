import React, { useState } from 'react';
import { Search, Filter, Layers, MessageSquare, Tag } from 'lucide-react';

export default function ThemeExplorer({ themesData }) {
  const [selectedSource, setSelectedSource] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');

  const themesBySource = themesData?.themes_by_source || {};
  const consolidatedThemes = themesData?.consolidated_themes || [];

  // Flatten all themes for filtering
  let allThemes = [];
  Object.entries(themesBySource).forEach(([src, tList]) => {
    if (Array.isArray(tList)) {
      tList.forEach(t => allThemes.push({ ...t, source: src }));
    }
  });

  const sources = ['all', ...Object.keys(themesBySource)];

  const filteredThemes = allThemes.filter(theme => {
    const matchesSource = selectedSource === 'all' || theme.source === selectedSource;
    const matchesSearch = 
      theme.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      theme.description?.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesSource && matchesSearch;
  });

  const getFreqColor = (freq) => {
    switch (freq?.toLowerCase()) {
      case 'high': return '#10b981';
      case 'medium': return '#f59e0b';
      case 'low': return '#94a3b8';
      default: return '#06b6d4';
    }
  };

  return (
    <div style={{ marginBottom: '32px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px', marginBottom: '20px' }}>
        <div>
          <h2 className="gradient-heading" style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '4px' }}>
            Extracted Theme Explorer
          </h2>
          <p style={{ fontSize: '0.88rem', color: '#94a3b8' }}>
            Browse recurring customer friction clusters extracted per feedback source
          </p>
        </div>

        {/* Search Bar */}
        <div style={{ position: 'relative', width: '280px' }}>
          <Search size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#64748b' }} />
          <input
            type="text"
            placeholder="Search themes..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              width: '100%',
              padding: '8px 12px 8px 36px',
              background: 'rgba(255,255,255,0.05)',
              border: '1px solid var(--border-color)',
              borderRadius: 'var(--radius-md)',
              color: '#f8fafc',
              fontSize: '0.85rem',
              outline: 'none',
            }}
          />
        </div>
      </div>

      {/* Source Filter Tabs */}
      <div style={{ display: 'flex', gap: '8px', overflowX: 'auto', paddingBottom: '8px', marginBottom: '20px' }}>
        {sources.map((src) => (
          <button
            key={src}
            onClick={() => setSelectedSource(src)}
            className={selectedSource === src ? 'btn-primary' : 'btn-secondary'}
            style={{
              padding: '6px 14px',
              fontSize: '0.82rem',
              textTransform: 'capitalize',
              borderRadius: '9999px',
            }}
          >
            {src === 'all' ? 'All Sources' : src.replace('_', ' ')}
          </button>
        ))}
      </div>

      {/* Themes Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '16px' }}>
        {filteredThemes.map((theme, idx) => (
          <div key={idx} className="glass-card" style={{ padding: '20px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '8px', marginBottom: '10px' }}>
                <span className="glass-pill" style={{ color: '#06b6d4', textTransform: 'capitalize' }}>
                  <Layers size={12} /> {theme.source?.replace('_', ' ')}
                </span>
                <span className="glass-pill" style={{ color: getFreqColor(theme.frequency) }}>
                  {theme.frequency?.toUpperCase()} FREQUENCY
                </span>
              </div>

              <h4 style={{ fontSize: '1.02rem', fontWeight: 700, color: '#f8fafc', marginBottom: '8px', lineHeight: 1.35 }}>
                {theme.name}
              </h4>

              <p style={{ fontSize: '0.85rem', color: '#94a3b8', lineHeight: 1.5, marginBottom: '14px' }}>
                {theme.description}
              </p>
            </div>

            <div style={{ paddingTop: '12px', borderTop: '1px solid rgba(255,255,255,0.05)', display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.78rem', color: '#64748b' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                <MessageSquare size={12} /> {theme.representative_quotes?.length || 0} Quotes
              </div>

              <div style={{ display: 'flex', gap: '4px' }}>
                {theme.research_question_mapping?.slice(0, 2).map((rq, rIdx) => (
                  <span key={rIdx} className="glass-pill" style={{ padding: '1px 6px', fontSize: '0.7rem' }}>
                    {rq}
                  </span>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>

      {filteredThemes.length === 0 && (
        <div style={{ textAling: 'center', padding: '40px', color: '#64748b', fontSize: '0.9rem' }}>
          No themes matching the selected filter or search query.
        </div>
      )}
    </div>
  );
}
