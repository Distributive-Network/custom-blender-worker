FROM python:3.10-slim as poetry-build
WORKDIR /app/

    # python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.0.3 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

# prepend poetry and venv to path
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

COPY . .
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        # deps for installing poetry
        curl \
        # deps for building python deps
        build-essential \
		&& curl -sSL https://install.python-poetry.org | python3 -
RUN poetry build

FROM python:3.10-slim

WORKDIR /app/

COPY --from=poetry-build /app/dist/*.whl ./
RUN apt-get update && \
	apt-get install --no-install-recommends -y curl build-essential && \
	python3 -m pip install ./*.whl && \
	curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
	apt-get install -y nodejs && \
	rm -rf ./*.whl

COPY . .

ENV DCP_SCHEDULER_LOCATION=http://scheduler.eliza.office.distributive.network
