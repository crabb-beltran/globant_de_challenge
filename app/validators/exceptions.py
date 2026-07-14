class BusinessRuleViolation(ValueError):
    """Base for validation failures with a structured reason code,
    distinguishing WHY a record was rejected (for reporting/alerting)
    from the human-readable message (for debugging)."""

    code: str = "VALIDATION_ERROR"


class ForeignKeyViolation(BusinessRuleViolation):
    code = "FK_VIOLATION"


class DuplicateRecordError(BusinessRuleViolation):
    code = "DUPLICATE_ID"


class ConstraintViolation(BusinessRuleViolation):
    code = "DB_CONSTRAINT_VIOLATION"
