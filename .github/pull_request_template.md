## 1. Loại thay đổi (Type of Change)
- [ ] `feat`: Tính năng mới
- [ ] `fix`: Sửa lỗi
- [ ] `docs`: Tài liệu
- [ ] `refactor`: Tái cấu trúc mã nguồn
- [ ] `test`: Bổ sung kiểm thử
- [ ] `ci`: Cập nhật luồng tự động

## 2. Liên kết Issue
Fixes #

## 3. Thuộc bài toán nào?
- [ ] Bài toán 1: ABSA Subsystem (Zero-shot NLI)
- [ ] Bài toán 2: Priority Triage & Queue Subsystem
- [ ] Hạ tầng chung / API / UI

## 4. Checklist kiểm tra trước khi Merge
- [ ] Đã chạy linter (`make lint`) và không còn cảnh báo
- [ ] Đã chạy kiểm thử (`make test`) và 100% pass
- [ ] Không commit file `.db`, `.env`, `node_modules`, weights mô hình
- [ ] Có ít nhất 1 thành viên review và approve PR
