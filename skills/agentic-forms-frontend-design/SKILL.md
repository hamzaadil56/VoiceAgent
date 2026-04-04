---
name: agentic-forms-frontend-design
description: Frontend design system and UI/UX skill for the Agentic Forms Platform — a multi-tenant platform where admins design conversational forms and consumers answer through public links. Use when building any UI component, page, screen, or layout for this application. Covers the admin builder, consumer chat/voice runtime, analytics dashboard, submissions table, auth screens, and public-facing form runtime. Enforces the platform's distinctive visual identity: modern light UI with a nature-inspired botanical palette (sage, teal, coral, lavender), Poppins + Montserrat typography, and fluid conversational UI.
---

# Agentic Forms Platform — Frontend Design Skill

You are building the frontend for a **conversational forms platform** — think Typeform meets an AI-native chatbot builder. Two distinct audiences use this product: **admins** who craft intelligent form journeys, and **consumers** who experience them. Every pixel must serve this duality.

---

## 🎨 Core Design Philosophy

**Aesthetic Direction: "Living Interface"**
Inspired by natural beauty — morning mist over water, botanical gardens, soft sunlight through leaves. The palette is alive, soothing, and modern. Think Notion meets Linear meets a wellness app that got a serious design upgrade. Light, airy, and breathable — but with precision and structure underneath.

**Mood Board in Words:**

- Soft sage greens + deep teal = grounded intelligence
- Warm coral + blush = human warmth, action
- Misty lavender = creativity, depth, innovation
- Crisp white + warm stone neutrals = clarity and calm

**What makes this UNFORGETTABLE:**

- Admin panels feel like a beautiful creative workspace, not a dashboard
- The consumer chat feels like messaging a thoughtful friend
- Color gradients shift like light — alive, never flat
- Every interaction has a satisfying, organic micro-response

---

## 🖋 Typography System

### Font Stack

```css
@import url("https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Montserrat:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap");

:root {
	--font-display:
		"Montserrat", sans-serif; /* Hero titles, brand moments, stat numbers */
	--font-body: "Poppins", sans-serif; /* All UI text, labels, body, buttons */
	--font-mono: "JetBrains Mono", monospace; /* IDs, slugs, tokens, code */
}
```

**Why this pairing:**

- **Montserrat** is bold, geometric, and confident — perfect for headings and brand moments. Its wide letterforms feel modern and trustworthy.
- **Poppins** is soft, rounded, and extraordinarily readable at small sizes — perfect for UI labels, chat messages, form fields. Its circular geometry echoes the organic, approachable brand.
- Together they feel cohesive: both geometric, both modern, but each has a distinct register (display vs. workhorse).

### Type Scale

```css
:root {
	--text-xs: 0.6875rem; /* 11px — metadata, timestamps, mono labels */
	--text-sm: 0.8125rem; /* 13px — secondary labels, captions */
	--text-base: 0.9375rem; /* 15px — body text, form fields */
	--text-md: 1.0625rem; /* 17px — subheadings */
	--text-lg: 1.25rem; /* 20px — section titles */
	--text-xl: 1.625rem; /* 26px — page headers */
	--text-2xl: 2.25rem; /* 36px — hero display */
	--text-3xl: 3.25rem; /* 52px — marketing/landing */

	--weight-light: 300;
	--weight-normal: 400;
	--weight-medium: 500;
	--weight-semibold: 600;
	--weight-bold: 700;
	--weight-extrabold: 800;

	--leading-tight: 1.2;
	--leading-snug: 1.4;
	--leading-normal: 1.6;
	--leading-relaxed: 1.75;

	--tracking-tighter: -0.04em;
	--tracking-tight: -0.02em;
	--tracking-normal: -0.005em;
	--tracking-wide: 0.04em;
	--tracking-widest: 0.1em;
}
```

### Typography Usage Rules

- **Page titles, stat numbers, brand name**: `Montserrat`, `--weight-bold` or `--weight-extrabold`, tight tracking
- **Section headings, card titles**: `Montserrat`, `--weight-semibold`
- **All UI text (nav, labels, buttons, body)**: `Poppins`, appropriate weight
- **Consumer chat — bot messages**: `Poppins`, `--weight-medium` — warm, approachable
- **Consumer chat — user messages**: `Poppins`, `--weight-normal`
- **Form slugs, session IDs, tokens**: `JetBrains Mono`, `--text-sm`
- **NEVER** use Inter, Roboto, DM Sans, or system-ui as primary typeface

---

## 🎨 Color System — "Botanical Palette"

Inspired by nature: deep forest teal, sage green, warm coral, soft lavender, and clean stone neutrals. Every color has a purpose; no color is decorative noise.

### Full Design Token Set

