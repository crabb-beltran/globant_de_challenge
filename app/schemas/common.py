from pydantic import BaseModel


class RejectedRecordDetail(BaseModel):
    record: dict
    reason: str
    reason_code: str


class BatchIngestResponse(BaseModel):
    inserted: int
    rejected: int
    rejected_records: list[RejectedRecordDetail] = []
