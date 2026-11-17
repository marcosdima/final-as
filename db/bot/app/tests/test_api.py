from pathlib import Path
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.main import app

REPO_ROOT = Path(__file__).resolve().parents[4]


def _login(client: TestClient, email: str, password: str = "isft189.2026") -> dict:
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200, resp.text
    return resp.json()


def test_health_and_auth_required():
    with TestClient(app) as client:
        health = client.get("/health")
        assert health.status_code == 200
        body = health.json()
        assert body["status"] == "healthy"
        assert "instituto" in body["schemas"]
        assert "isft189" in body["schemas"]
        assert "active" in body["pgvector"]

        # Unauthenticated requests must be rejected with 401
        assert client.get("/api/v1/documents/").status_code == 401
        assert client.get("/api/v1/academic/students/me/history").status_code == 401
        assert client.post("/api/v1/chat/", json={"question": "What is my attendance?"}).status_code == 401

        # OAuth2 form login for Swagger UI Authorize button
        oauth_resp = client.post(
            "/api/v1/auth/token",
            data={"username": "mdimatteo@alumno.isft189.edu.ar", "password": "isft189.2026"},
        )
        assert oauth_resp.status_code == 200
        assert "access_token" in oauth_resp.json()

        # Invalid credentials return 401
        bad_login = client.post(
            "/api/v1/auth/login",
            json={"email": "mdimatteo@alumno.isft189.edu.ar", "password": "wrong-password"},
        )
        assert bad_login.status_code == 401


def test_careers_nested_and_exam_boards_separation():
    with TestClient(app) as client:
        login = _login(client, "mdimatteo@alumno.isft189.edu.ar")
        headers = {"Authorization": f"Bearer {login['access_token']}"}

        # Careers must return nested subjects inside each career object
        careers_resp = client.get("/api/v1/academic/careers", headers=headers)
        assert careers_resp.status_code == 200
        careers = careers_resp.json()
        assert len(careers) == 2
        for career in careers:
            assert "subjects" in career
            assert isinstance(career["subjects"], list)
            assert len(career["subjects"]) >= 20

        # Exam boards must ONLY include EXAM enrollment periods (never COURSE periods)
        boards_resp = client.get("/api/v1/academic/exam-boards", headers=headers)
        assert boards_resp.status_code == 200
        boards_data = boards_resp.json()
        assert len(boards_data["exam_enrollment_periods"]) >= 1
        assert all(p["period_type"] == "EXAM" for p in boards_data["exam_enrollment_periods"])
        assert len(boards_data["exam_boards"]) >= 1

        # Separate enrollment periods endpoint returns both COURSE and EXAM
        periods_resp = client.get("/api/v1/academic/enrollment-periods", headers=headers)
        assert periods_resp.status_code == 200
        period_types = {p["period_type"] for p in periods_resp.json()}
        assert period_types == {"COURSE", "EXAM"}


