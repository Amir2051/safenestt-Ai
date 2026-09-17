# SafeNestT — Client Platform

A production-ready SafeNestT application for regular users to report scams and fraud, manage cases, preserve evidence, and receive investigator-assisted guidance.

## Architecture

- User-facing SafeNestT web application
- Dedicated case-management API and database layer
- SafeNestT AI investigation engine integration
- Investigator workflow for scam/fraud cases
- Evidence collection, case timeline, reports, and secure exports
- Authentication, tenant isolation, audit logging, and encrypted sensitive data

## AI Investigation

The client platform will use the existing SafeNestT AI investigation engine as the investigator service. The AI should analyze submitted evidence, organize findings, identify relevant leads, and draft case reports. AI findings are assistance for the user/investigator and are not presented as a determination of criminal liability.

## Build Plan

1. Establish the new application shell and repository structure.
2. Port the useful SafeNestT user experience from the existing Base44 application without carrying Base44 runtime dependencies forward.
3. Establish the client authentication and account model.
4. Build scam/fraud reporting and case creation.
5. Build evidence intake and secure case timeline.
6. Connect the SafeNestT AI investigator engine.
7. Build investigation status, findings, and investigator review.
8. Build reports, exports, notifications, and user support workflows.
9. Add security hardening, tests, CI, deployment configuration, and production verification.

## Security

Never commit API keys, access tokens, database credentials, encryption keys, or customer secrets. Sensitive case data must be tenant-scoped and protected by authorization checks and database-level isolation where supported.

## License

Proprietary — SafeNestT
