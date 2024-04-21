FROM mcr.microsoft.com/devcontainers/python:3.11

ENV PYTHONUNBUFFERED 1

RUN apt-get update \
  && apt-get install -y \
  libcairo2 \
  libgdk-pixbuf2.0-0 \
  liblcms2-2 \
  libopenjp2-7 \
  libpango-1.0-0 \
  libpangocairo-1.0-0 \
  libssl3 \
  libtiff6 \
  libwebp7 \
  libxml2 \
  libpq5 \
  shared-mime-info \
  mime-support

RUN echo 'image/webp webp' >> /etc/mime.types
RUN echo 'image/avif avif' >> /etc/mime.types

WORKDIR /app
RUN pip install poetry==1.8.2
RUN poetry config virtualenvs.create false
COPY poetry.lock pyproject.toml /app/
RUN poetry install --no-root


COPY . /app

ARG STATIC_URL
ENV STATIC_URL ${STATIC_URL:-/static/}
ARG SECRET_KEY
ENV SECRET_KEY ${SECRET_KEY:-changeme}
# RUN STATIC_URL=${STATIC_URL} python manage.py collectstatic --no-input
# RUN python manage.py migrate

EXPOSE 8000

LABEL org.opencontainers.image.title="weenspace/weenspace"                                  \
      org.opencontainers.image.description="\
A modular, high performance, headless e-commerce platform built with Python, \
GraphQL, Django, and ReactJS."                                                         \
      org.opencontainers.image.url="https://weenspace.com/"                                \
      org.opencontainers.image.source="https://github.com/weenspace/weenspace"               \
      org.opencontainers.image.authors="WeenSpace Platform (https://weenspace.com)"           \
      org.opencontainers.image.licenses="MIT"

CMD ["gunicorn", "--bind", ":8000", "--workers", "4", "--worker-class", "weenspace.asgi.gunicorn_worker.UvicornWorker", "weenspace.asgi:application"]
