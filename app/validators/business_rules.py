from validators.exceptions import ForeignKeyViolation


def department_exists(department_id: int, valid_department_ids: set[int]) -> None:
    if department_id not in valid_department_ids:
        raise ForeignKeyViolation(
            f"department_id {department_id} does not reference an existing department"
        )


def job_exists(job_id: int, valid_job_ids: set[int]) -> None:
    if job_id not in valid_job_ids:
        raise ForeignKeyViolation(f"job_id {job_id} does not reference an existing job")
