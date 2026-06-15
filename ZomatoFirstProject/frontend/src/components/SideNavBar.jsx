import React from 'react';

export default function SideNavBar({
  locations = [],
  cuisines = [],
  params = {},
  setParams,
  onSubmit,
  loading = false
}) {
  const handleSelectChange = (field, val) => {
    setParams(prev => ({
      ...prev,
      [field]: val
    }));
  };

  const handleBudgetSelect = (tier) => {
    setParams(prev => ({
      ...prev,
      budget: tier
    }));
  };

  const handleRatingChange = (e) => {
    const val = parseFloat(e.target.value);
    setParams(prev => ({
      ...prev,
      rating: val
    }));
  };

  const handleMoodChange = (e) => {
    setParams(prev => ({
      ...prev,
      mood: e.target.value
    }));
  };

  return (
    <aside className="hidden md:flex flex-col p-md pt-xl gap-sm bg-surface-container-low/40 backdrop-blur-sm fixed left-0 top-0 h-full w-[320px] z-40 border-r border-white/5 shadow-2xl overflow-y-auto">
      {/* Profile Header */}
      <div className="mb-lg flex flex-col items-center">
        <img
          alt="User Profile"
          className="w-16 h-16 rounded-full mb-sm border-2 border-surface-variant object-cover"
          src="https://lh3.googleusercontent.com/aida-public/AB6AXuB-m1EyaMAoIP1ADpyaHVeM_8zYEAX-XLXvW7e4HaCoUvVWQOZsxT-Sx6D4rLAD5Ce1-dlI9kAoVjm0Ox7fKDPLchjxyb9jcWduavDVxMykMiDEZHhjffIXw2I0VHkOK9C9hpjIS6jZZL_D4mQvc0A38XrZl6PPzAZadIY36ZmUiywOAELxkC1xQfPHenGxYJzp2cw0pIfHXKGafOYm8UFaDeRWtRxJ68kZsek8PU6XxbbQtqsOp0C3DudZEZ8v4rK2rLVejjAfD0d4"
        />
        <div className="font-title-md text-title-md text-primary font-semibold">Crave Concierge</div>
        <div className="font-label-md text-label-md text-on-surface-variant">AI Gourmet Assistant</div>
      </div>

      <nav className="flex flex-col gap-xs flex-grow">
        <div className="mb-sm mt-md font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider pl-sm">Search Parameters</div>
        <div className="flex flex-col gap-md">
          {/* Location Selection */}
          <div>
            <label className="block font-label-sm text-label-sm text-on-surface-variant mb-xs">Location</label>
            <div className="relative">
              <span className="material-symbols-outlined absolute left-[12px] top-1/2 -translate-y-1/2 text-on-surface-variant text-[18px]">location_on</span>
              <select
                value={params.location}
                onChange={(e) => handleSelectChange('location', e.target.value)}
                className="w-full bg-surface-container border border-white/10 rounded-lg pl-[40px] pr-sm py-sm text-on-surface font-body-md glass-input appearance-none focus:outline-none transition-colors"
              >
                {locations.length === 0 ? (
                  <option>Loading...</option>
                ) : (
                  locations.map(loc => (
                    <option key={loc} value={loc}>{loc}</option>
                  ))
                )}
              </select>
            </div>
          </div>

          {/* Cuisine Selection */}
          <div>
            <label className="block font-label-sm text-label-sm text-on-surface-variant mb-xs">Cuisine</label>
            <div className="relative">
              <span className="material-symbols-outlined absolute left-[12px] top-1/2 -translate-y-1/2 text-on-surface-variant text-[18px]">restaurant</span>
              <select
                value={params.cuisine}
                onChange={(e) => handleSelectChange('cuisine', e.target.value)}
                className="w-full bg-surface-container border border-white/10 rounded-lg pl-[40px] pr-sm py-sm text-on-surface font-body-md glass-input appearance-none focus:outline-none transition-colors"
              >
                {cuisines.length === 0 ? (
                  <option>Loading...</option>
                ) : (
                  cuisines.map(cuis => (
                    <option key={cuis} value={cuis}>
                      {String(cuis).split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
                    </option>
                  ))
                )}
              </select>
            </div>
          </div>

          {/* Budget Tier Buttons */}
          <div>
            <label className="block font-label-sm text-label-sm text-on-surface-variant mb-xs">Budget Tier</label>
            <div className="flex bg-surface-container rounded-lg p-xs border border-white/10">
              {['low', 'medium', 'high'].map((tier) => (
                <button
                  key={tier}
                  type="button"
                  onClick={() => handleBudgetSelect(tier)}
                  className={`flex-1 py-xs rounded font-label-md text-label-md transition-colors ${
                    params.budget === tier
                      ? 'bg-surface-variant text-on-surface shadow-sm font-semibold'
                      : 'text-on-surface-variant hover:text-on-surface'
                  }`}
                >
                  {tier.charAt(0).toUpperCase() + tier.slice(1)}
                </button>
              ))}
            </div>
          </div>

          {/* Rating Range Slider */}
          <div>
            <div className="flex justify-between items-center mb-xs">
              <label className="font-label-sm text-label-sm text-on-surface-variant">Min Rating</label>
              <span className="font-label-md text-label-md text-primary font-semibold">{params.rating.toFixed(1)}</span>
            </div>
            <input
              type="range"
              min="0"
              max="5"
              step="0.1"
              value={params.rating}
              onChange={handleRatingChange}
              className="w-full"
            />
          </div>

          {/* Mood context Textarea */}
          <div>
            <label className="block font-label-sm text-label-sm text-on-surface-variant mb-xs">Mood / Context</label>
            <textarea
              value={params.mood}
              onChange={handleMoodChange}
              className="w-full bg-surface-container border border-white/10 rounded-lg p-sm text-on-surface font-body-md glass-input focus:outline-none transition-colors resize-none h-24 placeholder-on-surface-variant/30"
              placeholder="e.g. a cozy, candle-lit spot for a romantic anniversary date"
            />
          </div>
        </div>
      </nav>

      {/* Main Action Trigger Buttons */}
      {loading ? (
        <button
          type="button"
          disabled
          className="mt-auto w-full bg-inverse-primary text-white rounded-lg py-sm font-label-md text-label-md glow-red hover:brightness-110 transition-all flex items-center justify-center gap-sm cursor-not-allowed opacity-80"
        >
          <span className="material-symbols-outlined spinner text-[18px]">progress_activity</span>
          Generating Suggestions...
        </button>
      ) : (
        <button
          type="button"
          onClick={onSubmit}
          className="mt-auto w-full bg-primary-container text-on-primary-container font-label-md text-label-md py-sm rounded-lg flex items-center justify-center gap-xs glow-hover transition-all duration-300 active:scale-95"
        >
          <span className="material-symbols-outlined text-[18px]">auto_awesome</span>
          Generate Suggestions
        </button>
      )}

      {/* Auxiliary Footer links */}
      <div className="mt-md pt-sm border-t border-white/5 flex flex-col gap-xs">
        <a className="flex items-center gap-sm px-sm py-sm text-on-surface-variant hover:bg-surface-variant/20 rounded-lg font-label-md text-label-md transition-colors" href="#">
          <span className="material-symbols-outlined">help</span> Help
        </a>
        <a className="flex items-center gap-sm px-sm py-sm text-on-surface-variant hover:bg-surface-variant/20 rounded-lg font-label-md text-label-md transition-colors" href="#">
          <span className="material-symbols-outlined">logout</span> Logout
        </a>
      </div>
    </aside>
  );
}
