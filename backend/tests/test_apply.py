
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def make_workspace(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    target = workspace / "calculator.py"
    target.write_text(
        "def calculate():\n    return 1\n",
        encoding="utf-8",
    )

    return workspace, target


def make_payload(workspace, old_text, new_text, file="calculator.py"):
    return {
        "workspace_path": str(workspace),
        "proposed_file": file,
        "proposed_old_text": old_text,
        "proposed_new_text": new_text,
    }


def test_apply_valid_fix(tmp_path):
    workspace, target = make_workspace(tmp_path)

    response = client.post(
        "/api/apply",
        json=make_payload(
            workspace,
            "return 1",
            "return 2",
        ),
    )

    assert response.status_code == 200
    assert response.json()["status"] == "applied"
    assert "return 2" in target.read_text(encoding="utf-8")


def test_reject_stale_old_text(tmp_path):
    workspace, target = make_workspace(tmp_path)
    original = target.read_text(encoding="utf-8")

    response = client.post(
        "/api/apply",
        json=make_payload(
            workspace,
            "return 999",
            "return 2",
        ),
    )

    assert response.status_code == 400
    assert target.read_text(encoding="utf-8") == original


def test_reject_path_outside_workspace(tmp_path):
    workspace, target = make_workspace(tmp_path)
    original = target.read_text(encoding="utf-8")

    response = client.post(
        "/api/apply",
        json=make_payload(
            workspace,
            "return 1",
            "return 2",
            file="../outside.py",
        ),
    )

    assert response.status_code == 400
    assert target.read_text(encoding="utf-8") == original


def test_reject_missing_file(tmp_path):
    workspace, _ = make_workspace(tmp_path)

    response = client.post(
        "/api/apply",
        json=make_payload(
            workspace,
            "return 1",
            "return 2",
            file="missing.py",
        ),
    )

    assert response.status_code == 400



def test_reject_ambiguous_replacement(tmp_path):
    workspace, target = make_workspace(tmp_path)

    target.write_text(
        "return 1\nreturn 1\n",
        encoding="utf-8",
    )
    original = target.read_text(encoding="utf-8")

    response = client.post(
        "/api/apply",
        json=make_payload(
            workspace,
            "return 1",
            "return 2",
        ),
    )

    assert response.status_code == 400
    assert target.read_text(encoding="utf-8") == original




def test_reject_absolute_path_outside_workspace(tmp_path):
    workspace, target = make_workspace(tmp_path)

    outside_file = tmp_path / "outside.py"
    outside_file.write_text("important = True\n", encoding="utf-8")
    original = outside_file.read_text(encoding="utf-8")

    response = client.post(
        "/api/apply",
        json=make_payload(
            workspace,
            "important = True",
            "important = False",
            file=str(outside_file),
        ),
    )

    assert response.status_code == 400
    assert outside_file.read_text(encoding="utf-8") == original
    assert target.read_text(encoding="utf-8") == (
        "def calculate():\n    return 1\n"
    )