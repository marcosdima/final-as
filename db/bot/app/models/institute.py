from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    Time,
)
from sqlalchemy.dialects.postgresql import ENUM as PgEnum
from sqlalchemy.orm import relationship

from app.core.database import Base

# PostgreSQL ENUM types defined in the `instituto` schema
UserRolePgEnum = PgEnum(
    "ALUMNO", "DOCENTE", "PRECEPTOR", "ADMINISTRADOR",
    name="rol_usuario", schema="instituto", create_type=False,
)
PrerequisiteTypePgEnum = PgEnum(
    "PARA_CURSAR", "PARA_RENDIR",
    name="tipo_correlatividad", schema="instituto", create_type=False,
)
CycleStatusPgEnum = PgEnum(
    "ABIERTO", "CERRADO",
    name="estado_ciclo", schema="instituto", create_type=False,
)
PeriodTypePgEnum = PgEnum(
    "CURSADA", "EXAMEN",
    name="tipo_periodo", schema="instituto", create_type=False,
)
StudentStatusPgEnum = PgEnum(
    "ACTIVO", "BAJA",
    name="estado_alumno", schema="instituto", create_type=False,
)
CareerEnrollmentStatusPgEnum = PgEnum(
    "ACTIVA", "BAJA",
    name="estado_inscripcion_carrera", schema="instituto", create_type=False,
)
TeacherRolePgEnum = PgEnum(
    "TITULAR", "OBSERVADOR",
    name="cargo_docente", schema="instituto", create_type=False,
)
CourseConditionPgEnum = PgEnum(
    "CURSANDO", "REGULAR", "PROMOCIONADO", "LIBRE",
    name="condicion_cursada", schema="instituto", create_type=False,
)
EvaluationInstancePgEnum = PgEnum(
    "PARCIAL", "TRABAJO_PRACTICO",
    name="instancia_evaluacion", schema="instituto", create_type=False,
)
RecordStatusPgEnum = PgEnum(
    "ABIERTA", "CERRADA",
    name="estado_acta", schema="instituto", create_type=False,
)
ExamEnrollmentStatusPgEnum = PgEnum(
    "INSCRIPTO", "ANULADO",
    name="estado_inscripcion_examen", schema="instituto", create_type=False,
)


