import os
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session
from .auth import current_user, hash_password, make_token, verify_password
from .db import Case, Evidence, Finding, Investigation, User, db_session
from .schemas import AuthRequest, CaseCreate, CaseOut, EvidenceCreate, FindingOut
from .investigator import run_investigation

app = FastAPI(title="SafeNestT Client API", version="0.5.0")
origins = [item.strip() for item in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:8080").split(",") if item.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["GET", "POST", "PATCH", "OPTIONS"], allow_headers=["Authorization", "Content-Type"])

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "app": "SafeNestT Client API", "version": app.version}

@app.post("/api/auth/register")
def register(body: AuthRequest, db: Session = Depends(db_session)):
    email = body.email.strip().lower()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(409, "An account with that email already exists")
    user = User(email=email, password_hash=hash_password(body.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"token": make_token(user.id), "user": {"id": user.id, "email": user.email}}

@app.post("/api/auth/login")
def login(body: AuthRequest, db: Session = Depends(db_session)):
    user = db.scalar(select(User).where(User.email == body.email.strip().lower()))
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(401, "Invalid email or password")
    return {"token": make_token(user.id), "user": {"id": user.id, "email": user.email}}

@app.get("/api/auth/me")
def me(user: User = Depends(current_user)):
    return {"id": user.id, "email": user.email}

@app.get("/api/cases", response_model=list[CaseOut])
def list_cases(user: User = Depends(current_user), db: Session = Depends(db_session)):
    return list(db.scalars(select(Case).where(Case.user_id == user.id).order_by(Case.created_at.desc())))

@app.post("/api/cases", response_model=CaseOut)
def create_case(body: CaseCreate, user: User = Depends(current_user), db: Session = Depends(db_session)):
    case = Case(user_id=user.id, title=(body.title or f"{body.case_type} report").strip(), case_type=body.case_type.strip(), description=body.description.strip())
    db.add(case)
    db.commit()
    db.refresh(case)
    return case

@app.get("/api/cases/{case_id}")
def get_case(case_id: int, user: User = Depends(current_user), db: Session = Depends(db_session)):
    case = db.scalar(select(Case).where(Case.id == case_id, Case.user_id == user.id))
    if not case:
        raise HTTPException(404, "Case not found")
    evidence = list(db.scalars(select(Evidence).where(Evidence.case_id == case.id).order_by(Evidence.created_at)))
    investigations = list(db.scalars(select(Investigation).where(Investigation.case_id == case.id).order_by(Investigation.created_at.desc())))
    findings = [f for inv in investigations for f in db.scalars(select(Finding).where(Finding.investigation_id == inv.id)).all()]
    return {"case": case, "evidence": evidence, "investigations": investigations, "findings": findings}

@app.post("/api/cases/{case_id}/evidence")
def add_evidence(case_id: int, body: EvidenceCreate, user: User = Depends(current_user), db: Session = Depends(db_session)):
    case = db.scalar(select(Case).where(Case.id == case_id, Case.user_id == user.id))
    if not case:
        raise HTTPException(404, "Case not found")
    item = Evidence(case_id=case.id, kind=body.kind.strip(), label=body.label.strip(), content=body.content.strip())
    db.add(item)
    case.updated_at = __import__("datetime").datetime.utcnow()
    db.commit()
    db.refresh(item)
    return {"id": item.id, "kind": item.kind, "label": item.label, "created_at": item.created_at}

@app.post("/api/cases/{case_id}/investigate")
def start_investigation(case_id: int, user: User = Depends(current_user), db: Session = Depends(db_session)):
    case = db.scalar(select(Case).where(Case.id == case_id, Case.user_id == user.id))
    if not case:
        raise HTTPException(404, "Case not found")
    inv = Investigation(case_id=case.id, status="running")
    db.add(inv)
    db.commit()
    db.refresh(inv)
    result = run_investigation(case, db)
    inv.status = result["status"]
    inv.summary = result["summary"]
    case.status = "investigating" if result["status"] == "running" else "open"
    for item in result["findings"]:
        db.add(Finding(investigation_id=inv.id, **item))
    db.commit()
    return {"id": inv.id, "status": inv.status, "summary": inv.summary}

@app.get("/api/cases/{case_id}/findings", response_model=list[FindingOut])
def list_findings(case_id: int, user: User = Depends(current_user), db: Session = Depends(db_session)):
    case = db.scalar(select(Case).where(Case.id == case_id, Case.user_id == user.id))
    if not case:
        raise HTTPException(404, "Case not found")
    invs = list(db.scalars(select(Investigation).where(Investigation.case_id == case.id)))
    ids = [x.id for x in invs]
    return list(db.scalars(select(Finding).where(Finding.investigation_id.in_(ids)))) if ids else []

@app.get("/api/cases/{case_id}/report")
def case_report(case_id: int, user: User = Depends(current_user), db: Session = Depends(db_session)):
    case = db.scalar(select(Case).where(Case.id == case_id, Case.user_id == user.id))
    if not case:
        raise HTTPException(404, "Case not found")
    evidence = list(db.scalars(select(Evidence).where(Evidence.case_id == case.id).order_by(Evidence.created_at)))
    investigations = list(db.scalars(select(Investigation).where(Investigation.case_id == case.id).order_by(Investigation.created_at.desc())))
    findings = [f for inv in investigations for f in db.scalars(select(Finding).where(Finding.investigation_id == inv.id)).all()]
    return {
        "report_version": "1.0",
        "case": {"id": case.id, "title": case.title, "type": case.case_type, "status": case.status, "description": case.description, "created_at": case.created_at, "updated_at": case.updated_at},
        "evidence": [{"id": x.id, "kind": x.kind, "label": x.label, "content": x.content, "created_at": x.created_at} for x in evidence],
        "investigations": [{"id": x.id, "status": x.status, "summary": x.summary, "created_at": x.created_at} for x in investigations],
        "findings": [{"id": x.id, "category": x.category, "title": x.title, "detail": x.detail, "confidence": x.confidence, "source": x.source} for x in findings],
    }