def test_rbac_and_academic_queries():
    with TestClient(app) as client:
        student_login = _login(client, "mdimatteo@alumno.isft189.edu.ar")
        stu_headers = {"Authorization": f"Bearer {student_login['access_token']}"}
        assert student_login["user"]["role"] == "STUDENT"
        assert student_login["user"]["full_name"] == "Marcos Di Matteo"
        assert student_login["user"]["file_number"] == 1001

        hist = client.get("/api/v1/academic/students/me/history", headers=stu_headers)
        assert hist.status_code == 200
        assert hist.json()["approved_finals_average"] == 7.5

        att = client.get("/api/v1/academic/students/me/attendance", headers=stu_headers)
        assert att.status_code == 200
        assert att.json()[0]["attendance_percentage"] == 80.0

        prereq_bd = client.get(
            "/api/v1/academic/students/me/prerequisites?subject=Base%20de%20Datos",
            headers=stu_headers,
        )
        assert prereq_bd.status_code == 200
        bd_match = next(m for m in prereq_bd.json()["matches"] if m["subject"] == "Base de Datos")
        assert bd_match["eligible_to_enroll"] is True
        assert bd_match["eligible_for_exam"] is True

        # Subject lookup by FK ID and 404 for unknown ID
        prereq_by_id = client.get(
            f"/api/v1/academic/students/me/prerequisites?subject_id={bd_match['subject_id']}",
            headers=stu_headers,
        )
        assert prereq_by_id.status_code == 200
        assert prereq_by_id.json()["matches"][0]["subject"] == "Base de Datos"
        assert (
            client.get(
                "/api/v1/academic/students/me/prerequisites?subject_id=9999",
                headers=stu_headers,
            ).status_code
            == 404
        )
        assert (
            client.get("/api/v1/academic/exam-boards?subject_id=9999", headers=stu_headers).status_code
            == 404
        )

        prereq_pp = client.get(
            "/api/v1/academic/students/me/prerequisites?subject=Pr%C3%A1ctica%20Profesional",
            headers=stu_headers,
        )
        assert prereq_pp.status_code == 200
        assert prereq_pp.json()["matches"][0]["eligible_to_enroll"] is False

        # RBAC checks: student cannot access teacher, admin, or other users' endpoints
        assert client.get("/api/v1/academic/teachers/me/rosters", headers=stu_headers).status_code == 403
        assert (
            client.get("/api/v1/academic/admin/students?file_number=1002", headers=stu_headers).status_code
            == 403
        )
        assert client.get("/api/v1/chat/history?user_id=1", headers=stu_headers).status_code == 403
        assert (
            client.post(
                "/api/v1/documents/ingest",
                headers=stu_headers,
                json={
                    "title": "Unauthorized attempt",
                    "document_type": "other",
                    "full_content": "Unauthorized test content.",
                },
            ).status_code
            == 403
        )

        # Teacher (Leonel Luengo) accesses rosters and exam boards
        teacher_login = _login(client, "lluengo@isft189.edu.ar")
        tea_headers = {"Authorization": f"Bearer {teacher_login['access_token']}"}
        assert teacher_login["user"]["role"] == "TEACHER"
        assert teacher_login["user"]["full_name"] == "Leonel Luengo"

        rosters = client.get("/api/v1/academic/teachers/me/rosters", headers=tea_headers)
        assert rosters.status_code == 200
        assert len(rosters.json()) >= 1
        boards = client.get("/api/v1/academic/teachers/me/exam-boards", headers=tea_headers)
        assert boards.status_code == 200
        assert len(boards.json()) >= 1

        # Second teacher (Juan Carlos Romero)
        teacher2_login = _login(client, "jcromero@isft189.edu.ar")
        assert teacher2_login["user"]["full_name"] == "Juan Carlos Romero"

        # Second student (Nahuel Quiñonez)
        student2_login = _login(client, "nquinonez@alumno.isft189.edu.ar")
        assert student2_login["user"]["full_name"] == "Nahuel Quiñonez"

        # Admin & Preceptor queries student record and validates enum query filter
        preceptor_login = _login(client, "rpaz@isft189.edu.ar")
        prec_headers = {"Authorization": f"Bearer {preceptor_login['access_token']}"}
        assert preceptor_login["user"]["role"] == "PRECEPTOR"
        assert client.get("/api/v1/academic/admin/students", headers=prec_headers).status_code == 400
        stu_prec = client.get("/api/v1/academic/admin/students?file_number=1002", headers=prec_headers)
        assert stu_prec.status_code == 200
        assert stu_prec.json()["student"]["file_number"] == 1002

        admin_login = _login(client, "admin@isft189.edu.ar")
        adm_headers = {"Authorization": f"Bearer {admin_login['access_token']}"}
        stu_adm = client.get("/api/v1/academic/admin/students?file_number=1001", headers=adm_headers)
        assert stu_adm.status_code == 200
        assert stu_adm.json()["student"]["file_number"] == 1001

        bad_type = client.get("/api/v1/documents/?document_type=invalid", headers=adm_headers)
        assert bad_type.status_code == 422

        # Whitespace-only payloads must be rejected with 422 before hitting DB CHECK constraints
        ws_chat = client.post("/api/v1/chat/", headers=stu_headers, json={"question": "   "})
        assert ws_chat.status_code == 422
        ws_ingest = client.post(
            "/api/v1/documents/ingest",
            headers=adm_headers,
            json={"title": "   ", "document_type": "other", "full_content": "Valid text content."},
        )
        assert ws_ingest.status_code == 422


