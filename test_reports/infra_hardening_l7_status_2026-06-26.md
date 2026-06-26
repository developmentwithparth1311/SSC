# Task L.7 Infra Hardening Status (2026-06-26)

## Completed checks

1. Production config endpoint confirms current state:
- turnstile_sitekey is empty (Turnstile disabled in production)
- TURN ICE servers are present in production config output

2. cloud_run.env inspection confirms:
- TURN_USERNAME and TURN_CREDENTIAL are configured
- CORS/Google redirect still point to Cloud Run default domain

## Remaining blockers for full L.7 completion

1. Turnstile production enable
- Missing TURNSTILE_SITEKEY and TURNSTILE_SECRET in cloud_run.env
- Requires Cloudflare Turnstile key pair generation and insertion

2. Custom domain rollout
- No custom domain + DNS records configured yet
- Requires domain ownership and DNS mapping to Cloud Run

3. TURN off-LAN verification
- Must be executed on real devices across cellular <-> Wi-Fi
- Cannot be validated from this workstation-only environment

## Required founder inputs to finish L.7

1. Cloudflare Turnstile site key and secret key
2. Target custom domain (e.g. api.yourdomain.com) and DNS provider access
3. Manual device call verification results (cellular-to-Wi-Fi and Wi-Fi-to-cellular)
