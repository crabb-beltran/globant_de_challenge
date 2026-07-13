from pydantic import BaseModel, field_validator


class Jobs(BaseModel):
    id: int
    job: str

    @field_validator("id", mode="before")
    @classmethod
    def id_required(cls, value):
        if value is None or value == "":
            raise ValueError("id is required and cannot be empty")
        return value

    @field_validator("job", mode="before")
    @classmethod
    def job_required(cls, value):
        if value == "":
            raise ValueError("job name is required and cannot be empty")
        return value