def test_document_ingest_list_delete_and_hybrid_chat():
    with TestClient(app) as client:
        admin_login = _login(client, "admin@isft189.edu.ar")
        adm_headers = {"Authorization": f"Bearer {admin_login['access_token']}"}

        # Non-existent career_id FK must be rejected with 404
        bad_career = client.post(
            "/api/v1/documents/ingest",
            headers=adm_headers,
            json={
                "title": "Invalid Career FK",
                "document_type": "resolution",
                "career_id": 9999,
                "full_content": "Content referencing a non-existent career ID.",
            },
        )
        assert bad_career.status_code == 404

        doc_id = None
        try:
            ingest_resp = client.post(
                "/api/v1/documents/ingest",
                headers=adm_headers,
                json={
                    "title": "Integration Test Resolution 2026",
                    "document_type": "resolution",
                    "career_id": 2,
                    "full_content": "Para Prácticas Profesionalizantes III en Desarrollo de Software se requiere aprobar Desarrollo de sistemas Web.",
                    "chunk_size": 300,
                    "chunk_overlap": 30,
                },
            )
            assert ingest_resp.status_code == 201, ingest_resp.text
            doc_id = ingest_resp.json()["document_id"]
            assert ingest_resp.json()["career_id"] == 2
            assert ingest_resp.json()["career_name"] == "Tecnicatura Superior en Desarrollo de Software"
            assert ingest_resp.json()["chunks_created"] == 1
        finally:
            if doc_id is not None:
                del_resp = client.delete(f"/api/v1/documents/{doc_id}", headers=adm_headers)
                assert del_resp.status_code == 200

        student_login = _login(client, "mdimatteo@alumno.isft189.edu.ar")
        stu_headers = {"Authorization": f"Bearer {student_login['access_token']}"}

        # Non-existent career_id_filter returns 404
        assert (
            client.post(
                "/api/v1/chat/",
                headers=stu_headers,
                json={"question": "¿Qué materias tiene?", "career_id_filter": 9999},
            ).status_code
            == 404
        )

        with patch("app.services.rag.llm_service.generate_with_tools", new=AsyncMock(return_value=None)):
            chat_resp = client.post(
                "/api/v1/chat/",
                headers=stu_headers,
                json={
                    "question": "¿Cuál es mi porcentaje de asistencia en las materias?",
                    "top_k": 3,
                },
            )
            assert chat_resp.status_code == 200, chat_resp.text
            data = chat_resp.json()
            assert data["user_role"] == "STUDENT"
            assert "instituto.asistencia" in data["academic_sources"]
            assert "80.0" in data["answer"]

            chat_rag = client.post(
                "/api/v1/chat/",
                headers=stu_headers,
                json={
                    "question": "¿Qué correlatividad pide Base de Datos en Res. 6175/03?",
                    "career_id_filter": 1,
                    "top_k": 3,
                },
            )
            assert chat_rag.status_code == 200, chat_rag.text
            assert len(chat_rag.json()["retrieved_chunks"]) >= 1

        hist_resp = client.get("/api/v1/chat/history?limit=5", headers=stu_headers)
        assert hist_resp.status_code == 200
        questions = [item["question"] for item in hist_resp.json()]
        assert "¿Cuál es mi porcentaje de asistencia en las materias?" in questions

        # Admin can filter history by instituto.usuario.id (Marcos = 8)
        adm_hist = client.get("/api/v1/chat/history?user_id=8&limit=5", headers=adm_headers)
        assert adm_hist.status_code == 200
        assert len(adm_hist.json()) >= 1
        assert client.get("/api/v1/chat/history?user_id=9999", headers=adm_headers).status_code == 404


def test_ingest_real_pdf_and_tool_calling_orchestration():
    pdf_path = (
        REPO_ROOT
        / "docs"
        / "planes"
        / "DC Tecnicatura Superior en Análisis, Desarrollo y Programación de Aplicaciones - Res. 6175-03 y Anexos.pdf"
    )
    assert pdf_path.exists()

    with TestClient(app) as client:
        admin_login = _login(client, "admin@isft189.edu.ar")
        adm_headers = {"Authorization": f"Bearer {admin_login['access_token']}"}

        # Reject corrupt/non-PDF file with 400 (never 500)
        bad_pdf = client.post(
            "/api/v1/documents/ingest-pdf",
            headers=adm_headers,
            data={"title": "Corrupt PDF", "document_type": "other"},
            files={"file": ("fake.pdf", b"not-a-real-pdf-header", "application/pdf")},
        )
        assert bad_pdf.status_code == 400

        pdf_doc_id = None
        try:
            with pdf_path.open("rb") as f:
                pdf_resp = client.post(
                    "/api/v1/documents/ingest-pdf",
                    headers=adm_headers,
                    data={
                        "title": "PDF Test Res 6175/03",
                        "document_type": "study_plan",
                        "career_id": "1",
                        "chunk_size": "800",
                        "chunk_overlap": "80",
                    },
                    files={"file": (pdf_path.name, f, "application/pdf")},
                )
            assert pdf_resp.status_code == 201, pdf_resp.text
            pdf_doc_id = pdf_resp.json()["document_id"]
            assert pdf_resp.json()["chunks_created"] >= 5
        finally:
            if pdf_doc_id is not None:
                del_resp = client.delete(f"/api/v1/documents/{pdf_doc_id}", headers=adm_headers)
                assert del_resp.status_code == 200

        student_login = _login(client, "mdimatteo@alumno.isft189.edu.ar")
        stu_headers = {"Authorization": f"Bearer {student_login['access_token']}"}

        async def fake_generate_with_tools(
            query, user_context, context_fragments, tools, tool_executor, temperature=0.2, max_rounds=3
        ):
            tool_names = {t["function"]["name"] for t in tools}
            assert "check_my_prerequisites" in tool_names
            assert "get_student_record_admin" not in tool_names
            tool_out = await tool_executor("check_my_prerequisites", {"subject_name": "Base de Datos"})
            return f"Verified result: {tool_out}"

        with patch(
            "app.services.rag.llm_service.generate_with_tools",
            side_effect=fake_generate_with_tools,
        ):
            chat_resp = client.post(
                "/api/v1/chat/",
                headers=stu_headers,
                json={"question": "¿Puedo rendir Base de Datos?"},
            )
            assert chat_resp.status_code == 200, chat_resp.text
            body = chat_resp.json()
            assert "instituto.correlatividad" in body["academic_sources"]
            assert '"eligible_for_exam": true' in body["answer"]
