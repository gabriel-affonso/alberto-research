# syntax=docker/dockerfile:1
#
# alberto-research runtime image.
#
# Multi-stage: the builder compiles wheels in an isolated virtualenv, and the
# runtime stage only receives that virtualenv plus the package source. No
# compilers, pip caches or build tooling reach the final image.
#
# Database migrations are bundled inside the package
# (src/alberto_research/migrations/*.sql) and ship in the wheel, so the image
# needs no separate migration copy step.

# -----------------------------------------------------------------------------
# Builder
# -----------------------------------------------------------------------------
FROM python:3.12-slim-bookworm AS builder

# Pin toolchain versions so rebuilds are reproducible.
ARG PIP_VERSION=24.2
ARG SETUPTOOLS_VERSION=75.1.0
ARG WHEEL_VERSION=0.44.0

ENV PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /build

# The base image already carries the OS trust store, so no apt packages are
# needed here and there are no package lists to clean up. Only pip and the
# build backend are pinned; hadolint's DL3013 does not model exact `==` pins.
# hadolint ignore=DL3013
RUN python -m venv "$VIRTUAL_ENV" \
    && pip install --no-cache-dir \
        "pip==${PIP_VERSION}" \
        "setuptools==${SETUPTOOLS_VERSION}" \
        "wheel==${WHEEL_VERSION}"

# Copy only metadata first so dependency resolution is cached independently of
# source edits.
COPY pyproject.toml README.md LICENSE ./
COPY src/ ./src/

# Install the project itself into the isolated virtualenv.
RUN pip install --no-cache-dir .

# -----------------------------------------------------------------------------
# Runtime
# -----------------------------------------------------------------------------
FROM python:3.12-slim-bookworm AS runtime

ARG BUILD_VERSION=0.0.0
ARG VCS_REF=unknown

LABEL org.opencontainers.image.title="alberto-research" \
      org.opencontainers.image.description="Scientific research automation: discovery, DOI resolution, full-text reading, synthesis and daily digests." \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.source="https://github.com/gabriel-affonso/alberto-research" \
      org.opencontainers.image.version="${BUILD_VERSION}" \
      org.opencontainers.image.revision="${VCS_REF}"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH" \
    ALBERTO_HOME=/home/app

# Fixed UID/GID keep bind-mounted volumes writable across rebuilds.
# --no-log-init avoids the sparse lastlog/lastlogin bookkeeping that upsets
# some image layers.
RUN groupadd --gid 10001 app \
    && useradd --uid 10001 --gid 10001 --create-home --no-log-init \
        --shell /usr/sbin/nologin app

COPY --from=builder /opt/venv /opt/venv

WORKDIR /home/app

USER app

# The CLI exposes --version (provided by the installed console script).
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD ["alberto-research", "--version"]

ENTRYPOINT ["alberto-research"]
CMD ["--help"]
