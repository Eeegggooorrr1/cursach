from pydantic import BaseModel, ConfigDict


class StrictSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")


class OrmSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")
