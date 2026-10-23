def test_health_endpoint(client):
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert "queue_size" in data

def test_meta_aspects_endpoint(client):
    res = client.get("/api/v1/meta/aspects")
    assert res.status_code == 200
    aspects = res.json()
    assert isinstance(aspects, list)
    if aspects:
        assert "id" in aspects[0]
        assert "weight" in aspects[0]

def test_triage_ticket_endpoint(client):
    payload = {"content": "I was charged twice! Refund immediately or I dispute chargeback!"}
    res = client.post("/api/v1/tickets", json=payload)
    assert res.status_code == 201
    ticket = res.json()
    assert ticket["id"] > 0
    assert ticket["priority_score"] >= 70.0
    assert ticket["priority_level"] == "CRITICAL"
    assert ticket["priority_breakdown"] is not None

def test_get_ticket_detail_and_update_status(client):
    # Tạo ticket
    create_res = client.post("/api/v1/tickets", json={"content": "Need help updating email."})
    t_id = create_res.json()["id"]

    # Đọc chi tiết
    get_res = client.get(f"/api/v1/tickets/{t_id}")
    assert get_res.status_code == 200
    assert get_res.json()["status"] == "new"

    # Cập nhật trạng thái sang assigned
    patch_res = client.patch(
        f"/api/v1/tickets/{t_id}/status",
        json={"status": "assigned", "assigned_to": "agent@example.com"}
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == "assigned"
    assert patch_res.json()["assigned_to"] == "agent@example.com"
