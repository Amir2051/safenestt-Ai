import json, os
from urllib import request, error
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


def _post(url: str, payload: dict) -> dict:
    data=json.dumps(payload).encode()
    headers={"Content-Type":"application/json"}
    if AI_KEY:
        headers["X-API-Key"]=AI_KEY
    req=request.Request(url,data=data,headers=headers,method="POST")
    with request.urlopen(req,timeout=60) as response:
        return json.loads(response.read().decode())


def run_investigation(case: Case, db: Session) -> dict:
    evidence=list(db.scalars(select(Evidence).where(Evidence.case_id == case.id)))
    if not AI_BASE_URL:
        return _fallback(case,evidence)

    tenant_id=f"user:{case.user_id}"
    context={
        "case_id": str(case.id),
        "case_type": case.case_type,
        "description": case.description,
        "evidence": [
            {"id": item.id, "kind": item.kind, "label": item.label, "content": item.content}
            for item in evidence
        ],
    }
    try:
        created=_post(
            f"{AI_BASE_URL}/v1/investigations",
            {
                "target":{"type":"case","value":case.description[:4000]},
                "investigation_type":case.case_type,
                "tenant_id":tenant_id,
                "context":context,
            },
        )
        investigation_id=created["investigation_id"]
        result=_post(f"{AI_BASE_URL}/v1/investigations/{investigation_id}/start?tenant_id={tenant_id}", {})
        findings=[]
        for item in result.get("findings",[]):
            findings.append({
                "category":item.get("category","investigation"),
                "title":item.get("title") or item.get("claim") or "Finding",
                "detail":item.get("detail") or item.get("description") or item.get("claim", ""),
                "confidence":str(item.get("confidence",item.get("risk_score","unknown"))),
                "source":"safenestt-ai",
            })
        status = result.get("status", "COMPLETED")
        return {
            "status":"completed" if status == "COMPLETED" else str(status).lower(),
            "summary":result.get("summary") or "SafeNestT AI investigation completed.",
            "findings":findings,
        }
    except (error.URLError, error.HTTPError, KeyError, ValueError, TimeoutError) as exc:
        return {
            "status":"completed_with_fallback",
            "summary":f"AI service unavailable; intake fallback completed ({type(exc).__name__}).",
            "findings":_fallback(case,evidence)["findings"],
        }
