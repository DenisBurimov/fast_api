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

    class Config:
        schema_extra = {
            "example": {
                "dataItems": [
                    {
                        "data": {
                            "date": "2023-01-31 03:00:00+00:00",
                            "message": "Diagnostics message",
                            "data": {},
                        },
                        "type": "diagnostics",
                    },
                    {
                        "data": {
                            "value": 0,
                            "startDate": "2023-01-31 03:00:00+00:00",
                            "endDate": "2023-01-31 13:00:00+00:00",
                            "source": "Apple Watch",
                        },
                        "type": "sleep",
                    },
                    {
                        "data": {
                            "date": "2023-01-31 03:00:00+00:00",
                            "x": -0.019287109375,
                            "y": -0.0205078125,
                            "z": -0.996826171875,
                        },
                        "type": "accelerometer",
                    },
                    {
                        "data": {
                            "date": "2023-01-31 03:00:00+00:00",
                            "unknown": 0,
                            "stationary": 0,
                            "walking": 1,
                            "running": 0,
                            "automotive": 0,
                            "cycling": 0,
                        },
                        "type": "step",
                    },
                    {
                        "data": {
                            "startDate": "2023-01-31 03:00:00+00:00",
                            "endDate": "2023-01-31 04:00:00+00:00",
                            "numberOfSteps": 6500,
                            "distance": 10.5,
                            "floorsAscended": 20,
                            "floorsDescended": 20,
                            "currentPace": 0.5,
                            "currentCadence": 1.5,
                            "averageActivePace": 0.8,
                        },
                        "type": "pedometer",
                    },
                ]
            }
        }


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
