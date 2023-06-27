import enum
from datetime import datetime
from pydantic import BaseModel  # , Field
from bson.objectid import ObjectId

from .db_object import DbObject


class SleepSampleValue(enum.Enum):
    inBed = 0
    asleepUnspecified = 1
    awake = 2
    asleepCore = 3
    asleepDeep = 4
    asleepREM = 5


class SleepSampleItem(BaseModel):
    value: SleepSampleValue
    startDate: str
    endDate: str
    source: str


class AccelerometerSampleItem(BaseModel):
    x: float
    y: float
    z: float
    timestamp: str


class StepsSampleItem(BaseModel):
    value: int
    startDate: str
    endDate: str


class DataFromIOS(BaseModel):
    # sleep_sample: list[SleepSampleItem] = Field(alias="StepsSample")
    StepsSample: list[SleepSampleItem]
    AccelerometerSample: list[AccelerometerSampleItem]
    StepsSample: list[StepsSampleItem]


class SleepBody(BaseModel):
    dataFromIOS: DataFromIOS
    dataFromDatabase: dict


class SleepBase(BaseModel):
    body: SleepBody

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        schema_extra = {
            "example": {
                "body": {
                    "dataFromIOS": {
                        "SleepSample": [
                            {
                                "value": 6,
                                "startDate": "2023-06-12T11:11:11-04:00",
                                "endDate": "2023-06-12T11:11:11-04:00",
                                "source": "str",
                            },
                            {
                                "value": 1,
                                "startDate": "2023-06-13T12:41:15-04:00",
                                "endDate": "2023-06-13T12:41:15-04:00",
                                "source": "WHOOP",
                            },
                        ],
                        "AccelerometerSample": [
                            {
                                "x": 0.1,
                                "y": 0.2,
                                "z": 0.3,
                                "timestamp": "2023-06-13T12:41:15-04:00",
                            },
                            {
                                "x": -0.019287109375,
                                "y": -0.0205078125,
                                "z": -0.996826171875,
                                "timestamp": "2023-06-14T12:12:12-04:00",
                            },
                        ],
                        "StepsSample": [
                            {
                                "value": 5,
                                "startDate": "2023-06-15T10:10:10-04:00",
                                "endDate": "2023-06-15T12:12:12-04:00",
                            },
                            {
                                "value": 18,
                                "startDate": "2023-06-13T12:41:15-04:00",
                                "endDate": "2023-06-13T12:41:15-04:00",
                            },
                        ],
                    },
                    "dataFromDatabase": {},
                }
            }
        }


class SleepDB(DbObject, SleepBase):
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: lambda v: str(v)}


"""
{"_id":{"$oid":"640a17f89d770e182aced59a"},
"sleepLastNight": int, // sleep duration
"sleepTimeline": [{"start": str, "end": str},
                    {"start": str, "end": str},
                    {"start": str, "end": str},
                    {"start": str, "end": str}]
"focusTimeline": [{"start": str, "end": str, "level": 0},
                    {"start": str, "end": str, "level": 1},
                    {"start": str, "end": str, "level": 2},
                    {"start": str, "end": str, "level": 1},
                    {"start": str, "end": str, "level": 2},
                    {"start": str, "end": str, "level": 1},
                    {"start": str, "end": str, "level": 2}]
"createdAt":{"$date":{"$numberLong":"1678383096251"}},
"__v":{"$numberInt":"0"}}
"""


class SleepTimeLineItem(BaseModel):
    start: str
    end: str


class FocusTimeLineItem(BaseModel):
    start: str
    end: str
    level: int


class SleepResult(BaseModel):
    user_id: str | None
    sleepLastNight: int
    sleepTimeline: list[SleepTimeLineItem]
    focusTimeline: list[FocusTimeLineItem]
    createdAt: str | None = datetime.now().isoformat()
    v: int | None = 0


class SleepList(BaseModel):
    sleep_items: list[SleepResult]

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: lambda v: str(v)}
