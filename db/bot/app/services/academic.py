from typing import Any, Dict, List, Optional

from sqlalchemy import case, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.institute_models import (
    AcademicCycle,
    Attendance,
    Career,
    CareerEnrollment,
    CourseEnrollment,
    EnrollmentPeriod,
    ExamBoard,
    ExamEnrollment,
    ExamRecord,
    Notice,
    PartialGrade,
    Prerequisite,
    Student,
    StudyPlan,
    Subject,
    SubjectAssignment,
    Teacher,
)
from app.security import ROLE_FROM_DB

PERIOD_TYPE_FROM_DB = {"CURSADA": "COURSE", "EXAMEN": "EXAM"}
PERIOD_TYPE_TO_DB = {v: k for k, v in PERIOD_TYPE_FROM_DB.items()}

COURSE_CONDITION_FROM_DB = {
    "CURSANDO": "IN_PROGRESS",
    "REGULAR": "REGULAR",
    "PROMOCIONADO": "PROMOTED",
    "LIBRE": "FAILED_ATTENDANCE",
}
RECORD_STATUS_FROM_DB = {"ABIERTA": "OPEN", "CERRADA": "CLOSED"}
PREREQ_TYPE_FROM_DB = {"PARA_CURSAR": "TO_ENROLL", "PARA_RENDIR": "TO_TAKE_EXAM"}
BOARD_ROLE_FROM_DB = {"TITULAR": "CHAIR", "OBSERVADOR": "OBSERVER"}


