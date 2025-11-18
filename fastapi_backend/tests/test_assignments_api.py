def test_assignments_and_progress_flow(app_client):
    # Create two lessons to be referenced by assignments
    l1 = app_client.post("/lessons", json={"title": "L1"}).json()
    l2 = app_client.post("/lessons", json={"title": "L2"}).json()
    employee_id = "emp-001"

    # Initially, progress is zero
    progress = app_client.get(f"/progress/{employee_id}")
    assert progress.status_code == 200
    p0 = progress.json()
    assert p0["employee_id"] == employee_id
    assert p0["assigned_count"] == 0
    assert p0["completed_count"] == 0
    assert p0["progress_percent"] == 0.0

    # Assign L1 to employee
    res = app_client.post("/assign", json={"lesson_id": l1["id"], "employee_id": employee_id})
    assert res.status_code == 200
    a1 = res.json()
    assert a1["lesson_id"] == l1["id"]
    assert a1["employee_id"] == employee_id

    # Assign L2 to employee
    res = app_client.post("/assign", json={"lesson_id": l2["id"], "employee_id": employee_id})
    assert res.status_code == 200
    a2 = res.json()
    assert a2["lesson_id"] == l2["id"]
    assert a2["employee_id"] == employee_id

    # List assignments should show two
    res = app_client.get(f"/assignments/{employee_id}")
    assert res.status_code == 200
    assignments = res.json()
    assert len(assignments) == 2
    lesson_ids = {a["lesson_id"] for a in assignments}
    assert {l1["id"], l2["id"]}.issubset(lesson_ids)

    # Progress now shows two assigned
    res = app_client.get(f"/progress/{employee_id}")
    assert res.status_code == 200
    p1 = res.json()
    assert p1["assigned_count"] == 2
    assert p1["completed_count"] == 0
    assert p1["progress_percent"] == 0.0

    # Mark completion for L1
    res = app_client.post("/complete", json={"lesson_id": l1["id"], "employee_id": employee_id})
    assert res.status_code == 200
    completion = res.json()
    assert completion["lesson_id"] == l1["id"]
    assert completion["employee_id"] == employee_id

    # Progress should reflect 50%
    res = app_client.get(f"/progress/{employee_id}")
    assert res.status_code == 200
    p2 = res.json()
    assert p2["assigned_count"] == 2
    assert p2["completed_count"] == 1
    assert p2["progress_percent"] == 50.0

    # Mark completion again for same lesson (idempotent via upsert)
    res = app_client.post("/complete", json={"lesson_id": l1["id"], "employee_id": employee_id})
    assert res.status_code == 200

    # Progress remains 50%
    res = app_client.get(f"/progress/{employee_id}")
    assert res.status_code == 200
    p3 = res.json()
    assert p3["completed_count"] == 1
    assert p3["progress_percent"] == 50.0
