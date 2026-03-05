"""Tests for case management endpoints."""

from unittest.mock import patch

from api.db_models import Case


def test_list_cases_empty(client, auth_headers):
    resp = client.get("/api/cases", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["cases"] == []
    assert data["total"] == 0


@patch("api.routes.cases_routes._bg_process")
def test_create_case(mock_bg, client, auth_headers, admin_user, db_session):
    resp = client.post(
        "/api/cases",
        json={"briefing": "Cliente quer registrar uma marca."},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "pending"
    assert data["id"]

    case = db_session.query(Case).filter(Case.id == data["id"]).first()
    assert case is not None
    assert case.briefing == "Cliente quer registrar uma marca."


def test_list_cases_with_results(client, auth_headers, admin_user, db_session):
    case = Case(
        briefing="Test briefing",
        user_id=admin_user.id,
        status="completed",
        materia="Marcas",
        cliente_nome="João Silva",
        caso_id="20260304-abc123",
    )
    db_session.add(case)
    db_session.commit()

    resp = client.get("/api/cases", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["cases"][0]["cliente_nome"] == "João Silva"


def test_list_cases_filter_materia(client, auth_headers, admin_user, db_session):
    db_session.add(Case(briefing="b1", user_id=admin_user.id, materia="Marcas", status="completed"))
    db_session.add(Case(briefing="b2", user_id=admin_user.id, materia="Civil", status="completed"))
    db_session.commit()

    resp = client.get("/api/cases?materia=Marcas", headers=auth_headers)
    data = resp.json()
    assert data["total"] == 1
    assert data["cases"][0]["materia"] == "Marcas"


def test_list_cases_search(client, auth_headers, admin_user, db_session):
    db_session.add(Case(briefing="b1", user_id=admin_user.id, cliente_nome="João Silva", status="completed"))
    db_session.add(Case(briefing="b2", user_id=admin_user.id, cliente_nome="Maria Santos", status="completed"))
    db_session.commit()

    resp = client.get("/api/cases?search=João", headers=auth_headers)
    data = resp.json()
    assert data["total"] == 1


def test_get_case_detail(client, auth_headers, admin_user, db_session):
    case = Case(
        briefing="Test briefing completo",
        user_id=admin_user.id,
        status="completed",
        materia="Marcas",
        panorama_md="## Panorama",
    )
    db_session.add(case)
    db_session.commit()

    resp = client.get(f"/api/cases/{case.id}", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["briefing"] == "Test briefing completo"
    assert data["panorama_md"] == "## Panorama"


def test_get_case_not_found(client, auth_headers):
    resp = client.get("/api/cases/nonexistent-id", headers=auth_headers)
    assert resp.status_code == 404


def test_case_status(client, auth_headers, admin_user, db_session):
    case = Case(briefing="b", user_id=admin_user.id, status="processing")
    db_session.add(case)
    db_session.commit()

    resp = client.get(f"/api/cases/{case.id}/status", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "processing"
