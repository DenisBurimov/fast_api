from typing import Union
from pydantic import BaseModel
from bson.objectid import ObjectId

from .db_object import DbObject


class BurnBase(BaseModel):
    # burn_data: dict[str, Union[str, list, dict]]
    sessionInfo: str
    timeStamps: dict[str, Union[str, int, float]]
    deviceInfo: dict[str, Union[str, int, float]]
    leftPupilInfo: list[dict]
    rightPupilInfo: list[dict]
    leftBlinkInfo: dict[str, Union[list, int]]
    rightBlinkInfo: dict[str, Union[list, int]]

    class Config:
        schema_extra = {
            "example": {
                "sessionInfo": "0B872D59-1E80-4A7F-9743-41A7D56DA73C",
                "timeStamps": {
                    "beginTimeZone": "Friday, 27 January 2023 at 10:22:06 Central European Standard Time",
                    "beginTime": 0,
                    "endTime": 30.353888988494873,
                },
                "deviceInfo": {
                    "deviceName": "iPhone",
                    "iosVersion": "16.2",
                    "UUID": "4BAACF6E-91FC-4A93-A383-C9398E80F42C",
                },
                "leftPupilInfo": [
                    {
                        "droopInfo": 0.06788557767868042,
                        "timePoint": 0.062120914459228516,
                        "pupilX": 0.012180243618786335,
                        "pupilY": -0.07051916420459747,
                    },
                    {
                        "droopInfo": 0.06792465597391129,
                        "timePoint": 0.08002281188964844,
                        "pupilX": 0.012866710312664509,
                        "pupilY": -0.07073412090539932,
                    },
                ],
                "rightPupilInfo": [
                    {
                        "droopInfo": 0.06788531690835953,
                        "timePoint": 0.06208181381225586,
                        "pupilX": 0.08784681558609009,
                        "pupilY": -0.06998830288648605,
                    },
                    {
                        "droopInfo": 0.06792449951171875,
                        "timePoint": 0.08002185821533203,
                        "pupilX": 0.08852659165859222,
                        "pupilY": -0.0701945573091507,
                    },
                ],
                "leftBlinkInfo": {
                    "blinkTotalDurations": [148, 112],
                    "blinkReopeningDurations": [99, 67],
                    "blinkStartTimes": [0.8153500556945801, 5.517504930496216],
                    "blinkFreq": 2.351508776603492,
                    "blinkEndTimes": [0.9644169807434082, 5.631086826324463],
                    "blinkClosingDurations": [49, 45],
                    "totalBlinks": 2,
                },
                "rightBlinkInfo": {
                    "blinkTotalDurations": [148, 112],
                    "blinkReopeningDurations": [99, 67],
                    "blinkStartTimes": [0.8153479099273682, 5.517493724822998],
                    "blinkFreq": 2.3515091501382703,
                    "blinkEndTimes": [0.9643518924713135, 5.631079912185669],
                    "blinkClosingDurations": [49, 45],
                    "totalBlinks": 2,
                },
            }
        }


class BurnDB(DbObject, BurnBase):
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: lambda v: str(v)}


class BurnList(BaseModel):
    burn_items: list[BurnDB]

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: lambda v: str(v)}


class BurnResultBody(BaseModel):
    burn_rating: int
    gaze_error: int
    reaction_time: int
    eye_droop: int


class BurnResult(BaseModel):
    statusCode: int
    headers: dict
    body: str


class BurnResultDB(BaseModel):
    burn_values: list[int]
    created_at: str


class BurnTimestamps(BaseModel):
    beginTimeZone: str
    beginTime: str
    endTime: str
