import React from 'react';
import { Repeat, ArrowRight, Zap, Award, AlertCircle, CheckCircle2 } from 'lucide-react';

export default function HabitLoopVisualizer({ habitData }) {
  const fallbackHabits = {
    habit_loops: [
      {
        habit_id: "hb_001",
        name: "Sunday Grocery Emergency Loop",
        trigger: "Sunday morning routine or sudden out-of-stock grocery item",
        action: "Open Blinkit app & click 'Reorder Past Grocery Items' row",
        reward: "10-minute instant delivery & instant peace of mind",
        exploration_impact: "Category exploration decreases to near 0%",
        frequency_percentage: 73.0,
        affected_segments: ["Routine Grocery Buyers", "Urban Working Professionals"]
      },
      {
        habit_id: "hb_002",
        name: "Late Night Snack Urgency Loop",
        trigger: "Late night impulse hunger / gaming / work break",
        action: "Direct search for chips/beverages & immediate checkout",
        reward: "Instant snack gratification in <15 minutes",
        exploration_impact: "Restricted strictly to Beverages & Snacks categories",
        frequency_percentage: 58.0,
        affected_segments: ["Tech-Savvy Young Adults", "Late-Night Impulse Shoppers"]
      }
    ]
  };

  const data = habitData && habitData.habit_loops ? habitData : fallbackHabits;
  const habits = data.habit_loops || [];

  return (
    <div className="glass-card animate-fade-in" style={{ padding: '24px', marginBottom: '32px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <Repeat size={22} style={{ color: '#c084fc' }} />
            <h2 className="gradient-heading" style={{ fontSize: '1.4rem', fontWeight: 700 }}>
              Agent 3: Habit Loop Detector (Secret Weapon)
            </h2>
          </div>
          <p style={{ fontSize: '0.86rem', color: '#94a3b8' }}>
            Behavioral science extraction: Trigger $\rightarrow$ Action $\rightarrow$ Reward $\rightarrow$ Exploration Lock-in
          </p>
        </div>
        <span className="glass-pill" style={{ color: '#c084fc' }}>
          Behavioral Science Engine
        </span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        {habits.map(habit => (
          <div 
            key={habit.habit_id}
            style={{
              background: 'rgba(15,23,42,0.75)',
              borderRadius: '12px',
              padding: '20px',
              border: '1px solid rgba(168,85,247,0.3)',
              boxShadow: '0 4px 20px rgba(0,0,0,0.2)'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px', flexWrap: 'wrap', gap: '8px' }}>
              <div style={{ fontSize: '1.05rem', fontWeight: 700, color: '#f8fafc' }}>
                {habit.name}
              </div>
              <div style={{ display: 'flex', gap: '8px' }}>
                <span className="glass-pill" style={{ color: '#c084fc', fontSize: '0.75rem' }}>
                  {habit.frequency_percentage}% Frequency
                </span>
              </div>
            </div>

            {/* Loop Sequence Flow */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px', marginBottom: '16px' }}>
              {/* Trigger */}
              <div style={{ background: 'rgba(59,130,246,0.1)', padding: '14px', borderRadius: '8px', border: '1px solid rgba(59,130,246,0.2)' }}>
                <div style={{ fontSize: '0.72rem', fontWeight: 700, color: '#60a5fa', textTransform: 'uppercase', marginBottom: '4px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <Zap size={12} /> 1. Trigger
                </div>
                <div style={{ fontSize: '0.85rem', color: '#e2e8f0', fontWeight: 600 }}>
                  {habit.trigger}
                </div>
              </div>

              {/* Action */}
              <div style={{ background: 'rgba(168,85,247,0.1)', padding: '14px', borderRadius: '8px', border: '1px solid rgba(168,85,247,0.2)' }}>
                <div style={{ fontSize: '0.72rem', fontWeight: 700, color: '#c084fc', textTransform: 'uppercase', marginBottom: '4px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <Repeat size={12} /> 2. Habitual Action
                </div>
                <div style={{ fontSize: '0.85rem', color: '#e2e8f0', fontWeight: 600 }}>
                  {habit.action}
                </div>
              </div>

              {/* Reward */}
              <div style={{ background: 'rgba(16,185,129,0.1)', padding: '14px', borderRadius: '8px', border: '1px solid rgba(16,185,129,0.2)' }}>
                <div style={{ fontSize: '0.72rem', fontWeight: 700, color: '#34d399', textTransform: 'uppercase', marginBottom: '4px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <Award size={12} /> 3. Reward
                </div>
                <div style={{ fontSize: '0.85rem', color: '#e2e8f0', fontWeight: 600 }}>
                  {habit.reward}
                </div>
              </div>
            </div>

            {/* Impact & Segment Footer */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px', background: 'rgba(10,15,26,0.6)', padding: '10px 14px', borderRadius: '8px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.8rem', color: '#f87171' }}>
                <AlertCircle size={14} />
                <span style={{ fontWeight: 600 }}>Exploration Impact: </span>
                {habit.exploration_impact}
              </div>
              <div style={{ display: 'flex', gap: '6px' }}>
                {habit.affected_segments.map((seg, idx) => (
                  <span key={idx} style={{ fontSize: '0.7rem', color: '#94a3b8', background: 'rgba(255,255,255,0.05)', padding: '2px 8px', borderRadius: '4px' }}>
                    {seg}
                  </span>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