```css
:root {
	/* ═══════════════════════════════
     BRAND CORE — Teal + Sage
  ═══════════════════════════════ */

	/* Primary: Deep Teal — intelligence, depth, trust */
	--teal-50: #f0fdfa;
	--teal-100: #ccfbf1;
	--teal-200: #99f6e4;
	--teal-300: #5eead4;
	--teal-400: #2dd4bf;
	--teal-500: #14b8a6; /* ← Primary brand color */
	--teal-600: #0d9488; /* hover states */
	--teal-700: #0f766e; /* pressed / active */
	--teal-800: #115e59;
	--teal-900: #134e4a;

	/* Secondary: Sage Green — calm, natural, grounded */
	--sage-50: #f6f9f4;
	--sage-100: #e8f0e3;
	--sage-200: #ccdfc4;
	--sage-300: #a7c79b;
	--sage-400: #7ead6f;
	--sage-500: #5d9150; /* ← Secondary brand color */
	--sage-600: #4a7840;
	--sage-700: #3b5f33;
	--sage-800: #2f4c28;
	--sage-900: #253c1f;

	/* Accent 1: Coral — action, warmth, human touch */
	--coral-50: #fff4f1;
	--coral-100: #ffe4dd;
	--coral-200: #ffbfb0;
	--coral-300: #ff9580;
	--coral-400: #ff6b52; /* ← CTA / action accent */
	--coral-500: #f4523a;
	--coral-600: #d93d27;
	--coral-700: #b32d1a;
	--coral-glow: rgba(255, 107, 82, 0.18);
	--coral-ring: rgba(255, 107, 82, 0.35);

	/* Accent 2: Lavender — creativity, AI, depth */
	--lavender-50: #f5f3ff;
	--lavender-100: #ede9fe;
	--lavender-200: #ddd6fe;
	--lavender-300: #c4b5fd;
	--lavender-400: #a78bfa; /* ← AI/bot identity color */
	--lavender-500: #8b5cf6;
	--lavender-600: #7c3aed;
	--lavender-glow: rgba(167, 139, 250, 0.15);
	--lavender-ring: rgba(167, 139, 250, 0.35);

	/* Accent 3: Blush — soft warmth, completions, delight */
	--blush-100: #fce7f3;
	--blush-200: #fbcfe8;
	--blush-400: #f472b6;
	--blush-500: #ec4899;

	/* Accent 4: Sky — clarity, information, links */
	--sky-100: #e0f2fe;
	--sky-400: #38bdf8;
	--sky-500: #0ea5e9;

	/* ═══════════════════════════════
     NEUTRAL — Warm Stone
  ═══════════════════════════════ */
	/* Warm stone neutrals — not cold grey, not clinical white */
	--stone-0: #ffffff;
	--stone-25: #fafaf9; /* page background */
	--stone-50: #f7f6f4; /* subtle surface */
	--stone-100: #f0edea; /* card backgrounds */
	--stone-150: #e8e4df; /* hover on surfaces */
	--stone-200: #ddd8d1; /* border default */
	--stone-300: #c8c1b8; /* border strong */
	--stone-400: #a89f95; /* placeholder text */
	--stone-500: #877d72; /* muted text */
	--stone-600: #6b6059; /* secondary text */
	--stone-700: #4e4540; /* body text */
	--stone-800: #342f2b; /* strong text */
	--stone-900: #1c1917; /* primary text */

	/* ═══════════════════════════════
     ADMIN THEME — Light, Airy
  ═══════════════════════════════ */
	--bg-page: var(--stone-25); /* main page bg */
	--bg-base: var(--stone-0); /* sidebar, panels */
	--bg-raised: var(--stone-0); /* cards */
	--bg-elevated: var(--stone-50); /* modal, dropdown */
	--bg-overlay: var(--stone-100); /* hover, active bg */

	--text-primary: var(--stone-900);
	--text-secondary: var(--stone-600);
	--text-muted: var(--stone-400);
	--text-faint: var(--stone-300);

	--border-subtle: rgba(0, 0, 0, 0.06);
	--border-default: rgba(0, 0, 0, 0.1);
	--border-strong: rgba(0, 0, 0, 0.18);
	--border-teal: rgba(20, 184, 166, 0.4);
	--border-coral: rgba(255, 107, 82, 0.4);

	/* ═══════════════════════════════
     SEMANTIC COLORS
  ═══════════════════════════════ */
	--color-success: #10b981;
	--color-warning: #f59e0b;
	--color-error: #ef4444;
	--color-info: var(--teal-500);

	--success-bg: rgba(16, 185, 129, 0.08);
	--success-border: rgba(16, 185, 129, 0.25);
	--warning-bg: rgba(245, 158, 11, 0.08);
	--error-bg: rgba(239, 68, 68, 0.08);
	--error-border: rgba(239, 68, 68, 0.25);
	--info-bg: rgba(20, 184, 166, 0.08);

	/* ═══════════════════════════════
     GRADIENT TOKENS
  ═══════════════════════════════ */
	--gradient-brand: linear-gradient(
		135deg,
		var(--teal-500) 0%,
		var(--lavender-500) 100%
	);
	--gradient-action: linear-gradient(
		135deg,
		var(--coral-400) 0%,
		var(--blush-500) 100%
	);
	--gradient-nature: linear-gradient(
		135deg,
		var(--sage-400) 0%,
		var(--teal-400) 100%
	);
	--gradient-dawn: linear-gradient(
		135deg,
		#fdd8b5 0%,
		#f9b5c8 50%,
		#c4b5fd 100%
	);
	--gradient-page-hero: linear-gradient(
		160deg,
		rgba(20, 184, 166, 0.06) 0%,
		rgba(167, 139, 250, 0.04) 40%,
		rgba(255, 107, 82, 0.04) 100%
	);

	/* Mesh gradient for hero backgrounds */
	--mesh-bg:
		radial-gradient(
			ellipse 80% 50% at 10% 0%,
			rgba(20, 184, 166, 0.12) 0%,
			transparent 60%
		),
		radial-gradient(
			ellipse 60% 40% at 90% 10%,
			rgba(167, 139, 250, 0.1) 0%,
			transparent 60%
		),
		radial-gradient(
			ellipse 50% 60% at 50% 100%,
			rgba(255, 107, 82, 0.06) 0%,
			transparent 60%
		),
		var(--stone-25);

	/* ═══════════════════════════════
     SHADOWS — Colored, not grey
  ═══════════════════════════════ */
	--shadow-xs: 0 1px 3px rgba(28, 25, 23, 0.06);
	--shadow-sm:
		0 2px 6px rgba(28, 25, 23, 0.08), 0 1px 2px rgba(28, 25, 23, 0.05);
	--shadow-md:
		0 4px 16px rgba(28, 25, 23, 0.1), 0 2px 4px rgba(28, 25, 23, 0.06);
	--shadow-lg:
		0 12px 32px rgba(28, 25, 23, 0.12), 0 4px 8px rgba(28, 25, 23, 0.06);
	--shadow-xl: 0 24px 56px rgba(28, 25, 23, 0.14);
	--shadow-teal: 0 4px 24px rgba(20, 184, 166, 0.25);
	--shadow-coral: 0 4px 24px rgba(255, 107, 82, 0.25);
	--shadow-lavender: 0 4px 24px rgba(167, 139, 250, 0.22);

	/* ═══════════════════════════════
     BORDER RADIUS
  ═══════════════════════════════ */
	--radius-sm: 4px;
	--radius-md: 8px;
	--radius-lg: 12px;
	--radius-xl: 16px;
	--radius-2xl: 20px;
	--radius-3xl: 28px;
	--radius-full: 9999px;

	/* ═══════════════════════════════
     SPACING (8pt grid)
  ═══════════════════════════════ */
	--space-1: 0.25rem;
	--space-2: 0.5rem;
	--space-3: 0.75rem;
	--space-4: 1rem;
	--space-5: 1.25rem;
	--space-6: 1.5rem;
	--space-8: 2rem;
	--space-10: 2.5rem;
	--space-12: 3rem;
	--space-16: 4rem;
	--space-20: 5rem;
}
```

### Color Combination Principles

**Primary UI Actions → Teal**
`--teal-500` / `--teal-600` for primary buttons, active states, progress bars, links. Conveys trust and capability.

**Destructive / High-Urgency Actions → Coral**
`--coral-400` for delete buttons, error states, required field indicators. Coral is warm, not aggressive — stays readable and non-alarming.

**AI / Bot Identity → Lavender**
`--lavender-400` for bot avatars, AI-related badges, processing states. Lavender = creativity, AI magic.

**Success / Complete → Sage + Teal**
Completion states blend sage green (natural achievement) fading into teal (intelligence verified).

**Accent Combinations That Work:**

- Teal CTA button on stone-50 card background ✅
- Lavender bot bubble on white chat surface ✅
- Coral "publish" button in builder header ✅
- Sage + teal gradient on analytics empty state ✅
- Dawn gradient (warm) on auth page hero ✅

**Combinations to Avoid:**

- Teal + coral as equally-weighted competing elements — pick one per context
- Lavender on dark backgrounds (loses soothing quality)
- Sage text on stone-100 — insufficient contrast

---

## 🧩 Component Library

### Button System

