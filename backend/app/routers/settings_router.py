from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.core.security import get_current_user, require_admin

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("/escalation-rules")
def list_rules(db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    return db.query(models.EscalationRule).all()


@router.post("/escalation-rules")
def create_rule(payload: schemas.EscalationRuleCreate, db: Session = Depends(get_db),
                 _: models.User = Depends(require_admin)):
    rule = models.EscalationRule(**payload.model_dump())
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


@router.delete("/escalation-rules/{rule_id}")
def delete_rule(rule_id: str, db: Session = Depends(get_db), _: models.User = Depends(require_admin)):
    rule = db.query(models.EscalationRule).filter(models.EscalationRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    db.delete(rule)
    db.commit()
    return {"ok": True}


@router.get("/app")
def get_app_settings(db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    rows = db.query(models.AppSettings).all()
    return {r.key: r.value for r in rows}


@router.put("/app/{key}")
def set_app_setting(key: str, value: dict, db: Session = Depends(get_db),
                     _: models.User = Depends(require_admin)):
    row = db.query(models.AppSettings).filter(models.AppSettings.key == key).first()
    if not row:
        row = models.AppSettings(key=key, value=value)
        db.add(row)
    else:
        row.value = value
    db.commit()
    return {"ok": True}
