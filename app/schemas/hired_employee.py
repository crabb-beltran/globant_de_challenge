import re
from datetime import datetime as dt
from pydantic import BaseModel, field_validator


ISO_DATETIME_PATTERN = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$"
)


class HiredEmployeeSchema(BaseModel):
    id: int
    name: str
    hire_datetime: str
    department_id: int
    job_id: int

    @field_validator("name", mode="before")
    @classmethod
    def name_required(cls, value):
        if value is None or value == "":
            raise ValueError("name is required and cannot be empty")
        return value

    @field_validator("hire_datetime", mode="before")
    @classmethod
    def validate_iso_format(cls, value):
        if not isinstance(value, str) or not ISO_DATETIME_PATTERN.match(value):
            raise ValueError(
                "hire_datetime must be a valid ISO 8601 datetime "
                "with UTC 'Z' suffix (e.g. 2021-07-27T16:02:08Z)"
            )
        return value

    @field_validator("department_id", mode="before")
    @classmethod
    def department_id_required(cls, value):
        if value is None or value == "":
            raise ValueError("department_id is required and cannot be empty")
        return value

    @field_validator("job_id", mode="before")
    @classmethod
    def job_id_required(cls, value):
        if value is None or value == "":
            raise ValueError("job_id is required and cannot be empty")
        return value

