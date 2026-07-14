import re
from pydantic import BaseModel, ConfigDict, field_validator


ISO_DATETIME_PATTERN = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$"
)


class HiredEmployeeSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int
    name: str
    hire_datetime: str
    department_id: int
    job_id: int

    @field_validator("id", mode="before")
    @classmethod
    def id_required(cls, value):
        if value is None or value == "":
            raise ValueError("id is required and cannot be empty")
        return value

    @field_validator("id")
    @classmethod
    def id_must_be_positive(cls, value):
        if value <= 0:
            raise ValueError("id must be a positive integer")
        return value

    @field_validator("name", mode="before")
    @classmethod
    def name_required(cls, value):
        if value is None or (isinstance(value, str) and value.strip() == ""):
            raise ValueError("name is required and cannot be empty or whitespace-only")
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

    @field_validator("department_id")
    @classmethod
    def department_id_must_be_positive(cls, value):
        if value <= 0:
            raise ValueError("department_id must be a positive integer")
        return value

    @field_validator("job_id", mode="before")
    @classmethod
    def job_id_required(cls, value):
        if value is None or value == "":
            raise ValueError("job_id is required and cannot be empty")
        return value

    @field_validator("job_id")
    @classmethod
    def job_id_must_be_positive(cls, value):
        if value <= 0:
            raise ValueError("job_id must be a positive integer")
        return value