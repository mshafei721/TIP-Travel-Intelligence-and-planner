# TIP Landing Page Visual Style Guide

Purpose: Define a conversion-focused, professional, modern, authoritative visual system for TIP landing pages. This guide is ready for designers or no-code implementation.

---

## 1. Color Palette
Use a restrained, high-contrast palette with one primary CTA color and one supporting accent.

### Brand Core
- Primary: Midnight Navy `#0C1B2A` (headlines, primary text, nav)
- Secondary: Slate Blue `#2C4A64` (subheads, secondary text, icons)
- Accent: Signal Teal `#00B3A4` (primary CTAs, highlights, key data points)

### Supporting Neutrals
- Ink `#101828` (body text)
- Steel `#475467` (secondary text)
- Fog `#E6ECF2` (borders, dividers)
- Mist `#F6F8FB` (section backgrounds)
- White `#FFFFFF` (base background)

### Status/Utility (use sparingly)
- Success: `#1FAD66`
- Warning: `#F59E0B`
- Risk: `#E5484D`

### Color Usage Rules
- Primary CTA uses Signal Teal on white or Mist backgrounds.
- Avoid more than 1 accent color on a single screen.
- Use Mist for alternating sections to create rhythm.
- Maintain 4.5:1 contrast ratio for body text.

---

## 2. Typography
Choose one clean, high-legibility sans serif with a strong professional tone.

### Recommended Typeface Options
- Primary: "Manrope" (modern, technical, readable)
- Alternate: "IBM Plex Sans" (authoritative, enterprise)
- Fallback: `system-ui, -apple-system, Segoe UI, Arial, sans-serif`

### Type Scale (Desktop)
- H1: 48/56, weight 700, letter-spacing -0.5px
- H2: 36/44, weight 700, letter-spacing -0.3px
- H3: 28/36, weight 600, letter-spacing -0.2px
- Subhead: 20/30, weight 500
- Body: 16/26, weight 400
- Small: 14/22, weight 400

### Type Scale (Mobile)
- H1: 34/40, weight 700
- H2: 28/34, weight 700
- H3: 22/30, weight 600
- Subhead: 18/28, weight 500
- Body: 16/24, weight 400
- Small: 14/20, weight 400

### Typography Rules
- Limit to 2 font weights per section.
- Headings use Midnight Navy; body uses Ink.
- Keep line length 55 to 75 characters for body text.

---

## 3. Buttons and CTAs
CTAs must be instantly visible and consistent across the page.

### Primary Button
- Background: Signal Teal `#00B3A4`
- Text: White `#FFFFFF`
- Hover: Darker Teal `#009686`
- Active: `#007C70`
- Focus ring: 2px `#7FE5DC` with 2px offset
- Padding: 14px 22px (desktop), 12px 18px (mobile)
- Radius: 10px
- Font: 16px, weight 600

### Secondary Button
- Background: Transparent
- Border: 1px Solid `#00B3A4`
- Text: `#00B3A4`
- Hover: Background `#E6FBF9`
- Active: Background `#CCF4EF`
- Radius and padding match Primary

### Text Link CTA
- Color: `#00B3A4`
- Underline on hover only
- Arrow icon optional, 12 to 16px

### Button Guidance
- One primary CTA per section.
- Above-the-fold CTA should be visible without scrolling.
- Ensure tap target minimum 44px height on mobile.

---

## 4. Whitespace and Spacing
Whitespace drives clarity and conversion. Use a consistent spacing scale.

### Spacing Scale (px)
4, 8, 12, 16, 24, 32, 48, 64, 96

### Section Spacing
- Desktop: 96px top/bottom for major sections
- Mobile: 64px top/bottom for major sections

### Content Spacing
- Headline to subhead: 12 to 16px
- Subhead to body: 16 to 24px
- Paragraph gaps: 16px
- Card padding: 24 to 32px

---

## 5. Layout and Grid System
Keep a clean grid that supports visual hierarchy and fast scanning.

### Grid
- Desktop: 12 columns, 72px margins, 24px gutters
- Tablet: 8 columns, 48px margins, 20px gutters
- Mobile: 4 columns, 20px margins, 16px gutters

### Max Widths
- Main container: 1200px
- Text blocks: 640 to 720px for readability

### Layout Rules
- Use asymmetry for hero: text left, product visual right.
- Alternate light section backgrounds for rhythm.
- Align text blocks to the same left edge across sections.

---

## 6. Image and Icon Guidance
Visuals should reinforce credibility and accuracy.

### Images
- Use crisp UI mockups with real data callouts (e.g., "E-Visa Required (98% Confidence)").
- Prefer light backgrounds with subtle shadows.
- Avoid stock photos of generic travel scenes.
- Use 1 focal image per section max.

### Icons
- Style: line icons, 1.5 to 2px stroke, rounded ends.
- Color: Secondary Slate Blue or Signal Teal for emphasis.
- Size: 24 to 32px standard; 48px for hero highlights.

### Visual Treatment
- Apply soft shadow: 0 8px 24px rgba(12, 27, 42, 0.12)
- Use 8 to 12px radius for cards and images.

---

## 7. Mobile Optimization Principles
Mobile-first design ensures conversions on smaller screens.

- Single-column layouts below 768px.
- Stack CTA under headline with no competing elements.
- Keep hero image below text on mobile.
- Use accordion FAQ to reduce scroll length.
- Maintain 44px minimum tap targets for all buttons and links.
- Avoid dense multi-column tables; convert to stacked cards.

---

## 8. Visual Hierarchy and Conversion Flow
The page should guide the user from pain to action in seconds.

### Hierarchy Rules
- H1 should state the main outcome and time-to-value.
- Use one dominant CTA color across the page.
- Use bold weights and larger size for key metrics (e.g., 60 seconds, 98% confidence).
- Place trust cues directly below CTAs or in the hero.

### Conversion Reinforcement
- Repeat primary CTA every 2 to 3 sections.
- Keep copy blocks short and scannable.
- Use checkmarks in comparison tables for TIP column.

---

## 9. Component Defaults
Keep components consistent for faster design and development.

### Cards
- Background: White
- Border: 1px solid `#E6ECF2`
- Radius: 12px
- Padding: 24px
- Shadow: 0 6px 18px rgba(12, 27, 42, 0.08)

### Badges
- Background: `#E6FBF9`
- Text: `#007C70`
- Padding: 4px 8px
- Radius: 999px
- Font: 12px, weight 600

### Dividers
- Color: `#E6ECF2`
- Thickness: 1px

---

## 10. Accessibility Checklist
- 4.5:1 contrast ratio for body text.
- Focus states on all interactive elements.
- Avoid color-only indicators; pair with icon or label.
- Use descriptive link labels, not "Click here".

---

## Implementation Notes (No-Code Friendly)
- Define color tokens and typography as global styles.
- Set a base spacing unit of 8px and build all spacing from it.
- Create reusable CTA, card, and badge components.
- Ensure all sections reuse the same grid and container width.
