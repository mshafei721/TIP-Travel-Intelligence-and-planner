# Tailwind Color Configuration

## Color Choices

- **Primary:** `blue` — Used for buttons, links, key accents, active navigation items
- **Secondary:** `amber` — Used for CTAs, highlights, hover states, Create Trip button
- **Neutral:** `slate` — Used for backgrounds, text, borders, inactive elements

## Usage Examples

### Primary Button
```html
<button class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg">
  Create Trip
</button>
```

### Secondary Button
```html
<button class="bg-amber-500 hover:bg-amber-600 text-white px-4 py-2 rounded-lg">
  Quick Action
</button>
```

### Outline Button
```html
<button class="border border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 px-4 py-2 rounded-lg">
  Secondary
</button>
```

### Text Colors
```html
<!-- Primary text -->
<p class="text-slate-900 dark:text-slate-50">Heading text</p>

<!-- Secondary text -->
<p class="text-slate-600 dark:text-slate-400">Supporting text</p>

<!-- Muted text -->
<p class="text-slate-400 dark:text-slate-500">Placeholder text</p>
```

### Backgrounds
```html
<!-- Page background -->
<div class="bg-slate-50 dark:bg-slate-950">

<!-- Card background -->
<div class="bg-white dark:bg-slate-900">

<!-- Elevated surface -->
<div class="bg-slate-100 dark:bg-slate-800">
```

### Borders
```html
<!-- Default border -->
<div class="border border-slate-200 dark:border-slate-800">

<!-- Subtle border -->
<div class="border border-slate-100 dark:border-slate-900">
```

### Status Colors (using Tailwind defaults)
```html
<!-- Success -->
<span class="text-green-600 dark:text-green-400">Success message</span>

<!-- Warning -->
<span class="text-amber-600 dark:text-amber-400">Warning message</span>

<!-- Error -->
<span class="text-red-600 dark:text-red-400">Error message</span>

<!-- Info -->
<span class="text-blue-600 dark:text-blue-400">Info message</span>
```

### Navigation
```html
<!-- Active nav item -->
<a class="text-blue-600 dark:text-blue-400 font-medium">Active</a>

<!-- Inactive nav item -->
<a class="text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200">Inactive</a>
```

### Badges
```html
<!-- Primary badge -->
<span class="bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 px-2 py-1 rounded">
  Badge
</span>

<!-- Secondary badge -->
<span class="bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200 px-2 py-1 rounded">
  Badge
</span>

<!-- Neutral badge -->
<span class="bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-200 px-2 py-1 rounded">
  Badge
</span>
```

## Dark Mode Support

All components use Tailwind's `dark:` variant for dark mode support. The design automatically adapts based on user's system preference or manual toggle.

Key dark mode patterns:
- Light backgrounds become dark (`bg-white` → `dark:bg-slate-900`)
- Dark text becomes light (`text-slate-900` → `dark:text-slate-50`)
- Borders adjust for visibility (`border-slate-200` → `dark:border-slate-800`)
