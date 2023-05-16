import enum
from typing import Union
from pydantic import BaseModel
from bson.objectid import ObjectId

from .db_object import DbObject


class RecordsType(str, enum.Enum):
    DiagnosticRecord = "diagnostics"
    SleepRecord = "sleep"
    AccelerometerRecord = "accelerometer"
    StepRecord = "step"
    PedometerRecord = "pedometer"


class DiagnosticRecord(BaseModel):
    date: str
    message: str
    data: dict


class SleepRecord(BaseModel):
    value: int
    startDate: str
    endDate: str
    source: str


class AccelerometerRecord(BaseModel):
    date: str
    x: float
    y: float
    z: float


class StepRecord(BaseModel):
    date: str
    unknown: int
    stationary: int
    walking: int
    running: int
    automotive: int
    cycling: int


class PedometerRecord(BaseModel):
    startDate: str
    endDate: str
    numberOfSteps: int
    distance: float
    floorsAscended: int
    floorsDescended: int
    currentPace: float
    currentCadence: float
    averageActivePace: float


class SleepData(BaseModel):
    data: dict[str, Union[str, dict, int]]
    type: RecordsType


class SleepBase(BaseModel):
    sleep_data: list[SleepData]


class SleepDB(DbObject, SleepBase):
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: lambda v: str(v)}


class SleepList(BaseModel):
    sleep_items: list[SleepDB]

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: lambda v: str(v)}
