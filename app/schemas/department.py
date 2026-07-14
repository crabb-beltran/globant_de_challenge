from pydantic import BaseModel, ConfigDict, field_validator


class Departments(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int
    department: str

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

    @field_validator("department", mode="before")
    @classmethod
    def department_required(cls, value):
        if value is None or (isinstance(value, str) and value.strip() == ""):
            raise ValueError(
                "department name is required and cannot be empty or whitespace-only"
            )
        return value
