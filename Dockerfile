FROM python:3.12-slim AS backend-base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=2.2.1 \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app/backend

RUN pip install --no-cache-dir "poetry==$POETRY_VERSION"

COPY backend/pyproject.toml backend/poetry.lock ./
RUN poetry install --no-root --only main

FROM backend-base AS backend-runtime

COPY backend/ ./
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM backend-base AS backend-test

RUN poetry install --no-root --extras test
COPY backend/ ./
CMD ["pytest"]

FROM node:22-alpine AS frontend-deps

WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

FROM frontend-deps AS frontend-build

ARG VITE_API_BASE_URL=/api
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
COPY frontend/ ./
RUN npm run build

FROM nginx:1.27-alpine AS frontend-runtime

COPY frontend/nginx/default.conf.template /etc/nginx/templates/default.conf.template
COPY --from=frontend-build /app/frontend/dist /usr/share/nginx/html

FROM frontend-deps AS frontend-test

ARG VITE_API_BASE_URL=/api
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
COPY frontend/ ./
CMD ["npm", "run", "test"]