```css
/* === PRIMARY — Teal (main actions: Save, Continue, Submit) === */
.btn-primary {
	background: var(--teal-500);
	color: #ffffff;
	font-family: var(--font-body);
	font-weight: var(--weight-semibold);
	font-size: var(--text-sm);
	letter-spacing: 0.01em;
	padding: 10px var(--space-6);
	border-radius: var(--radius-lg);
	border: none;
	cursor: pointer;
	transition:
		background 0.15s ease,
		box-shadow 0.15s ease,
		transform 0.1s ease;
	display: inline-flex;
	align-items: center;
	gap: var(--space-2);
}
.btn-primary:hover {
	background: var(--teal-600);
	box-shadow: var(--shadow-teal);
}
.btn-primary:active {
	transform: translateY(1px);
	background: var(--teal-700);
}
.btn-primary:focus-visible {
	outline: none;
	box-shadow:
		0 0 0 3px var(--teal-100),
		0 0 0 5px var(--teal-500);
}

/* === ACTION — Coral (publish, launch, highlight CTA) === */
.btn-action {
	background: var(--gradient-action);
	color: #ffffff;
	font-family: var(--font-body);
	font-weight: var(--weight-semibold);
	font-size: var(--text-sm);
	padding: 10px var(--space-6);
	border-radius: var(--radius-lg);
	border: none;
	cursor: pointer;
	transition:
		opacity 0.15s,
		box-shadow 0.15s,
		transform 0.1s;
	display: inline-flex;
	align-items: center;
	gap: var(--space-2);
}
.btn-action:hover {
	opacity: 0.9;
	box-shadow: var(--shadow-coral);
}
.btn-action:active {
	transform: translateY(1px);
	opacity: 0.95;
}

/* === SECONDARY — Outlined teal === */
.btn-secondary {
	background: transparent;
	color: var(--teal-600);
	border: 1.5px solid var(--teal-300);
	font-family: var(--font-body);
	font-weight: var(--weight-medium);
	font-size: var(--text-sm);
	padding: 9px var(--space-5);
	border-radius: var(--radius-lg);
	cursor: pointer;
	transition: all 0.15s;
	display: inline-flex;
	align-items: center;
	gap: var(--space-2);
}
.btn-secondary:hover {
	background: var(--teal-50);
	border-color: var(--teal-400);
	box-shadow: var(--shadow-xs);
}

/* === GHOST === */
.btn-ghost {
	background: transparent;
	color: var(--text-secondary);
	border: none;
	padding: 8px var(--space-4);
	font-family: var(--font-body);
	font-weight: var(--weight-medium);
	font-size: var(--text-sm);
	border-radius: var(--radius-lg);
	cursor: pointer;
	transition:
		color 0.12s,
		background 0.12s;
	display: inline-flex;
	align-items: center;
	gap: var(--space-2);
}
.btn-ghost:hover {
	color: var(--text-primary);
	background: var(--bg-overlay);
}

/* === DANGER === */
.btn-danger {
	background: var(--error-bg);
	color: var(--color-error);
	border: 1.5px solid var(--error-border);
	font-family: var(--font-body);
	font-weight: var(--weight-medium);
	font-size: var(--text-sm);
	padding: 9px var(--space-5);
	border-radius: var(--radius-lg);
	cursor: pointer;
	transition: all 0.15s;
}
.btn-danger:hover {
	background: rgba(239, 68, 68, 0.14);
}

/* === SIZES === */
.btn-sm {
	padding: 6px var(--space-4);
	font-size: var(--text-xs);
}
.btn-lg {
	padding: 13px var(--space-8);
	font-size: var(--text-base);
}
.btn-icon {
	width: 36px;
	height: 36px;
	padding: 0;
	display: inline-grid;
	place-items: center;
	border-radius: var(--radius-md);
}
.btn-icon-round {
	border-radius: var(--radius-full);
}

/* === GRADIENT OUTLINED (special hero CTA) === */
.btn-gradient-outline {
	background: transparent;
	position: relative;
	padding: 10px var(--space-6);
	border-radius: var(--radius-lg);
	font-family: var(--font-body);
	font-weight: var(--weight-semibold);
	font-size: var(--text-sm);
	color: var(--teal-600);
	cursor: pointer;
	border: 2px solid transparent;
	background-clip: padding-box;
	/* Gradient border via box-shadow */
	box-shadow: 0 0 0 2px transparent;
	background-image:
		linear-gradient(white, white),
		linear-gradient(135deg, var(--teal-400), var(--lavender-400));
	background-origin: border-box;
	background-clip: padding-box, border-box;
	border: 2px solid transparent;
	transition: all 0.15s;
}
.btn-gradient-outline:hover {
	box-shadow: 0 4px 16px rgba(20, 184, 166, 0.2);
}
```

### Input / Form Controls

```css
/* === INPUT FIELD === */
.input {
	width: 100%;
	background: var(--stone-0);
	border: 1.5px solid var(--stone-200);
	border-radius: var(--radius-lg);
	color: var(--text-primary);
	font-family: var(--font-body);
	font-size: var(--text-base);
	font-weight: var(--weight-normal);
	padding: 10px var(--space-4);
	transition:
		border-color 0.15s,
		box-shadow 0.15s;
	outline: none;
}
.input::placeholder {
	color: var(--text-muted);
}
.input:hover {
	border-color: var(--stone-300);
}
.input:focus {
	border-color: var(--teal-400);
	box-shadow: 0 0 0 3px rgba(20, 184, 166, 0.12);
}
.input.error {
	border-color: var(--color-error);
	box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}
.input.success {
	border-color: var(--color-success);
	box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}

/* === LABEL === */
.field-label {
	display: block;
	font-family: var(--font-body);
	font-size: var(--text-xs);
	font-weight: var(--weight-semibold);
	letter-spacing: var(--tracking-widest);
	text-transform: uppercase;
	color: var(--text-secondary);
	margin-bottom: var(--space-2);
}

/* === SELECT === */
.select {
	appearance: none;
	background: var(--stone-0) url("data:image/svg+xml,...") no-repeat right
		12px center;
	border: 1.5px solid var(--stone-200);
	border-radius: var(--radius-lg);
	color: var(--text-primary);
	font-family: var(--font-body);
	font-size: var(--text-base);
	padding: 10px 36px 10px var(--space-4);
	cursor: pointer;
	transition:
		border-color 0.15s,
		box-shadow 0.15s;
	outline: none;
}
.select:focus {
	border-color: var(--teal-400);
	box-shadow: 0 0 0 3px rgba(20, 184, 166, 0.12);
}

/* === TOGGLE === */
.toggle-track {
	width: 42px;
	height: 24px;
	background: var(--stone-200);
	border-radius: var(--radius-full);
	border: 2px solid transparent;
	cursor: pointer;
	transition:
		background 0.2s,
		box-shadow 0.2s;
	position: relative;
}
.toggle-track[data-checked="true"] {
	background: var(--teal-500);
}
.toggle-track:focus-visible {
	box-shadow: 0 0 0 3px rgba(20, 184, 166, 0.2);
}
.toggle-thumb {
	position: absolute;
	top: 2px;
	left: 2px;
	width: 16px;
	height: 16px;
	background: white;
	border-radius: 50%;
	box-shadow: var(--shadow-sm);
	transition: transform 0.22s cubic-bezier(0.34, 1.56, 0.64, 1);
}
[data-checked="true"] .toggle-thumb {
	transform: translateX(18px);
}

/* === CHECKBOX === */
.checkbox {
	width: 18px;
	height: 18px;
	border: 2px solid var(--stone-300);
	border-radius: var(--radius-sm);
	background: white;
	cursor: pointer;
	transition: all 0.15s;
	display: grid;
	place-items: center;
}
.checkbox[data-checked="true"] {
	background: var(--teal-500);
	border-color: var(--teal-500);
}
.checkbox::after {
	content: "";
	width: 4px;
	height: 7px;
	border: 2px solid white;
	border-top: none;
	border-left: none;
	transform: rotate(45deg) translateY(-1px);
	opacity: 0;
}
.checkbox[data-checked="true"]::after {
	opacity: 1;
}
```

