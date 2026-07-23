FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HEALTHCARE_FRONTEND_MODE=local \
    HEALTHCARE_EMBEDDING_BACKEND=keyword

WORKDIR /app

COPY requirements.txt ./requirements.txt
COPY ai-healthcare-intel-engine/requirements.txt ./ai-healthcare-intel-engine/requirements.txt
RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -r requirements.txt

COPY ai-healthcare-intel-engine ./ai-healthcare-intel-engine
COPY .streamlit ./.streamlit

EXPOSE 8501

CMD ["streamlit", "run", "ai-healthcare-intel-engine/frontend/app.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true"]
