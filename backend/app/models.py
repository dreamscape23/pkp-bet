from datetime import datetime, date

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Station(Base):
    __tablename__ = 'stations'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    station_code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)


class TrainRun(Base):
    __tablename__ = 'train_runs'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    external_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    train_number: Mapped[str] = mapped_column(String(32), index=True)
    carrier: Mapped[str] = mapped_column(String(16), index=True)
    route_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    service_date: Mapped[date] = mapped_column(Date, index=True)

    updates: Mapped[list['RunUpdate']] = relationship(back_populates='train_run')


class RunUpdate(Base):
    __tablename__ = 'run_updates'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    train_run_id: Mapped[int] = mapped_column(ForeignKey('train_runs.id'), index=True)
    fetched_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    delay_minutes: Mapped[float] = mapped_column(Float, default=0)
    payload: Mapped[str] = mapped_column(Text)

    train_run: Mapped['TrainRun'] = relationship(back_populates='updates')


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)


class Bet(Base):
    __tablename__ = 'bets'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    train_run_id: Mapped[int] = mapped_column(ForeignKey('train_runs.id'), index=True)
    predicted_delay_minutes: Mapped[int] = mapped_column(Integer)
    stake: Mapped[float] = mapped_column(Numeric(10, 2))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)


class LedgerEntry(Base):
    __tablename__ = 'ledger'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    amount: Mapped[float] = mapped_column(Numeric(10, 2))
    reason: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
