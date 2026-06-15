import React from 'react';

export default function TopNavBar() {
  return (
    <>
      {/* TopNavBar (Mobile Only) */}
      <nav className="md:hidden flex justify-between items-center px-lg h-xl bg-surface/80 backdrop-blur-md fixed top-0 w-full z-50 border-b border-white/10 shadow-xl">
        <div className="font-display-lg text-headline-lg-mobile tracking-tighter text-primary">GASTRO AI</div>
        <div className="flex gap-sm">
          <span className="material-symbols-outlined text-on-surface-variant hover:text-primary transition-colors cursor-pointer active:scale-95">notifications</span>
          <span className="material-symbols-outlined text-on-surface-variant hover:text-primary transition-colors cursor-pointer active:scale-95">account_circle</span>
        </div>
      </nav>

      {/* TopNavBar (Desktop Web) */}
      <nav className="hidden md:flex justify-between items-center px-lg h-xl fixed top-0 w-full z-50 bg-surface/80 backdrop-blur-md shadow-xl border-b border-white/10">
        <div className="font-display-lg text-headline-lg tracking-tighter text-primary">GASTRO AI</div>
        <div className="flex gap-md items-center">
          <span class="material-symbols-outlined text-on-surface-variant hover:text-primary transition-colors cursor-pointer active:scale-95">notifications</span>
          <span class="material-symbols-outlined text-on-surface-variant hover:text-primary transition-colors cursor-pointer active:scale-95">account_circle</span>
        </div>
      </nav>
    </>
  );
}
