import React, { useState } from 'react';

// Dynamic image mappings for standard cuisines
const CUISINE_IMAGES = {
  italian: 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?q=80&w=600&auto=format&fit=crop',
  japanese: 'https://images.unsplash.com/photo-1579871494447-9811cf80d66c?q=80&w=600&auto=format&fit=crop',
  mediterranean: 'https://images.unsplash.com/photo-1540189549336-e6e99c3679fe?q=80&w=600&auto=format&fit=crop',
  indian: 'https://images.unsplash.com/photo-1585938338392-50a59970d8ee?q=80&w=600&auto=format&fit=crop',
  'north indian': 'https://images.unsplash.com/photo-1626777552726-4a6b54c97e46?q=80&w=600&auto=format&fit=crop',
  'south indian': 'https://images.unsplash.com/photo-1589301760014-d929f3979dbc?q=80&w=600&auto=format&fit=crop',
  cafe: 'https://images.unsplash.com/photo-1509042239860-f550ce710b93?q=80&w=600&auto=format&fit=crop',
  bakery: 'https://images.unsplash.com/photo-1509440159596-0249088772ff?q=80&w=600&auto=format&fit=crop',
  mexican: 'https://images.unsplash.com/photo-1565299585323-38d6b0865b47?q=80&w=600&auto=format&fit=crop',
  chinese: 'https://images.unsplash.com/photo-1563245372-f21724e3856d?q=80&w=600&auto=format&fit=crop',
  continental: 'https://images.unsplash.com/photo-1467003909585-2f8a72700288?q=80&w=600&auto=format&fit=crop',
  default: 'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?q=80&w=600&auto=format&fit=crop'
};

