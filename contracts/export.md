Lệnh 1: Xuất đặc tả OpenAPI từ Backend:
```PowerShell
docker compose -f docker.yaml exec backend python -c "from ticket_triage.api.main import app; import json; print(json.dumps(app.openapi()))" | Out-File -Encoding utf8 contracts/openapi.json
```

Lệnh 2: Cho Frontend tự động dịch thành kiểu TypeScript:

docker compose -f docker.yaml exec frontend pnpm run gen-api
