import React from 'react';
import { HelpCircle, Filter, CheckCircle2 } from 'lucide-react';

export default function ResearchQuestionNav({ selectedRQ, onSelectRQ }) {
  const researchQuestions = [
    { id: 'all', title: 'All Insights & Themes', desc: 'Show complete un-filtered discovery matrix' },
    { id: 'Q1', title: 'Q1: Repetitive Category Purchases', desc: 'Why do users repeatedly buy from the same categories?' },
    { id: 'Q2', title: 'Q2: Exploration Barriers', desc: 'What prevents users from exploring new categories?' },
    { id: 'Q3', title: 'Q3: Current Discovery Pathways', desc: 'How do users discover products today?' },
    { id: 'Q4', title: 'Q4: Role of Habits in Shopping', desc: 'What role do habits play in shopping behavior?' },
    { id: 'Q5', title: 'Q5: Pre-Purchase Information Needs', desc: 'What information do users need before trying a new category?' },
    { id: 'Q6', title: 'Q6: Recurring Friction Points', desc: 'What frustrations emerge repeatedly?' },
    { id: 'Q7', title: 'Q7: High-Receptivity User Segments', desc: 'Which user segments are more likely to experiment?' },
    { id: 'Q8', title: 'Q8: Unmet Customer Needs', desc: 'What unmet needs emerge consistently across discussions?' },
  ];

  return (
    <div style={{ marginBottom: '24px' }}>
      <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#64748b', textTransform: 'uppercase', tracking: '0.05em', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '6px' }}>
        <HelpCircle size={14} style={{ color: '#10b981' }} /> Filter by Research Question
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
        {researchQuestions.map((rq) => {
          const isSelected = selectedRQ === rq.id;
          return (
            <button
              key={rq.id}
              onClick={() => onSelectRQ(rq.id)}
              style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: '10px',
                padding: '10px 12px',
                borderRadius: 'var(--radius-md)',
                background: isSelected ? 'rgba(16, 185, 129, 0.15)' : 'transparent',
                border: isSelected ? '1px solid rgba(16, 185, 129, 0.4)' : '1px solid transparent',
                color: isSelected ? '#34d399' : '#94a3b8',
                cursor: 'pointer',
                textAlign: 'left',
                width: '100%',
                transition: 'all 0.2s ease',
              }}
            >
              <div style={{
                minWidth: '24px', height: '24px', borderRadius: '6px',
                background: isSelected ? '#10b981' : 'rgba(255,255,255,0.05)',
                color: isSelected ? '#000' : '#64748b',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: '0.75rem', fontWeight: 700, marginTop: '1px'
              }}>
                {rq.id === 'all' ? '*' : rq.id}
              </div>

              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontSize: '0.85rem', fontWeight: isSelected ? 700 : 500, color: isSelected ? '#f8fafc' : '#cbd5e1' }}>
                  {rq.title}
                </div>
                <div style={{ fontSize: '0.74rem', color: '#64748b', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {rq.desc}
                </div>
              </div>

              {isSelected && <CheckCircle2 size={16} style={{ color: '#10b981', flexShrink: 0, marginTop: '2px' }} />}
            </button>
          );
        })}
      </div>
    </div>
  );
}