export default function RestaurantCard({ recommendation }) {
  const { rank, restaurant, explanation } = recommendation;
  const { name, location, cuisines = [], rating, estimated_cost } = restaurant;

  const [isFavorite, setIsFavorite] = useState(false);

  // Pick standard high-fidelity mock image if matching name, otherwise select dynamic theme image
  const getRestaurantImage = () => {
    const lowerName = name.toLowerCase();
    if (lowerName.includes('trattoria bella notte')) {
      return 'https://lh3.googleusercontent.com/aida-public/AB6AXuCkT1bGwfre9fHwJFdrbQYWLe7IydzGXuWrarOkvWuRZ-PEHY1mD8dTEigxwuAHp_0JU1hbdH1sNjVn6y_eMOeBx9LtXF39WMIesXslTJcz7SQe40kvlOs8MzHHYuhLHdwDxL1tAEMK5QCIU5xxgpikTTEVbyqI4WkjYGj2tvfcPfrCIIkQibMxakCPfY0_GINZs0IN5Lv_DrWdNIjf8YOrU6_U4y_BuagAXKyvmizCWlurQBUv7tKmL6uUGZy5l2QFYUotKsAmxiqN';
    }
    if (lowerName.includes('vino') || lowerName.includes('formaggio')) {
      return 'https://lh3.googleusercontent.com/aida-public/AB6AXuBjHLDVqRshuRgHK9-KQK8bMZxfeurVfV-bO0qvlPfHyBIFEH7m-kAhmO1lKxiCEw2uKPyMJ37RAcyLQjcaPPY2ETz9noxiWOx-wC1TzI9WeGhycXlRSDb6qSx06S2edO7VLVsLeX_Gxrha7KU6VxW6lKrpfBSiqyRaoqLfrej2DeWW291hqyk2TM7O6nZxvUXUXCFugvGh-ozUE-XEavNfAQPlsFXDyim2qi7YNJPpEih4cO9grBW5-rZRA2yJS0mF2EMmxsxeDxb5';
    }
    if (lowerName.includes('olive canvas')) {
      return 'https://lh3.googleusercontent.com/aida-public/AB6AXuBdoE4uK56avdyt4j63k4NF7djklWEyZkObKJDHJvW6WaHmHd7IsssNCZ92AOq9TtOq8s8MQJ4VPdWzB-OSnoYffV2vd-qLQudgGKQ3oyAOYWM9j-_i7MGdihHnQ89_6XhmSet37wjhn2W36HROEHLONkVz9REF64ubLSgGvA0kW8PJv-kjnSTLlmZRW0uJf648f-D2SY2NC6o5dMf4q4QVD73LEl90jHwCud3Fg5KBzvivtBP3uaruswB9B6f38H1jcjRUW_a0zInz';
    }

    // Dynamic selection by cuisine match
    for (const c of cuisines) {
      const lowerC = c.toLowerCase();
      if (CUISINE_IMAGES[lowerC]) {
        return CUISINE_IMAGES[lowerC];
      }
    }
    return CUISINE_IMAGES.default;
  };

  return (
    <article className="glass-panel-2 card-hover rounded-xl overflow-hidden group flex flex-col hover:border-primary/30 transition-all duration-300">
      {/* Restaurant Image Block */}
      <div className="relative h-48 overflow-hidden">
        <img
          alt={name}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700"
          src={getRestaurantImage()}
        />
        <div className="absolute inset-0 bg-gradient-to-t from-[#111317] via-transparent to-transparent"></div>
        
        {/* Rank Badge overlay */}
        <div className="absolute top-sm left-sm bg-surface/80 backdrop-blur-md px-2 py-1 rounded font-label-sm text-label-sm text-primary border border-white/10 flex items-center gap-1 shadow-md">
          <span className="material-symbols-outlined text-[14px]">military_tech</span> Rank #{rank}
        </div>

        {/* Favorite Button overlay */}
        <button
          type="button"
          onClick={() => setIsFavorite(!isFavorite)}
          className="absolute top-sm right-sm bg-surface/80 backdrop-blur-md w-8 h-8 rounded-full flex items-center justify-center border border-white/10 cursor-pointer hover:bg-surface transition-colors focus:outline-none"
        >
          <span className={`material-symbols-outlined text-[18px] transition-colors ${
            isFavorite ? 'text-primary fill-current' : 'text-on-surface-variant hover:text-primary'
          }`} style={isFavorite ? { fontVariationSettings: "'FILL' 1" } : {}}>
            favorite
          </span>
        </button>
      </div>

      {/* Details Container */}
      <div className="p-md flex flex-col flex-grow">
        <div className="flex justify-between items-start mb-2">
          <h2 className="font-title-md text-title-md text-on-surface font-semibold line-clamp-1" title={name}>
            {name}
          </h2>
        </div>

        {/* Location & Cuisines Summary */}
        <div className="flex items-center gap-2 mb-sm text-on-surface-variant font-label-sm text-label-sm">
          <span className="flex items-center gap-1">
            <span className="material-symbols-outlined text-[14px] text-primary">location_on</span> {location}
          </span>
          <span>•</span>
          <span className="line-clamp-1">
            {cuisines.map(c => c.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')).join(', ')}
          </span>
        </div>

        {/* Rating and Estimated cost badges */}
        <div className="flex gap-2 mb-md">
          <span className="bg-secondary-container text-on-secondary-container px-2 py-1 rounded font-label-sm text-label-sm flex items-center gap-1 shadow-sm font-semibold">
            <span className="material-symbols-outlined text-[12px] fill-current" style={{ fontVariationSettings: "'FILL' 1" }}>star</span>
            {rating.toFixed(1)}
          </span>
          <span className="bg-tertiary-container/20 text-tertiary px-2 py-1 rounded font-label-sm text-label-sm border border-tertiary/30 font-semibold shadow-sm">
            ₹{estimated_cost.toLocaleString()} for two
          </span>
        </div>

        {/* AI Rationale Block with left Crimson Red border */}
        <div className="mt-auto pt-sm border-t border-white/5">
          <div className="pl-2 border-l-2 border-primary-container">
            <p className="font-label-md text-label-md text-on-surface-variant italic line-clamp-2" title={explanation}>
              "{explanation}"
            </p>
          </div>
        </div>
      </div>
    </article>
  );
}