### Card System

```css
/* === BASE CARD === */
.card {
	background: var(--stone-0);
	border: 1px solid var(--border-default);
	border-radius: var(--radius-2xl);
	padding: var(--space-6);
	transition:
		border-color 0.2s,
		box-shadow 0.2s,
		transform 0.2s;
}

/* === INTERACTIVE CARD === */
.card-interactive {
	cursor: pointer;
}
.card-interactive:hover {
	border-color: var(--teal-200);
	box-shadow: var(--shadow-md);
	transform: translateY(-2px);
}
.card-interactive:active {
	transform: translateY(0);
}

/* === FORM CARD (forms list) === */
.form-card {
	background: var(--stone-0);
	border: 1px solid var(--border-default);
	border-radius: var(--radius-2xl);
	overflow: hidden;
	cursor: pointer;
	transition: all 0.22s cubic-bezier(0.34, 1.56, 0.64, 1);
	position: relative;
}
.form-card::before {
	content: "";
	position: absolute;
	inset: 0;
	border-radius: var(--radius-2xl);
	opacity: 0;
	background: linear-gradient(
		135deg,
		rgba(20, 184, 166, 0.04),
		rgba(167, 139, 250, 0.04)
	);
	transition: opacity 0.2s;
}
.form-card:hover {
	border-color: var(--teal-200);
	box-shadow: 0 8px 32px rgba(20, 184, 166, 0.12);
	transform: translateY(-3px);
}
.form-card:hover::before {
	opacity: 1;
}

/* Form card preview strip — gradient by form status */
.form-card-preview {
	height: 100px;
	background: var(--gradient-nature); /* default: nature gradient */
	position: relative;
	overflow: hidden;
}
.form-card-preview.draft {
	background: linear-gradient(135deg, var(--stone-100), var(--stone-150));
}
.form-card-preview.published {
	background: linear-gradient(135deg, var(--teal-100), var(--teal-200));
}
.form-card-preview.live {
	background: var(--gradient-brand);
}

.form-card-body {
	padding: var(--space-5);
}
.form-card-name {
	font-family: var(--font-display);
	font-size: var(--text-md);
	font-weight: var(--weight-semibold);
	color: var(--text-primary);
	margin-bottom: var(--space-2);
	white-space: nowrap;
	overflow: hidden;
	text-overflow: ellipsis;
	letter-spacing: var(--tracking-tight);
}

/* === STAT CARD === */
.card-stat {
	background: var(--stone-0);
	border: 1px solid var(--border-subtle);
	border-radius: var(--radius-2xl);
	padding: var(--space-6);
	position: relative;
	overflow: hidden;
}
/* Decorative gradient blob in corner */
.card-stat::after {
	content: "";
	position: absolute;
	top: -20px;
	right: -20px;
	width: 80px;
	height: 80px;
	border-radius: 50%;
	background: var(--gradient-brand);
	opacity: 0.08;
	pointer-events: none;
}
.card-stat .stat-value {
	font-family: var(--font-display);
	font-size: var(--text-2xl);
	font-weight: var(--weight-bold);
	color: var(--text-primary);
	letter-spacing: var(--tracking-tighter);
	line-height: 1;
	margin-bottom: var(--space-1);
}
.card-stat .stat-label {
	font-family: var(--font-body);
	font-size: var(--text-xs);
	font-weight: var(--weight-semibold);
	color: var(--text-muted);
	letter-spacing: var(--tracking-widest);
	text-transform: uppercase;
}
.card-stat .stat-delta {
	font-size: var(--text-xs);
	font-weight: var(--weight-medium);
	margin-top: var(--space-2);
}
.card-stat .stat-delta.up {
	color: var(--color-success);
}
.card-stat .stat-delta.down {
	color: var(--color-error);
}

/* Color-tinted stat variants */
.card-stat.teal {
	border-top: 3px solid var(--teal-400);
}
.card-stat.sage {
	border-top: 3px solid var(--sage-400);
}
.card-stat.coral {
	border-top: 3px solid var(--coral-400);
}
.card-stat.lavender {
	border-top: 3px solid var(--lavender-400);
}
```

### Badge / Status Pills

```css
.badge {
	display: inline-flex;
	align-items: center;
	gap: var(--space-1);
	padding: 3px 10px;
	border-radius: var(--radius-full);
	font-family: var(--font-body);
	font-size: 11px;
	font-weight: var(--weight-semibold);
	letter-spacing: 0.03em;
	white-space: nowrap;
}

.badge-draft {
	background: var(--stone-50);
	color: var(--stone-500);
	border: 1px solid var(--stone-200);
}
.badge-published {
	background: var(--success-bg);
	color: #059669;
	border: 1px solid var(--success-border);
}
.badge-live {
	background: rgba(20, 184, 166, 0.1);
	color: var(--teal-600);
	border: 1px solid rgba(20, 184, 166, 0.25);
}
.badge-archived {
	background: var(--stone-50);
	color: var(--stone-400);
	border: 1px solid var(--stone-200);
}
.badge-ai {
	background: var(--lavender-glow);
	color: var(--lavender-600);
	border: 1px solid rgba(167, 139, 250, 0.25);
}

/* Live pulse dot */
.badge-live::before {
	content: "";
	width: 6px;
	height: 6px;
	background: var(--teal-500);
	border-radius: 50%;
	animation: pulse-dot 2s ease infinite;
}
@keyframes pulse-dot {
	0%,
	100% {
		opacity: 1;
		transform: scale(1);
	}
	50% {
		opacity: 0.4;
		transform: scale(0.75);
	}
}
```

### Sidebar Navigation

```css
.sidebar {
	width: 248px;
	flex-shrink: 0;
	background: var(--stone-0);
	border-right: 1px solid var(--border-subtle);
	display: flex;
	flex-direction: column;
	padding: var(--space-4) var(--space-3);
	gap: var(--space-1);
	height: 100vh;
	position: sticky;
	top: 0;
}

/* Logo */
.sidebar-logo {
	display: flex;
	align-items: center;
	gap: var(--space-3);
	padding: var(--space-3) var(--space-2);
	margin-bottom: var(--space-5);
}
.logo-mark {
	width: 32px;
	height: 32px;
	background: var(--gradient-brand);
	border-radius: var(--radius-lg);
	display: grid;
	place-items: center;
	flex-shrink: 0;
	box-shadow: var(--shadow-teal);
}
.logo-name {
	font-family: var(--font-display);
	font-size: var(--text-md);
	font-weight: var(--weight-bold);
	color: var(--text-primary);
	letter-spacing: var(--tracking-tight);
}

/* Nav items */
.nav-section-label {
	font-family: var(--font-body);
	font-size: 10px;
	font-weight: var(--weight-semibold);
	letter-spacing: var(--tracking-widest);
	text-transform: uppercase;
	color: var(--text-faint);
	padding: var(--space-3) var(--space-3) var(--space-1);
	margin-top: var(--space-4);
}

.nav-item {
	display: flex;
	align-items: center;
	gap: var(--space-3);
	padding: 9px var(--space-3);
	border-radius: var(--radius-lg);
	color: var(--text-secondary);
	font-family: var(--font-body);
	font-size: var(--text-sm);
	font-weight: var(--weight-medium);
	cursor: pointer;
	transition:
		color 0.12s,
		background 0.12s;
	text-decoration: none;
	position: relative;
}
.nav-item:hover {
	color: var(--text-primary);
	background: var(--stone-50);
}
.nav-item.active {
	color: var(--teal-700);
	background: var(--teal-50);
	font-weight: var(--weight-semibold);
}
.nav-item.active .nav-icon {
	color: var(--teal-500);
}

/* Active indicator bar */
.nav-item.active::before {
	content: "";
	position: absolute;
	left: 0;
	top: 25%;
	bottom: 25%;
	width: 3px;
	background: var(--teal-500);
	border-radius: 0 var(--radius-full) var(--radius-full) 0;
}
```

