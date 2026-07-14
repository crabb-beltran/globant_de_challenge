from pydantic import BaseModel, ConfigDict, field_validator


class Jobs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int
    job: str

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

    @field_validator("job", mode="before")
    @classmethod
    def job_required(cls, value):
        if value is None or (isinstance(value, str) and value.strip() == ""):
            raise ValueError(
                "job name is required and cannot be empty or whitespace-only"
            )
        return value
