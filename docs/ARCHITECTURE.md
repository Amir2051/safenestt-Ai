# SafeNestT Client Architecture

## Product boundary

This repository is the user-facing SafeNestT product. The existing SafeNestT AI engine remains a separate service and repository.

## User flow

User account → report scam/fraud → create case → upload/record evidence → investigation queue → AI-assisted investigation → findings and next steps → report/export.

## Case model

Every case belongs to an authenticated user/tenant. Evidence, timeline events, findings, and generated reports inherit the same authorization boundary.

## AI boundary

The client app sends an explicitly scoped investigation package to the AI engine. The engine returns structured findings and recommended investigative next steps. The client app stores the resulting case artifacts and clearly distinguishes AI-generated material from verified evidence.

## Migration strategy

The existing Base44 application is the product reference for user-facing features and workflows. Its proprietary runtime and SDK are not a dependency of this application. Features will be reimplemented in the new stack and connected to SafeNestT's own backend services.

## Initial stack

Frontend: React + TypeScript + Vite.
Backend: FastAPI + Pydantic.
Database: PostgreSQL in production with tenant-aware authorization/RLS.
AI: SafeNestT AI investigation engine through a private service boundary.

## Security principles

- Server-side authorization for every case operation.
- Tenant isolation at the application and database layers.
- Encrypt sensitive evidence and credentials at rest.
- Never expose service credentials to the browser.
- Audit security-sensitive case and account operations.
- Minimize retention of raw third-party payloads.
