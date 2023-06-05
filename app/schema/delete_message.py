from pydantic import BaseModel


class DeleteMessage(BaseModel):
    message: str
