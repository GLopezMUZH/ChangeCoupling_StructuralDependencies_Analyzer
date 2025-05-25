FROM python:3.13.2-slim

RUN apt-get update \
  && apt-get install -y \
  gcc \
  curl \
  libxml2 \
  libarchive13 \
  default-jdk \
  make \
  gettext \
  zlib1g-dev \
  libssl-dev \
  libcurl4-openssl-dev \
  autoconf \
  && rm -rf /var/lib/apt/lists/*

# Install latest Git from source
RUN curl -L https://github.com/git/git/archive/refs/tags/v2.43.0.tar.gz | tar xz \
  && cd git-2.43.0 \
  && make configure \
  && ./configure --prefix=/usr/local \
  && make all \
  && make install \
  && cd .. \
  && rm -rf git-2.43.0

ENV SHELL=/bin/bash \
  POETRY_VERSION=1.8

RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /var/project

COPY pyproject.toml poetry.lock /var/project/

RUN poetry install
