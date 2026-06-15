import React from 'react';

export default function EmptyState({ onClear, onBroaden }) {
  return (
    <section className="mt-lg animate-fadeIn">
      <div className="glass-panel-2 rounded-xl p-lg flex flex-col items-center justify-center text-center min-h-[400px] border-dashed border-2 border-surface-variant relative overflow-hidden">
        {/* Atmospheric radial red glow background */}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-error-container/10 via-transparent to-transparent pointer-events-none"></div>
        
        <span className="material-symbols-outlined text-[64px] text-error mb-md opacity-80" style={{ fontVariationSettings: "'FILL' 1" }}>
          warning
        </span>
        
        <h3 className="font-title-md text-title-md text-on-surface mb-sm font-semibold">No Results Found</h3>
        
        <p className="font-body-md text-body-md text-on-surface-variant max-w-md mb-lg leading-relaxed">
          ⚠️ No restaurants match these filters. Try expanding your rating boundary, updating your budget, or selecting a different cuisine!
        </p>
        
        <div className="flex gap-md relative z-10">
          <button
            type="button"
            onClick={onClear}
            className="px-md py-sm bg-surface-variant hover:bg-surface-variant/80 text-on-surface rounded-lg font-label-md text-label-md border border-white/5 transition-all active:scale-95 cursor-pointer"
          >
            Clear Filters
          </button>
          
          <button
            type="button"
            onClick={onBroaden}
            className="px-md py-sm bg-inverse-primary text-white rounded-lg font-label-md text-label-md glow-red hover:brightness-110 transition-all active:scale-95 cursor-pointer"
          >
            Broaden Search
          </button>
        </div>
      </div>
    </section>
  );
}
