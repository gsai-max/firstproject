import React, { useState } from 'react';
import { Network, Activity, ArrowRight, Layers, Sparkles, Filter, Info } from 'lucide-react';

export default function BehaviorGraphView({ graphData }) {
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [activeNodeId, setActiveNodeId] = useState(null);

  const fallbackGraph = {
    nodes: [
      { id: "n1", label: "Sunday Grocery Emergency Need", node_type: "trigger", details: "Sudden stock-out or weekly recurring staple restocking." },
      { id: "n2", label: "Reorder Previous Grocery Basket", node_type: "habit", details: "Defaulting to 1-click repeat order row in <30 seconds." },
      { id: "n3", label: "Risk Perception & Trial Uncertainty", node_type: "emotion", details: "Fear of poor quality or wrong SKU delivered in non-grocery." },
      { id: "n4", label: "Grocery & Staples Lock-in", node_type: "category", details: "95% basket concentration in milk, bread, produce, snacks." },
      { id: "n5", label: "Zero-Friction Sample Bundle Cross-Sell", node_type: "opportunity", details: "Attach low-cost trial SKU (e.g. pet treat sample) to grocery basket." }
    ],
    edges: [
      { source: "n1", target: "n2", relation: "triggers_habit", weight: 0.95, label: "Triggers Repeat Order" },
      { source: "n2", target: "n3", relation: "reinforces_barrier", weight: 0.88, label: "Bypasses Category Browsing" },
      { source: "n3", target: "n4", relation: "locks_into", weight: 0.91, label: "Restricts to Staples" },
      { source: "n4", target: "n5", relation: "unlocks_opportunity", weight: 0.85, label: "Target for Cross-Sell" }
    ],
    density_summary: {
      total_nodes: 5,
      total_edges: 4,
      network_density: 0.85,
      primary_blocker: "Risk Perception & Habit Loop Tunnel Vision"
    }
  };

  const data = graphData && graphData.nodes ? graphData : fallbackGraph;
  const nodes = data.nodes || [];
  const edges = data.edges || [];
  const summary = data.density_summary || fallbackGraph.density_summary;

  const filteredNodes = selectedCategory === 'all' 
    ? nodes 
    : nodes.filter(n => n.node_type === selectedCategory);

  const getNodeColor = (type) => {
    switch (type) {
      case 'trigger': return { bg: 'rgba(59, 130, 246, 0.15)', border: '#3b82f6', text: '#60a5fa' };
      case 'habit': return { bg: 'rgba(168, 85, 247, 0.15)', border: '#a855f7', text: '#c084fc' };
      case 'emotion': return { bg: 'rgba(239, 68, 68, 0.15)', border: '#ef4444', text: '#f87171' };
      case 'category': return { bg: 'rgba(234, 179, 8, 0.15)', border: '#eab308', text: '#fde047' };
      case 'opportunity': return { bg: 'rgba(16, 185, 129, 0.15)', border: '#10b981', text: '#34d399' };
      default: return { bg: 'rgba(148, 163, 184, 0.15)', border: '#94a3b8', text: '#cbd5e1' };
    }
  };

  return (
    <div className="glass-card animate-fade-in" style={{ padding: '24px', marginBottom: '32px' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <Network size={22} style={{ color: '#10b981' }} />
            <h2 className="gradient-heading" style={{ fontSize: '1.4rem', fontWeight: 700 }}>
              Interconnected Behavior Graph
            </h2>
          </div>
          <p style={{ fontSize: '0.86rem', color: '#94a3b8' }}>
            Graph mapping user triggers, habitual loops, emotional barriers, and category expansion opportunities
          </p>
        </div>

        {/* Metrics Pill Badges */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span className="glass-pill" style={{ color: '#60a5fa' }}>
            <Layers size={14} /> {summary.total_nodes || nodes.length} Nodes
          </span>
          <span className="glass-pill" style={{ color: '#c084fc' }}>
            <Activity size={14} /> {summary.total_edges || edges.length} Edges
          </span>
          <span className="glass-pill" style={{ color: '#34d399' }}>
            <Sparkles size={14} /> Density: {Math.round((summary.network_density || 0.85) * 100)}%
          </span>
        </div>
      </div>

      {/* Filter Tabs */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '20px', overflowX: 'auto', paddingBottom: '4px' }}>
        {['all', 'trigger', 'habit', 'emotion', 'category', 'opportunity'].map(cat => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            style={{
              padding: '6px 14px',
              borderRadius: '20px',
              border: selectedCategory === cat ? '1px solid #10b981' : '1px solid rgba(255,255,255,0.08)',
              background: selectedCategory === cat ? 'rgba(16,185,129,0.18)' : 'rgba(15,23,42,0.6)',
              color: selectedCategory === cat ? '#34d399' : '#94a3b8',
              fontSize: '0.8rem',
              fontWeight: 600,
              cursor: 'pointer',
              textTransform: 'capitalize',
              transition: 'all 0.2s ease'
            }}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Graph Nodes Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '16px', marginBottom: '24px' }}>
        {filteredNodes.map(node => {
          const style = getNodeColor(node.node_type);
          const isSelected = activeNodeId === node.id;
          return (
            <div
              key={node.id}
              onClick={() => setActiveNodeId(isSelected ? null : node.id)}
              style={{
                padding: '16px',
                borderRadius: '12px',
                background: isSelected ? style.bg : 'rgba(15,23,42,0.7)',
                border: `1px solid ${isSelected ? style.border : 'rgba(255,255,255,0.08)'}`,
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                boxShadow: isSelected ? `0 0 16px ${style.bg}` : 'none'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span 
                  style={{ 
                    padding: '2px 8px', 
                    borderRadius: '6px', 
                    fontSize: '0.7rem', 
                    fontWeight: 700, 
                    textTransform: 'uppercase',
                    background: style.bg,
                    color: style.text,
                    border: `1px solid ${style.border}`
                  }}
                >
                  {node.node_type}
                </span>
                <span style={{ fontSize: '0.72rem', color: '#64748b', fontFamily: 'monospace' }}>
                  {node.id}
                </span>
              </div>
              <div style={{ fontSize: '0.92rem', fontWeight: 700, color: '#f8fafc', marginBottom: '6px' }}>
                {node.label}
              </div>
              {node.details && (
                <div style={{ fontSize: '0.78rem', color: '#94a3b8', lineHeight: 1.4 }}>
                  {node.details}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Edge Relationships */}
      <div style={{ background: 'rgba(10,15,26,0.6)', borderRadius: '12px', padding: '16px', border: '1px solid rgba(255,255,255,0.05)' }}>
        <div style={{ fontSize: '0.82rem', fontWeight: 700, color: '#64748b', textTransform: 'uppercase', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '6px' }}>
          <Info size={14} /> Key Pathway Edges & Causal Relations
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {edges.map((edge, idx) => {
            const srcNode = nodes.find(n => n.id === edge.source);
            const tgtNode = nodes.find(n => n.id === edge.target);
            return (
              <div 
                key={idx} 
                style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  justify: 'space-between',
                  padding: '10px 14px', 
                  borderRadius: '8px', 
                  background: 'rgba(15,23,42,0.8)', 
                  border: '1px solid rgba(255,255,255,0.04)',
                  flexWrap: 'wrap',
                  gap: '8px'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '0.85rem' }}>
                  <span style={{ color: '#38bdf8', fontWeight: 600 }}>{srcNode ? srcNode.label : edge.source}</span>
                  <ArrowRight size={14} style={{ color: '#10b981' }} />
                  <span style={{ color: '#c084fc', fontWeight: 600 }}>{tgtNode ? tgtNode.label : edge.target}</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <span style={{ fontSize: '0.78rem', color: '#94a3b8', fontStyle: 'italic' }}>
                    {edge.label || edge.relation}
                  </span>
                  <span className="glass-pill" style={{ fontSize: '0.7rem', color: '#34d399', padding: '2px 8px' }}>
                    W: {edge.weight || 0.9}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
