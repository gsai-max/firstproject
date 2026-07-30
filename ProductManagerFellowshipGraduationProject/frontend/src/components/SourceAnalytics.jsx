import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from 'recharts';
import { BarChart3, PieChart as PieIcon, Tag } from 'lucide-react';

export default function SourceAnalytics({ summaryData, sentimentData, categoryData }) {
  // 1. Source Breakdown Data
  const sourceBreakdown = summaryData?.source_breakdown || {
    play_store: 829,
    app_store: 6,
    twitter: 6,
    reddit: 5,
    forums: 4,
  };

  const sourceChartData = Object.entries(sourceBreakdown).map(([source, count]) => ({
    name: source.replace('_', ' ').toUpperCase(),
    count: count,
  }));

  // 2. Sentiment Data
  const overallSentiment = sentimentData?.overall_sentiment || {
    positive: 412,
    negative: 397,
    neutral: 41,
  };

  const sentimentChartData = [
    { name: 'Positive', value: overallSentiment.positive || 412, color: '#10b981' },
    { name: 'Negative', value: overallSentiment.negative || 397, color: '#f43f5e' },
    { name: 'Neutral', value: overallSentiment.neutral || 41, color: '#94a3b8' },
  ];

  // 3. Category Data
  const categoriesDist = categoryData?.categories_distribution || {
    general: 631,
    groceries: 84,
    pet_supplies: 60,
    beverages: 40,
    stationery: 39,
    electronics: 15,
    household: 13,
    pharmacy: 10,
  };

  const categoryChartData = Object.entries(categoriesDist)
    .filter(([cat]) => cat !== 'general')
    .map(([cat, count]) => ({
      category: cat.replace('_', ' ').toUpperCase(),
      mentions: count,
    }))
    .slice(0, 8);

  return (
    <div style={{ marginBottom: '32px' }}>
      <div style={{ marginBottom: '20px' }}>
        <h2 className="gradient-heading" style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '4px' }}>
          Source & Feedback Analytics
        </h2>
        <p style={{ fontSize: '0.88rem', color: '#94a3b8' }}>
          Quantitative analytics breakdown of reviews, sentiments, and category mentions
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '20px' }}>
        {/* Source Breakdown Bar Chart */}
        <div className="glass-card" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px', fontSize: '1rem', fontWeight: 700, color: '#f8fafc' }}>
            <BarChart3 size={18} style={{ color: '#10b981' }} /> Record Volume by Platform
          </div>
          <div style={{ width: '100%', height: '220px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={sourceChartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <XAxis dataKey="name" stroke="#64748b" fontSize={11} tickLine={false} />
                <YAxis stroke="#64748b" fontSize={11} tickLine={false} />
                <Tooltip 
                  contentStyle={{ background: '#0f172a', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '8px', color: '#f8fafc' }}
                />
                <Bar dataKey="count" fill="#10b981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Sentiment Distribution Pie Chart */}
        <div className="glass-card" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px', fontSize: '1rem', fontWeight: 700, color: '#f8fafc' }}>
            <PieIcon size={18} style={{ color: '#06b6d4' }} /> Sentiment Distribution
          </div>
          <div style={{ width: '100%', height: '220px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={sentimentChartData} cx="50%" cy="50%" innerRadius={50} outerRadius={80} paddingAngle={4} dataKey="value">
                  {sentimentChartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ background: '#0f172a', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '8px', color: '#f8fafc' }}
                />
                <Legend iconType="circle" wrapperStyle={{ fontSize: '12px', color: '#94a3b8' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Category Mention Distribution */}
        <div className="glass-card" style={{ padding: '24px', gridColumn: '1 / -1' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px', fontSize: '1rem', fontWeight: 700, color: '#f8fafc' }}>
            <Tag size={18} style={{ color: '#8b5cf6' }} /> Non-Grocery Category Mentions (Volume)
          </div>
          <div style={{ width: '100%', height: '220px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={categoryChartData} layout="vertical" margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
                <XAxis type="number" stroke="#64748b" fontSize={11} tickLine={false} />
                <YAxis dataKey="category" type="category" stroke="#64748b" fontSize={11} tickLine={false} width={120} />
                <Tooltip 
                  contentStyle={{ background: '#0f172a', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '8px', color: '#f8fafc' }}
                />
                <Bar dataKey="mentions" fill="#06b6d4" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