---

## 🏗 Layout Architecture

### Admin App Shell

```css
.admin-shell {
	display: flex;
	min-height: 100vh;
	background: var(--bg-page);
}

.content-area {
	flex: 1;
	display: flex;
	flex-direction: column;
	overflow-y: auto;
	min-width: 0;
}

.page-header {
	position: sticky;
	top: 0;
	z-index: 20;
	padding: var(--space-5) var(--space-8);
	background: rgba(250, 250, 249, 0.85);
	backdrop-filter: blur(16px);
	-webkit-backdrop-filter: blur(16px);
	border-bottom: 1px solid var(--border-subtle);
	display: flex;
	align-items: center;
	justify-content: space-between;
	gap: var(--space-4);
}

.page-title {
	font-family: var(--font-display);
	font-size: var(--text-xl);
	font-weight: var(--weight-bold);
	color: var(--text-primary);
	letter-spacing: var(--tracking-tighter);
}

.page-body {
	padding: var(--space-8);
	max-width: 1200px;
	width: 100%;
	margin: 0 auto;
}
```

### Form Builder Layout

```css
.builder-shell {
	height: 100vh;
	display: grid;
	grid-template-rows: 52px 1fr;
	grid-template-columns: 208px 1fr 312px;
	background: var(--bg-page);
	overflow: hidden;
}
.builder-header {
	grid-column: 1 / -1;
	background: var(--stone-0);
	border-bottom: 1px solid var(--border-subtle);
	display: flex;
	align-items: center;
	padding: 0 var(--space-5);
	gap: var(--space-4);
	box-shadow: var(--shadow-xs);
}
.builder-form-name {
	font-family: var(--font-display);
	font-size: var(--text-md);
	font-weight: var(--weight-semibold);
	color: var(--text-primary);
	flex: 1;
	border: none;
	background: transparent;
	outline: none;
	letter-spacing: var(--tracking-tight);
}
.builder-form-name:focus {
	background: var(--stone-50);
	border-radius: var(--radius-md);
	padding: 0 var(--space-3);
}

/* Canvas */
.builder-canvas {
	background-color: var(--stone-25);
	background-image: radial-gradient(
		circle,
		var(--stone-200) 1.5px,
		transparent 1.5px
	);
	background-size: 28px 28px;
	overflow: hidden;
	position: relative;
}
/* Subtle gradient overlay on canvas */
.builder-canvas::before {
	content: "";
	position: absolute;
	inset: 0;
	background: var(--gradient-page-hero);
	pointer-events: none;
	z-index: 0;
}

/* Graph nodes */
.graph-node {
	background: var(--stone-0);
	border: 1.5px solid var(--stone-200);
	border-radius: var(--radius-xl);
	min-width: 228px;
	padding: var(--space-4) var(--space-5);
	box-shadow: var(--shadow-sm);
	cursor: grab;
	transition:
		border-color 0.15s,
		box-shadow 0.15s,
		transform 0.15s;
	position: absolute;
	z-index: 1;
}
.graph-node:hover {
	border-color: var(--teal-300);
	box-shadow: var(--shadow-md);
	transform: translateY(-1px);
}
.graph-node.selected {
	border-color: var(--teal-400);
	box-shadow:
		0 0 0 3px rgba(20, 184, 166, 0.15),
		var(--shadow-teal);
}
.graph-node-type-label {
	font-family: var(--font-body);
	font-size: 10px;
	font-weight: var(--weight-semibold);
	letter-spacing: var(--tracking-widest);
	text-transform: uppercase;
	color: var(--teal-500);
	margin-bottom: var(--space-2);
	display: flex;
	align-items: center;
	gap: var(--space-1);
}
/* Node type colors */
.graph-node.type-question .graph-node-type-label {
	color: var(--teal-500);
}
.graph-node.type-branch .graph-node-type-label {
	color: var(--lavender-500);
}
.graph-node.type-end .graph-node-type-label {
	color: var(--sage-500);
}

.graph-node-content {
	font-family: var(--font-body);
	font-size: var(--text-sm);
	color: var(--text-primary);
	line-height: var(--leading-snug);
}

/* Connection edges — SVG */
.graph-edge {
	stroke: var(--teal-300);
	stroke-width: 2;
	fill: none;
}
.graph-edge:hover {
	stroke: var(--teal-500);
}
.graph-edge.selected {
	stroke: var(--teal-500);
	stroke-width: 2.5;
}

/* Tool panel */
.builder-tools {
	background: var(--stone-0);
	border-right: 1px solid var(--border-subtle);
	padding: var(--space-5) var(--space-4);
	overflow-y: auto;
}
.node-type-item {
	background: var(--stone-0);
	border: 1.5px solid var(--stone-200);
	border-radius: var(--radius-lg);
	padding: var(--space-3) var(--space-4);
	font-family: var(--font-body);
	font-size: var(--text-sm);
	font-weight: var(--weight-medium);
	color: var(--text-secondary);
	cursor: grab;
	margin-bottom: var(--space-2);
	transition: all 0.15s;
	display: flex;
	align-items: center;
	gap: var(--space-3);
}
.node-type-item:hover {
	color: var(--teal-700);
	border-color: var(--teal-300);
	background: var(--teal-50);
	box-shadow: var(--shadow-xs);
}

/* Properties panel */
.builder-props {
	background: var(--stone-0);
	border-left: 1px solid var(--border-subtle);
	padding: var(--space-5);
	overflow-y: auto;
}
```

---

## 💬 Consumer Chat Runtime

The consumer side is its own visual world: white + stone, teal for the bot's intelligence, lavender for AI moments, with a clean and breathable layout.

