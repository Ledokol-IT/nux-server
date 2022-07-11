FROM python:3.10.4-slim-buster AS build

ARG BUILD_TYPE

ENV BUILD_TYPE=${BUILD_TYPE} \
  # python:
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PYTHONDONTWRITEBYTECODE=1 \
  # pip:
  PIP_NO_CACHE_DIR=1 \
  PIP_DISABLE_PIP_VERSION_CHECK=1 \
  PIP_DEFAULT_TIMEOUT=100 \
  # dockerize:
  DOCKERIZE_VERSION=v0.6.1 \
  # tini:
  TINI_VERSION=v0.19.0 \
  # poetry:
  POETRY_VERSION=1.1.13 \
  POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_CACHE_DIR='/var/cache/pypoetry' \
  POETRY_HOME='/usr/local'

SHELL ["/bin/bash", "-eo", "pipefail", "-c"]

# System deps, we don't use exact versions because it is hard to update them, pin when needed:
# hadolint ignore=DL3008
RUN apt-get update && apt-get upgrade -y \
  && apt-get install --no-install-recommends -y \
    bash \
    build-essential \
    curl \
    gettext \
    git \
    libpq-dev \
  # Installing `dockerize` utility:
  # https://github.com/jwilder/dockerize
  && curl -sSLO "https://github.com/jwilder/dockerize/releases/download/${DOCKERIZE_VERSION}/dockerize-linux-amd64-${DOCKERIZE_VERSION}.tar.gz" \
  && tar -C /usr/local/bin -xzvf "dockerize-linux-amd64-${DOCKERIZE_VERSION}.tar.gz" \
  && rm "dockerize-linux-amd64-${DOCKERIZE_VERSION}.tar.gz" && dockerize --version \
  # Installing `tini` utility:
  # https://github.com/krallin/tini
  # Get architecture to download appropriate tini release: See https://github.com/wemake-services/wemake-django-template/issues/1725
  && dpkgArch="$(dpkg --print-architecture | awk -F- '{ print $NF }')" \
  && curl -o /usr/local/bin/tini -sSLO "https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini-${dpkgArch}" \
  && chmod +x /usr/local/bin/tini && tini --version \
  # Installing `poetry` package manager:
  # https://github.com/python-poetry/poetry
  && curl -sSL 'https://install.python-poetry.org' | python - \
  && poetry --version \
  # Cleaning cache:
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && apt-get clean -y && rm -rf /var/lib/apt/lists/*

WORKDIR /code

RUN groupadd -r web && useradd -d /code -r -g web web \
  && chown web:web -R /code

# Copy only requirements, to cache them in docker layer
COPY --chown=web:web ./poetry.lock ./pyproject.toml /code/

RUN poetry version && poetry run pip install -U pip




FROM base as image-dev
# Project initialization:
# hadolint ignore=SC2046
RUN poetry install \
    --no-interaction --no-ansi \

COPY --chown=web:web . /code

# Running as non-root user:
USER web

RUN ["chmod", "+x", "/code/scripts/start_dev.sh"]
ENTRYPOINT ["scripts/start_dev.sh"]




FROM base as image-prod

RUN poetry install \
    --no-interaction --no-ansi \
    --no-dev \
  # Cleaning poetry installation's cache for production:
  && rm -rf "$POETRY_CACHE_DIR"

COPY --chown=web:web . /code

# Running as non-root user:
USER web

RUN ["chmod", "+x", "/code/scripts/start_prod.sh"]
ENTRYPOINT ["scripts/start_prod.sh"]
