from datetime import datetime
from sqlalchemy import func, extract

from database import db
from models import Transaction, UserProfile


# ---------------------------------------------------------------------------
# Perfil do usuário
# ---------------------------------------------------------------------------

def get_or_create_profile(phone: str) -> UserProfile:
    profile = UserProfile.query.filter_by(phone=phone).first()
    if not profile:
        profile = UserProfile(phone=phone)
        db.session.add(profile)
        db.session.commit()
    return profile


def set_monthly_goal(phone: str, goal: float) -> UserProfile:
    profile = get_or_create_profile(phone)
    profile.monthly_goal = goal
    profile.goal_alerted = False
    db.session.commit()
    return profile


# ---------------------------------------------------------------------------
# Transações
# ---------------------------------------------------------------------------

def add_transaction(phone: str, type_: str, amount: float,
                     category: str, description: str) -> Transaction:
    t = Transaction(
        phone=phone,
        type=type_,
        amount=amount,
        category=category,
        description=description,
    )
    db.session.add(t)
    db.session.commit()
    return t


# ---------------------------------------------------------------------------
# Consultas mensais
# ---------------------------------------------------------------------------

def _current_month_query(phone: str):
    now = datetime.utcnow()
    return Transaction.query.filter(
        Transaction.phone == phone,
        extract("year", Transaction.created_at) == now.year,
        extract("month", Transaction.created_at) == now.month,
    )


def get_monthly_totals(phone: str) -> dict:
    q = _current_month_query(phone)

    income = (
        q.filter(Transaction.type == "income")
        .with_entities(func.sum(Transaction.amount))
        .scalar() or 0.0
    )
    expense = (
        q.filter(Transaction.type == "expense")
        .with_entities(func.sum(Transaction.amount))
        .scalar() or 0.0
    )
    return {"income": income, "expense": expense, "balance": income - expense}


def get_categories(phone: str) -> list:
    """Retorna lista de (category, total) para gastos do mês."""
    q = _current_month_query(phone).filter(Transaction.type == "expense")
    rows = (
        q.with_entities(Transaction.category, func.sum(Transaction.amount))
        .group_by(Transaction.category)
        .all()
    )
    return [(row[0], row[1]) for row in rows]


def get_recent_transactions(phone: str, limit: int = 10) -> list:
    rows = (
        Transaction.query.filter_by(phone=phone)
        .order_by(Transaction.created_at.desc())
        .limit(limit)
        .all()
    )
    return [t.to_dict() for t in rows]


def get_all_transactions(phone: str) -> list:
    rows = (
        Transaction.query.filter_by(phone=phone)
        .order_by(Transaction.created_at.desc())
        .all()
    )
    return [t.to_dict() for t in rows]


def check_goal_alert(phone: str) -> bool:
    """Retorna True se o usuário ultrapassou a meta e ainda não foi alertado."""
    profile = get_or_create_profile(phone)
    if profile.monthly_goal <= 0 or profile.goal_alerted:
        return False

    totals = get_monthly_totals(phone)
    if totals["expense"] >= profile.monthly_goal:
        profile.goal_alerted = True
        db.session.commit()
        return True
    return False