```css
/* === Consumer shell === */
.consumer-runtime {
	min-height: 100vh;
	background: var(--stone-25);
	background-image: var(--mesh-bg);
	display: flex;
	flex-direction: column;
	align-items: center;
	font-family: var(--font-body);
}

/* Form header */
.consumer-header {
	width: 100%;
	max-width: 640px;
	padding: var(--space-8) var(--space-6) var(--space-4);
}
.consumer-form-title {
	font-family: var(--font-display);
	font-size: var(--text-2xl);
	font-weight: var(--weight-bold);
	color: var(--text-primary);
	letter-spacing: var(--tracking-tighter);
	line-height: var(--leading-tight);
	margin-bottom: var(--space-2);
}
.consumer-org-badge {
	display: inline-flex;
	align-items: center;
	gap: var(--space-2);
	font-size: var(--text-xs);
	color: var(--text-muted);
	font-weight: var(--weight-medium);
}
/* Powered-by teal dot */
.consumer-org-badge::before {
	content: "";
	width: 8px;
	height: 8px;
	background: var(--gradient-brand);
	border-radius: 50%;
}

/* Progress bar */
.consumer-progress {
	width: 100%;
	max-width: 640px;
	padding: 0 var(--space-6) var(--space-2);
}
.progress-track {
	height: 4px;
	background: var(--stone-150);
	border-radius: var(--radius-full);
	overflow: hidden;
}
.progress-fill {
	height: 100%;
	background: var(--gradient-brand);
	border-radius: var(--radius-full);
	transition: width 0.6s cubic-bezier(0.65, 0, 0.35, 1);
}
.progress-text {
	font-size: var(--text-xs);
	color: var(--text-muted);
	text-align: right;
	margin-top: var(--space-1);
	font-weight: var(--weight-medium);
}

/* Chat thread */
.chat-thread {
	width: 100%;
	max-width: 640px;
	flex: 1;
	padding: var(--space-4) var(--space-6);
	display: flex;
	flex-direction: column;
	gap: var(--space-5);
	overflow-y: auto;
}

/* === BOT MESSAGE === */
.msg-bot {
	display: flex;
	gap: var(--space-3);
	align-items: flex-end;
	max-width: 88%;
	align-self: flex-start;
	animation: bubble-in-left 0.3s cubic-bezier(0.34, 1.56, 0.64, 1) both;
}
.msg-bot-avatar {
	width: 32px;
	height: 32px;
	background: var(--gradient-brand);
	border-radius: var(--radius-full);
	flex-shrink: 0;
	display: grid;
	place-items: center;
	box-shadow: 0 2px 8px rgba(20, 184, 166, 0.3);
	font-size: 13px;
	color: white;
	font-weight: 700;
}
.msg-bot-bubble {
	background: var(--stone-0);
	border: 1px solid var(--border-default);
	color: var(--text-primary);
	padding: var(--space-4) var(--space-5);
	border-radius: var(--radius-2xl) var(--radius-2xl) var(--radius-2xl)
		var(--radius-sm);
	font-family: var(--font-body);
	font-size: var(--text-base);
	font-weight: var(--weight-normal);
	line-height: var(--leading-relaxed);
	box-shadow: var(--shadow-sm);
}

/* === USER MESSAGE === */
.msg-user {
	display: flex;
	justify-content: flex-end;
	align-self: flex-end;
	max-width: 88%;
	animation: bubble-in-right 0.2s ease-out both;
}
.msg-user-bubble {
	background: var(--gradient-brand);
	color: white;
	padding: var(--space-3) var(--space-5);
	border-radius: var(--radius-2xl) var(--radius-2xl) var(--radius-sm)
		var(--radius-2xl);
	font-family: var(--font-body);
	font-size: var(--text-base);
	font-weight: var(--weight-medium);
	line-height: var(--leading-snug);
	box-shadow: var(--shadow-teal);
}

/* === TYPING INDICATOR === */
.typing-indicator {
	display: flex;
	gap: 5px;
	align-items: center;
	padding: var(--space-4) var(--space-5);
	background: var(--stone-0);
	border: 1px solid var(--border-default);
	border-radius: var(--radius-2xl) var(--radius-2xl) var(--radius-2xl)
		var(--radius-sm);
	width: fit-content;
	align-self: flex-start;
	box-shadow: var(--shadow-xs);
}
.typing-dot {
	width: 7px;
	height: 7px;
	background: var(--teal-400);
	border-radius: 50%;
	animation: typing-bounce 1.5s infinite ease-in-out;
}
.typing-dot:nth-child(2) {
	animation-delay: 0.18s;
	background: var(--lavender-400);
}
.typing-dot:nth-child(3) {
	animation-delay: 0.36s;
	background: var(--sage-400);
}
@keyframes typing-bounce {
	0%,
	60%,
	100% {
		transform: translateY(0);
		opacity: 0.4;
	}
	30% {
		transform: translateY(-7px);
		opacity: 1;
	}
}

/* === QUICK REPLIES === */
.quick-replies {
	display: flex;
	flex-wrap: wrap;
	gap: var(--space-2);
	align-self: flex-start;
	animation: fade-up 0.25s ease-out both;
}
.quick-reply-chip {
	padding: 8px 18px;
	background: var(--stone-0);
	border: 1.5px solid var(--stone-200);
	border-radius: var(--radius-full);
	font-family: var(--font-body);
	font-size: var(--text-sm);
	font-weight: var(--weight-medium);
	color: var(--text-primary);
	cursor: pointer;
	transition: all 0.15s;
	box-shadow: var(--shadow-xs);
}
.quick-reply-chip:hover {
	border-color: var(--teal-400);
	background: var(--teal-50);
	color: var(--teal-700);
	box-shadow: var(--shadow-teal);
	transform: translateY(-1px);
}
.quick-reply-chip:active {
	transform: translateY(0);
}

/* === CHAT INPUT AREA === */
.chat-input-area {
	width: 100%;
	max-width: 640px;
	padding: var(--space-4) var(--space-6) var(--space-8);
	position: sticky;
	bottom: 0;
	background: linear-gradient(to top, var(--stone-25) 75%, transparent);
}
.chat-input-wrapper {
	display: flex;
	align-items: flex-end;
	gap: var(--space-3);
	background: var(--stone-0);
	border: 1.5px solid var(--stone-200);
	border-radius: var(--radius-3xl);
	padding: var(--space-3) var(--space-3) var(--space-3) var(--space-5);
	box-shadow: var(--shadow-md);
	transition:
		border-color 0.15s,
		box-shadow 0.15s;
}
.chat-input-wrapper:focus-within {
	border-color: var(--teal-300);
	box-shadow:
		var(--shadow-md),
		0 0 0 3px rgba(20, 184, 166, 0.1);
}
.chat-input {
	flex: 1;
	border: none;
	outline: none;
	font-family: var(--font-body);
	font-size: var(--text-base);
	color: var(--text-primary);
	background: transparent;
	resize: none;
	max-height: 120px;
	line-height: var(--leading-normal);
}
.chat-input::placeholder {
	color: var(--text-muted);
}
.chat-send-btn {
	width: 38px;
	height: 38px;
	background: var(--gradient-brand);
	border: none;
	border-radius: var(--radius-full);
	display: grid;
	place-items: center;
	cursor: pointer;
	color: white;
	flex-shrink: 0;
	transition:
		opacity 0.15s,
		transform 0.1s,
		box-shadow 0.15s;
	box-shadow: var(--shadow-teal);
}
.chat-send-btn:hover {
	opacity: 0.9;
	transform: scale(1.05);
}
.chat-send-btn:active {
	transform: scale(0.94);
}
.chat-send-btn:disabled {
	background: var(--stone-150);
	color: var(--stone-400);
	box-shadow: none;
	cursor: not-allowed;
}
```

### Completion Screen

