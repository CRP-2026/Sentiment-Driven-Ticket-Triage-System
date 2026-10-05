FROM python:3.11-slim

ARG INSTALL_ML=false
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app
COPY pyproject.toml ./
COPY src ./src

# Cài torch bản CPU trước để extras "ml" không kéo bản CUDA nặng
RUN if [ "$INSTALL_ML" = "true" ]; then \
      pip install torch --index-url https://download.pytorch.org/whl/cpu && \
      pip install -e ".[dev,ml]"; \
    else \
      pip install -e ".[dev]"; \
    fi

COPY configs ./configs
COPY scripts ./scripts

EXPOSE 8000
# Một worker duy nhất vì max-heap nằm trong RAM
CMD ["uvicorn", "ticket_triage.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]