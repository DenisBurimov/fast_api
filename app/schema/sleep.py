import enum
from pydantic import BaseModel
from bson.objectid import ObjectId

from .db_object import DbObject


class RecordsType(enum.Enum):
    DiagnosticRecord = "diagnostics"
    SleepRecord = "sleep"
    AccelerometerRecord = "accelerometer"
    StepRecord = "step"
    PedometerRecord = "pedometer"


class SleepData(BaseModel):
    data: dict
    type: RecordsType


class SleepBase(BaseModel):
    sleep_data: SleepData


class SleepCreate(SleepBase):
    pass


class SleepUpdate(BaseModel):
    pass


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
