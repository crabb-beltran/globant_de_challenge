from pydantic import BaseModel, field_validator


class Departments(BaseModel):
    id: int
    department: str

    @field_validator("id", mode="before")
    @classmethod
    def id_required(cls, value):
        if value is None or value == "":
            raise ValueError("id is required and cannot be empty")
        return value

    @field_validator("department", mode="before")
    @classmethod
    def department_required(cls, value):
        if value == "":
            raise ValueError("department name is required and cannot be empty")
        return value