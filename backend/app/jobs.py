import json
from datetime import date, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import SessionLocal
from .models import RunUpdate, TrainRun
from .plk_client import PLKClient


async def sync_runs_snapshot() -> None:
    client = PLKClient()
    operations = await client.fetch_ic_operations()
    if not operations:
        return

    db: Session = SessionLocal()
    try:
        fetched_at = datetime.utcnow()
        for item in operations:
            external_id = str(item.get('id') or item.get('runId') or item.get('trainId') or '')
            if not external_id:
                continue

            train_number = str(item.get('trainNumber') or item.get('number') or 'unknown')
            carrier = str(item.get('carrier') or 'IC')
            route_name = item.get('name') or item.get('routeName')

            service_date_raw = item.get('operationDate') or item.get('serviceDate')
            try:
                service_date = date.fromisoformat(str(service_date_raw)[:10]) if service_date_raw else fetched_at.date()
            except ValueError:
                service_date = fetched_at.date()

            delay = float(item.get('delayMinutes') or item.get('delay') or 0)

            run = db.scalar(select(TrainRun).where(TrainRun.external_id == external_id))
            if not run:
                run = TrainRun(
                    external_id=external_id,
                    train_number=train_number,
                    carrier=carrier,
                    route_name=route_name,
                    service_date=service_date,
                )
                db.add(run)
                db.flush()

            update = RunUpdate(
                train_run_id=run.id,
                fetched_at=fetched_at,
                delay_minutes=delay,
                payload=json.dumps(item),
            )
            db.add(update)

        db.commit()
    finally:
        db.close()
