import json

from starlette.testclient import TestClient

from ticket_triage.api.main import app


def run_rigorous_tests():
    print("=" * 70)
    print("BẮT ĐẦU KIỂM THỬ THỰC TẾ TOÀN DIỆN HỆ THỐNG (LIVE SYSTEM VERIFICATION)")
    print("=" * 70)

    # Sử dụng context manager để kích hoạt toàn bộ sự kiện FastAPI Lifespan (CSDL, Taxonomy, Model, Queue)
    with TestClient(app) as client:
        # 1. Kiểm tra /health
        print("\n[1] Kiểm tra Endpoint /api/v1/health:")
        res = client.get("/api/v1/health")
        assert res.status_code == 200, f"Lỗi health: {res.text}"
        health = res.json()
        print("   ✓ Health response:", json.dumps(health, indent=2))
        assert "is_mock" in health
        assert "model_loaded" in health
        assert "queue_size" in health

        # 2. Kiểm tra /meta/aspects
        print("\n[2] Kiểm tra Endpoint /api/v1/meta/aspects:")
        res = client.get("/api/v1/meta/aspects")
        assert res.status_code == 200
        meta_aspects = res.json()
        print(f"   ✓ Lấy được {len(meta_aspects)} khía cạnh cấu hình: {[a['id'] for a in meta_aspects]}")

        # 3. Kiểm tra /stats/overview và /stats/aspects
        print("\n[3] Kiểm tra Endpoint /api/v1/stats/overview & /stats/aspects:")
        res_ov = client.get("/api/v1/stats/overview")
        assert res_ov.status_code == 200
        stats_ov = res_ov.json()
        print(f"   ✓ Overview: Total tickets = {stats_ov['total_tickets']}, Status counts = {stats_ov['status_counts']}")

        res_asp = client.get("/api/v1/stats/aspects")
        assert res_asp.status_code == 200
        aspects_stats = res_asp.json()
        print(f"   ✓ Aspect matrix: {len(aspects_stats)} nhóm kết hợp khía cạnh x cảm xúc.")

        # 4. Kiểm tra Validation Input (Lỗi 5 trong Issue.md)
        print("\n[4] Kiểm tra phòng thủ Input rỗng / spam / DoS (Issue #5):")
        bad_payloads = [
            ("Khoảng trắng rỗng", {"content": "      "}),
            ("Thẻ HTML rỗng", {"content": "<b></b>"}),
            ("Toàn dấu chấm", {"content": ".........."}),
            ("Chuỗi siêu dài DoS (6000 ký tự)", {"content": "a" * 6000}),
        ]
        for desc, payload in bad_payloads:
            res = client.post("/api/v1/tickets", json=payload)
            assert res.status_code == 422, f"Kỳ vọng 422 Unprocessable Entity cho '{desc}', nhưng nhận {res.status_code}"
            print(f"   ✓ Chặn thành công: '{desc}' -> HTTP 422")

        # 5. Kiểm tra câu ngắn tiếng Anh (Lỗi 1 trong Issue.md)
        print("\n[5] Kiểm tra câu ngắn tiếng Anh không bị nhận nhầm ngoại ngữ (Issue #1):")
        short_tickets = [
            "Item arrived broken",
            "Order missing",
            "Need help",
        ]
        for text in short_tickets:
            res = client.post("/api/v1/tickets", json={"content": text})
            assert res.status_code == 201, f"Lỗi tạo ticket: {res.text}"
            data = res.json()
            assert data["language_flag"] == "en", f"'{text}' phải nhận là en nhưng nhận {data['language_flag']}"
            assert data["needs_manual_review"] is False, f"'{text}' không được gắn cờ manual review"
            print(f"   ✓ '{text}' -> language: {data['language_flag']}, score: {data['priority_score']}, manual_review: {data['needs_manual_review']}")

        # 6. Kiểm tra câu ngoại ngữ thật
        print("\n[6] Kiểm tra câu tiếng Việt ngoại ngữ vẫn gắn cờ thủ công chuẩn xác:")
        res = client.post("/api/v1/tickets", json={"content": "Tôi muốn trả lại đơn hàng này vì bị hỏng."})
        assert res.status_code == 201
        data_vi = res.json()
        assert data_vi["language_flag"] != "en"
        assert data_vi["needs_manual_review"] is True
        assert data_vi["priority_score"] == 50.0
        print(f"   ✓ Tiếng Việt -> language: {data_vi['language_flag']}, score: {data_vi['priority_score']}, manual_review: {data_vi['needs_manual_review']}")

        # 7. Kiểm tra Logic phủ định sự cố vs hạ nhiệt (Lỗi 2 trong Issue.md)
        print("\n[7] Kiểm tra Logic Phủ định (Issue #2):")
        # Khiếu nại "not receive my refund"
        res_refund = client.post("/api/v1/tickets", json={"content": "I did not receive my refund for order #1234."})
        assert res_refund.status_code == 201
        data_rf = res_refund.json()
        urgency_refund = data_rf["priority_breakdown"]["urgency_bonus"]
        assert urgency_refund > 0.0, f"Kỳ vọng urgency_bonus > 0 cho 'did not receive my refund', nhưng nhận {urgency_refund}"
        print(f"   ✓ 'I did not receive my refund' -> Urgency Bonus: +{urgency_refund} (Không bị triệt tiêu sai)")

        # Câu hạ nhiệt "not urgent"
        res_not_urgent = client.post("/api/v1/tickets", json={"content": "This question is not urgent, reply when you are free."})
        assert res_not_urgent.status_code == 201
        data_nu = res_not_urgent.json()
        urgency_not_urgent = data_nu["priority_breakdown"]["urgency_bonus"]
        assert urgency_not_urgent == 0.0, f"Kỳ vọng urgency_bonus == 0 cho 'not urgent', nhưng nhận {urgency_not_urgent}"
        print(f"   ✓ 'This question is not urgent' -> Urgency Bonus: {urgency_not_urgent} (Bị triệt tiêu chuẩn xác)")

        # 8. Kiểm tra Mock Model Word Boundary (Lỗi 3 trong Issue.md)
        print("\n[8] Kiểm tra Ranh giới từ Word Boundary Mock Model (Issue #3):")
        res_issue = client.post("/api/v1/tickets", json={"content": "I have an issue with accessing my profile settings."})
        assert res_issue.status_code == 201
        data_iss = res_issue.json()
        assert data_iss["sentiment_label"] != "negative", "Từ 'issue' không được khớp nhầm 'sue' (dọa kiện)"
        print(f"   ✓ 'I have an issue' -> Sentiment: {data_iss['sentiment_label']} (Không bị nhận nhầm thành lawsuit/sue)")

        # 9. Kiểm tra Múi giờ UTC có hậu tố Z (Lỗi 6 trong Issue.md)
        print("\n[9] Kiểm tra Múi giờ UTC định dạng ISO kết thúc bằng 'Z' (Issue #6):")
        created_at_str = data_iss["created_at"]
        assert created_at_str.endswith("Z"), f"created_at phải kết thúc bằng 'Z', nhưng nhận '{created_at_str}'"
        print(f"   ✓ created_at serialization: '{created_at_str}' (Chuẩn ISO-8601 UTC)")

        # 10. Kiểm tra Vòng đời trạng thái và Đồng bộ Hàng đợi (Lỗi 7 trong Issue.md)
        print("\n[10] Kiểm tra Vòng đời Ticket và Đồng bộ Hàng đợi (Issue #7):")
        test_ticket_id = data_iss["id"]
        h_before = client.get("/api/v1/health").json()
        q_size_before = h_before["queue_size"]

        # Kiểm tra chặn chuyển trạng thái không hợp lệ: new -> resolved trực tiếp bị chặn
        res_invalid_skip = client.patch(f"/api/v1/tickets/{test_ticket_id}/status", json={"status": "resolved"})
        assert res_invalid_skip.status_code == 400, "Không được phép chuyển từ new -> resolved trực tiếp"
        print("   ✓ Chặn thành công bước nhảy cóc không hợp lệ (new -> resolved) -> HTTP 400 Bad Request")

        # Chuyển trạng thái hợp lệ theo quy trình chuẩn: new -> assigned -> in_progress -> resolved
        res_p1 = client.patch(f"/api/v1/tickets/{test_ticket_id}/status", json={"status": "assigned", "assigned_to": "agent_alpha"})
        assert res_p1.status_code == 200
        assert res_p1.json()["status"] == "assigned"

        res_p2 = client.patch(f"/api/v1/tickets/{test_ticket_id}/status", json={"status": "in_progress"})
        assert res_p2.status_code == 200
        assert res_p2.json()["status"] == "in_progress"

        res_p3 = client.patch(f"/api/v1/tickets/{test_ticket_id}/status", json={"status": "resolved"})
        assert res_p3.status_code == 200
        assert res_p3.json()["status"] == "resolved"

        # Kiểm tra queue size đã giảm đi 1 khi ticket được resolved
        h_after = client.get("/api/v1/health").json()
        q_size_after = h_after["queue_size"]
        assert q_size_after == q_size_before - 1, f"Kỳ vọng queue size giảm từ {q_size_before} xuống {q_size_before - 1}, nhưng nhận {q_size_after}"
        print(f"   ✓ Khi ticket #{test_ticket_id} chuyển sang 'resolved', queue_size tự động giảm: {q_size_before} -> {q_size_after}")

        # Kiểm tra chặn chuyển trạng thái không hợp lệ từ resolved -> in_progress
        res_invalid_reopen = client.patch(f"/api/v1/tickets/{test_ticket_id}/status", json={"status": "in_progress"})
        assert res_invalid_reopen.status_code == 400, "Không được phép chuyển từ resolved -> in_progress trực tiếp"
        print("   ✓ Chặn bước chuyển không hợp lệ (resolved -> in_progress) -> HTTP 400 Bad Request")

        # Kiểm tra mở lại ticket hợp lệ (resolved -> new) và kiểm tra ticket được nạp lại vào hàng đợi
        res_reopen = client.patch(f"/api/v1/tickets/{test_ticket_id}/status", json={"status": "new"})
        assert res_reopen.status_code == 200
        assert res_reopen.json()["status"] == "new"
        h_reopen = client.get("/api/v1/health").json()
        assert h_reopen["queue_size"] == q_size_before, "Khi reopen ticket, queue_size phải tăng lại vào hàng đợi"
        print(f"   ✓ Reopen ticket #{test_ticket_id} (resolved -> new) thành công, queue_size phục hồi: {h_reopen['queue_size']}")

        print("\n" + "=" * 70)
        print("HOÀN THÀNH 100% CÁC BƯỚC KIỂM THỬ THỰC TẾ: TẤT CẢ ĐỀU ĐẠT CHUẨN!")
        print("=" * 70)

if __name__ == "__main__":
    run_rigorous_tests()
