# Security audit scope

Copy this to `.claude/security-audit.md` in the project and fill it in.
The security-auditor agent reads it before every run and will not start
without it. Never put a secret or password in this file.

## Owned (the agent only touches what's listed here)

- Repo: <local path or GitHub URL>
- Domains: <example.com, staging.example.com>
  (Subdomains are not included unless listed.)
- Third-party projects: <Supabase project ref, Firebase project ID, Vercel project, S3 bucket names>

## Live URL

<https://example.com, or "none">

## What the app does

<One or two sentences.>

## User data it holds

<For example: emails, names, uploaded files, chat history, payments (through Stripe)>

## What would hurt most if leaked

<For example: student records, the OpenAI key (spend), admin access>

## Pre-approved active tests (optional)

<Leave this empty and the agent will ask first. Example: "On staging only:
log in as two test accounts and try to read each other's data.
Credentials are in the env vars AUDIT_USER_A and AUDIT_USER_B.">