```css
.completion-screen {
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	min-height: 60vh;
	text-align: center;
	padding: var(--space-12) var(--space-8);
	gap: var(--space-5);
}
.completion-icon {
	width: 72px;
	height: 72px;
	background: var(--gradient-nature);
	border-radius: 50%;
	display: grid;
	place-items: center;
	font-size: 32px;
	box-shadow: 0 8px 32px rgba(20, 184, 166, 0.3);
	animation: success-burst 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) both;
}
.completion-title {
	font-family: var(--font-display);
	font-size: var(--text-2xl);
	font-weight: var(--weight-bold);
	color: var(--text-primary);
	letter-spacing: var(--tracking-tighter);
}
.completion-subtitle {
	font-size: var(--text-base);
	color: var(--text-secondary);
	max-width: 320px;
	line-height: var(--leading-relaxed);
}
```

### Voice Mode

```css
.voice-overlay {
	position: fixed;
	inset: 0;
	background: rgba(250, 250, 249, 0.95);
	backdrop-filter: blur(16px);
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	gap: var(--space-10);
	z-index: 100;
}
.waveform {
	display: flex;
	align-items: center;
	gap: 4px;
	height: 52px;
}
.waveform-bar {
	width: 4px;
	border-radius: 2px;
	animation: waveform-anim 0.9s ease infinite;
}
/* Tri-color waveform bars */
.waveform-bar:nth-child(3n + 1) {
	background: var(--teal-400);
}
.waveform-bar:nth-child(3n + 2) {
	background: var(--lavender-400);
}
.waveform-bar:nth-child(3n + 3) {
	background: var(--sage-400);
}
@keyframes waveform-anim {
	0%,
	100% {
		height: 8px;
		opacity: 0.35;
	}
	50% {
		height: 44px;
		opacity: 1;
	}
}

.mic-btn {
	width: 80px;
	height: 80px;
	background: var(--gradient-brand);
	border-radius: 50%;
	border: none;
	display: grid;
	place-items: center;
	cursor: pointer;
	color: white;
	animation: mic-pulse 2.2s ease infinite;
	transition: transform 0.15s;
}
.mic-btn:hover {
	transform: scale(1.05);
}
@keyframes mic-pulse {
	0% {
		box-shadow: 0 0 0 0 rgba(20, 184, 166, 0.4);
	}
	70% {
		box-shadow: 0 0 0 22px rgba(20, 184, 166, 0);
	}
	100% {
		box-shadow: 0 0 0 0 rgba(20, 184, 166, 0);
	}
}
.mic-status {
	font-family: var(--font-display);
	font-size: var(--text-lg);
	font-weight: var(--weight-semibold);
	color: var(--text-primary);
	letter-spacing: var(--tracking-tight);
}
```

---

## 🔐 Auth Screens

```css
.auth-page {
	min-height: 100vh;
	background: var(--mesh-bg);
	display: flex;
	align-items: center;
	justify-content: center;
	padding: var(--space-8);
}
.auth-card {
	width: 100%;
	max-width: 420px;
	background: rgba(255, 255, 255, 0.85);
	backdrop-filter: blur(20px);
	border: 1px solid rgba(255, 255, 255, 0.9);
	border-radius: var(--radius-3xl);
	padding: var(--space-10);
	box-shadow: var(--shadow-xl);
	animation: fade-up 0.45s cubic-bezier(0.34, 1.56, 0.64, 1) both;
}
.auth-logo-wrap {
	text-align: center;
	margin-bottom: var(--space-8);
}
.auth-logo-icon {
	width: 52px;
	height: 52px;
	background: var(--gradient-brand);
	border-radius: var(--radius-xl);
	display: inline-grid;
	place-items: center;
	box-shadow: var(--shadow-teal);
	font-size: 24px;
	color: white;
	margin-bottom: var(--space-4);
}
.auth-title {
	font-family: var(--font-display);
	font-size: var(--text-2xl);
	font-weight: var(--weight-bold);
	color: var(--text-primary);
	letter-spacing: var(--tracking-tighter);
	margin-bottom: var(--space-2);
}
.auth-subtitle {
	font-size: var(--text-sm);
	color: var(--text-secondary);
	line-height: var(--leading-normal);
}

/* Social login button */
.btn-social {
	width: 100%;
	background: var(--stone-0);
	border: 1.5px solid var(--stone-200);
	border-radius: var(--radius-lg);
	padding: 11px var(--space-5);
	font-family: var(--font-body);
	font-weight: var(--weight-medium);
	font-size: var(--text-sm);
	color: var(--text-primary);
	cursor: pointer;
	display: flex;
	align-items: center;
	justify-content: center;
	gap: var(--space-3);
	transition: all 0.15s;
}
.btn-social:hover {
	background: var(--stone-50);
	border-color: var(--stone-300);
	box-shadow: var(--shadow-sm);
}

/* Divider */
.auth-divider {
	display: flex;
	align-items: center;
	gap: var(--space-4);
	margin: var(--space-6) 0;
}
.auth-divider::before,
.auth-divider::after {
	content: "";
	flex: 1;
	height: 1px;
	background: var(--stone-200);
}
.auth-divider span {
	font-size: var(--text-xs);
	color: var(--text-muted);
	font-weight: var(--weight-medium);
	letter-spacing: var(--tracking-wide);
	text-transform: uppercase;
}
```

---

## 📊 Analytics & Submissions

```css
/* Funnel bars */
.funnel-row {
	display: flex;
	align-items: center;
	gap: var(--space-4);
	padding: var(--space-3) 0;
}
.funnel-step-name {
	font-family: var(--font-body);
	font-size: var(--text-sm);
	font-weight: var(--weight-medium);
	color: var(--text-secondary);
	width: 160px;
	flex-shrink: 0;
}
.funnel-track {
	flex: 1;
	height: 10px;
	background: var(--stone-100);
	border-radius: var(--radius-full);
	overflow: hidden;
}
.funnel-fill {
	height: 100%;
	background: var(--gradient-brand);
	border-radius: var(--radius-full);
	transition: width 1.2s cubic-bezier(0.65, 0, 0.35, 1);
}
.funnel-pct {
	font-family: var(--font-display);
	font-size: var(--text-sm);
	font-weight: var(--weight-semibold);
	color: var(--teal-600);
	width: 48px;
	text-align: right;
}

/* Submissions table */
.submissions-table {
	width: 100%;
	border-collapse: collapse;
}
.submissions-table th {
	text-align: left;
	font-family: var(--font-body);
	font-size: 11px;
	font-weight: var(--weight-semibold);
	letter-spacing: var(--tracking-widest);
	text-transform: uppercase;
	color: var(--text-muted);
	padding: var(--space-3) var(--space-4);
	border-bottom: 1.5px solid var(--border-subtle);
	background: var(--stone-25);
}
.submissions-table td {
	font-family: var(--font-body);
	font-size: var(--text-sm);
	color: var(--text-primary);
	padding: var(--space-4);
	border-bottom: 1px solid var(--border-subtle);
	vertical-align: middle;
}
.submissions-table tr:hover td {
	background: var(--stone-25);
}
.session-id-cell {
	font-family: var(--font-mono);
	font-size: 11px;
	color: var(--text-secondary);
	background: var(--stone-50);
	border: 1px solid var(--stone-200);
	padding: 2px 8px;
	border-radius: var(--radius-sm);
	display: inline-block;
	max-width: 120px;
	overflow: hidden;
	text-overflow: ellipsis;
}
```

