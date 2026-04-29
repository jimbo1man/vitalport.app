# Changelog

## Unreleased

### Fixed
- Email form submissions were failing with `401 UNAUTHORIZED` — Supabase edge functions require a JWT by default; added `Authorization: Bearer <anon-key>` header to the frontend fetch call.

---

## [0.2.0] — 2026-04-28

### Added
- Waitlist email capture via Supabase Edge Function (`subscribe`)
- Resend integration: confirmation email to subscriber + admin notification on signup
- Duplicate signup handling (silent success, no error shown to user)
- `waitlist` table with RLS and unique email constraint

---

## [0.1.0] — 2026-04-27

### Added
- Initial landing page (`index.html`) — hero, differentiators, fidelity comparison, privacy statement, bottom CTA
- Bricolage Grotesque + DM Mono + Instrument Serif type stack
- Scroll-reveal animations, noise overlay, grid background
- Responsive layout (mobile email form stacking)
- GitHub Pages deployment via CNAME (`vitalport.app`)
