FROM python:3.11-slim

ARG INSTALL_ML=false
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Cài đặt dependencies từ requirements
COPY requirements.txt ./
COPY requirements-dev.txt ./
RUN pip install --upgrade pip && \
    pip install -r requirements-dev.txt

# Cài đặt thêm ML dependencies nếu kích hoạt flag
COPY requirements-ml.txt ./
RUN if [ "$INSTALL_ML" = "true" ]; then \
      pip install torch --index-url https://download.pytorch.org/whl/cpu && \
      pip install -r requirements-ml.txt; \
    fi

COPY src ./src
COPY configs ./configs
COPY scripts ./scripts
COPY pyproject.toml ./
RUN pip install -e . --no-deps

EXPOSE 8000
CMD ["uvicorn", "ticket_triage.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]