import enum
from pydantic import BaseModel, Field
from bson.objectid import ObjectId

from .db_object import DbObject


class SleepSampleItem(BaseModel):
    value: int
    startDate: str
    endDate: str
    source: str


class AccelerometerSampleItem(BaseModel):
    x: float
    y: float
    z: float
    timestamp: str


class SleepSampleValue(enum.Enum):
    inBed = 0
    asleepUnspecified = 1
    awake = 2
    asleepCore = 3
    asleepDeep = 4
    asleepREM = 5


class StepsSampleItem(BaseModel):
    value: SleepSampleValue
    startDate: str
    endDate: str


class DataFromIOS(BaseModel):
    # sleep_sample: list[SleepSampleItem] = Field(alias="StepsSample")
    StepsSample: list = Field(alias="StepsSample")
    accelerometer_sample: list = Field(alias="AccelerometerSample")
    steps_sample: list = Field(alias="StepsSample")


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


class SleepList(BaseModel):
    sleep_items: list[SleepDB]

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: lambda v: str(v)}
