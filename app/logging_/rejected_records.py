"""
Structured logging for records rejected during ingestion (historical CSV
load or, later, the REST API — see ADR-004: CloudWatch Logs).

For local development, this writes structured JSON lines to stdout, which
Docker Compose already captures (`docker-compose logs api`). In the AWS
Lambda deployment (Phase 12), the same log stream is automatically
forwarded to CloudWatch Logs by the Lambda runtime — no code change needed,
only the execution environment differs.
"""

import json
import logging
import sys

logger = logging.getLogger("rejected_records")
logger.setLevel(logging.WARNING)

if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)


def log_rejected_record(row, error: str, source: str = "historical_loader") -> None:
    """
    Logs a single rejected record as a structured JSON line.

    source: origin of the rejection — "historical_loader" (CSV batch),
            "reference_data_loader" (departments/jobs CSV), or
            "rest_api" (Phase 6 ingestion endpoints). Kept as a parameter
            (not hardcoded) so callers stay attributable in CloudWatch.
    """
    entry = {
        "event": "record_rejected",
        "source": source,
        "raw_row": row,
        "reason": error,
    }
    logger.warning(json.dumps(entry))