---

## ✨ Animations & Motion

```css
/* === Entry animations === */
@keyframes fade-up {
	from {
		opacity: 0;
		transform: translateY(14px);
	}
	to {
		opacity: 1;
		transform: translateY(0);
	}
}
@keyframes fade-in {
	from {
		opacity: 0;
	}
	to {
		opacity: 1;
	}
}
@keyframes bubble-in-left {
	from {
		opacity: 0;
		transform: translateX(-12px) scale(0.94);
	}
	to {
		opacity: 1;
		transform: translateX(0) scale(1);
	}
}
@keyframes bubble-in-right {
	from {
		opacity: 0;
		transform: translateX(12px) scale(0.94);
	}
	to {
		opacity: 1;
		transform: translateX(0) scale(1);
	}
}
@keyframes success-burst {
	0% {
		transform: scale(0.4);
		opacity: 0;
	}
	65% {
		transform: scale(1.18);
	}
	100% {
		transform: scale(1);
		opacity: 1;
	}
}

/* === Skeleton loader === */
.skeleton {
	border-radius: var(--radius-md);
	background: linear-gradient(
		90deg,
		var(--stone-100) 0%,
		var(--stone-50) 50%,
		var(--stone-100) 100%
	);
	background-size: 200% 100%;
	animation: skeleton-shimmer 1.6s ease infinite;
}
@keyframes skeleton-shimmer {
	from {
		background-position: 200% 0;
	}
	to {
		background-position: -200% 0;
	}
}

/* === Staggered list reveals === */
.stagger > * {
	animation: fade-up 0.4s ease both;
}
.stagger > *:nth-child(1) {
	animation-delay: 0.05s;
}
.stagger > *:nth-child(2) {
	animation-delay: 0.1s;
}
.stagger > *:nth-child(3) {
	animation-delay: 0.15s;
}
.stagger > *:nth-child(4) {
	animation-delay: 0.2s;
}
.stagger > *:nth-child(5) {
	animation-delay: 0.25s;
}
.stagger > *:nth-child(6) {
	animation-delay: 0.3s;
}

/* === Page load === */
.page-enter {
	animation: fade-up 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) both;
}
```

---

## 🔔 Feedback Components

```css
/* Toast */
.toast {
	background: var(--stone-0);
	border: 1px solid var(--border-default);
	border-radius: var(--radius-xl);
	padding: var(--space-4) var(--space-5);
	display: flex;
	align-items: center;
	gap: var(--space-3);
	box-shadow: var(--shadow-lg);
	font-family: var(--font-body);
	font-size: var(--text-sm);
	font-weight: var(--weight-medium);
	color: var(--text-primary);
	max-width: 380px;
	animation: toast-in 0.35s cubic-bezier(0.34, 1.56, 0.64, 1) both;
}
.toast.success {
	border-left: 3px solid var(--color-success);
}
.toast.error {
	border-left: 3px solid var(--color-error);
}
.toast.info {
	border-left: 3px solid var(--teal-400);
}
@keyframes toast-in {
	from {
		opacity: 0;
		transform: translateY(14px) scale(0.94);
	}
	to {
		opacity: 1;
		transform: translateY(0) scale(1);
	}
}

/* Empty state */
.empty-state {
	display: flex;
	flex-direction: column;
	align-items: center;
	text-align: center;
	padding: var(--space-20) var(--space-8);
	gap: var(--space-3);
}
.empty-icon-wrap {
	width: 64px;
	height: 64px;
	background: var(--stone-50);
	border: 1.5px solid var(--stone-200);
	border-radius: var(--radius-2xl);
	display: grid;
	place-items: center;
	font-size: 28px;
	margin-bottom: var(--space-2);
}
.empty-title {
	font-family: var(--font-display);
	font-size: var(--text-xl);
	font-weight: var(--weight-bold);
	color: var(--text-primary);
	letter-spacing: var(--tracking-tight);
}
.empty-desc {
	font-size: var(--text-sm);
	color: var(--text-secondary);
	max-width: 260px;
	line-height: var(--leading-relaxed);
}

/* Publish modal */
.publish-modal-overlay {
	position: fixed;
	inset: 0;
	background: rgba(28, 25, 23, 0.45);
	backdrop-filter: blur(4px);
	display: grid;
	place-items: center;
	z-index: 200;
	animation: fade-in 0.2s ease;
}
.publish-modal {
	background: var(--stone-0);
	border-radius: var(--radius-3xl);
	padding: var(--space-10);
	max-width: 480px;
	width: 90vw;
	box-shadow: var(--shadow-xl);
	animation: fade-up 0.3s cubic-bezier(0.34, 1.56, 0.64, 1) both;
}
.publish-url-row {
	display: flex;
	align-items: center;
	gap: var(--space-3);
	background: var(--stone-50);
	border: 1.5px solid var(--stone-200);
	border-radius: var(--radius-lg);
	padding: var(--space-3) var(--space-4);
	margin: var(--space-5) 0;
}
.publish-url-text {
	font-family: var(--font-mono);
	font-size: var(--text-sm);
	color: var(--teal-600);
	flex: 1;
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
}
```

---

## ✅ Design Rules to Always Follow

1. **Light theme throughout** — both admin and consumer use light backgrounds; no dark mode surfaces
2. **Teal is the primary action color** — all primary buttons, active nav, focus rings, progress bars
3. **Coral for CTAs that demand immediate attention** — Publish button, launch actions, important alerts
4. **Lavender exclusively for AI/bot identity** — bot avatar, AI-generated badge, processing indicators
5. **Sage for success/completion** — end nodes, completion screens, success states blend sage into teal
6. **Montserrat for all headings** — page titles, card titles, stat numbers, auth titles
7. **Poppins for all UI text** — buttons, labels, body, chat messages, nav items
8. **JetBrains Mono only for system data** — IDs, session tokens, form slugs, JSON snippets
9. **Colored shadows** — never grey box-shadows; use `--shadow-teal`, `--shadow-coral` on interactive elements
10. **Gradient brand on key elements** — logo mark, send button, progress bar fill, bot avatar, primary icon areas
11. **8pt spacing grid** — all spacing via CSS variables, never arbitrary values
12. **`border-radius: var(--radius-2xl)` on cards** — soft, approachable corners throughout
13. **Mesh background on auth + consumer** — gradient noise makes background feel alive and premium
14. **Animate chat bubbles directionally** — bot comes in from left, user from right
15. **Focus rings = teal** — `box-shadow: 0 0 0 3px rgba(20,184,166,0.15)` always

---

## 🚫 Anti-Patterns to Avoid

- **Yellow or amber as the primary accent** — replaced with teal + coral
- **Dark/black backgrounds on admin panels** — this product is light, airy, botanical
- **Grey shadows on colored elements** — always use colored shadow tokens
- **Flat white cards with no elevation** — cards need subtle border + shadow
- **Generic blue links** — use `var(--teal-500)` for all interactive text
- **High-contrast, cold color combinations** — keep the palette warm and soft
- **Overloaded rainbow UI** — max 2 accent colors visible at once per screen region
- **System-default font fallbacks** — always load Poppins and Montserrat from Google Fonts
- **Loading spinners without skeleton screens** — skeleton layouts only
- **Full-width buttons on desktop** — constrain to content width or max 320px
