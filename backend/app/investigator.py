import os
from urllib import request
import json
from sqlalchemy import select
from sqlalchemy.orm import Session
from .db import Case, Evidence

AI_BASE_URL = os.getenv("SAFENESTT_AI_BASE_URL", "").rstrip("/")
AI_KEY = os.getenv("SAFENESTT_AI_API_KEY", "")

def _fallback(case: Case, evidence: list[Evidence]) -> dict:
    findings = [{"category":"case_intake","title":"Investigation package created","detail":"The case was organized for investigation. Review the reported facts and preserve original evidence before taking further action.","confidence":"high","source":"client"}]
    if case.case_type.lower() == "crypto fraud":
        findings.append({"category":"crypto","title":"Transaction evidence should be preserved","detail":"Collect wallet addresses, transaction hashes, chain/network, timestamps, and exchange records where available.","confidence":"high","source":"client"})
    return {"status":"completed","summary":f"Case intake completed with {len(evidence)} evidence item(s). External SafeNestT AI is not configured.","findings":findings}

def run_investigation(case: Case, db: Session) -> dict:
    evidence = list(db.scalars(select(Evidence).where(Evidence.case_id == case.id)))
    if not AI_BASE_URL: return _fallback(case, evidence)
    payload = json.dumps({"case_id":case.id,"case_type":case.case_type,"description":case.description,"evidence":[{"kind":e.kind,"label":e.label,"content":e.content} for e in evidence]}).encode()
    req = request.Request(f"{AI_BASE_URL}/api/investigations", data=payload, headers={"Content-Type":"application/json","Authorization":f"Bearer {AI_KEY}"})
    try:
        with request.urlopen(req, timeout=45) as response: return json.loads(response.read().decode())
    except Exception as exc:
        return {"status":"completed_with_fallback","summary":f"AI service unavailable; client-side investigation intake completed ({type(exc).__name__}).","findings":_fallback(case,evidence)["findings"]}
