.PHONY: up demo down reset-db gen-api seed lint test install

install:
	cd ticket-triage-be && pip install -r requirements-dev.txt
	cd ticket-triage-fe && pnpm install

up:
	docker compose -f docker.yaml up --build

demo:
	docker compose -f docker.yaml -f docker-compose.demo.yml up --build

down:
	docker compose -f docker.yaml down

reset-db:
	docker compose -f docker.yaml down -v && docker compose -f docker.yaml up -d

gen-api:
	docker compose -f docker.yaml exec backend python -c \
	  "from ticket_triage.api.main import app; import json; \
	   print(json.dumps(app.openapi()))" > contracts/openapi.json
	docker compose -f docker.yaml exec frontend pnpm run gen-api

seed:
	docker compose -f docker.yaml exec backend python scripts/seed_demo_data.py

lint:
	docker compose -f docker.yaml exec backend ruff check .
	docker compose -f docker.yaml exec frontend pnpm run check

test:
	docker compose -f docker.yaml exec backend pytest -v
	docker compose -f docker.yaml exec frontend pnpm run test
