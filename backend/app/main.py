from collections import defaultdict
from contextlib import asynccontextmanager
from datetime import date

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import desc, func, select, tuple_
from sqlalchemy.orm import Session

from .database import Base, SessionLocal, engine, get_db
from .jobs import sync_runs_snapshot
from .models import Bet, LedgerEntry, RunUpdate, TrainRun, User
from .schemas import BetCreate, BetResponse, LeaderboardRow, RunBase, RunDetails

scheduler = AsyncIOScheduler()


def seed_users(db: Session) -> None:
    existing = db.scalars(select(User)).all()
    if existing:
        return
    db.add_all([User(username='alice'), User(username='bob'), User(username='charlie')])
    db.add_all(
        [
            LedgerEntry(user_id=1, amount=100, reason='Initial balance'),
            LedgerEntry(user_id=2, amount=100, reason='Initial balance'),
            LedgerEntry(user_id=3, amount=100, reason='Initial balance'),
        ]
    )
    db.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_users(db)
    finally:
        db.close()
    scheduler.add_job(sync_runs_snapshot, 'interval', minutes=2, id='sync_runs_snapshot', replace_existing=True)
    scheduler.start()
    await sync_runs_snapshot()
    yield
    scheduler.shutdown()


app = FastAPI(title='pkp-bet backend', lifespan=lifespan)


@app.get('/healthz')
def healthz():
    return {'ok': True}


@app.get('/runs/today', response_model=list[RunBase])
def runs_today(db: Session = Depends(get_db)):
    today = date.today()
    runs = db.scalars(select(TrainRun).where(TrainRun.service_date == today).order_by(TrainRun.train_number)).all()
    if not runs:
        return []

    run_ids = [r.id for r in runs]
    latest_updates = db.execute(
        select(RunUpdate.train_run_id, func.max(RunUpdate.fetched_at).label('max_fetched'))
        .where(RunUpdate.train_run_id.in_(run_ids))
        .group_by(RunUpdate.train_run_id)
    ).all()
    latest_map = {r.train_run_id: r.max_fetched for r in latest_updates}

    delays = defaultdict(float)
    if latest_map:
        rows = db.execute(
            select(RunUpdate).where(tuple_(RunUpdate.train_run_id, RunUpdate.fetched_at).in_([(k, v) for k, v in latest_map.items()]))
        ).scalars().all()
        for row in rows:
            delays[row.train_run_id] = row.delay_minutes

    return [
        RunBase(
            id=r.id,
            external_id=r.external_id,
            train_number=r.train_number,
            carrier=r.carrier,
            route_name=r.route_name,
            service_date=r.service_date,
            latest_delay_minutes=delays[r.id],
        )
        for r in runs
    ]


@app.get('/runs/{run_id}', response_model=RunDetails)
def run_details(run_id: int, db: Session = Depends(get_db)):
    run = db.get(TrainRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail='run not found')
    latest = db.scalar(select(RunUpdate).where(RunUpdate.train_run_id == run_id).order_by(desc(RunUpdate.fetched_at)).limit(1))
    return RunDetails(
        id=run.id,
        external_id=run.external_id,
        train_number=run.train_number,
        carrier=run.carrier,
        route_name=run.route_name,
        service_date=run.service_date,
        latest_delay_minutes=latest.delay_minutes if latest else 0,
        last_update_at=latest.fetched_at if latest else None,
    )


@app.post('/bets', response_model=BetResponse)
def create_bet(payload: BetCreate, db: Session = Depends(get_db)):
    if not db.get(User, payload.user_id):
        raise HTTPException(status_code=404, detail='user not found')
    if not db.get(TrainRun, payload.train_run_id):
        raise HTTPException(status_code=404, detail='run not found')

    bet = Bet(
        user_id=payload.user_id,
        train_run_id=payload.train_run_id,
        predicted_delay_minutes=payload.predicted_delay_minutes,
        stake=payload.stake,
    )
    db.add(bet)
    db.add(LedgerEntry(user_id=payload.user_id, amount=-payload.stake, reason=f'Bet #{payload.train_run_id}'))
    db.commit()
    db.refresh(bet)
    return BetResponse(
        id=bet.id,
        user_id=bet.user_id,
        train_run_id=bet.train_run_id,
        predicted_delay_minutes=bet.predicted_delay_minutes,
        stake=float(bet.stake),
    )


@app.get('/leaderboard', response_model=list[LeaderboardRow])
def leaderboard(db: Session = Depends(get_db)):
    rows = db.execute(
        select(User.id, User.username, func.coalesce(func.sum(LedgerEntry.amount), 0).label('balance'))
        .join(LedgerEntry, LedgerEntry.user_id == User.id, isouter=True)
        .group_by(User.id, User.username)
        .order_by(desc('balance'))
    ).all()
    return [LeaderboardRow(user_id=r.id, username=r.username, balance=float(r.balance)) for r in rows]
