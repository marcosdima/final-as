from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import (
    CareerResponse,
    EnrollmentPeriodResponse,
    ExamBoardsOverviewResponse,
    NoticeResponse,
    PeriodType,
    SubjectAttendanceResponse,
)
from app.security import AuthenticatedUser, get_current_user, require_roles
from app.services import academic

router = APIRouter(prefix="/academic", tags=["Academic Management (Institute)"])


@router.get(
    "/careers",
    response_model=List[CareerResponse],
    summary="List active careers with nested subjects",
)
async def list_careers(
    search: Optional[str] = Query(None, description="Filter by partial career name"),
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await academic.get_careers_with_subjects(db, search=search)


@router.get(
    "/notices",
    response_model=List[NoticeResponse],
    summary="List institutional notices visible to current role",
)
async def list_notices(
    limit: int = Query(10, ge=1, le=50),
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await academic.get_active_notices(db, current_user.db_role, limit=limit)


@router.get(
    "/enrollment-periods",
    response_model=List[EnrollmentPeriodResponse],
    summary="List enrollment periods for open academic cycles",
)
async def list_enrollment_periods(
    period_type: Optional[PeriodType] = Query(None, description="Filter by COURSE or EXAM"),
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await academic.get_enrollment_periods(db, period_type=period_type)


@router.get(
    "/exam-boards",
    response_model=ExamBoardsOverviewResponse,
    summary="List scheduled exam boards and EXAM enrollment periods",
)
async def list_exam_boards(
    subject: Optional[str] = Query(None, description="Filter by partial subject name"),
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await academic.get_exam_boards_overview(db, subject_name=subject)


@router.get(
    "/students/me/history",
    summary="Get authenticated student's academic history",
)
async def my_academic_history(
    current_user: AuthenticatedUser = Depends(require_roles("STUDENT")),
    db: AsyncSession = Depends(get_db),
):
    if current_user.student_id is None:
        raise HTTPException(status_code=404, detail="No student record is linked to this user.")
    return await academic.get_student_history(db, current_user.student_id)


@router.get(
    "/students/me/attendance",
    response_model=List[SubjectAttendanceResponse],
    summary="Get authenticated student's attendance percentage per subject",
)
async def my_attendance(
    current_user: AuthenticatedUser = Depends(require_roles("STUDENT")),
    db: AsyncSession = Depends(get_db),
):
    if current_user.student_id is None:
        raise HTTPException(status_code=404, detail="No student record is linked to this user.")
    return await academic.get_student_attendance(db, current_user.student_id)


@router.get(
    "/students/me/prerequisites",
    summary="Check prerequisites to enroll or take final exam for a subject",
)
async def my_prerequisites(
    subject: str = Query(..., min_length=2, description="Subject name to validate"),
    current_user: AuthenticatedUser = Depends(require_roles("STUDENT")),
    db: AsyncSession = Depends(get_db),
):
    if current_user.student_id is None:
        raise HTTPException(status_code=404, detail="No student record is linked to this user.")
    return await academic.check_student_prerequisites(db, current_user.student_id, subject)


@router.get(
    "/teachers/me/rosters",
    summary="Get assigned courses and enrolled student rosters for authenticated teacher",
)
async def my_course_rosters(
    subject: Optional[str] = Query(None, description="Filter by partial subject name"),
    current_user: AuthenticatedUser = Depends(require_roles("TEACHER")),
    db: AsyncSession = Depends(get_db),
):
    if current_user.teacher_id is None:
        raise HTTPException(status_code=404, detail="No teacher record is linked to this user.")
    return await academic.get_teacher_course_rosters(db, current_user.teacher_id, subject)


@router.get(
    "/teachers/me/exam-boards",
    summary="Get exam boards assigned to authenticated teacher",
)
async def my_exam_boards(
    current_user: AuthenticatedUser = Depends(require_roles("TEACHER")),
    db: AsyncSession = Depends(get_db),
):
    if current_user.teacher_id is None:
        raise HTTPException(status_code=404, detail="No teacher record is linked to this user.")
    return await academic.get_teacher_exam_boards(db, current_user.teacher_id)


@router.get(
    "/admin/students",
    summary="Look up a student's academic record (Preceptor / Admin only)",
)
async def admin_lookup_student(
    file_number: Optional[int] = Query(None, description="Student file number (legajo)"),
    dni: Optional[str] = Query(None, description="Student national ID (DNI)"),
    current_user: AuthenticatedUser = Depends(require_roles("PRECEPTOR", "ADMIN")),
    db: AsyncSession = Depends(get_db),
):
    if file_number is None and not (dni and dni.strip()):
        raise HTTPException(status_code=400, detail="Either file_number or dni must be provided.")
    data = await academic.get_student_admin_detail(db, file_number=file_number, dni=dni)
    if "error" in data:
        raise HTTPException(status_code=404, detail=data["error"])
    return data