async def get_careers_with_subjects(
    db: AsyncSession,
    search: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Return active careers with their current study plan metadata and a nested list of subjects.
    """
    career_stmt = select(Career).where(Career.active == True).order_by(Career.name)
    if search:
        career_stmt = career_stmt.where(Career.name.ilike(f"%{search.strip()}%"))

    careers = (await db.execute(career_stmt)).scalars().all()
    if not careers:
        return []

    career_ids = [c.id for c in careers]
    plans_stmt = (
        select(StudyPlan)
        .where(StudyPlan.career_id.in_(career_ids), StudyPlan.active == True)
        .order_by(StudyPlan.year.desc())
    )
    plans = (await db.execute(plans_stmt)).scalars().all()
    active_plan_by_career: Dict[int, StudyPlan] = {}
    for plan in plans:
        active_plan_by_career.setdefault(plan.career_id, plan)

    plan_ids = [p.id for p in active_plan_by_career.values()]
    subjects_by_plan: Dict[int, List[Dict[str, Any]]] = {}
    if plan_ids:
        subj_stmt = (
            select(Subject)
            .where(Subject.study_plan_id.in_(plan_ids))
            .order_by(Subject.year_in_plan, Subject.name)
        )
        for subj in (await db.execute(subj_stmt)).scalars().all():
            subjects_by_plan.setdefault(subj.study_plan_id, []).append({
                "id": subj.id,
                "name": subj.name,
                "year_in_plan": subj.year_in_plan,
                "workload_hours": subj.workload_hours,
            })

    result = []
    for career in careers:
        plan = active_plan_by_career.get(career.id)
        result.append({
            "id": career.id,
            "name": career.name,
            "awarded_title": career.awarded_title,
            "active": career.active,
            "plan_year": plan.year if plan else None,
            "resolution": plan.resolution if plan else None,
            "subjects": subjects_by_plan.get(plan.id, []) if plan else [],
        })
    return result


async def get_active_notices(
    db: AsyncSession,
    db_role: str,
    limit: int = 10,
) -> List[Dict[str, Any]]:
    """Return institution-wide notices or notices targeted to the user's role."""
    stmt = (
        select(Notice)
        .where(or_(Notice.target_role.is_(None), Notice.target_role == db_role))
        .order_by(Notice.published_at.desc())
        .limit(limit)
    )
    notices = (await db.execute(stmt)).scalars().all()
    return [
        {
            "id": n.id,
            "title": n.title,
            "body": n.body,
            "published_at": n.published_at.isoformat(),
            "target_role": ROLE_FROM_DB.get(n.target_role, "ALL_COMMUNITY") if n.target_role else "ALL_COMMUNITY",
        }
        for n in notices
    ]


async def get_enrollment_periods(
    db: AsyncSession,
    period_type: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Return enrollment periods for open academic cycles, optionally filtered by COURSE or EXAM."""
    stmt = (
        select(
            EnrollmentPeriod.id,
            AcademicCycle.year.label("academic_year"),
            EnrollmentPeriod.period_type,
            EnrollmentPeriod.start_date,
            EnrollmentPeriod.end_date,
        )
        .join(AcademicCycle, EnrollmentPeriod.academic_cycle_id == AcademicCycle.id)
        .where(AcademicCycle.status == "ABIERTO")
        .order_by(EnrollmentPeriod.start_date)
    )
    if period_type:
        db_period_type = PERIOD_TYPE_TO_DB.get(period_type, period_type)
        stmt = stmt.where(EnrollmentPeriod.period_type == db_period_type)

    rows = (await db.execute(stmt)).mappings().all()
    return [
        {
            "id": r["id"],
            "academic_year": r["academic_year"],
            "period_type": PERIOD_TYPE_FROM_DB.get(r["period_type"], r["period_type"]),
            "start_date": r["start_date"].isoformat(),
            "end_date": r["end_date"].isoformat(),
        }
        for r in rows
    ]


async def get_exam_boards_overview(
    db: AsyncSession,
    subject_name: Optional[str] = None,
) -> Dict[str, Any]:
    """Return ONLY EXAM enrollment periods in open cycles together with scheduled exam boards."""
    exam_periods = await get_enrollment_periods(db, period_type="EXAM")

    ChairTeacher = aliased(Teacher)
    ObserverTeacher = aliased(Teacher)
    boards_stmt = (
        select(
            ExamBoard.id,
            Career.name.label("career"),
            Subject.name.label("subject"),
            AcademicCycle.year.label("academic_year"),
            ExamBoard.exam_date,
            ExamBoard.exam_time,
            ChairTeacher.full_name.label("chair_teacher"),
            ObserverTeacher.full_name.label("observer_teacher"),
            ExamRecord.record_number,
            ExamRecord.status.label("record_status"),
        )
        .join(Subject, ExamBoard.subject_id == Subject.id)
        .join(StudyPlan, Subject.study_plan_id == StudyPlan.id)
        .join(Career, StudyPlan.career_id == Career.id)
        .join(AcademicCycle, ExamBoard.academic_cycle_id == AcademicCycle.id)
        .join(ChairTeacher, ExamBoard.chair_teacher_id == ChairTeacher.id)
        .outerjoin(ObserverTeacher, ExamBoard.observer_teacher_id == ObserverTeacher.id)
        .outerjoin(ExamRecord, ExamRecord.exam_board_id == ExamBoard.id)
        .order_by(ExamBoard.exam_date.desc(), ExamBoard.exam_time)
    )
    if subject_name:
        boards_stmt = boards_stmt.where(Subject.name.ilike(f"%{subject_name.strip()}%"))

    boards = [
        {
            "id": r["id"],
            "career": r["career"],
            "subject": r["subject"],
            "academic_year": r["academic_year"],
            "exam_date": r["exam_date"].isoformat(),
            "exam_time": r["exam_time"].isoformat(),
            "chair_teacher": r["chair_teacher"],
            "observer_teacher": r["observer_teacher"],
            "record_number": r["record_number"],
            "record_status": RECORD_STATUS_FROM_DB.get(r["record_status"], r["record_status"])
            if r["record_status"]
            else None,
        }
        for r in (await db.execute(boards_stmt)).mappings().all()
    ]

    return {
        "exam_enrollment_periods": exam_periods,
        "exam_boards": boards,
    }


async def get_student_history(
    db: AsyncSession,
    student_id: int,
) -> Dict[str, Any]:
    """Consolidated academic history for a student (RF-038)."""
    student = (await db.execute(select(Student).where(Student.id == student_id))).scalar_one_or_none()
    if not student:
        return {"error": "Student record not found."}

    careers_stmt = (
        select(Career.name, CareerEnrollment.status, CareerEnrollment.enrolled_date)
        .join(Career, CareerEnrollment.career_id == Career.id)
        .where(CareerEnrollment.student_id == student_id)
    )
    careers = [
        {
            "career": r["name"],
            "status": "ACTIVE" if r["status"] == "ACTIVA" else "DROPPED",
            "enrolled_date": r["enrolled_date"].isoformat(),
        }
        for r in (await db.execute(careers_stmt)).mappings().all()
    ]

    enrollments_stmt = (
        select(
            CourseEnrollment.id.label("enrollment_id"),
            Subject.name.label("subject"),
            Subject.year_in_plan,
            AcademicCycle.year.label("academic_year"),
            CourseEnrollment.condition,
            CourseEnrollment.late_enrollment,
        )
        .join(Subject, CourseEnrollment.subject_id == Subject.id)
        .join(AcademicCycle, CourseEnrollment.academic_cycle_id == AcademicCycle.id)
        .where(CourseEnrollment.student_id == student_id)
        .order_by(AcademicCycle.year.desc(), Subject.year_in_plan, Subject.name)
    )
    enrollment_rows = (await db.execute(enrollments_stmt)).mappings().all()

    grades_stmt = (
        select(
            PartialGrade.course_enrollment_id,
            PartialGrade.instance,
            PartialGrade.instance_number,
            PartialGrade.grade,
        )
        .join(CourseEnrollment, PartialGrade.course_enrollment_id == CourseEnrollment.id)
        .where(CourseEnrollment.student_id == student_id)
        .order_by(PartialGrade.instance, PartialGrade.instance_number)
    )
    grades_map: Dict[int, List[Dict[str, Any]]] = {}
    for g in (await db.execute(grades_stmt)).mappings().all():
        grades_map.setdefault(g["course_enrollment_id"], []).append({
            "instance": "MIDTERM" if g["instance"] == "PARCIAL" else "PRACTICAL_WORK",
            "number": g["instance_number"],
            "grade": float(g["grade"]),
        })

    enrollments = [
        {
            "subject": r["subject"],
            "year_in_plan": r["year_in_plan"],
            "academic_year": r["academic_year"],
            "condition": COURSE_CONDITION_FROM_DB.get(r["condition"], r["condition"]),
            "late_enrollment": r["late_enrollment"],
            "partial_grades": grades_map.get(r["enrollment_id"], []),
        }
        for r in enrollment_rows
    ]

    finals_stmt = (
        select(
            Subject.name.label("subject"),
            ExamBoard.exam_date,
            ExamEnrollment.final_grade,
            ExamEnrollment.status,
            ExamRecord.record_number,
            ExamRecord.status.label("record_status"),
        )
        .join(ExamBoard, ExamEnrollment.exam_board_id == ExamBoard.id)
        .join(Subject, ExamBoard.subject_id == Subject.id)
        .outerjoin(ExamRecord, ExamEnrollment.exam_record_id == ExamRecord.id)
        .where(ExamEnrollment.student_id == student_id)
        .order_by(ExamBoard.exam_date.desc())
    )
    final_rows = (await db.execute(finals_stmt)).mappings().all()
    finals = [
        {
            "subject": r["subject"],
            "exam_date": r["exam_date"].isoformat(),
            "final_grade": float(r["final_grade"]) if r["final_grade"] is not None else None,
            "enrollment_status": "ENROLLED" if r["status"] == "INSCRIPTO" else "CANCELLED",
            "record_number": r["record_number"],
            "record_status": RECORD_STATUS_FROM_DB.get(r["record_status"], r["record_status"])
            if r["record_status"]
            else None,
        }
        for r in final_rows
    ]

    passed_grades = [
        float(r["final_grade"])
        for r in final_rows
        if r["final_grade"] is not None and float(r["final_grade"]) >= 4.0 and r["status"] == "INSCRIPTO"
    ]
    avg_grade = round(sum(passed_grades) / len(passed_grades), 2) if passed_grades else None

    return {
        "student": {
            "file_number": student.file_number,
            "full_name": f"{student.last_name}, {student.first_name}",
            "dni": student.dni,
            "status": "ACTIVE" if student.status == "ACTIVO" else "INACTIVE",
        },
        "careers": careers,
        "course_enrollments": enrollments,
        "final_exams": finals,
        "approved_finals_average": avg_grade,
    }


async def get_student_attendance(
    db: AsyncSession,
    student_id: int,
) -> List[Dict[str, Any]]:
    """Calculate accumulated attendance percentage per subject for a student (RF-029)."""
    present_expr = func.sum(case((Attendance.present == True, 1), else_=0))
    total_expr = func.count(Attendance.id)

    stmt = (
        select(
            Subject.name.label("subject"),
            AcademicCycle.year.label("academic_year"),
            CourseEnrollment.condition,
            total_expr.label("total_classes"),
            present_expr.label("attended_classes"),
        )
        .join(Subject, CourseEnrollment.subject_id == Subject.id)
        .join(AcademicCycle, CourseEnrollment.academic_cycle_id == AcademicCycle.id)
        .join(Attendance, Attendance.course_enrollment_id == CourseEnrollment.id)
        .where(CourseEnrollment.student_id == student_id)
        .group_by(Subject.name, AcademicCycle.year, CourseEnrollment.condition)
        .order_by(AcademicCycle.year.desc(), Subject.name)
    )
    rows = (await db.execute(stmt)).mappings().all()
    return [
        {
            "subject": r["subject"],
            "academic_year": r["academic_year"],
            "condition": COURSE_CONDITION_FROM_DB.get(r["condition"], r["condition"]),
            "total_classes": int(r["total_classes"]),
            "attended_classes": int(r["attended_classes"]),
            "attendance_percentage": round((int(r["attended_classes"]) / int(r["total_classes"])) * 100, 2)
            if r["total_classes"]
            else 0.0,
        }
        for r in rows
    ]


async def check_student_prerequisites(
    db: AsyncSession,
    student_id: int,
    subject_name: str,
) -> Dict[str, Any]:
    """
    Validate TO_ENROLL and TO_TAKE_EXAM prerequisites for a student (RF-021 / RF-026),
    considering regular/promoted courses and passed final exams (>= 4.00).
    """
    subj_stmt = (
        select(
            Subject.id,
            Subject.name,
            Career.name.label("career"),
            StudyPlan.year.label("plan_year"),
        )
        .join(StudyPlan, Subject.study_plan_id == StudyPlan.id)
        .join(Career, StudyPlan.career_id == Career.id)
        .where(
            Career.active == True,
            StudyPlan.active == True,
            Subject.name.ilike(f"%{subject_name.strip()}%"),
        )
        .order_by(Career.name, Subject.name)
    )
    subjects = (await db.execute(subj_stmt)).mappings().all()
    if not subjects:
        return {
            "searched_subject": subject_name,
            "matches": [],
            "message": "No matching subject found in active study plans.",
        }

    course_rows = (
        await db.execute(
            select(CourseEnrollment.subject_id, CourseEnrollment.condition)
            .where(CourseEnrollment.student_id == student_id)
        )
    ).all()
    conditions_by_subject: Dict[int, set[str]] = {}
    for sid, cond in course_rows:
        conditions_by_subject.setdefault(sid, set()).add(cond)

    final_rows = (
        await db.execute(
            select(ExamBoard.subject_id, ExamEnrollment.final_grade)
            .join(ExamBoard, ExamEnrollment.exam_board_id == ExamBoard.id)
            .where(
                ExamEnrollment.student_id == student_id,
                ExamEnrollment.status == "INSCRIPTO",
                ExamEnrollment.final_grade >= 4.00,
            )
        )
    ).all()
    passed_finals: Dict[int, float] = {}
    for sid, grade in final_rows:
        passed_finals[sid] = max(passed_finals.get(sid, 0.0), float(grade))

    ReqSubject = aliased(Subject)
    matches = []
    for subj in subjects:
        prereq_stmt = (
            select(
                Prerequisite.prerequisite_type,
                ReqSubject.id.label("req_id"),
                ReqSubject.name.label("req_name"),
            )
            .join(ReqSubject, Prerequisite.required_subject_id == ReqSubject.id)
            .where(Prerequisite.subject_id == subj["id"])
            .order_by(Prerequisite.prerequisite_type, ReqSubject.name)
        )
        reqs = (await db.execute(prereq_stmt)).mappings().all()

        req_details = []
        eligible_to_enroll = True
        eligible_for_exam = True

        for r in reqs:
            req_id = r["req_id"]
            conds = conditions_by_subject.get(req_id, set())
            final_grade = passed_finals.get(req_id)
            has_final_or_promo = (final_grade is not None) or ("PROMOCIONADO" in conds)
            has_regular = has_final_or_promo or ("REGULAR" in conds)

            if r["prerequisite_type"] == "PARA_CURSAR":
                satisfied = has_regular
                if not satisfied:
                    eligible_to_enroll = False
            else:
                satisfied = has_final_or_promo
                if not satisfied:
                    eligible_for_exam = False

            req_details.append({
                "type": PREREQ_TYPE_FROM_DB.get(r["prerequisite_type"], r["prerequisite_type"]),
                "required_subject": r["req_name"],
                "course_conditions": sorted(
                    COURSE_CONDITION_FROM_DB.get(c, c) for c in conds
                ) if conds else ["NOT_TAKEN"],
                "passed_final_grade": final_grade,
                "satisfied": satisfied,
            })

        matches.append({
            "subject_id": subj["id"],
            "subject": subj["name"],
            "career": subj["career"],
            "plan_year": subj["plan_year"],
            "eligible_to_enroll": eligible_to_enroll,
            "eligible_for_exam": eligible_for_exam,
            "requirements": req_details,
        })

    return {"searched_subject": subject_name, "matches": matches}


async def get_teacher_course_rosters(
    db: AsyncSession,
    teacher_id: int,
    subject_name: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Return subjects assigned to the teacher and enrolled student rosters (RF-014 / RF-015)."""
    assign_stmt = (
        select(
            SubjectAssignment.subject_id,
            SubjectAssignment.academic_cycle_id,
            SubjectAssignment.role,
            Subject.name.label("subject"),
            Career.name.label("career"),
            AcademicCycle.year.label("academic_year"),
        )
        .join(Subject, SubjectAssignment.subject_id == Subject.id)
        .join(StudyPlan, Subject.study_plan_id == StudyPlan.id)
        .join(Career, StudyPlan.career_id == Career.id)
        .join(AcademicCycle, SubjectAssignment.academic_cycle_id == AcademicCycle.id)
        .where(SubjectAssignment.teacher_id == teacher_id)
        .order_by(AcademicCycle.year.desc(), Subject.name)
    )
    if subject_name:
        assign_stmt = assign_stmt.where(Subject.name.ilike(f"%{subject_name.strip()}%"))

    assignments = (await db.execute(assign_stmt)).mappings().all()
    rosters = []

    for a in assignments:
        roster_stmt = (
            select(
                Student.file_number,
                Student.last_name,
                Student.first_name,
                Student.email,
                CourseEnrollment.condition,
                CourseEnrollment.late_enrollment,
            )
            .join(Student, CourseEnrollment.student_id == Student.id)
            .where(
                CourseEnrollment.subject_id == a["subject_id"],
                CourseEnrollment.academic_cycle_id == a["academic_cycle_id"],
            )
            .order_by(Student.last_name, Student.first_name)
        )
        students = [
            {
                "file_number": s["file_number"],
                "full_name": f"{s['last_name']}, {s['first_name']}",
                "email": s["email"],
                "condition": COURSE_CONDITION_FROM_DB.get(s["condition"], s["condition"]),
                "late_enrollment": s["late_enrollment"],
            }
            for s in (await db.execute(roster_stmt)).mappings().all()
        ]
        rosters.append({
            "career": a["career"],
            "subject": a["subject"],
            "academic_year": a["academic_year"],
            "teaching_role": BOARD_ROLE_FROM_DB.get(a["role"], a["role"]),
            "enrolled_count": len(students),
            "students": students,
        })

    return rosters


async def get_teacher_exam_boards(
    db: AsyncSession,
    teacher_id: int,
) -> List[Dict[str, Any]]:
    """Return exam boards where the authenticated teacher serves as chair or observer (RF-017)."""
    stmt = (
        select(
            ExamBoard.id.label("exam_board_id"),
            Subject.name.label("subject"),
            ExamBoard.exam_date,
            ExamBoard.exam_time,
            ExamBoard.chair_teacher_id,
            ExamRecord.record_number,
            ExamRecord.status.label("record_status"),
        )
        .join(Subject, ExamBoard.subject_id == Subject.id)
        .outerjoin(ExamRecord, ExamRecord.exam_board_id == ExamBoard.id)
        .where(
            or_(
                ExamBoard.chair_teacher_id == teacher_id,
                ExamBoard.observer_teacher_id == teacher_id,
            )
        )
        .order_by(ExamBoard.exam_date.desc())
    )
    rows = (await db.execute(stmt)).mappings().all()
    return [
        {
            "exam_board_id": r["exam_board_id"],
            "subject": r["subject"],
            "exam_date": r["exam_date"].isoformat(),
            "exam_time": r["exam_time"].isoformat(),
            "board_role": "CHAIR" if r["chair_teacher_id"] == teacher_id else "OBSERVER",
            "record_number": r["record_number"],
            "record_status": RECORD_STATUS_FROM_DB.get(r["record_status"], r["record_status"])
            if r["record_status"]
            else None,
        }
        for r in rows
    ]


async def get_student_admin_detail(
    db: AsyncSession,
    file_number: Optional[int] = None,
    dni: Optional[str] = None,
) -> Dict[str, Any]:
    """Lookup student record, history, and attendance for PRECEPTOR or ADMIN (RF-003)."""
    stmt = select(Student)
    if file_number is not None:
        stmt = stmt.where(Student.file_number == file_number)
    elif dni:
        stmt = stmt.where(Student.dni == dni.strip())
    else:
        return {"error": "Either file_number or dni must be provided."}

    student = (await db.execute(stmt)).scalar_one_or_none()
    if not student:
        return {"error": "Student not found."}

    history = await get_student_history(db, student.id)
    history["attendance"] = await get_student_attendance(db, student.id)
    return history
