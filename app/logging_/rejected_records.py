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


def log_rejected_record(row: list[str], error: str) -> None:
    """
    Logs a single rejected record as a structured JSON line.

    Args:
        row: the raw CSV row (list of strings), unmodified — preserves
             exactly what was rejected, for auditability.
        error: the validation error message (from Pydantic or business_rules).
    """
    entry = {
        "event": "record_rejected",
        "source": "historical_loader",
        "raw_row": row,
        "reason": error,
    }
    logger.warning(json.dumps(entry))