class InstituteUser(Base):
    __tablename__ = "usuario"
    __table_args__ = {"schema": "instituto"}

    id = Column(BigInteger, primary_key=True)
    full_name = Column("nombre", String(100), nullable=False)
    email = Column(String(150), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    role = Column("rol", UserRolePgEnum, nullable=False)
    created_at = Column("fecha_alta", DateTime(timezone=True), nullable=False)
    active = Column("activo", Boolean, nullable=False, default=True)

    student = relationship("Student", back_populates="user", uselist=False)
    teacher = relationship("Teacher", back_populates="user", uselist=False)


class Notice(Base):
    __tablename__ = "aviso"
    __table_args__ = {"schema": "instituto"}

    id = Column(BigInteger, primary_key=True)
    published_by_id = Column("publicado_por_id", BigInteger, ForeignKey("instituto.usuario.id"), nullable=False)
    title = Column("titulo", String(200), nullable=False)
    body = Column("cuerpo", Text, nullable=False)
    published_at = Column("fecha_publicacion", DateTime(timezone=True), nullable=False)
    target_role = Column("dirigido_a", UserRolePgEnum, nullable=True)


class Career(Base):
    __tablename__ = "carrera"
    __table_args__ = {"schema": "instituto"}

    id = Column(BigInteger, primary_key=True)
    name = Column("nombre", String(150), nullable=False, unique=True)
    awarded_title = Column("titulo_otorgado", String(200), nullable=False)
    active = Column("activa", Boolean, nullable=False, default=True)

    study_plans = relationship("StudyPlan", back_populates="career")


class StudyPlan(Base):
    __tablename__ = "plan_estudio"
    __table_args__ = {"schema": "instituto"}

    id = Column(BigInteger, primary_key=True)
    career_id = Column("carrera_id", BigInteger, ForeignKey("instituto.carrera.id"), nullable=False)
    year = Column("anio", Integer, nullable=False)
    resolution = Column("resolucion", String(100), nullable=True)
    active = Column("vigente", Boolean, nullable=False, default=True)

    career = relationship("Career", back_populates="study_plans")
    subjects = relationship("Subject", back_populates="study_plan")


class Subject(Base):
    __tablename__ = "materia"
    __table_args__ = {"schema": "instituto"}

    id = Column(BigInteger, primary_key=True)
    study_plan_id = Column("plan_estudio_id", BigInteger, ForeignKey("instituto.plan_estudio.id"), nullable=False)
    name = Column("nombre", String(150), nullable=False)
    year_in_plan = Column("anio_en_plan", Integer, nullable=False)
    workload_hours = Column("carga_horaria", Integer, nullable=False)

    study_plan = relationship("StudyPlan", back_populates="subjects")


class Prerequisite(Base):
    __tablename__ = "correlatividad"
    __table_args__ = {"schema": "instituto"}

    id = Column(BigInteger, primary_key=True)
    subject_id = Column("materia_id", BigInteger, ForeignKey("instituto.materia.id"), nullable=False)
    required_subject_id = Column("materia_correlativa_id", BigInteger, ForeignKey("instituto.materia.id"), nullable=False)
    prerequisite_type = Column("tipo", PrerequisiteTypePgEnum, nullable=False)


class AcademicCycle(Base):
    __tablename__ = "ciclo_lectivo"
    __table_args__ = {"schema": "instituto"}

    id = Column(BigInteger, primary_key=True)
    year = Column("anio", Integer, nullable=False, unique=True)
    status = Column("estado", CycleStatusPgEnum, nullable=False)


class EnrollmentPeriod(Base):
    __tablename__ = "periodo_inscripcion"
    __table_args__ = {"schema": "instituto"}

    id = Column(BigInteger, primary_key=True)
    academic_cycle_id = Column("ciclo_lectivo_id", BigInteger, ForeignKey("instituto.ciclo_lectivo.id"), nullable=False)
    period_type = Column("tipo", PeriodTypePgEnum, nullable=False)
    start_date = Column("fecha_inicio", Date, nullable=False)
    end_date = Column("fecha_fin", Date, nullable=False)


class Student(Base):
    __tablename__ = "alumno"
    __table_args__ = {"schema": "instituto"}

    id = Column(BigInteger, primary_key=True)
    user_id = Column("usuario_id", BigInteger, ForeignKey("instituto.usuario.id"), nullable=False, unique=True)
    file_number = Column("legajo", Integer, nullable=False, unique=True)
    first_name = Column("nombre", String(100), nullable=False)
    last_name = Column("apellido", String(100), nullable=False)
    dni = Column(String(20), nullable=False, unique=True)
    birth_date = Column("fecha_nacimiento", Date, nullable=False)
    email = Column(String(150), nullable=False)
    phone = Column("telefono", String(50), nullable=True)
    status = Column("estado", StudentStatusPgEnum, nullable=False)

    user = relationship("InstituteUser", back_populates="student")


class CareerEnrollment(Base):
    __tablename__ = "inscripcion_carrera"
    __table_args__ = {"schema": "instituto"}

    id = Column(BigInteger, primary_key=True)
    student_id = Column("alumno_id", BigInteger, ForeignKey("instituto.alumno.id"), nullable=False)
    career_id = Column("carrera_id", BigInteger, ForeignKey("instituto.carrera.id"), nullable=False)
    enrolled_date = Column("fecha_inscripcion", Date, nullable=False)
    status = Column("estado", CareerEnrollmentStatusPgEnum, nullable=False)


class Teacher(Base):
    __tablename__ = "docente"
    __table_args__ = {"schema": "instituto"}

    id = Column(BigInteger, primary_key=True)
    user_id = Column("usuario_id", BigInteger, ForeignKey("instituto.usuario.id"), nullable=False, unique=True)
    file_number = Column("legajo", Integer, nullable=False, unique=True)
    full_name = Column("nombre", String(150), nullable=False)
    cuil = Column(String(20), nullable=False, unique=True)
    email = Column(String(150), nullable=False)
    active = Column("activo", Boolean, nullable=False, default=True)

    user = relationship("InstituteUser", back_populates="teacher")


class SubjectAssignment(Base):
    __tablename__ = "asignacion_materia"
    __table_args__ = {"schema": "instituto"}

    id = Column(BigInteger, primary_key=True)
    teacher_id = Column("docente_id", BigInteger, ForeignKey("instituto.docente.id"), nullable=False)
    subject_id = Column("materia_id", BigInteger, ForeignKey("instituto.materia.id"), nullable=False)
    academic_cycle_id = Column("ciclo_lectivo_id", BigInteger, ForeignKey("instituto.ciclo_lectivo.id"), nullable=False)
    role = Column("cargo", TeacherRolePgEnum, nullable=False)


class CourseEnrollment(Base):
    __tablename__ = "inscripcion_cursada"
    __table_args__ = {"schema": "instituto"}

    id = Column(BigInteger, primary_key=True)
    subject_id = Column("materia_id", BigInteger, ForeignKey("instituto.materia.id"), nullable=False)
    student_id = Column("alumno_id", BigInteger, ForeignKey("instituto.alumno.id"), nullable=False)
    academic_cycle_id = Column("ciclo_lectivo_id", BigInteger, ForeignKey("instituto.ciclo_lectivo.id"), nullable=False)
    enrolled_date = Column("fecha", Date, nullable=False)
    condition = Column("condicion", CourseConditionPgEnum, nullable=False)
    late_enrollment = Column("fuera_de_termino", Boolean, nullable=False, default=False)


class Attendance(Base):
    __tablename__ = "asistencia"
    __table_args__ = {"schema": "instituto"}

    id = Column(BigInteger, primary_key=True)
    course_enrollment_id = Column("inscripcion_cursada_id", BigInteger, ForeignKey("instituto.inscripcion_cursada.id"), nullable=False)
    class_date = Column("fecha_clase", Date, nullable=False)
    present = Column("presente", Boolean, nullable=False)


class PartialGrade(Base):
    __tablename__ = "calificacion_parcial"
    __table_args__ = {"schema": "instituto"}

    id = Column(BigInteger, primary_key=True)
    course_enrollment_id = Column("inscripcion_cursada_id", BigInteger, ForeignKey("instituto.inscripcion_cursada.id"), nullable=False)
    instance = Column("instancia", EvaluationInstancePgEnum, nullable=False)
    instance_number = Column("numero_instancia", Integer, nullable=False, default=1)
    grade = Column("nota", Numeric(4, 2), nullable=False)
    graded_date = Column("fecha_carga", Date, nullable=False)


class ExamBoard(Base):
    __tablename__ = "mesa_examen"
    __table_args__ = {"schema": "instituto"}

    id = Column(BigInteger, primary_key=True)
    subject_id = Column("materia_id", BigInteger, ForeignKey("instituto.materia.id"), nullable=False)
    academic_cycle_id = Column("ciclo_lectivo_id", BigInteger, ForeignKey("instituto.ciclo_lectivo.id"), nullable=False)
    exam_date = Column("fecha", Date, nullable=False)
    exam_time = Column("hora", Time, nullable=False)
    chair_teacher_id = Column("docente_titular_id", BigInteger, ForeignKey("instituto.docente.id"), nullable=False)
    observer_teacher_id = Column("docente_observador_id", BigInteger, ForeignKey("instituto.docente.id"), nullable=True)


class ExamRecord(Base):
    __tablename__ = "acta_examen"
    __table_args__ = {"schema": "instituto"}

    id = Column(BigInteger, primary_key=True)
    exam_board_id = Column("mesa_examen_id", BigInteger, ForeignKey("instituto.mesa_examen.id"), nullable=False, unique=True)
    record_number = Column("numero", Integer, nullable=False, unique=True)
    status = Column("estado", RecordStatusPgEnum, nullable=False)
    closed_at = Column("fecha_cierre", DateTime(timezone=True), nullable=True)


class ExamEnrollment(Base):
    __tablename__ = "inscripcion_examen"
    __table_args__ = {"schema": "instituto"}

    id = Column(BigInteger, primary_key=True)
    exam_board_id = Column("mesa_examen_id", BigInteger, ForeignKey("instituto.mesa_examen.id"), nullable=False)
    student_id = Column("alumno_id", BigInteger, ForeignKey("instituto.alumno.id"), nullable=False)
    exam_record_id = Column("acta_examen_id", BigInteger, ForeignKey("instituto.acta_examen.id"), nullable=True)
    enrolled_date = Column("fecha", Date, nullable=False)
    late_enrollment = Column("fuera_de_termino", Boolean, nullable=False, default=False)
    final_grade = Column("nota_final", Numeric(4, 2), nullable=True)
    status = Column("estado", ExamEnrollmentStatusPgEnum, nullable=False)


class DocumentTemplate(Base):
    __tablename__ = "plantilla_documento"
    __table_args__ = {"schema": "instituto"}

    id = Column(BigInteger, primary_key=True)
    uploaded_by_user_id = Column("cargada_por_usuario_id", BigInteger, ForeignKey("instituto.usuario.id"), nullable=False)
    name = Column("nombre", String(150), nullable=False)
    record_type = Column("tipo_acta", String(100), nullable=False)
    file_path = Column("archivo", String(255), nullable=False)
    version = Column(Integer, nullable=False, default=1)
    uploaded_at = Column("fecha_carga", DateTime(timezone=True), nullable=False)
