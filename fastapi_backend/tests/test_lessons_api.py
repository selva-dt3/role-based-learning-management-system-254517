from typing import List


def test_lessons_crud_flow(app_client):
    # Initially empty list
    res = app_client.get("/lessons")
    assert res.status_code == 200
    assert res.json() == []

    # Create a lesson
    payload = {"title": "Safety 101", "description": "Basics", "file_url": "https://files/a.pdf"}
    res = app_client.post("/lessons", json=payload)
    assert res.status_code == 200
    created = res.json()
    assert created["title"] == payload["title"]
    assert created["description"] == payload["description"]
    assert created["file_url"] == payload["file_url"]
    assert "id" in created
    lesson_id = created["id"]

    # List again should include the created lesson
    res = app_client.get("/lessons")
    assert res.status_code == 200
    lessons: List[dict] = res.json()
    assert any(l["id"] == lesson_id for l in lessons)

    # Update the lesson
    update_payload = {"title": "Safety 101 - Revised", "description": "Updated basics"}
    res = app_client.put(f"/lessons/{lesson_id}", json=update_payload)
    assert res.status_code == 200
    updated = res.json()
    assert updated["id"] == lesson_id
    assert updated["title"] == update_payload["title"]
    assert updated["description"] == update_payload["description"]

    # Delete the lesson
    res = app_client.delete(f"/lessons/{lesson_id}")
    assert res.status_code == 200
    deleted = res.json()
    assert deleted["deleted"] is True
    assert deleted["id"] == lesson_id

    # Deleting again should 404
    res = app_client.delete(f"/lessons/{lesson_id}")
    assert res.status_code == 404
