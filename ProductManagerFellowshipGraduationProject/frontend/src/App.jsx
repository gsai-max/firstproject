import React, { useState, useEffect } from 'react';
import ExecutiveSummary from './components/ExecutiveSummary';
import InsightCard from './components/InsightCard';
import ThemeExplorer from './components/ThemeExplorer';
import SourceAnalytics from './components/SourceAnalytics';
import ResearchQuestionNav from './components/ResearchQuestionNav';
import PipelineStatus from './components/PipelineStatus';
import HypothesisExperimentViewer from './components/HypothesisExperimentViewer';

// Phase 6 Multi-Agent Behavioral Science Components
import BehaviorGraphView from './components/BehaviorGraphView';
import EmotionSpectrumCard from './components/EmotionSpectrumCard';
import HabitLoopVisualizer from './components/HabitLoopVisualizer';
import JTBDMatrix from './components/JTBDMatrix';
import ArchetypeSegmentGrid from './components/ArchetypeSegmentGrid';
import ContradictionCard from './components/ContradictionCard';
import ConsensusReportModal from './components/ConsensusReportModal';

import { Target, Layers, BarChart2, Zap, RefreshCw, X, Sparkles, Network, ShieldCheck, HeartHandshake, Repeat, GitCompare, Users } from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('insights'); // 'insights' | 'multi_agent' | 'analytics'
  const [selectedRQ, setSelectedRQ] = useState('all');
  const [isConsensusModalOpen, setIsConsensusModalOpen] = useState(false);

  // Core Intelligence States
  const [insights, setInsights] = useState([]);
  const [themesData, setThemesData] = useState({ themes_by_source: {}, consolidated_themes: [] });
  const [patterns, setPatterns] = useState([]);
  const [hypotheses, setHypotheses] = useState([]);
  const [experiments, setExperiments] = useState([]);
  const [summaryData, setSummaryData] = useState(null);
  const [categoryData, setCategoryData] = useState(null);
  const [sentimentData, setSentimentData] = useState(null);
  const [statusData, setStatusData] = useState(null);

  // Phase 5 & 6 Multi-Agent States
  const [graphData, setGraphData] = useState(null);
  const [emotionData, setEmotionData] = useState(null);
  const [habitData, setHabitData] = useState(null);
  const [jtbdData, setJtbdData] = useState(null);
  const [archetypeData, setArchetypeData] = useState(null);
  const [contradictionData, setContradictionData] = useState(null);
  const [validationReport, setValidationReport] = useState(null);

  const [loading, setLoading] = useState(true);
  const API_BASE = import.meta.env.VITE_API_URL || '/api/v1';

  const fetchData = async () => {
    setLoading(true);
    try {
      const endpoints = [
        `${API_BASE}/insights`,
        `${API_BASE}/themes`,
        `${API_BASE}/analytics/summary`,
        `${API_BASE}/analytics/categories`,
        `${API_BASE}/analytics/sentiment`,
        `${API_BASE}/pipeline/status`,
        `${API_BASE}/patterns`,
        `${API_BASE}/hypotheses`,
        `${API_BASE}/experiments`,
        `${API_BASE}/behavior-graph`,
        `${API_BASE}/archetypes`,
        `${API_BASE}/agents/emotion`,
        `${API_BASE}/agents/habit`,
        `${API_BASE}/agents/jtbd`,
        `${API_BASE}/agents/contradiction`,
        `${API_BASE}/validation/report`
      ];

      const results = await Promise.allSettled(
        endpoints.map(url => fetch(url).then(r => r.ok ? r.json() : Promise.reject()))
      );

      if (results[0].status === 'fulfilled') setInsights(results[0].value.insights || []);
      if (results[1].status === 'fulfilled') setThemesData(results[1].value);
      if (results[2].status === 'fulfilled') setSummaryData(results[2].value);
      if (results[3].status === 'fulfilled') setCategoryData(results[3].value);
      if (results[4].status === 'fulfilled') setSentimentData(results[4].value);
      if (results[5].status === 'fulfilled') setStatusData(results[5].value);
      if (results[6].status === 'fulfilled') setPatterns(results[6].value.patterns || []);
      if (results[7].status === 'fulfilled') setHypotheses(results[7].value.hypotheses || []);
      if (results[8].status === 'fulfilled') setExperiments(results[8].value.experiments || []);
      if (results[9].status === 'fulfilled') setGraphData(results[9].value);
      if (results[10].status === 'fulfilled') setArchetypeData(results[10].value);
      if (results[11].status === 'fulfilled') setEmotionData(results[11].value);
      if (results[12].status === 'fulfilled') setHabitData(results[12].value);
      if (results[13].status === 'fulfilled') setJtbdData(results[13].value);
      if (results[14].status === 'fulfilled') setContradictionData(results[14].value);
      if (results[15].status === 'fulfilled') setValidationReport(results[15].value);

    } catch (err) {
      console.warn("API fetch error, components will use built-in fallback datasets:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleTriggerRun = async () => {
    try {
      await fetch(`${API_BASE}/pipeline/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ stage: 'all' })
      });
      await fetchData();
    } catch (err) {
      console.error("Pipeline trigger failed:", err);
    }
  };

  const filteredInsights = selectedRQ === 'all'
    ? insights
    : insights.filter(ins => ins.research_questions_addressed?.includes(selectedRQ));

  return (
    <div className="app-container">
      {/* Sidebar Navigation */}
      <aside className="sidebar">
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '28px', padding: '0 8px' }}>
          <div style={{ width: '36px', height: '36px', borderRadius: '10px', background: 'linear-gradient(135deg, #10b981 0%, #06b6d4 100%)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#000', fontWeight: 800 }}>
            ⚡
          </div>
          <div>
            <div style={{ fontSize: '1.05rem', fontWeight: 800, color: '#f8fafc', letterSpacing: '-0.01em', fontFamily: 'var(--font-heading)' }}>
              Blinkit AI
            </div>
            <div style={{ fontSize: '0.72rem', color: '#10b981', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Discovery Engine
            </div>
          </div>
        </div>

        {/* Section Tabs */}
        <div style={{ marginBottom: '24px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
          <button
            onClick={() => setActiveTab('insights')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              padding: '10px 14px',
              borderRadius: '8px',
              border: 'none',
              background: activeTab === 'insights' ? 'rgba(16,185,129,0.18)' : 'transparent',
              color: activeTab === 'insights' ? '#34d399' : '#94a3b8',
              fontSize: '0.85rem',
              fontWeight: 600,
              cursor: 'pointer',
              textAlign: 'left'
            }}
          >
            <Target size={16} /> Product Insights
          </button>
          <button
            onClick={() => setActiveTab('multi_agent')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              padding: '10px 14px',
              borderRadius: '8px',
              border: 'none',
              background: activeTab === 'multi_agent' ? 'rgba(168,85,247,0.18)' : 'transparent',
              color: activeTab === 'multi_agent' ? '#c084fc' : '#94a3b8',
              fontSize: '0.85rem',
              fontWeight: 600,
              cursor: 'pointer',
              textAlign: 'left'
            }}
          >
            <Network size={16} /> Behavior Graph & 6 Agents
          </button>
          <button
            onClick={() => setActiveTab('analytics')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              padding: '10px 14px',
              borderRadius: '8px',
              border: 'none',
              background: activeTab === 'analytics' ? 'rgba(56,189,248,0.18)' : 'transparent',
              color: activeTab === 'analytics' ? '#38bdf8' : '#94a3b8',
              fontSize: '0.85rem',
              fontWeight: 600,
              cursor: 'pointer',
              textAlign: 'left'
            }}
          >
            <BarChart2 size={16} /> Source & Theme Analytics
          </button>
        </div>

        {/* Research Questions Filter */}
        <ResearchQuestionNav selectedRQ={selectedRQ} onSelectRQ={setSelectedRQ} />

        {/* Consensus Modal Trigger Button */}
        <div style={{ marginTop: '20px', paddingTop: '16px', borderTop: '1px solid var(--border-color)' }}>
          <button
            onClick={() => setIsConsensusModalOpen(true)}
            style={{
              width: '100%',
              padding: '10px',
              borderRadius: '8px',
              border: '1px solid rgba(16,185,129,0.3)',
              background: 'rgba(16,185,129,0.1)',
              color: '#34d399',
              fontSize: '0.8rem',
              fontWeight: 700,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justify: 'center',
              gap: '6px'
            }}
          >
            <ShieldCheck size={16} /> Multi-LLM Consensus
          </button>
        </div>

        <div style={{ marginTop: 'auto', paddingTop: '16px', borderTop: '1px solid var(--border-color)', fontSize: '0.75rem', color: '#64748b' }}>
          <div>Blinkit Product Fellowship</div>
          <div style={{ color: '#94a3b8', marginTop: '2px' }}>Graduation Project 2026</div>
        </div>
      </aside>

      {/* Main Dashboard Content */}
      <main className="main-content">
        <ExecutiveSummary 
          summaryData={summaryData} 
          totalInsights={insights.length || 10}
          totalThemes={themesData?.total_themes || 12}
          rqCoverage={statusData?.details?.rq_coverage || '100%'}
          onOpenConsensus={() => setIsConsensusModalOpen(true)}
        />

        <PipelineStatus statusData={statusData} onTriggerRun={handleTriggerRun} />

        {/* Navigation Tab Content */}
        {activeTab === 'insights' && (
          <>
            {/* Closed-Loop Growth Intelligence Section */}
            <HypothesisExperimentViewer 
              patterns={patterns} 
              hypotheses={hypotheses} 
              experiments={experiments} 
              onOutcomeLogged={fetchData} 
            />

            {/* Filter Indicator */}
            {selectedRQ !== 'all' && (
              <div className="glass-card animate-fade-in" style={{ padding: '12px 20px', marginBottom: '24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderColor: 'rgba(16,185,129,0.4)', background: 'rgba(16,185,129,0.08)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '0.9rem', color: '#34d399', fontWeight: 600 }}>
                  <Sparkles size={16} /> Filtering by Research Question: <span style={{ color: '#fff', fontWeight: 700 }}>{selectedRQ}</span>
                  <span style={{ fontSize: '0.8rem', color: '#94a3b8', fontWeight: 400 }}>({filteredInsights.length} insights match)</span>
                </div>
                <button 
                  onClick={() => setSelectedRQ('all')}
                  style={{ background: 'transparent', border: 'none', color: '#94a3b8', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.8rem' }}
                >
                  <X size={16} /> Reset Filter
                </button>
              </div>
            )}

            {/* Insights Section */}
            <section style={{ marginBottom: '40px' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
                <div>
                  <h2 className="gradient-heading" style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '4px' }}>
                    Validated Product Insights
                  </h2>
                  <p style={{ fontSize: '0.88rem', color: '#94a3b8' }}>
                    Ranked strategic findings backed by multi-source evidence and representative quotes
                  </p>
                </div>
                <span className="glass-pill" style={{ color: '#34d399' }}>
                  <Target size={12} /> {filteredInsights.length} Insights
                </span>
              </div>

              {loading && insights.length === 0 ? (
                <div style={{ padding: '40px', textAlign: 'center', color: '#64748b' }}>
                  <RefreshCw size={24} className="animate-spin" style={{ margin: '0 auto 12px auto', color: '#10b981' }} />
                  Loading customer intelligence insights...
                </div>
              ) : (
                filteredInsights.map((insight) => (
                  <InsightCard key={insight.id} insight={insight} />
                ))
              )}
            </section>
          </>
        )}

        {activeTab === 'multi_agent' && (
          <section>
            <BehaviorGraphView graphData={graphData} />
            <HabitLoopVisualizer habitData={habitData} />
            <EmotionSpectrumCard emotionData={emotionData} />
            <JTBDMatrix jtbdData={jtbdData} />
            <ArchetypeSegmentGrid archetypeData={archetypeData} />
            <ContradictionCard contradictionData={contradictionData} />
          </section>
        )}

        {activeTab === 'analytics' && (
          <section style={{ marginBottom: '40px' }}>
            <ThemeExplorer themesData={themesData} />
            <div style={{ marginTop: '32px' }}>
              <SourceAnalytics 
                summaryData={summaryData} 
                sentimentData={sentimentData} 
                categoryData={categoryData} 
              />
            </div>
          </section>
        )}
      </main>

      {/* Consensus Modal Overlay */}
      <ConsensusReportModal 
        isOpen={isConsensusModalOpen} 
        onClose={() => setIsConsensusModalOpen(false)}
        reportData={validationReport}
      />
    </div>
  );
}
