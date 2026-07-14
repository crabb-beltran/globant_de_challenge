from pydantic import BaseModel


class QuarterlyHiring(BaseModel):
    department: str
    job: str
    q1: int
    q2: int
    q3: int
    q4: int


class DepartmentAboveAverage(BaseModel):
    id: int
    department: str
    hired: int


class HiringDistributionSummary(BaseModel):
    mean_hired: float
    median_hired: float
    stdev_hired: float | None
    coefficient_of_variation: float | None


class DepartmentZScore(BaseModel):
    id: int
    department: str
    hired: int
    z_score: float | None


class HiringDistributionStats(BaseModel):
    summary: HiringDistributionSummary
    departments: list[DepartmentZScore]
