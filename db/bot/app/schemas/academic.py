from typing import Literal

from pydantic import BaseModel, Field

PeriodType = Literal["COURSE", "EXAM"]


class SubjectItemResponse(BaseModel):
    id: int
    name: str
    year_in_plan: int
    workload_hours: int


class CareerResponse(BaseModel):
    id: int
    name: str
    awarded_title: str
    active: bool
    plan_year: int | None = None
    resolution: str | None = None
    subjects: list[SubjectItemResponse] = Field(default_factory=list)


class NoticeResponse(BaseModel):
    id: int
    title: str
    body: str
    published_at: str
    target_role: str


class EnrollmentPeriodResponse(BaseModel):
    id: int
    academic_year: int
    period_type: PeriodType
    start_date: str
    end_date: str


class ExamBoardItemResponse(BaseModel):
    id: int
    career: str
    subject: str
    academic_year: int
    exam_date: str
    exam_time: str
    chair_teacher: str
    observer_teacher: str | None = None
    record_number: int | None = None
    record_status: str | None = None


class ExamBoardsOverviewResponse(BaseModel):
    exam_enrollment_periods: list[EnrollmentPeriodResponse]
    exam_boards: list[ExamBoardItemResponse]


class SubjectAttendanceResponse(BaseModel):
    subject: str
    academic_year: int
    condition: str
    total_classes: int
    attended_classes: int
    attendance_percentage: float
