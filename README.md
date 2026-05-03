# Vitalport.app

Landing page and waitlist capture for [vitalport.app](https://vitalport.app) — an iOS app that exports and routes Apple Health data with workout-type fidelity.

## Stack

| Layer | Technology |
|---|---|
| Frontend | Static HTML/CSS/JS (single file) |
| Waitlist API | Supabase Edge Function (Deno) |
| Email delivery | Resend |
| Hosting | GitHub Pages |

## Project structure

```
index.html                        # Landing page
supabase/
  functions/subscribe/index.ts    # Edge function — saves email, sends confirmation
  waitlist-setup.sql              # One-time DB setup (run in Supabase SQL editor)
```

## Local development

Open `index.html` directly in a browser. No build step required.

## Supabase edge function

### Deploy

```bash
supabase functions deploy subscribe --project-ref lltdndpfzhlrionhgzrl
```

### Required secrets

Set these via the Supabase dashboard (Project → Edge Functions → Secrets) or CLI:

```bash
supabase secrets set RESEND_API_KEY=re_...
supabase secrets set FROM_DOMAIN=vitalport.app
supabase secrets set ADMIN_EMAIL=your-admin@example.com
```

`SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` are injected automatically.

### Database setup

Run `supabase/waitlist-setup.sql` once in the Supabase SQL editor to create the `waitlist` table with RLS enabled.

## Email flow

1. User submits email → `POST /functions/v1/subscribe`
2. Email saved to `waitlist` table (duplicate → silent success)
3. Confirmation sent to subscriber via Resend
4. Admin notification sent to `ADMIN_EMAIL`
