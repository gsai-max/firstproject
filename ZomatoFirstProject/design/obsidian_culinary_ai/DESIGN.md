---
name: Obsidian Culinary AI
colors:
  surface: '#111317'
  surface-dim: '#111317'
  surface-bright: '#37393d'
  surface-container-lowest: '#0c0e11'
  surface-container-low: '#1a1c1f'
  surface-container: '#1e2023'
  surface-container-high: '#282a2d'
  surface-container-highest: '#333538'
  on-surface: '#e2e2e6'
  on-surface-variant: '#e4beba'
  inverse-surface: '#e2e2e6'
  inverse-on-surface: '#2f3034'
  outline: '#ab8986'
  outline-variant: '#5b403e'
  surface-tint: '#ffb3ad'
  primary: '#ffb3ad'
  on-primary: '#68000a'
  primary-container: '#ff5451'
  on-primary-container: '#5c0008'
  inverse-primary: '#b91a24'
  secondary: '#4ae176'
  on-secondary: '#003915'
  secondary-container: '#00b954'
  on-secondary-container: '#004119'
  tertiary: '#adc6ff'
  on-tertiary: '#002e6a'
  tertiary-container: '#4d8eff'
  on-tertiary-container: '#00285d'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#ffdad7'
  primary-fixed-dim: '#ffb3ad'
  on-primary-fixed: '#410004'
  on-primary-fixed-variant: '#930013'
  secondary-fixed: '#6bff8f'
  secondary-fixed-dim: '#4ae176'
  on-secondary-fixed: '#002109'
  on-secondary-fixed-variant: '#005321'
  tertiary-fixed: '#d8e2ff'
  tertiary-fixed-dim: '#adc6ff'
  on-tertiary-fixed: '#001a42'
  on-tertiary-fixed-variant: '#004395'
  background: '#111317'
  on-background: '#e2e2e6'
  surface-variant: '#333538'
typography:
  display-lg:
    fontFamily: Outfit
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Outfit
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Outfit
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  title-md:
    fontFamily: Outfit
    fontSize: 20px
    fontWeight: '500'
    lineHeight: 28px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
    letterSpacing: 0.01em
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 8px
  xs: 4px
  sm: 12px
  md: 24px
  lg: 48px
  xl: 80px
  container-max: 1440px
  gutter: 24px
  margin-mobile: 16px
---

## Brand & Style
The design system is centered on a premium, high-fidelity dark mode aesthetic tailored for discerning food enthusiasts. It targets a tech-savvy audience that values speed, precision, and a "luxury-concierge" experience.

The visual style is **Glassmorphism**, emphasizing depth through transparency and background blurs rather than traditional solid shadows. The interface should feel like a series of suspended, glowing panes over a deep obsidian void. The emotional response is one of sophistication, culinary passion, and futuristic intelligence.

## Colors
The palette is rooted in a **Rich Obsidian** base to provide maximum contrast for the vibrant brand accents. 

- **Primary (Vibrant Crimson Red):** Used exclusively for high-priority actions, brand moments, and active focus states.
- **Success/Ratings (Emerald Gradient):** Communicates high-quality scores and positive AI match percentages.
- **Info/Budget (Royal Blue Gradient):** Categorizes metadata, price tiers, and secondary utility information.
- **Surface Layering:** All cards and panels utilize a semi-transparent slate base with a 12px backdrop blur and a subtle 1px white-tinted border to define edges against the dark background.

## Typography
This design system uses a dual-font strategy to balance character with utility. **Outfit** is utilized for headlines to provide a modern, geometric flair that complements the futuristic theme. **Inter** is used for all body text and labels to ensure maximum legibility at small sizes and high-density data views.

Headlines should always use the pure white `#ffffff` token. Primary body text uses the slightly softer `#e2e8f0` to reduce eye strain, while metadata and descriptions use the muted `#94a3b8` token.

## Layout & Spacing
The layout follows a **12-column fluid grid** for desktop, transitioning to a **4-column grid** for mobile. 

A strict 8px spatial system is used to define margins and padding. High-level sections should be separated by `lg` (48px) spacing to maintain the premium, airy feel of the glass panels. Card interiors should use `md` (24px) padding to ensure the content doesn't feel cramped against the glass borders. 

On mobile, gutters reduce to 16px to maximize screen real estate for restaurant imagery.

## Elevation & Depth
Depth is achieved through the stacking of **Tonal Glass Layers**. 
- **Level 0 (Background):** Solid #0d0f12.
- **Level 1 (Sub-Navigation/Sidebar):** Glass base with 4px backdrop blur.
- **Level 2 (Main Cards/Content):** Glass base with 12px backdrop blur.
- **Level 3 (Modals/Popovers):** Glass base with 24px backdrop blur and a slightly brighter 2px border.

**Interaction States:**
When a card is hovered, it must transition with a `translateY(-4px)` float effect. Buttons and primary interactive elements should emit a soft, crimson glow (`box-shadow: 0 0 20px rgba(239, 68, 68, 0.3)`) when hovered or focused.

## Shapes
The design system uses a **Rounded** shape language to soften the high-tech aesthetic and make it feel more approachable. 

- **Small Components:** Checkboxes and small tags use 4px (Soft) radii.
- **Standard Components:** Buttons, input fields, and small cards use 8px (Rounded) radii.
- **Container Components:** Large restaurant cards and modal containers use 16px (Rounded-LG) radii.
- **Interactive Pill:** Segmented controls and search bars should use full pill-shaped (100px+) radii.

## Components

### Restaurant Cards
The core component of the system. It features a top-aligned image with a gradient overlay, followed by the glassmorphism body.
- **AI Rationale Block:** A distinct text area within the card featuring a **4px solid Crimson Red left-border**. This highlights why the AI recommended the venue.
- **Rating Badges:** Use the Emerald Green gradient for the background with white text.

### Buttons & Inputs
- **Primary Button:** Solid Crimson Red background with white text. On hover, apply the crimson glow shadow.
- **Sidebar Inputs:** Glass-styled text fields. When focused, the 1px border transitions from `rgba(255, 255, 255, 0.08)` to solid `#ef4444`.
- **Range Sliders:** Use a Crimson Red track for the active state and a white circular handle with a subtle drop shadow.

### Segmented Controls
Used for switching between "Best Match," "Nearest," and "Top Rated." These should look like a single glass pill where the active state is a secondary, slightly more opaque glass layer or a solid crimson fill with white text.

### Badge Systems
- **Price Badges ($$$):** Use the Royal Blue gradient.
- **Tag Badges (Cuisine):** Use a low-opacity white fill `rgba(255,255,255,0.05)` with the `label-sm` typography.