from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import AuthenticatedUser, get_current_user, require_roles
from app.schemas.academic import (
    CareerResponse,
    EnrollmentPeriodResponse,
    ExamBoardsOverviewResponse,
    NoticeResponse,
    PeriodType,
    SubjectAttendanceResponse,
)
from app.services import academic

router = APIRouter(prefix="/academic", tags=["Academic Management (Institute)"])


@router.get(
    "/careers",
    response_model=list[CareerResponse],
    summary="List active careers with nested subjects",
)
async def list_careers(
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    search: Annotated[str | None, Query(description="Filter by partial career name")] = None,
):
    return await academic.get_careers_with_subjects(db, search=search)


@router.get(
    "/notices",
    response_model=list[NoticeResponse],
    summary="List institutional notices visible to current role",
)
async def list_notices(
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
):
    return await academic.get_active_notices(db, current_user.db_role, limit=limit)


@router.get(
    "/enrollment-periods",
    response_model=list[EnrollmentPeriodResponse],
    summary="List enrollment periods for open academic cycles",
)
async def list_enrollment_periods(
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    period_type: Annotated[PeriodType | None, Query(description="Filter by COURSE or EXAM")] = None,
):
    return await academic.get_enrollment_periods(db, period_type=period_type)


@router.get(
    "/exam-boards",
    response_model=ExamBoardsOverviewResponse,
    summary="List scheduled exam boards and EXAM enrollment periods",
)
async def list_exam_boards(
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    subject_id: Annotated[int | None, Query(ge=1, description="Filter by subject ID from `instituto.materia`")] = None,
    subject: Annotated[str | None, Query(description="Filter by partial subject name")] = None,
):
    try:
        return await academic.get_exam_boards_overview(
            db, subject_id=subject_id, subject_name=subject
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get(
    "/students/me/history",
    summary="Get authenticated student's academic history",
)
async def my_academic_history(
    current_user: Annotated[AuthenticatedUser, Depends(require_roles("STUDENT"))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    if current_user.student_id is None:
        raise HTTPException(status_code=404, detail="No student record is linked to this user.")
    return await academic.get_student_history(db, current_user.student_id)


@router.get(
    "/students/me/attendance",
    response_model=list[SubjectAttendanceResponse],
    summary="Get authenticated student's attendance percentage per subject",
)
async def my_attendance(
    current_user: Annotated[AuthenticatedUser, Depends(require_roles("STUDENT"))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    if current_user.student_id is None:
        raise HTTPException(status_code=404, detail="No student record is linked to this user.")
    return await academic.get_student_attendance(db, current_user.student_id)


@router.get(
    "/students/me/prerequisites",
    summary="Check prerequisites to enroll or take final exam for a subject",
)
async def my_prerequisites(
    current_user: Annotated[AuthenticatedUser, Depends(require_roles("STUDENT"))],
    db: Annotated[AsyncSession, Depends(get_db)],
    subject_id: Annotated[int | None, Query(ge=1, description="Subject ID from `instituto.materia`")] = None,
    subject: Annotated[str | None, Query(min_length=2, description="Subject name to validate")] = None,
):
    if current_user.student_id is None:
        raise HTTPException(status_code=404, detail="No student record is linked to this user.")
    if subject_id is None and not (subject and subject.strip()):
        raise HTTPException(status_code=400, detail="Either subject_id or subject must be provided.")
    try:
        return await academic.check_student_prerequisites(
            db, current_user.student_id, subject_name=subject, subject_id=subject_id
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get(
    "/teachers/me/rosters",
    summary="Get assigned courses and enrolled student rosters for authenticated teacher",
)
async def my_course_rosters(
    current_user: Annotated[AuthenticatedUser, Depends(require_roles("TEACHER"))],
    db: Annotated[AsyncSession, Depends(get_db)],
    subject_id: Annotated[int | None, Query(ge=1, description="Filter by subject ID from `instituto.materia`")] = None,
    subject: Annotated[str | None, Query(description="Filter by partial subject name")] = None,
):
    if current_user.teacher_id is None:
        raise HTTPException(status_code=404, detail="No teacher record is linked to this user.")
    try:
        return await academic.get_teacher_course_rosters(
            db, current_user.teacher_id, subject_id=subject_id, subject_name=subject
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get(
    "/teachers/me/exam-boards",
    summary="Get exam boards assigned to authenticated teacher",
)
async def my_exam_boards(
    current_user: Annotated[AuthenticatedUser, Depends(require_roles("TEACHER"))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    if current_user.teacher_id is None:
        raise HTTPException(status_code=404, detail="No teacher record is linked to this user.")
    return await academic.get_teacher_exam_boards(db, current_user.teacher_id)


@router.get(
    "/admin/students",
    summary="Look up a student's academic record (Preceptor / Admin only)",
)
async def admin_lookup_student(
    current_user: Annotated[AuthenticatedUser, Depends(require_roles("PRECEPTOR", "ADMIN"))],
    db: Annotated[AsyncSession, Depends(get_db)],
    file_number: Annotated[int | None, Query(description="Student file number (legajo)")] = None,
    dni: Annotated[str | None, Query(description="Student national ID (DNI)")] = None,
):
    if file_number is None and not (dni and dni.strip()):
        raise HTTPException(status_code=400, detail="Either file_number or dni must be provided.")
    data = await academic.get_student_admin_detail(db, file_number=file_number, dni=dni)
    if "error" in data:
        raise HTTPException(status_code=404, detail=data["error"])
    return data
