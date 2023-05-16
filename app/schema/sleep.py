import enum
from pydantic import BaseModel
from bson.objectid import ObjectId

from .db_object import DbObject


class RecordsType(str, enum.Enum):
    DiagnosticRecord = "diagnostics"
    SleepRecord = "sleep"
    AccelerometerRecord = "accelerometer"
    StepRecord = "step"
    PedometerRecord = "pedometer"


class DataBase(BaseModel):
    pass


class DiagnosticRecord(DataBase):
    date: str
    message: str
    data: dict


class SleepRecord(DataBase):
    value: int
    startDate: str
    endDate: str
    source: str


class AccelerometerRecord(DataBase):
    date: str
    x: float
    y: float
    z: float


class StepRecord(DataBase):
    date: str
    unknown: int
    stationary: int
    walking: int
    running: int
    automotive: int
    cycling: int


class PedometerRecord(DataBase):
    startDate: str
    endDate: str
    numberOfSteps: int
    distance: float
    floorsAscended: int
    floorsDescended: int
    currentPace: float
    currentCadence: float
    averageActivePace: float


class DataItem(BaseModel):
    data: DiagnosticRecord | SleepRecord | AccelerometerRecord | StepRecord | PedometerRecord
    type: RecordsType


class SleepBase(BaseModel):
    dataItems: list[DataItem]


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
