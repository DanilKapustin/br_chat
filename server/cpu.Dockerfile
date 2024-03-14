# syntax=docker/dockerfile:1
# Keep this syntax directive! It's used to enable Docker BuildKit

################################
# Base
# Sets up all our shared environment variables
################################
FROM python:3.10-slim AS base

# app environment variables
ENV DATABASE_HOST=postgres
ENV DATABASE_PORT=5432
ENV DATABASE_NAME=br
ENV DATABASE_USER=br
ENV DATABASE_PASSWORD=br
ENV REDIS_HOST=redis
ENV REDIS_PORT=6379
ENV REDIS_PASSWORD=loL311tSCc
ENV CHROMA_HOST=chroma
ENV CHROMA_PORT=7777

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.7.0 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

# prepend poetry and venv to path
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

################################
# App Builder
# Used to build deps + create our virtual environment
################################
FROM base AS app-builder

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        curl \
        build-essential \
    && apt-get clean

# install poetry - respects $POETRY_VERSION & $POETRY_HOME
# The --mount will mount the buildx cache directory to where
# Poetry and Pip store their cache so that they can re-use it
RUN --mount=type=cache,target=/root/.cache \
    curl -sSL https://install.python-poetry.org | python3 -

# copy project requirement files here to ensure they will be cached.
WORKDIR $PYSETUP_PATH
COPY poetry.lock pyproject.toml ./

# install runtime deps - uses $POETRY_VIRTUALENVS_IN_PROJECT internally
RUN --mount=type=cache,target=/root/.cache \
    poetry install --sync --no-root \
    && pip install llama-cpp-python==0.2.22

################################
# API
# API runtime
################################
FROM base AS api

# Environment variables
ENV FASTAPI_ENV=production
ENV API_CORS_ORIGIN=""
ENV API_PORT=8000
ENV API_WORKERS=4
ENV FILE_STORAGE_PATH=/app/file

COPY --from=app-builder $PYSETUP_PATH $PYSETUP_PATH
COPY . /app/

WORKDIR /app
VOLUME /app/file

EXPOSE 8000
CMD ["bash", "scripts/run-app.sh"]


################################
# Background
# Background runtime
################################
FROM base AS background

# Environment variables
ENV E5_MODEL_PATH=/app/model/e5
ENV BACKGROUND_WORKERS=4

COPY --from=app-builder $PYSETUP_PATH $PYSETUP_PATH
COPY . /app/

WORKDIR /app
VOLUME /app/model
VOLUME /app/file

RUN python -m spacy download en_core_web_sm \
    && python -m spacy download ru_core_news_sm

CMD ["bash", "scripts/run-background.sh"]
