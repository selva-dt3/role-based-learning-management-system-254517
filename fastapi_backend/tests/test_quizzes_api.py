def test_quizzes_crud_flow(app_client):
    # Need a lesson to relate quiz to
    lesson = app_client.post("/lessons", json={"title": "With Quiz"}).json()

    # Initially none
    res = app_client.get("/quizzes")
    assert res.status_code == 200
    assert res.json() == []

    # Create quiz
    payload = {
        "lesson_id": lesson["id"],
        "title": "Quiz A",
        "questions": [{"q": "1+1", "a": "2"}],
    }
    res = app_client.post("/quizzes", json=payload)
    assert res.status_code == 200
    created = res.json()
    assert created["lesson_id"] == payload["lesson_id"]
    assert created["title"] == payload["title"]
    assert created["questions"] == payload["questions"]
    quiz_id = created["id"]

    # List should have 1
    res = app_client.get("/quizzes")
    assert res.status_code == 200
    quizzes = res.json()
    assert any(q["id"] == quiz_id for q in quizzes)

    # Update quiz
    update_payload = {"title": "Quiz A v2", "questions": [{"q": "2+2", "a": "4"}]}
    res = app_client.put(f"/quizzes/{quiz_id}", json=update_payload)
    assert res.status_code == 200
    updated = res.json()
    assert updated["id"] == quiz_id
    assert updated["title"] == update_payload["title"]
    assert updated["questions"] == update_payload["questions"]

    # Delete quiz
    res = app_client.delete(f"/quizzes/{quiz_id}")
    assert res.status_code == 200
    assert res.json()["deleted"] is True

    # Deleting again should 404
    res = app_client.delete(f"/quizzes/{quiz_id}")
    assert res.status_code == 404
