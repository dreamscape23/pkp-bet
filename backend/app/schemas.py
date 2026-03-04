from datetime import datetime, date

from pydantic import BaseModel, Field


class RunBase(BaseModel):
    id: int
    external_id: str
    train_number: str
    carrier: str
    route_name: str | None
    service_date: date
    latest_delay_minutes: float


class RunDetails(RunBase):
    last_update_at: datetime | None


class BetCreate(BaseModel):
    user_id: int = Field(ge=1)
    train_run_id: int = Field(ge=1)
    predicted_delay_minutes: int = Field(ge=0, le=600)
    stake: float = Field(gt=0)


class BetResponse(BaseModel):
    id: int
    user_id: int
    train_run_id: int
    predicted_delay_minutes: int
    stake: float


class LeaderboardRow(BaseModel):
    user_id: int
    username: str
    balance: float
