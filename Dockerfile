FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements/base.txt .
RUN pip install --user -r base.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
