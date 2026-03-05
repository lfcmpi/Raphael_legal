"""Tests for document upload and download endpoints."""

import io
import tempfile
from pathlib import Path

from api.db_models import Case, Document


def test_upload_file(client, auth_headers, admin_user, db_session, tmp_path, monkeypatch):
    # Patch uploads dir
    monkeypatch.setattr("api.routes.documents_routes._UPLOADS_DIR", tmp_path)

    case = Case(briefing="b", user_id=admin_user.id, status="completed")
    db_session.add(case)
    db_session.commit()

    file_content = b"test file content"
    resp = client.post(
        f"/api/cases/{case.id}/upload",
        headers=auth_headers,
        files=[("files", ("test.txt", io.BytesIO(file_content), "text/plain"))],
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["nome_arquivo"] == "test.txt"
    assert data[0]["tamanho"] == len(file_content)


def test_upload_file_too_large(client, auth_headers, admin_user, db_session, monkeypatch, tmp_path):
    monkeypatch.setattr("api.routes.documents_routes._UPLOADS_DIR", tmp_path)
    monkeypatch.setattr("api.routes.documents_routes._MAX_FILE_SIZE", 10)

    case = Case(briefing="b", user_id=admin_user.id, status="completed")
    db_session.add(case)
    db_session.commit()

    resp = client.post(
        f"/api/cases/{case.id}/upload",
        headers=auth_headers,
        files=[("files", ("big.txt", io.BytesIO(b"x" * 100), "text/plain"))],
    )
    assert resp.status_code == 413


def test_download_document(client, auth_headers, admin_user, db_session, tmp_path):
    case = Case(briefing="b", user_id=admin_user.id, status="completed")
    db_session.add(case)
    db_session.commit()

    # Create a file on disk
    file_path = tmp_path / "test.txt"
    file_path.write_text("hello world")

    doc = Document(
        case_id=case.id,
        tipo="upload",
        nome_arquivo="test.txt",
        caminho=str(file_path),
        content_type="text/plain",
        tamanho=11,
    )
    db_session.add(doc)
    db_session.commit()

    resp = client.get(f"/api/documents/{doc.id}/download", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.content == b"hello world"


def test_download_nonexistent_document(client, auth_headers):
    resp = client.get("/api/documents/nonexistent/download", headers=auth_headers)
    assert resp.status_code == 404
