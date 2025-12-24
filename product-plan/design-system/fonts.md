# Typography Configuration

## Google Fonts Import

Add to your HTML `<head>`:

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,100..1000;1,9..40,100..1000&family=IBM+Plex+Mono:ital,wght@0,400;0,500;0,600;1,400&display=swap" rel="stylesheet">
```

Or in CSS:

```css
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,100..1000;1,9..40,100..1000&family=IBM+Plex+Mono:ital,wght@0,400;0,500;0,600;1,400&display=swap');
```

## Font Usage

### DM Sans — Headings & Body Text

DM Sans is used for all text in the application, providing a clean, modern, and highly readable typeface.

```css
font-family: 'DM Sans', sans-serif;
```

Usage in Tailwind (add to tailwind.config.js or CSS):
```css
.font-heading {
  font-family: 'DM Sans', sans-serif;
}

.font-body {
  font-family: 'DM Sans', sans-serif;
}
```

### IBM Plex Mono — Code & Technical Content

IBM Plex Mono is used for code snippets, technical data, error codes, and monospace content.

```css
font-family: 'IBM Plex Mono', monospace;
```

Usage in Tailwind:
```css
.font-mono {
  font-family: 'IBM Plex Mono', monospace;
}
```

## Typography Scale

| Element | Size | Weight | Class |
|---------|------|--------|-------|
| H1 | 2.25rem (36px) | Bold (700) | `text-4xl font-bold` |
| H2 | 1.875rem (30px) | Semibold (600) | `text-3xl font-semibold` |
| H3 | 1.5rem (24px) | Semibold (600) | `text-2xl font-semibold` |
| H4 | 1.25rem (20px) | Medium (500) | `text-xl font-medium` |
| Body | 1rem (16px) | Normal (400) | `text-base` |
| Small | 0.875rem (14px) | Normal (400) | `text-sm` |
| Caption | 0.75rem (12px) | Normal (400) | `text-xs` |

## Line Heights

- Headings: `leading-tight` (1.25)
- Body text: `leading-normal` (1.5)
- Condensed: `leading-snug` (1.375)
- Relaxed: `leading-relaxed` (1.625)

## Example Usage

```html
<!-- Page heading -->
<h1 class="text-4xl font-bold text-slate-900 dark:text-slate-50">
  Welcome to TIP
</h1>

<!-- Section heading -->
<h2 class="text-2xl font-semibold text-slate-900 dark:text-slate-50">
  Your Trips
</h2>

<!-- Body text -->
<p class="text-base text-slate-600 dark:text-slate-400">
  Plan your next adventure with AI-powered travel intelligence.
</p>

<!-- Code/technical content -->
<code class="font-mono text-sm bg-slate-100 dark:bg-slate-800 px-1 rounded">
  ERR_404_NOT_FOUND
</code>
```
