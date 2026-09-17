# SafeNestT — Client Platform

A production-ready SafeNestT application for regular users to report scams and fraud, manage cases, preserve evidence, and receive investigator-assisted guidance.

## Architecture

- User-facing SafeNestT web application
- Dedicated case-management API and database layer
- SafeNestT AI investigation engine integration
- Investigator workflow for scam/fraud cases
- Evidence collection, case timeline, reports, and secure exports
- Authentication, tenant isolation, audit logging, and encrypted sensitive data

## Current user flow

1. Create an account or sign in.
2. Report a scam or fraud incident.
3. Open the case workspace.
4. Add evidence and notes.
5. Start the SafeNestT AI investigation.
6. Review the investigation status and findings.
7. Retrieve the structured case report from the API.

## AI Investigation

The client platform uses the existing SafeNestT AI investigation engine as a separate investigator service. The client sends a scoped case package through the server-side integration boundary; browser clients never receive the AI service credential. AI findings are assistance for the user/investigator and are not presented as a determination of criminal liability.

## Production deployment

The repository includes a Docker Compose stack with PostgreSQL, the FastAPI backend, and the React/Vite frontend served by Nginx. Copy `.env.example` to `.env`, set strong `POSTGRES_PASSWORD` and `SESSION_SECRET` values, optionally configure `SAFENESTT_AI_BASE_URL` and `SAFENESTT_AI_API_KEY`, then run:

```bash
docker compose up -d --build
```

The frontend is exposed on port `8080`; Nginx proxies `/api/` to the backend. PostgreSQL data is persisted in a named volume.

GitHub Pages is maintained as a **frontend preview**. It is not the production API deployment because the backend and database must remain server-side.

## Build Plan

1. Establish the application shell and repository structure — complete.
2. Port the useful SafeNestT user experience from Base44 without carrying Base44 runtime dependencies forward — foundation complete; continue expanding feature coverage.
3. Establish the client authentication and account model — complete for the initial account flow.
4. Build scam/fraud reporting and case creation — complete for the initial flow.
5. Build evidence intake and secure case timeline — initial evidence intake complete; file attachments and richer timeline remain.
6. Connect the SafeNestT AI investigator engine — server-side adapter complete; live service verification remains an environment/deployment task.
7. Build investigation status, findings, and investigator review — initial findings view complete; richer review remains.
8. Build reports, exports, notifications, and user support workflows — structured case report API complete; UI export/notifications/support remain.
9. Add security hardening, tests, CI, deployment configuration, and production verification — CI and Docker foundation complete; final production verification remains.

## Security

Never commit API keys, access tokens, database credentials, encryption keys, or customer secrets. Sensitive case data must be tenant-scoped and protected by authorization checks and database-level isolation where supported. Production sessions require a strong secret, and the AI credential stays server-side.

## License

Proprietary — SafeNestT
