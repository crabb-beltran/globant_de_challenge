from datetime import datetime as dt
from sqlalchemy import ForeignKey, Integer, String, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column
from db.base import Base


class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    department: Mapped[str] = mapped_column(String(255), nullable=False)


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    job: Mapped[str] = mapped_column(String(255), nullable=False)


class HiredEmployee(Base):
    __tablename__ = "hired_employees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    hire_datetime: Mapped[dt] = mapped_column("datetime", TIMESTAMP(timezone=True), nullable=False, index=True)
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id", ondelete="RESTRICT"), nullable=False, index=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id", ondelete="RESTRICT"), nullable=False, index=True)