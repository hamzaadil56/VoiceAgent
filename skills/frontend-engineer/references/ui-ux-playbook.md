# UI/UX Playbook

## UI system rules

- Define tokens first: color, spacing, typography, radius, elevation, motion.
- Build primitive components with variant APIs and composition slots.
- Keep visual consistency through tokens; avoid hard-coded values.

## UX quality checklist

- Make primary actions obvious and stable across views.
- Show clear feedback for loading, success, empty, and error states.
- Preserve user context during navigation and async updates.
- Keep forms concise; validate inline with actionable error text.
- Optimize for keyboard and screen reader flows.

## Responsive strategy

- Start from smallest supported viewport.
- Use fluid layout primitives before custom breakpoint hacks.
- Keep touch targets and readable type at all breakpoints.

## Interaction standards

- Use motion to support comprehension, not decoration.
- Keep transitions short and interruptible.
- Avoid layout shift by reserving space for async content.

## Accessibility standards

- Maintain color contrast compliant with WCAG AA.
- Provide visible focus states on interactive controls.
- Use semantic structure (headings, landmarks, lists, buttons/links).
- Test with keyboard-only navigation and screen reader spot checks.
