# SafeNestT Client API

The backend owns authentication, authorization, case data, evidence metadata, investigation jobs, and the private adapter to the SafeNestT AI investigation engine.

Run locally with:

```bash
python -m uvicorn app.main:app --reload --port 8000
```

Health check: `GET /health`.
